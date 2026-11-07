"""Per-room temperatures used by the weekly and system programs."""
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTemperature

from .entity import LKRoomEntity, discover_rooms

SETTINGS = ("comfort_deg", "economy_deg", "holiday_deg", "setback_deg")


async def async_setup_entry(hass, entry, async_add_entities):
    discover_rooms(entry, async_add_entities, lambda tid: [
        LKRoomTemperature(entry.runtime_data, entry.unique_id, tid, key) for key in SETTINGS
    ])


class LKRoomTemperature(LKRoomEntity, NumberEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = 7
    _attr_native_max_value = 40
    _attr_native_step = 0.5
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, mac, tid, key):
        super().__init__(coordinator, mac, tid, key)
        self._attr_translation_key = key

    @property
    def native_value(self):
        value = self.coordinator.details.get(self.tid, {}).get(self.translation_key)
        try:
            return int(value) / 100
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value):
        await self.coordinator.run("setting", {
            "tid": self.tid, "key": self.translation_key, "value": value,
        })

