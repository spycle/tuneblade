# TuneBlade Controller
Home Assistant custom integration for controlling AirPlay devices connected to a TuneBlade server.

## Setup
Add https://github.com/spycle/tuneblade as a custom repository in HACS.  
Instalation is then via the Integrations Page of Home Assistant.

Details required;
host and port of the TuneBlade server and device_id of the AirPlay device to be added to Home Assistant. This can be found by entering http://host:port/devices into any browser e.g 546E1C242F65@Living Room.

The integration will add a simple switch for turning the connection on/off, and a media player which can be used in the same way but can also control volume (from TuneBlade). Either can be removed from the integration options menu.

## Master Volume Control
Create a new device with a device_id of 'Master'

