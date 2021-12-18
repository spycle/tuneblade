# TuneBlade Controller
Home Assistant custom integration for controlling AirPlay devices connected to a TuneBlade server.

## Setup
Search HACS for TuneBlade and download.  
Instalation is then via the Integrations Page of Home Assistant.

Details required;
host and port of the TuneBlade server and device_id of the AirPlay device to be added to Home Assistant. This can be found by entering http://host:port/devices into any browser e.g 112347690@Living Room AirPort Express.

The integration will add a simple switch for turning the connection on/off, and a media player which can be used in the same way but can also control volume (from TuneBlade). Either can be removed from the integration options menu.

## Master Volume Control
Create a new device with a device_id of 'Master'.  

The Master control setting must be enabled in TuneBlade settings.

