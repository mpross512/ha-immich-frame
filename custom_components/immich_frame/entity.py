"""Shared Immich Frame entity helpers."""

from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COMMAND_TIMEOUT, CONF_HOST, COORDINATOR, DOMAIN, STATUS_REFRESH_DELAY
from .coordinator import ImmichFrameCoordinator, build_base_url


def get_coordinator(hass: HomeAssistant, config_entry: ConfigEntry) -> ImmichFrameCoordinator:
    return hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]


class ImmichFrameEntity(CoordinatorEntity[ImmichFrameCoordinator]):
    """Base entity for Immich Frame."""

    def __init__(
        self,
        coordinator: ImmichFrameCoordinator,
        config_entry: ConfigEntry,
        name: str,
        key: str,
    ) -> None:
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._cancel_refresh: CALLBACK_TYPE | None = None
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"

    @property
    def _host(self) -> str:
        return self.config_entry.data[CONF_HOST]

    @property
    def status(self) -> dict[str, object] | None:
        """Return the frame's last status report, or None if it has none."""
        return self.coordinator.data

    @property
    def available(self) -> bool:
        # A frame without /status cannot be told apart from one that is off, so it
        # stays available with assumed state, as it always has
        if not self.coordinator.supports_status:
            return True
        return super().available

    @property
    def device_info(self) -> dict[str, str] | dict[str, object]:
        info: dict[str, object] = {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": f"Immich Frame {self._host}",
            "manufacturer": "Immich Frame",
            "model": "Immich Frame",
        }
        if self.status and self.status.get("version"):
            info["sw_version"] = self.status["version"]
        return info

    async def async_will_remove_from_hass(self) -> None:
        if self._cancel_refresh:
            self._cancel_refresh()
            self._cancel_refresh = None
        await super().async_will_remove_from_hass()

    def _schedule_status_refresh(self) -> None:
        if not self.coordinator.supports_status:
            return
        if self._cancel_refresh:
            self._cancel_refresh()

        async def _refresh(_now) -> None:
            self._cancel_refresh = None
            await self.coordinator.async_request_refresh()

        self._cancel_refresh = async_call_later(self.hass, STATUS_REFRESH_DELAY, _refresh)

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
            async with asyncio.timeout(COMMAND_TIMEOUT):
                async with session.get(url) as response:
                    if response.status != 200:
                        raise HomeAssistantError(
                            f"Immich Frame returned {response.status} for {url}"
                        )
        except Exception as err:
            raise HomeAssistantError(
                f"Unable to communicate with Immich Frame at {url}"
            ) from err

        self._schedule_status_refresh()
