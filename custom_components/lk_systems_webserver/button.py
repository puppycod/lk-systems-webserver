"""Webserver clock synchronization."""
from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory

from .entity import LKHubEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LKSyncClock(entry.runtime_data, entry.unique_id, "sync_clock")])


class LKSyncClock(LKHubEntity, ButtonEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:clock-sync"

    async def async_press(self):
        await self.coordinator.run("sync_clock", {})

