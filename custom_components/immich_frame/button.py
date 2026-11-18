"""Button platform for Immich Frame."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.const import EntityCategory

from .const import BUTTON_COMMANDS, DOMAIN, RELOAD_COMMAND
from .coordinator import ImmichFrameCoordinator
from .entity import ImmichFrameEntity, get_coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities for Immich Frame."""
    coordinator = get_coordinator(hass, config_entry)
    descriptions = [
        ButtonEntityDescription(key=key, name=name)
        for key, name in BUTTON_COMMANDS
    ]
    # Reload arrived in the same build of the app as the media report
    if coordinator.data and "media" in coordinator.data:
        descriptions.append(
            ButtonEntityDescription(
                key=RELOAD_COMMAND,
                name="Reload",
                entity_category=EntityCategory.CONFIG,
            )
        )

    async_add_entities(
        ImmichFrameButton(coordinator, config_entry, description)
        for description in descriptions
    )


class ImmichFrameButton(ImmichFrameEntity, ButtonEntity):
    """Immich Frame button entity."""

    entity_description: ButtonEntityDescription

    def __init__(
        self,
        coordinator: ImmichFrameCoordinator,
        config_entry: ConfigEntry,
        description: ButtonEntityDescription,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            name=description.name,
            key=description.key,
        )
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the configured command to the Immich Frame."""
        await self._async_send_command(self.entity_description.key)
