"""
Support for TuneBlade devices

"""
import asyncio
import logging

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.components.media_player import MediaPlayerEntity, PLATFORM_SCHEMA
from homeassistant.components.media_player.const import (
    SUPPORT_PLAY,
    SUPPORT_PAUSE,
    SUPPORT_STOP,
    SUPPORT_VOLUME_SET,
    SUPPORT_TURN_ON,
    SUPPORT_TURN_OFF,
)
from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_HOST,
)
from homeassistant.const import (
	CONF_NAME, 
	CONF_HOST, 
	CONF_PORT, 
	CONF_USERNAME, 
	CONF_PASSWORD,
	STATE_IDLE, 
	STATE_OFF, 
	STATE_PLAYING
	)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.template as tmpl

#DOMAIN = "tune_blade"

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = 'device_id'
CONF_AIRPLAY_PASSWORD = 'airplay_password'

SUPPORTED_FEATURES = (
    SUPPORT_VOLUME_SET
    | SUPPORT_TURN_ON
    | SUPPORT_TURN_OFF
)

METHOD = 'put'
TIMEOUT = 10

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_PORT): cv.string,
	vol.Required(CONF_DEVICE_ID): cv.string,
	vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
	vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_USERNAME, 'authentication', default = "MYTUNEBLADE"): cv.string,
    vol.Optional(CONF_PASSWORD, 'authentication'): cv.string,
	vol.Optional(CONF_AIRPLAY_PASSWORD, 'authentication'): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
	"""Set up the TuneBlade."""
	name = config.get(CONF_NAME)
	host = config.get(CONF_HOST)
	port = config.get(CONF_PORT)
	url ="http://"+host+":"+port+"/devices/"
#    url = f"http://{host}:{port}/devices/"
	device_id = config.get(CONF_DEVICE_ID)
	airplay_password = config.get(CONF_AIRPLAY_PASSWORD)
	username = config.get(CONF_USERNAME)
	password = config.get(CONF_PASSWORD)


	auth = None
	if password:
		auth = aiohttp.BasicAuth(username, password=password)


	try:
		media_player = TuneBladeDevice(hass, name, url, device_id, password, auth)
		req = await media_player.get_device_state(hass)
		async_add_entities([media_player])
	except (TypeError, ValueError):
		_LOGGER.error("Missing resource or schema in configuration.")
	except (asyncio.TimeoutError, aiohttp.ClientError):
		_LOGGER.error("No route to endpoint: %s", url)


