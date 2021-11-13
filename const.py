"""Constants for the TuneBlade integration."""

import voluptuous as vol

from homeassistant.components.media_player.const import (
    SUPPORT_PLAY,
    SUPPORT_PAUSE,
    SUPPORT_STOP,
    SUPPORT_VOLUME_SET,
    SUPPORT_TURN_ON,
    SUPPORT_TURN_OFF,
)
from homeassistant.const import (
    CONF_NAME, 
    CONF_HOST, 
    CONF_PORT, 
    CONF_USERNAME, 
    CONF_PASSWORD,
    STATE_IDLE, 
    STATE_OFF, 
    STATE_PLAYING,
)
from datetime import timedelta

DOMAIN = "tune_blade"
PLATFORMS = ["media_player"]
VERSION = "0.0.1"

DEFAULT_HOST = "localhost"
DEFAULT_NAME = "TuneBlade Speaker"

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): str,
    }
)