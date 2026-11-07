"""Local configuration through the Home Assistant UI."""
from urllib.parse import urlsplit

import probatio as schema

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import LKAuthError, LKClient, LKError

DOMAIN = "lk_systems_webserver"


def base_url(host):
    host = host.strip()
    parts = urlsplit(host if "://" in host else f"http://{host}")
    if (
        parts.scheme not in ("http", "https") or not parts.hostname
        or any(char.isspace() for char in parts.netloc)
        or parts.username is not None or parts.password is not None
        or parts.path not in ("", "/") or parts.query or parts.fragment
    ):
        raise ValueError
    _ = parts.port
    return f"{parts.scheme}://{parts.netloc}"


class LKConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _validate_credentials(self, url, username, password):
        api = LKClient(async_get_clientsession(self.hass), url, username, password)
        await api.rooms()
        network = await api.network()
        mac = "".join(c for c in str(network["mac_address"]).lower() if c in "0123456789abcdef")
        if len(mac) != 12 or mac == "0" * 12:
            raise LKError("Invalid MAC address.")
        return mac

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                url = base_url(user_input["host"])
                mac = await self._validate_credentials(
                    url, user_input["username"], user_input["password"]
                )
            except LKAuthError:
                errors["base"] = "invalid_auth"
            except (LKError, KeyError):
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["host"] = "invalid_host"
            else:
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="LK Systems Webserver", data={**user_input, "host": url}
                )
        return self.async_show_form(
            step_id="user",
            data_schema=schema.Schema({
                schema.Required("host"): str,
                schema.Required("username", default="lk"): str,
                schema.Required(schema.Secret("password")): str,
            }),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        return await self._update_password(self._get_reconfigure_entry(), "reconfigure", user_input)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._update_password(self._get_reauth_entry(), "reauth_confirm", user_input)

    async def _update_password(self, entry, step_id, user_input):
        errors = {}
        if user_input is not None:
            password = user_input["password"]
            try:
                mac = await self._validate_credentials(
                    entry.data["host"], entry.data["username"], password
                )
            except (LKAuthError, ValueError):
                errors["base"] = "invalid_auth"
            except (LKError, KeyError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self.async_update_reload_and_abort(entry, data_updates={"password": password})

        return self.async_show_form(
            step_id=step_id,
            data_schema=schema.Schema({
                schema.Required(schema.Secret("password")): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }),
            errors=errors,
        )
