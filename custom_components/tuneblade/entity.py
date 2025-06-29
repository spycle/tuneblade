"""TuneBladeEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION


class TuneBladeEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry, device_id=None, device_name=None):
        """Initialize entity with coordinator, config entry, and device info."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.device_id = device_id
        self.device_name = device_name or "Master"

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_{self.device_id or 'master'}"

    @property
    def device_info(self):
        """Return device info for the device this entity represents."""
        return {
            "identifiers": {(DOMAIN, self.device_id or self.config_entry.entry_id)},
            "name": f"{self.device_name} {NAME}",
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        data = self.coordinator.data or {}
        # Use per-device data if available
        if self.device_id:
            device_data = data.get(self.device_id, {})
            return {
                "status": device_data.get("Status"),
                "sub_state": device_data.get("SubState"),
                "buffering": device_data.get("Buffering"),
                "buffering_percent": device_data.get("BufferingPercent"),
            }
        else:
            # Fallback to global data
            return {
                "status": data.get("Status"),
            }
