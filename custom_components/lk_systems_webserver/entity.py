"""Shared room and hub entity identities."""
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN


@callback
def discover_rooms(entry, async_add_entities, build_entities):
    """Add entities when active thermostats are first discovered."""
    coordinator = entry.runtime_data
    added = set()

    @callback
    def discover():
        new = sorted(coordinator.rooms.keys() - added)
        if new:
            async_add_entities([entity for tid in new for entity in build_entities(tid)])
            added.update(new)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class LKRoomEntity(CoordinatorEntity):
    """An entity attached to the existing ICS.2 room device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, mac, tid, key=None):
        super().__init__(coordinator)
        self.tid = tid
        device_key = f"{mac}_{tid}"
        self._attr_unique_id = f"{device_key}_{key}" if key else device_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_key)},
            manufacturer="LK Systems",
            model="ICS.2",
            name=coordinator.rooms[tid]["name"],
            via_device_id=coordinator.hub_device_id,
        )

    @property
    def available(self):
        return super().available and self.coordinator.failures < 3 and self.tid in self.coordinator.rooms


class LKHubEntity(CoordinatorEntity):
    """An entity attached to the Webserver device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, mac, key):
        super().__init__(coordinator)
        self._attr_unique_id = f"{mac}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, mac)})

    @property
    def available(self):
        return super().available and self.coordinator.failures < 3

