###Version 1.3.5
from homeassistant.const import CONF_NAME
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp
import voluptuous as vol
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("url", default="http://10.0.0.20"): str,
        vol.Required("username", default="admin1"): str,
        vol.Required("password",default=""): str,
        vol.Required("zone",default="hz_3"): str,
        vol.Required("scan_interval", default=5): int,
        vol.Optional("heating_zone0",default=""): str,
        vol.Optional("heating_zone0_radiator",default=""): str,
        vol.Optional("heating_zone1",default=""): str,
        vol.Optional("heating_zone1_radiator",default=""): str,
        vol.Optional("heating_zone2",default=""): str,
        vol.Optional("heating_zone2_radiator",default=""): str,
        vol.Optional("heating_zone3",default=""): str,
        vol.Optional("heating_zone3_radiator",default=""): str,
        vol.Optional("heating_zone4",default=""): str,
        vol.Optional("heating_zone4_radiator",default=""): str,
        vol.Optional("heating_zone5",default=""): str,
        vol.Optional("heating_zone5_radiator",default=""): str
    }
)

REAUTH_SCHEMA = vol.Schema(
    {
        vol.Required("password"): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        _LOGGER.debug("ConfigFlow start")
        
        errors = {}
        
        if user_input is not None:
            await self.async_set_unique_id(
                    user_input["url"], raise_on_progress=False
                )

            self._abort_if_unique_id_configured()

            return self.async_create_entry( title="xcomfort",  data=user_input,
                )
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors,
        )

    async def _async_check_credentials(self, url, username, password):
        """Return an error key if the SHC rejects these credentials, else None."""
        session = async_get_clientsession(self.hass)
        auth = aiohttp.BasicAuth(login=username, password=password)
        try:
            async with session.get(url, auth=auth) as response:
                if response.status == 401:
                    return "invalid_auth"
                if response.status != 200:
                    _LOGGER.error(
                        "Reauth check: SHC responded with status %s", response.status
                    )
                    return "cannot_connect"
        except aiohttp.ClientError as err:
            _LOGGER.error("Reauth check: cannot reach SHC: %s", err)
            return "cannot_connect"
        return None

    async def async_step_reauth(self, entry_data):
        """Triggered when the SHC rejects the stored credentials."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Ask for a new password and verify it against the SHC."""
        entry = self._reauth_entry
        errors = {}

        if user_input is not None:
            error = await self._async_check_credentials(
                entry.data["url"], entry.data["username"], user_input["password"]
            )
            if error is None:
                self.hass.config_entries.async_update_entry(
                    entry, data={**entry.data, "password": user_input["password"]}
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            errors["base"] = error

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=REAUTH_SCHEMA,
            description_placeholders={"username": entry.data["username"]},
            errors=errors,
        )
