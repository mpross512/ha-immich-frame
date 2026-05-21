"""Shared Immich Frame entity helpers."""

from __future__ import annotations

from urllib.parse import urlparse

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity

from .const import COMMAND_TIMEOUT, DEFAULT_PORT, DOMAIN, CONF_HOST


def build_base_url(host: str) -> str:
    parsed = urlparse(host if "://" in host else f"//{host}", scheme="http")
    netloc = parsed.netloc or parsed.path
    if not netloc:
        raise ValueError("No host provided")

    if parsed.port is None:
        netloc = f"{netloc}:{DEFAULT_PORT}"

    return f"{parsed.scheme}://{netloc}"


class ImmichFrameEntity(Entity):
    """Base entity for Immich Frame."""

    def __init__(self, config_entry: ConfigEntry, name: str, key: str) -> None:
        self.config_entry = config_entry
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"

    @property
    def _host(self) -> str:
        return self.config_entry.data[CONF_HOST]

    @property
    def device_info(self) -> dict[str, str] | dict[str, object]:
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": f"Immich Frame {self._host}",
            "manufacturer": "Immich Frame",
            "model": "Immich Frame",
        }

    def _build_url(self, path: str, query: str | None = None) -> str:
        base_url = build_base_url(self._host)
        url = f"{base_url}/{path}"
        if query:
            url = f"{url}?{query}"
        return url

    async def _async_send_command(self, path: str, query: str | None = None) -> None:
        url = self._build_url(path, query)
        session = async_get_clientsession(self.hass)

        try:
            with async_timeout.timeout(COMMAND_TIMEOUT):
                async with session.get(url) as response:
                    if response.status != 200:
                        raise HomeAssistantError(
                            f"Immich Frame returned {response.status} for {url}"
                        )
        except Exception as err:
            raise HomeAssistantError(
                f"Unable to communicate with Immich Frame at {url}"
            ) from err
