"""Poll LK state and serialize verified writes."""
import asyncio
from datetime import date, timedelta
import time

from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import LKAuthError, LKError, clock_values, holiday_hours, schedule_day, temperature

TEMPERATURES = {
    "comfort_deg", "economy_deg", "holiday_deg", "setback_deg",
    "restrict_deg_min", "restrict_deg_max", "sensor_mode_min_deg", "sensor_mode_max_deg",
}
CHOICES = {
    "backlight_enable": (0, 1), "adaptive_enable": (0, 1), "keylock_enable": (0, 1),
    "bypass_mode": (0, 1, 2), "sensor_mode": (0, 2, 3),
}
DETAIL_FIELDS = TEMPERATURES | CHOICES.keys() | {
    "week_program", "week_program_enable", "week_program_mode", "operation_mode",
    "fireplace_hours", "fireplace_level", "battery", "link_quality", "zone_alarms",
}
SYSTEM_FIELDS = {"date", "override", "override_web", "holiday_counter", "pump_state", "boiler_state", "bypass_state"}
SYSTEM_MODES = {"0": "normal", "1": "holiday", "2": "setback"}
HOLIDAY_END = "holiday_end"


class LKCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, logger, entry, api):
        super().__init__(
            hass, logger, name="LK Systems Webserver",
            config_entry=entry, update_interval=timedelta(minutes=1),
        )
        self.api = api
        self.lock = asyncio.Lock()
        self.rooms = {}
        self.details = {}
        self.system = {}
        self.last_success = None
        self.failures = 0
        self.detail_due = 0

    def snapshot(self):
        return {
            "rooms": {tid: {**room, "details": self.details.get(tid, {})} for tid, room in self.rooms.items()},
            "system": self.system,
            "failures": self.failures,
            "last_success": self.last_success,
        }

    async def _async_update_data(self):
        async with self.lock:
            try:
                self.rooms = await self.api.rooms()
            except LKAuthError as err:
                raise ConfigEntryAuthFailed from err
            except LKError as err:
                self.failures += 1
                if self.last_success is None:
                    raise UpdateFailed(str(err)) from err
                return self.snapshot()
            self.last_success = dt_util.utcnow().isoformat()
            self.failures = 0
            try:
                self.system = {k: v for k, v in (await self.api.system()).items() if k in SYSTEM_FIELDS}
            except LKError:
                self.system = {}
            if time.monotonic() >= self.detail_due:
                self.detail_due = time.monotonic() + 3600
                for tid in self.rooms:
                    try:
                        await self.read_details(tid)
                    except LKError:
                        self.details.pop(tid, None)
            return self.snapshot()

    async def read_details(self, tid):
        details = await self.api.thermostat(tid)
        self.details[tid] = {k: v for k, v in details.items() if k in DETAIL_FIELDS}
        return details

    async def confirm(self, reader, expected):
        for delay in (0, 0.5, 1, 2):
            if delay:
                await asyncio.sleep(delay)
            data = await reader()
            if all(str(data.get(k)) == str(v) for k, v in expected.items()):
                return data
        raise LKError("The Webserver did not confirm the new value.")

    async def run(self, action, args):
        async with self.lock:
            try:
                if action in ("system_mode", "sync_clock"):
                    await self.write_system(action, args)
                else:
                    tid = args["tid"]
                    if type(tid) is not int or tid not in self.rooms:
                        raise ValueError("Unknown thermostat.")
                    details = await self.read_details(tid)
                    if action != "details":
                        await self.write_room(tid, details, action, args)
            except (LKError, ValueError, KeyError, TypeError) as err:
                raise HomeAssistantError(str(err)) from err
            finally:
                self.async_set_updated_data(self.snapshot())

    async def write_room(self, tid, details, action, args):
        async def reader():
            return await self.read_details(tid)

        expected = {}
        writes = []
        if action == "target":
            minimum = int(details["restrict_deg_min"]) / 100
            maximum = int(details["restrict_deg_max"]) / 100
            value = temperature(args["value"], minimum, maximum)
            writes = [("set_room_deg", value), ("operation_mode", 1)]
            expected = {"set_room_deg": value}
            if details["week_program_enable"] == "1":
                expected["operation_mode"] = 1
        elif action == "week_enabled":
            enable = args["value"]
            if type(enable) is not bool:
                raise ValueError("Expected an on/off value.")
            writes = [("week_program_enable", int(enable))]
            if enable:
                writes += [("operation_mode", 0), ("week_program_mode", 2)]
            expected = dict(writes)
        elif action == "day":
            day = args["day"]
            if type(day) is not int or not 0 <= day < 7:
                raise ValueError("Invalid weekday.")
            values = [minute for pair in schedule_day(args["periods"]) for minute in pair]
            current = list(map(int, details["week_program"]))
            if len(current) != 42:
                raise ValueError("Invalid existing schedule.")
            start = 6 * day
            expected_day = current[:start] + values + current[start + 6:]
            # Match LK's two writes per changed period.
            for offset in range(0, 6, 2):
                index = start + offset
                if current[index:index + 2] == values[offset:offset + 2]:
                    continue
                for position in (offset, offset + 1):
                    await self.api.write(tid=tid, index=start + position, week_program=values[position])
            await self.confirm(
                lambda: self.read_week(tid), {"week_program": expected_day}
            )
            return
        elif action == "setting":
            key, value = args["key"], args["value"]
            if key in TEMPERATURES:
                value = temperature(value)
                if key == "restrict_deg_min" and value >= int(details["restrict_deg_max"]):
                    raise ValueError("Minimum must be below maximum.")
                if key == "restrict_deg_max" and value <= int(details["restrict_deg_min"]):
                    raise ValueError("Maximum must be above minimum.")
            elif key in CHOICES:
                if type(value) is not int or value not in CHOICES[key]:
                    raise ValueError("Invalid setting value.")
            elif key == "fireplace_hours":
                if type(value) is not int or not 0 <= value <= 99:
                    raise ValueError("Expected 0–99 hours.")
            elif key == "fireplace_level":
                if type(value) is not int or not 5 <= value <= 100:
                    raise ValueError("Expected 5–100%.")
                value *= 100
            else:
                raise ValueError("Unknown setting.")
            writes = [(key, value)]
            expected = dict(writes)
        else:
            raise ValueError("Unknown action.")
        for key, value in writes:
            await self.api.write(tid=tid, **{key: value})
        result = await self.confirm(reader, expected)
        if action == "target":
            self.rooms[tid]["target"] = int(result["set_room_deg"]) / 100

    async def read_week(self, tid):
        data = await self.read_details(tid)
        return {"week_program": list(map(int, data["week_program"]))}

    async def write_system(self, action, args):
        async def reader():
            data = await self.api.system()
            self.system = {k: v for k, v in data.items() if k in SYSTEM_FIELDS}
            return self.system

        if action == "sync_clock":
            now = dt_util.as_local(dt_util.utcnow())
            for index, value in enumerate(clock_values(now)):
                await self.api.write(index=index, date=value)
            after = await reader()
            accepted = [str(v) for v in clock_values(now)]
            following = [str(v) for v in clock_values(now + timedelta(minutes=1))]
            if after.get("date") not in (accepted, following):
                raise LKError("The Webserver did not confirm the clock.")
            return

        mode = args["value"]
        if type(mode) is not int or mode not in (0, 1, 2):
            raise ValueError("Invalid system mode.")
        expected = {"override_web": mode}
        if mode == 1:
            before = await reader()
            today = date(*map(int, before["date"][:3]))
            hours = holiday_hours(args["end"], today)
            expected["holiday_counter"] = hours
            try:
                await self.api.write(override_web=mode)
                await self.api.write(holiday_counter=hours)
            except LKError:
                await self.api.write(override_web=int(before["override_web"]))
                await reader()
                raise
        else:
            await self.api.write(override_web=mode)
        await self.confirm(reader, expected)

