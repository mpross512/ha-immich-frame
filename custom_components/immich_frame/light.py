"""Light platform for Immich Frame."""

from __future__ import annotations

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BRIGHTNESS_COMMAND, DOMAIN
from .entity import ImmichFrameEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Immich Frame light entity."""
    async_add_entities([ImmichFrameLight(config_entry)])


class ImmichFrameLight(ImmichFrameEntity, LightEntity):
    """Immich Frame light entity."""

    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_is_on = False
    _attr_brightness = 255

    def __init__(self, config_entry: ConfigEntry) -> None:
        super().__init__(config_entry, "Immich Frame Display", "light")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the frame display on or set brightness."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        if brightness is not None:
            if not self.is_on:
                await self._async_send_command("undim")
            value = brightness / 255.0
            await self._async_send_command(BRIGHTNESS_COMMAND, f"value={value:.2f}")
            self._attr_brightness = brightness
        else:
            await self._async_send_command("undim")
            self._attr_brightness = 255

        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the frame display off."""
        await self._async_send_command("dim")
        self._attr_is_on = False
        self._attr_brightness = 0
        self.async_write_ha_state()
