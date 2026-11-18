"""Status polling for Immich Frame."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any
from urllib.parse import urlparse

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import COMMAND_TIMEOUT, CONF_HOST, DEFAULT_PORT, DOMAIN, STATUS_COMMAND

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


def build_base_url(host: str) -> str:
    parsed = urlparse(host if "://" in host else f"//{host}", scheme="http")
    netloc = parsed.netloc or parsed.path
    if not netloc:
        raise ValueError("No host provided")

    if parsed.port is None:
        netloc = f"{netloc}:{DEFAULT_PORT}"

    return f"{parsed.scheme}://{netloc}"


class ImmichFrameCoordinator(DataUpdateCoordinator[dict[str, Any] | None]):
    """
    Polls the frame's /status endpoint.

    The endpoint only exists in newer builds of the app. A frame without it
    answers 404, in which case the data is None and the entities carry on
    assuming their state, exactly as they did before status support existed.
    """

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.entry = config_entry
        # None until the frame has answered once, then whether it has /status
        self.supports_status: bool | None = None

    async def _async_update_data(self) -> dict[str, Any] | None:
        url = f"{build_base_url(self.entry.data[CONF_HOST])}/{STATUS_COMMAND}"
        session = async_get_clientsession(self.hass)

        try:
            async with asyncio.timeout(COMMAND_TIMEOUT):
                async with session.get(url) as response:
                    if response.status == 404:
                        self.supports_status = False
                        return None
                    response.raise_for_status()
                    data = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            if self.supports_status:
                # Only a frame known to report status can be called unreachable
                raise UpdateFailed(f"Unable to reach Immich Frame at {url}") from err
            return None

        if not isinstance(data, dict):
            self.supports_status = False
            return None

        self.supports_status = True
        return data
