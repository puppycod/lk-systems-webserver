"""Store the date to send when activating Holiday mode from Home Assistant."""
from datetime import date

from homeassistant.components.date import DateEntity

from .coordinator import HOLIDAY_END
from .entity import LKHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LKHolidayEnd(entry)])


class LKHolidayEnd(LKHubEntity, DateEntity):
    def __init__(self, entry):
        super().__init__(entry.runtime_data, entry.unique_id, HOLIDAY_END)
        self.entry = entry

    @property
    def available(self):
        return True

    @property
    def native_value(self):
        value = self.entry.options.get(HOLIDAY_END)
        return date.fromisoformat(value) if value else None

    async def async_set_value(self, value):
        self.hass.config_entries.async_update_entry(
            self.entry, options={**self.entry.options, HOLIDAY_END: value.isoformat()}
        )
        self.async_write_ha_state()
