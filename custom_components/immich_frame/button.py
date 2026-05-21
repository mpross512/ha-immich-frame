"""Button platform for Immich Frame."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BUTTON_COMMANDS, DOMAIN
from .entity import ImmichFrameEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities for Immich Frame."""
    async_add_entities(
        ImmichFrameButton(config_entry, description)
        for description in _get_button_descriptions()
    )


def _get_button_descriptions() -> tuple[ButtonEntityDescription, ...]:
    return tuple(
        ButtonEntityDescription(key=key, name=name) for key, name in BUTTON_COMMANDS
    )


class ImmichFrameButton(ImmichFrameEntity, ButtonEntity):
    """Immich Frame button entity."""

    entity_description: ButtonEntityDescription

    def __init__(self, config_entry: ConfigEntry, description: ButtonEntityDescription) -> None:
        super().__init__(config_entry, description.name, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the configured command to the Immich Frame."""
        await self._async_send_command(self.entity_description.key)
