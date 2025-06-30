# TuneBlade Controller
Home Assistant custom integration for controlling AirPlay devices connected to a TuneBlade server.

## Setup
Search HACS for TuneBlade and download.  
Installation is then via the Integrations Page of Home Assistant.

Details required;
Host and port of the TuneBlade server (if discovery hasn't worked).

The integration will add a simple switch for turning the connection on/off, and a media player which can be used in the same way but can also control volume (from TuneBlade). 

## Master Volume Control
The Master control setting must be enabled in TuneBlade settings. If so then a device named 'Master' will be automatically created.

