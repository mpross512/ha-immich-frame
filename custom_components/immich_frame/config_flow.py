"""Config flow for Immich Frame."""

from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_PORT, DOMAIN


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(HomeAssistantError):
    """Error to indicate the host is invalid."""


def _build_base_url(host: str) -> str:
    parsed = urlparse(host if "://" in host else f"//{host}", scheme="http")
    netloc = parsed.netloc or parsed.path
    if not netloc:
        raise InvalidHost

    if parsed.port is None:
        netloc = f"{netloc}:{DEFAULT_PORT}"

    return f"{parsed.scheme}://{netloc}"


async def _async_validate_input(hass: HomeAssistant, host: str) -> dict[str, str]:
    base_url = _build_base_url(host)
    parsed_url = urlparse(base_url)
    if parsed_url.port is None:
        test_url = f"{base_url}:{DEFAULT_PORT}/undim"
    else:
        test_url = f"{base_url}/undim"

    session = async_get_clientsession(hass)
    try:
        async with session.get(test_url, timeout=10) as response:
            if response.status != 200:
                raise CannotConnect
    except Exception as err:
        raise CannotConnect from err

    return {CONF_HOST: host}


class ImmichFrameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Immich Frame."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_ASSUMED_STATE

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlow:
        return ImmichFrameOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: ConfigType | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                validated = await _async_validate_input(self.hass, user_input[CONF_HOST])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["host"] = "invalid_host"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=validated
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): cv.string,
                }
            ),
            errors=errors,
        )


class ImmichFrameOptionsFlowHandler(OptionsFlow):
    """Options flow for Immich Frame."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: ConfigType | None = None):
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await _async_validate_input(self.hass, user_input[CONF_HOST])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["host"] = "invalid_host"
            else:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    title=user_input[CONF_HOST],
                    data={**self.config_entry.data, CONF_HOST: user_input[CONF_HOST]},
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=self.config_entry.data[CONF_HOST],
                    ): cv.string,
                }
            ),
            errors=errors,
        )
