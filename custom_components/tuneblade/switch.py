import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    added_device_ids = set()

    async def _update_entities():
        new_entities = []
        for device_id, device_data in (coordinator.data or {}).items():
            if device_id not in added_device_ids:
                entity = TuneBladeSwitch(coordinator, device_id, device_data)
                new_entities.append(entity)
                added_device_ids.add(device_id)
                _LOGGER.debug("Added new TuneBlade switch: %s", device_data.get("name", device_id))
        if new_entities:
            async_add_entities(new_entities)

    # Initial add
    await _update_entities()

    # Track future additions
    coordinator.async_add_listener(_update_entities)

class TuneBladeSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device_id, device_data):
        super().__init__(coordinator)
        self._device_id = device_id
        self._name = device_data.get("name", device_id)

    @property
    def unique_id(self):
        safe_name = self._name.replace(" ", "_")
        return f"{self._device_id}@{safe_name}_switch"

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        device = self.coordinator.data.get(self._device_id)
        return device.get("connected", False) if device else False

    async def async_turn_on(self):
        await self.coordinator.client.connect(self._device_id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        await self.coordinator.client.disconnect(self._device_id)
        await self.coordinator.async_request_refresh()

    @property
    def available(self):
        return self._device_id in self.coordinator.data

    async def async_added_to_hass(self):
        """Register callback when entity is added."""
        self.coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self):
        self.async_write_ha_state()
