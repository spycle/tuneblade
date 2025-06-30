import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .tuneblade import TuneBladeApiClient

_LOGGER = logging.getLogger(__name__)

MAIN_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("port"): str,
    }
)


class TuneBladeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TuneBlade."""

    VERSION = 1

    @property
    def is_hub(self) -> bool:
        """Return True to indicate this config entry is a hub."""
        return True

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the user-initiated configuration."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=MAIN_SCHEMA)

        session = async_get_clientsession(self.hass)

        try:
            client = TuneBladeApiClient(
                host=user_input["host"],
                port=user_input["port"],
                session=session,
            )
            devices = await client.async_get_data()
            if devices is None:
                raise Exception("Failed to connect or get devices")
        except Exception as err:
            _LOGGER.error("Error connecting to TuneBlade hub: %s", err)
            return self.async_show_form(
                step_id="user",
                data_schema=MAIN_SCHEMA,
                errors={"base": "cannot_connect"},
            )

        await self.async_set_unique_id(f"{user_input['host']}:{user_input['port']}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title="TuneBlade Hub", data=user_input)

    async def async_step_zeroconf(self, discovery_info: dict) -> FlowResult:
        """Handle a Zeroconf discovery."""
        _LOGGER.debug("Discovered TuneBlade via Zeroconf: %s", discovery_info)

        host = discovery_info["host"]
        port = discovery_info["port"]
        name = discovery_info["name"]

        await self.async_set_unique_id(f"{host}:{port}")
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {"name": name}
        self._discovered_host = host
        self._discovered_port = port

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> FlowResult:
        """Confirm setting up TuneBlade after discovery."""
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                client = TuneBladeApiClient(
                    host=self._discovered_host,
                    port=self._discovered_port,
                    session=session,
                )
                devices = await client.async_get_data()
                if devices is None:
                    raise Exception("Failed to get data")
            except Exception as err:
                _LOGGER.error("Error connecting to TuneBlade during discovery: %s", err)
                return self.async_abort(reason="cannot_connect")

            return self.async_create_entry(
                title=f"TuneBlade ({self._discovered_host})",
                data={
                    "host": self._discovered_host,
                    "port": self._discovered_port,
                },
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self.context["title_placeholders"]["name"]
            },
        )
