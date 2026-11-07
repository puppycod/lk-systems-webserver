"""Reported pump and boiler relay states."""
from homeassistant.components.binary_sensor import BinarySensorEntity

from .entity import LKHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        LKRelay(entry.runtime_data, entry.unique_id, key)
        for key in ("pump_state", "boiler_state")
    ])


class LKRelay(LKHubEntity, BinarySensorEntity):
    @property
    def is_on(self):
        value = self.coordinator.system.get(self.translation_key)
        return value == "1" if value in ("0", "1") else None

