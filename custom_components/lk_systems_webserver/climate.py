"""One HA climate entity per active LK thermostat."""
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from .entity import LKRoomEntity, discover_rooms


async def async_setup_entry(hass, entry, async_add_entities):
    discover_rooms(entry, async_add_entities, lambda tid: [
        LKThermostat(entry.runtime_data, entry.unique_id, tid)
    ])


class LKThermostat(LKRoomEntity, ClimateEntity):
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5

    @property
    def native_current_temperature(self):
        return self.coordinator.rooms.get(self.tid, {}).get("current")

    @property
    def native_target_temperature(self):
        return self.coordinator.rooms.get(self.tid, {}).get("target")

    @property
    def hvac_action(self):
        return HVACAction.HEATING if self.coordinator.rooms.get(self.tid, {}).get("heating") else HVACAction.IDLE

    @property
    def min_temp(self):
        return int(self.coordinator.details.get(self.tid, {}).get("restrict_deg_min", "700")) / 100

    @property
    def max_temp(self):
        return int(self.coordinator.details.get(self.tid, {}).get("restrict_deg_max", "4000")) / 100

    async def async_set_temperature(self, **kwargs):
        await self.coordinator.run("target", {"tid": self.tid, "value": kwargs[ATTR_TEMPERATURE]})

    async def async_set_hvac_mode(self, hvac_mode):
        """HEAT is the only mode exposed by this entity."""

