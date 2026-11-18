"""Light platform for Immich Frame."""

from __future__ import annotations

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    EFFECT_OFF,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    BRIGHTNESS_COMMAND,
    DOMAIN,
    EFFECT_SYSTEM_BRIGHTNESS,
    SYSTEM_BRIGHTNESS_QUERY,
)
from .coordinator import ImmichFrameCoordinator
from .entity import ImmichFrameEntity, get_coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Immich Frame light entity."""
    async_add_entities([ImmichFrameLight(get_coordinator(hass, config_entry), config_entry)])


class ImmichFrameLight(ImmichFrameEntity, LightEntity):
    """Immich Frame light entity."""

    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_is_on = False
    _attr_brightness = 255
    # "System brightness" is offered as an effect so that it sits with the brightness
    # slider: choosing it hands the display back to the device's own brightness setting
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = [EFFECT_OFF, EFFECT_SYSTEM_BRIGHTNESS]
    _attr_effect = EFFECT_OFF

    def __init__(self, coordinator: ImmichFrameCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            name="Immich Frame Display",
            key="light",
        )
        self._apply_status()

    def _apply_status(self) -> None:
        """Take on and brightness from the frame's own report, when it gives one."""
        status = self.status
        if not status or "active" not in status:
            return

        self._attr_is_on = bool(status["active"])
        brightness = status.get("brightness")
        if not self._attr_is_on:
            self._attr_brightness = 0
        elif isinstance(brightness, (int, float)) and brightness >= 0:
            self._attr_brightness = round(min(brightness, 1.0) * 255)
            self._attr_effect = EFFECT_OFF
        else:
            # A negative value means the frame is following the system brightness
            self._attr_brightness = 255
            self._attr_effect = EFFECT_SYSTEM_BRIGHTNESS

    @callback
    def _handle_coordinator_update(self) -> None:
        self._apply_status()
        super()._handle_coordinator_update()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the frame display on or set brightness."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        effect = kwargs.get(ATTR_EFFECT)

        if brightness is None and effect == EFFECT_OFF:
            # Leaving system brightness needs a level to go to
            brightness = self._attr_brightness or 255

        if brightness is not None:
            if not self.is_on:
                await self._async_send_command("undim")
            value = brightness / 255.0
            await self._async_send_command(BRIGHTNESS_COMMAND, f"value={value:.2f}")
            self._attr_brightness = brightness
            self._attr_effect = EFFECT_OFF
        elif effect == EFFECT_SYSTEM_BRIGHTNESS:
            if not self.is_on:
                await self._async_send_command("undim")
            await self._async_send_command(BRIGHTNESS_COMMAND, SYSTEM_BRIGHTNESS_QUERY)
            self._attr_brightness = 255
            self._attr_effect = EFFECT_SYSTEM_BRIGHTNESS
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
