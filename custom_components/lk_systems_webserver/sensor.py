"""Thermostat diagnostics and hub status."""
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature

from .coordinator import SYSTEM_MODES
from .entity import LKHubEntity, LKRoomEntity, discover_rooms

ROOM_SENSORS = (
    SensorEntityDescription(
        key="battery", translation_key="battery", device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="link_quality", translation_key="link_quality", icon="mdi:signal",
        state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
ROOM_TEMPERATURES = (
    SensorEntityDescription(
        key="current", translation_key="room_temperature",
        device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="target", translation_key="target_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator, mac = entry.runtime_data, entry.unique_id
    async_add_entities([
        LKConnection(coordinator, mac, "connection"),
        LKLastRead(coordinator, mac, "last_success"),
        LKSystemMode(coordinator, mac, "system_mode"),
        LKHolidayEndEstimate(coordinator, mac, "holiday_end_estimate"),
    ])
    discover_rooms(entry, async_add_entities, lambda tid: [
        LKRoomSensor(coordinator, mac, tid, description) for description in ROOM_SENSORS
    ] + [
        LKRoomTemperature(coordinator, mac, tid, description) for description in ROOM_TEMPERATURES
    ])


class LKRoomSensor(LKRoomEntity, SensorEntity):
    def __init__(self, coordinator, mac, tid, description):
        super().__init__(coordinator, mac, tid, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        value = self.coordinator.details.get(self.tid, {}).get(self.entity_description.key)
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class LKRoomTemperature(LKRoomSensor):
    @property
    def native_value(self):
        return self.coordinator.rooms.get(self.tid, {}).get(self.entity_description.key)


class LKConnection(LKHubEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["connected", "degraded", "disconnected"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:lan-connect"

    @property
    def available(self):
        return True

    @property
    def native_value(self):
        if (
            not self.coordinator.last_success or not self.coordinator.last_update_success
            or self.coordinator.failures >= 3
        ):
            return "disconnected"
        return "degraded" if self.coordinator.failures else "connected"


class LKLastRead(LKHubEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self):
        return True

    @property
    def native_value(self):
        value = self.coordinator.last_success
        return datetime.fromisoformat(value) if value else None


class LKSystemMode(LKHubEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(SYSTEM_MODES.values())

    @property
    def native_value(self):
        return SYSTEM_MODES.get(self.coordinator.system.get("override"))


class LKHolidayEndEstimate(LKHubEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.DATE

    @property
    def native_value(self):
        system = self.coordinator.system
        if system.get("override_web") != "1":
            return None
        try:
            hours = int(system["holiday_counter"])
            if not 0 <= hours <= 99 * 24:
                return None
            year, month, day, hour, minute = map(int, system["date"][:5])
            clock = datetime(year, month, day, hour, minute)
            return (clock + timedelta(hours=hours)).date()
        except (KeyError, ValueError, TypeError, OverflowError):
            return None

