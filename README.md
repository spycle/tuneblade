TuneBlade is a simple Windows tray utility that lets you stream system-wide audio to AirPort Express, Apple TV, AirPlay enabled speakers and HiFi receivers, and to AirPlay audio receiving applications such as ShairPort, XBMC/Kodi. Connect an Alexa/Google/other speaker to the host and output via AirPlay.

# TuneBlade Remote
Home Assistant custom integration for controlling AirPlay devices via TuneBlade Remote.

## Setup
Install TuneBlade on a Windows device.
Ensure Romote Control is set to on in the TuneBlade settings. 

Search HACS for TuneBlade and download.  
Installation is then via the Integrations Page of Home Assistant.

Restart TuneBlade to ensure it's broadcasting (seems to stop advertising Bonjour after a while).

TuneBlade should be automatically discovered however, manually configuration is possible with the host (without http://) and the port.

The integration will add a simple switch for turning the connection on/off, and a media player which can be used in the same way but can also control volume (from TuneBlade). 

## Master Volume Control
The Master control setting must be enabled in TuneBlade settings. A device named Master will then also be available.