class TuneBladeDevice(MediaPlayerEntity):
	"""Representation of a Tune Blade Media Player."""

	def __init__(self, hass, name, url, device_id, password, auth):
		"""Initialize the Tune Blade media player."""
		self._state = None
		self._name = name
		self._name_by_device = None
		self._url = url
		self._device_id = device_id
		self._password = password
		self._auth = auth
		self._volume = 100
		self._status = None
		self._previous_status = None
		self._substate = ""
		self._buffering = False
		self._buffering_percent = 0
		self._timeout = TIMEOUT
		self.hass = hass
		
	@property
	def name(self):
		"""Return the name of the media player."""
		return self._name

	@property
	def is_on(self):
		"""Return true if device is on."""
		return self._state

	async def turn_on(self):
		"""Play media.

		This method must be run in the event loop and returns a coroutine.
		"""

		payload = '"Status":"Connect"'
		if self._password is not None:
			payload = payload + ',"Password:":"'+self._password+'"'
		payload = '{'+payload+'}'
		body_on = tmpl.Template(payload, self.hass)
		body_on_t = body_on.async_render()

		try:
			req = await self.set_device_state(body_on_t)
		except (asyncio.TimeoutError, aiohttp.ClientError):
			_LOGGER.error("Error while connecting %s", self._url)

	async def turn_off(self):
		body_off = tmpl.Template('{"Status":"Disconnect"}', self.hass)
		body_off_t = body_off.async_render()

		try:
			req = await self.set_device_state(body_off_t)
		except (asyncio.TimeoutError, aiohttp.ClientError):
			_LOGGER.error("Error while disconnecting %s", self._url)

	async def async_turn_on(self):
	    await self.turn_on()

	async def async_turn_off(self):
		await self.turn_off()

	async def async_set_volume_level(self, volume):
		"""Set volume level, range 0..1.

		This method must be run in the event loop and returns a coroutine.
		"""
		body_volume = tmpl.Template('{"Volume":"'+str(int(volume*100))+'"}', self.hass)
		body_volume_t = body_volume.async_render()

		try:
			req = await self.set_device_state(body_volume_t)
		except (asyncio.TimeoutError, aiohttp.ClientError):
			_LOGGER.error("Error while changing volume on %s", self._url)


	async def set_device_state(self, body):
		"""Send a state update to the device."""
		websession = async_get_clientsession(self.hass, False)

		with async_timeout.timeout(TIMEOUT, loop=self.hass.loop):
			my_resource = self._url+self._device_id
			req = await getattr(websession, METHOD)(
				my_resource, auth=self._auth, data=bytes(str(body), 'utf-8'))
			return req

	async def async_update(self):
		"""Get the current state, catching errors."""
		try:
			await self.get_device_state(self.hass)
		except asyncio.TimeoutError:
			_LOGGER.exception("Timed out while fetching data")
		except aiohttp.ClientError as err:
			_LOGGER.exception("Error while fetching data: %s", err)

	@property
	def state(self):
		if self._status in ['Connected','Connecting']:
			return STATE_PLAYING
		else:
			return STATE_OFF
			

	async def get_device_state(self, hass):
		"""Get the latest data from REST API and update the state."""
		websession = async_get_clientsession(hass, False)
		my_resource = self._url+self._device_id
		with async_timeout.timeout(self._timeout, loop=hass.loop):
			req = None
			try:
				req = await websession.get(my_resource, auth=self._auth)
				if req.status >=400:
					raise Exception()
			except Exception as e:
				error_messages = {"400":"Required information was missing or malformed",
								  "401":"Authentication failure",
								  "404":"Device not available",
								  "500":"An error occurred on the server"
								 }
				self._state = False
				prev_status = self._status
				if req is None:
					self._status = "TuneBlade not available"
				else:
					self._status = error_messages[str(req.status)]
				if prev_status != self._status:
					self._previous_status = prev_status
				self._substate = None
				self._volume = None
				self._name_by_device = None
				self._buffering = None
				self._buffering_percent = None
				return False
				
			text = await req.text()

			prev_status = self._status
			template = tmpl.Template("{{ value_json.Status }}", self.hass)
			self._status = template.async_render_with_possible_json_value(
				text, 'None')
			if prev_status != self._status:
				self._previous_status = prev_status
			self._state = self._status in ['Connected','Connecting']
			

			template = tmpl.Template("{{ value_json.SubState }}", self.hass)
			self._substate = template.async_render_with_possible_json_value(
				text, 'None')

			template = tmpl.Template("{{ value_json.Volume }}", self.hass)
			self._volume = float(template.async_render_with_possible_json_value(
				text, 'None'))

			template = tmpl.Template("{{ value_json.Name }}", self.hass)
			self._name_by_device = template.async_render_with_possible_json_value(
				text, 'None')
			
			template = tmpl.Template("{{ value_json.Buffering }}", self.hass)
			self._buffering = template.async_render_with_possible_json_value(
				text, 'None')

			template = tmpl.Template("{{ value_json.BufferingPercent }}", self.hass)
			self._buffering_percent = template.async_render_with_possible_json_value(
				text, 'None')

		return req

	@property
	def volume_level(self):
		"""Volume level of the media player (0..1)."""
		if self._volume is not None:
			return self._volume / 100.0


	@property
	def supported_features(self):
		"""Flag media player features that are supported."""

		return SUPPORTED_FEATURES

	@property
	def state_attributes(self):
		"""Return optional state attributes."""
		new_attributes = super(TuneBladeDevice, self).state_attributes
		new_attributes["status"] = self._status
		if self._substate is not None:
			new_attributes["sub_state"] = self._substate
		if self._volume is not None:
			new_attributes["volume"] = self._volume
		if self._buffering is not None:
			new_attributes["buffering"] = self._buffering
		if self._buffering_percent is not None:
			new_attributes["buffering_percent"] = self._buffering_percent
		if self._previous_status is not None:
			new_attributes["previous_status"] = self._previous_status

		return new_attributes