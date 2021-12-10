"""Switch platform for TuneBlade."""
from homeassistant.components.switch import SwitchEntity

from .const import DEFAULT_NAME, DOMAIN, ICON, SWITCH
from .entity import TuneBladeEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([TuneBladeBinarySwitch(coordinator, entry)])


class TuneBladeBinarySwitch(TuneBladeEntity, SwitchEntity):
    """TuneBlade switch class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        await self.coordinator.api.async_conn("Connect")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        await self.coordinator.api.async_conn("Disconnect")
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        device = self.coordinator.data.get("Name")
        name = device+" "+NAME
        return name

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.data.get("Status", "") in ['Connected','Connecting']
