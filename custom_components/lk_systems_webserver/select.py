"""Select the operating mode requested through the LK Webserver."""
from homeassistant.components.select import SelectEntity
from homeassistant.exceptions import ServiceValidationError

from . import DOMAIN
from .coordinator import HOLIDAY_END, SYSTEM_MODES
from .entity import LKHubEntity

MODE_VALUES = {option: int(value) for value, option in SYSTEM_MODES.items()}


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LKRequestedSystemMode(entry)])


class LKRequestedSystemMode(LKHubEntity, SelectEntity):
    _attr_options = list(MODE_VALUES)

    def __init__(self, entry):
        super().__init__(entry.runtime_data, entry.unique_id, "requested_system_mode")
        self.entry = entry

    @property
    def available(self):
        return super().available and self.current_option is not None

    @property
    def current_option(self):
        return SYSTEM_MODES.get(self.coordinator.system.get("override_web"))

    async def async_select_option(self, option):
        args = {"value": MODE_VALUES[option]}
        if option == "holiday":
            end = self.entry.options.get(HOLIDAY_END)
            if not end:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="holiday_end_required"
                )
            args["end"] = end
        await self.coordinator.run("system_mode", args)
