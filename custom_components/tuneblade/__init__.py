"""
Custom integration to integrate TuneBlade with Home Assistant.

"""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .tuneblade import TuneBladeApiClient

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_AIRPLAY_PASSWORD,
    CONF_HOST,
    CONF_PORT,
    CONF_DEVICE_ID,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    password = entry.data.get(CONF_PASSWORD)
    airplay_password = entry.data.get(CONF_AIRPLAY_PASSWORD)
    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT)
    device_id = entry.data.get(CONF_DEVICE_ID)

    username = "MYTUNEBLADE"
    auth = None
    if password:
        auth = aiohttp.BasicAuth(username, password=password)

    session = async_get_clientsession(hass)
    
    client = TuneBladeApiClient(host, port, device_id, username, password, airplay_password, session, auth)

    coordinator = TuneBladeDataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_create_background_task(
                hass.config_entries.async_forward_entry_setups(entry, [platform]),
                name=f"tuneblade: forward {platform}"
            )

    entry.add_update_listener(async_reload_entry)
    return True


class TuneBladeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: TuneBladeApiClient
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.async_get_data()
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
