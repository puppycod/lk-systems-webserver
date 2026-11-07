"""Home Assistant integration for the local LK Webserver."""
import logging
from pathlib import Path

import probatio as schema

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LKClient
from .coordinator import LKCoordinator

DOMAIN = "lk_systems_webserver"
PANEL = "lk-systems-webserver"
ASSETS = "/lk_systems_webserver_static"
LOGGER = logging.getLogger(__name__)
PLATFORMS = ("binary_sensor", "button", "climate", "date", "number", "select", "sensor", "switch")


async def async_setup(hass, config):
    hass.data[DOMAIN] = {}
    await hass.http.async_register_static_paths([
        StaticPathConfig(f"{ASSETS}/panel.js", str(Path(__file__).with_name("panel.js")), False)
    ])
    websocket_api.async_register_command(hass, ws_state)
    websocket_api.async_register_command(hass, ws_action)
    return True


async def async_setup_entry(hass, entry):
    api = LKClient(
        async_get_clientsession(hass), entry.data["host"],
        entry.data["username"], entry.data["password"],
    )
    coordinator = LKCoordinator(hass, LOGGER, entry, api)
    await coordinator.async_config_entry_first_refresh()
    hub = device_registry.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id)},
        manufacturer="LK Systems",
        model="LK Webserver",
        name="LK Systems Webserver",
        configuration_url=entry.data["host"],
    )
    coordinator.hub_device_id = hub.id
    entries = hass.data[DOMAIN]
    if not entries:
        await panel_custom.async_register_panel(
            hass, frontend_url_path=PANEL, webcomponent_name=PANEL,
            sidebar_title="Lattialämmitys" if hass.config.language == "fi" else "Floor Heating",
            sidebar_icon="mdi:heating-coil", module_url=f"{ASSETS}/panel.js?v=0.3.1",
            require_admin=True,
        )
    entries[entry.entry_id] = coordinator
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    entries = hass.data[DOMAIN]
    entries.pop(entry.entry_id)
    if not entries:
        frontend.async_remove_panel(hass, PANEL)
    return True


@websocket_api.websocket_command({"type": f"{DOMAIN}/state"})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_state(hass, connection, msg):
    connection.send_result(msg["id"], {
        entry_id: coordinator.snapshot()
        for entry_id, coordinator in hass.data[DOMAIN].items()
    })


@websocket_api.websocket_command({
    "type": f"{DOMAIN}/action",
    schema.Required("entry"): str,
    schema.Required("action"): str,
    schema.Required("args"): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_action(hass, connection, msg):
    coordinator = hass.data[DOMAIN].get(msg["entry"])
    if coordinator is None:
        raise HomeAssistantError("LK Webserver is unavailable.")
    await coordinator.run(msg["action"], msg["args"])
    connection.send_result(msg["id"], coordinator.snapshot())

