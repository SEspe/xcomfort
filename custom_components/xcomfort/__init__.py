###Version 1.3.7
import async_timeout
import logging

from datetime import timedelta
from homeassistant.helpers import entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import ConfigEntryAuthFailed

#from xcomfortshc import xcomfortAPI
from .xcomfortAPI import xcomfortAPI

from .const import DOMAIN, VERSION
_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "light", "switch", "button", "cover", "climate"]

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, config_entry):

    websession = async_get_clientsession(hass)
    coordinator = XCDataUpdateCoordinator(hass, websession, config_entry.data["url"],config_entry.data["zone"],
        config_entry.data["username"], config_entry.data["password"], config_entry.data["scan_interval"])
    await coordinator.xc.connect()
    await coordinator.async_refresh()
    hass.data[DOMAIN] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    async def async_service1(service_call):
        await coordinator.xc.debug()

    hass.services.async_register(DOMAIN,"save_status_files",async_service1,)
    return True

async def async_unload_entry(hass, config_entry):
    """Unload the entry so it can be reloaded or removed without restarting HA."""
    unloaded = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unloaded:
        # The service closes over this entry's coordinator, so it goes with it.
        hass.services.async_remove(DOMAIN, "save_status_files")
        hass.data.pop(DOMAIN, None)
    return unloaded

class XCDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, url, zone, username, password, scan_interval,  ):
        stat_interval = 60 // scan_interval
        if stat_interval == 0:
            stat_interval = 1
        self.xc = xcomfortAPI(session, url, zone, username, password, stat_interval)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval))

    async def _async_update_data(self):
        try:
            await self.xc.get_statuses()
        except ConfigEntryAuthFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error talking to the xComfort SHC: {err}") from err
        if not self.xc.devices:
            raise UpdateFailed("Invalid sensors data")
        return self.xc.devices
