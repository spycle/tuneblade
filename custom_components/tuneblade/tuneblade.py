"""TuneBlade API Client."""
import logging
import asyncio
import socket
from typing import Optional
import aiohttp
import async_timeout

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}

class TuneBladeApiClient:
    def __init__(
        self, host: str, port: str, device_id: str, username: str, password: str, airplay_password: str, session: aiohttp.ClientSession, auth
    ) -> None:
        """Sample API Client."""
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._airplay_password = airplay_password
        self._session = session
        if device_id == "Master":
            self._url = "http://"+host+":"+port+"/master"
        else:
        	self._url = "http://"+host+":"+port+"/devices/"+device_id

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        return await self.api_wrapper("get", self._url)

    async def async_conn(self, value: str) -> None:
        """Get data from the API."""
        await self.api_wrapper("put", self._url, data={"Password": self._airplay_password, "Status": value}, headers=HEADERS)

    async def async_set_volume(self, volume: str) -> None:
        """Get data from the API."""
        await self.api_wrapper("put", self._url, data={"Password": self._airplay_password, "Volume": str(int(volume*100))}, headers=HEADERS)

    async def async_set_volume_master(self, volume: str) -> None:
        """Get data from the API."""
        await self.api_wrapper("put", self._url, data={"Status": "Connect", "Volume": str(int(volume*100))}, headers=HEADERS)

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    return await response.json()

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await self._session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
