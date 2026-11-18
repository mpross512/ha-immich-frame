"""Immich Frame integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF_HOST, COORDINATOR, DOMAIN, PLATFORMS, REMOVED_BUTTON_KEYS
from .coordinator import ImmichFrameCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Immich Frame from a config entry."""
    coordinator = ImmichFrameCoordinator(hass, entry)
    # Not the first-refresh variant: a frame that is switched off must not block setup
    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        CONF_HOST: entry.data[CONF_HOST],
        COORDINATOR: coordinator,
    }

    _remove_replaced_buttons(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _remove_replaced_buttons(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Clear out the slideshow buttons that the Slideshow media player replaced."""
    registry = er.async_get(hass)
    for key in REMOVED_BUTTON_KEYS:
        entity_id = registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_{key}")
        if entity_id:
            registry.async_remove(entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Immich Frame config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
