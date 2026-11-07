"""Local LK Webserver HTTP protocol."""
from datetime import date, datetime
import math

import aiohttp

EMPTY_PERIOD = (720, 720)


class LKError(Exception):
    """A request failed or returned unexpected data."""


class LKAuthError(LKError):
    """The local credentials were rejected."""


def decode_name(value, tid):
    """Decode the byte-encoded LK display name."""
    try:
        raw = bytes.fromhex(value)
        try:
            return raw.decode("utf-8").strip() or f"Thermostat {tid}"
        except UnicodeDecodeError:
            return raw.decode("latin-1").strip() or f"Thermostat {tid}"
    except (TypeError, ValueError):
        return f"Thermostat {tid}"


def temperature(value, minimum=7, maximum=40):
    """Validate and convert a half-degree temperature into hundredths."""
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("Temperature must be a number.")
    if not minimum <= value <= maximum or value * 2 != round(value * 2):
        raise ValueError("Temperature must be in range and use 0.5 °C steps.")
    return round(value * 100)


def schedule_day(periods):
    """Encode zero to three non-overlapping economy periods."""
    if not isinstance(periods, list) or len(periods) > 3:
        raise ValueError("Expected up to three periods.")
    pairs = []
    for period in periods:
        if (
            not isinstance(period, list) or len(period) != 2
            or any(type(v) is not int for v in period)
            or not 0 <= period[0] < period[1] <= 1440
        ):
            raise ValueError("Invalid economy period.")
        pairs.append(tuple(period))
    ordered = sorted(pairs)
    if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
        raise ValueError("Economy periods overlap.")
    return pairs + [EMPTY_PERIOD] * (3 - len(pairs))


def holiday_hours(end, today):
    """Encode the calendar selection as observed in the LK interface."""
    days = (date.fromisoformat(end) - today).days
    if not 1 <= days <= 99:
        raise ValueError("Choose a date 1–99 days from today.")
    return days * 24


class LKClient:
    def __init__(self, session, url, username, password):
        self.session = session
        self.url = url
        self.headers = {
            "Authorization": aiohttp.BasicAuth(username, password).encode(),
            "Cache-Control": "no-cache",
        }

    async def get(self, path, params=None):
        try:
            async with self.session.get(
                f"{self.url}/{path}", params=params, headers=self.headers,
                allow_redirects=False, timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status in (401, 403):
                    raise LKAuthError("LK Webserver rejected the credentials.")
                if response.status != 200:
                    raise LKError(f"LK Webserver returned HTTP {response.status}.")
                data = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise LKError("Could not read a valid response from LK Webserver.") from err
        if not isinstance(data, dict):
            raise LKError("Expected a JSON object from LK Webserver.")
        return {key.strip(): value for key, value in data.items()}

    async def rooms(self):
        data = await self.get("main.json")
        try:
            active = data["active"]
            if not isinstance(active, list) or not active or any(v not in ("0", "1") for v in active):
                raise ValueError
            return {
                index + 1: {
                    "name": decode_name(data["name"][index], index + 1),
                    "current": int(data["get_room_deg"][index]) / 100,
                    "target": int(data["set_room_deg"][index]) / 100,
                    "heating": data["heat_status"][index] == "1",
                }
                for index, value in enumerate(active) if value == "1"
            }
        except (KeyError, TypeError, IndexError, ValueError) as err:
            raise LKError("Invalid thermostat list.") from err

    async def thermostat(self, tid):
        data = await self.get("thermostat.json", {"tid": tid})
        if str(data.get("tid")) != str(tid) or data.get("active") != "1":
            raise LKError("The requested thermostat is inactive or missing.")
        return data

    async def system(self):
        return await self.get("system.json")

    async def network(self):
        return await self.get("network.json")

    async def write(self, **params):
        result = await self.get("update.cgi", params)
        if str(result.get("modbus_status")) != "0":
            raise LKError("LK Webserver did not acknowledge the write.")


def clock_values(now: datetime):
    """LK uses Sunday=0 and minute precision."""
    return (now.year, now.month, now.day, now.hour, now.minute, now.isoweekday() % 7)

