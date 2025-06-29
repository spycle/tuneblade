import logging
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MediaPlayerState,
    MediaPlayerEntityFeature,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [
        TuneBladeMediaPlayer(coordinator, device_id, device_data)
        for device_id, device_data in coordinator.data.items()
    ]
    _LOGGER.debug("Adding %d media player(s): %s", len(entities), [e.name for e in entities])
    async_add_entities(entities, True)

class TuneBladeMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    def __init__(self, coordinator, device_id, device_data):
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_name = device_data["name"]
        safe_name = self._attr_name.replace(" ", "_")
        self._attr_unique_id = f"{device_id}@{safe_name}"
        self._attr_volume_level = None
        self._attr_state = MediaPlayerState.OFF
        self._attr_supported_features = (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
        )

    @property
    def available(self) -> bool:
        return self.device_id in self.coordinator.data

    async def async_turn_on(self):
        await self.coordinator.client.connect(self.device_id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        await self.coordinator.client.disconnect(self.device_id)
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume):
        await self.coordinator.client.set_volume(self.device_id, int(volume * 100))
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Register callback when entity is added."""
        self.coordinator.async_add_listener(self._handle_coordinator_update)
        self._handle_coordinator_update()

    def _handle_coordinator_update(self):
        device_data = self.coordinator.data.get(self.device_id)
        if device_data is None:
            self._attr_state = MediaPlayerState.OFF
            self._attr_volume_level = None
        else:
            code = str(device_data.get("status_code", "0"))
            if code == "100":
                self._attr_state = MediaPlayerState.PLAYING
            elif code == "200":
                self._attr_state = MediaPlayerState.IDLE
            elif code == "0":
                self._attr_state = MediaPlayerState.OFF
            else:
                self._attr_state = MediaPlayerState.UNAVAILABLE

            volume = device_data.get("volume")
            self._attr_volume_level = volume / 100 if volume is not None else None

        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        device_data = self.coordinator.data.get(self.device_id, {})
        code = str(device_data.get("status_code", "0"))
        status_map = {
            "0": "disconnected",
            "100": "playing",
            "200": "standby",
        }

        return {
            "device_name": device_data.get("name"),
            "status_code": code,
            "status_text": status_map.get(code, "unknown"),
            "volume": device_data.get("volume"),
        }
