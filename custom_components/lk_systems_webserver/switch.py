"""Per-room thermostat configuration switches."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory

from .entity import LKRoomEntity, discover_rooms

SETTINGS = ("week_program_enable", "adaptive_enable", "backlight_enable", "keylock_enable")


async def async_setup_entry(hass, entry, async_add_entities):
    discover_rooms(entry, async_add_entities, lambda tid: [
        LKRoomSwitch(entry.runtime_data, entry.unique_id, tid, key) for key in SETTINGS
    ])


class LKRoomSwitch(LKRoomEntity, SwitchEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, mac, tid, key):
        super().__init__(coordinator, mac, tid, key)
        self._attr_translation_key = key

    @property
    def is_on(self):
        value = self.coordinator.details.get(self.tid, {}).get(self.translation_key)
        return value == "1" if value in ("0", "1") else None

    async def async_turn_on(self, **kwargs):
        await self._write(True)

    async def async_turn_off(self, **kwargs):
        await self._write(False)

    async def _write(self, enabled):
        if self.translation_key == "week_program_enable":
            await self.coordinator.run("week_enabled", {"tid": self.tid, "value": enabled})
        else:
            await self.coordinator.run("setting", {
                "tid": self.tid, "key": self.translation_key, "value": int(enabled),
            })

