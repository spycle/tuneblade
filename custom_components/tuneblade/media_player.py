"""Media Player platform for TuneBlade."""
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_VOLUME_SET,
    SUPPORT_TURN_ON,
    SUPPORT_TURN_OFF
)
from homeassistant.const import (
    STATE_OFF,
    STATE_IDLE,
    STATE_PLAYING
    )
from .const import NAME, DOMAIN, ICON, MEDIA_PLAYER
from .entity import TuneBladeEntity

SUPPORTED_FEATURES = (
    SUPPORT_VOLUME_SET
    | SUPPORT_TURN_ON
    | SUPPORT_TURN_OFF
)

SUPPORTED_FEATURES_MASTER = (SUPPORT_VOLUME_SET)

async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([TuneBladeMediaPlayer(coordinator, entry)])


class TuneBladeMediaPlayer(TuneBladeEntity, MediaPlayerEntity):
    """TuneBlade Media Player class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        await self.coordinator.api.async_conn("Connect")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        await self.coordinator.api.async_conn("Disconnect")
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        if self.coordinator.data.get("Name") == None:
            await self.coordinator.api.async_set_volume_master(volume)
            await self.coordinator.async_request_refresh()
        else:
            await self.coordinator.api.async_set_volume(volume)
            await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        device = self.coordinator.data.get("Name")
        if device == None:
            device = "Master"
        name = device+" "+NAME
        return name

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        volume = self.coordinator.data.get("Volume", "")
        return volume / 100.0

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.data.get("Status", "") in ['Connected','Connecting']

    @property
    def state(self):
        if self.coordinator.data.get("Name") == None and self.coordinator.data.get("Status", "") in ['Connected','Connecting']:
            return STATE_PLAYING
        elif self.coordinator.data.get("SubState", "") == "Streaming" and self.coordinator.data.get("Status", "") in ['Connected','Connecting']:
            return STATE_PLAYING
        elif self.coordinator.data.get("Status", "") in ['Connected','Connecting'] and self.coordinator.data.get("SubState", "") != "Streaming":
            return STATE_IDLE
        else:
            return STATE_OFF

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        if self.coordinator.data.get("Name") == None:
            return SUPPORTED_FEATURES_MASTER
        else:
            return SUPPORTED_FEATURES
