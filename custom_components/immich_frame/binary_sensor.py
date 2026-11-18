"""Binary sensor platform for Immich Frame."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ImmichFrameCoordinator
from .entity import ImmichFrameEntity, get_coordinator

# Keyed by the field name in the frame's status report
BINARY_SENSORS = (
    BinarySensorEntityDescription(key="playingVideo", name="Playing video"),
    BinarySensorEntityDescription(key="screenOn", name="Screen on"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors for frames that report their status."""
    coordinator = get_coordinator(hass, config_entry)
    if not coordinator.supports_status:
        return

    async_add_entities(
        ImmichFrameBinarySensor(coordinator, config_entry, description)
        for description in BINARY_SENSORS
    )


class ImmichFrameBinarySensor(ImmichFrameEntity, BinarySensorEntity):
    """Immich Frame binary sensor entity."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: ImmichFrameCoordinator,
        config_entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            name=description.name,
            key=description.key,
        )
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        status = self.status
        value = status.get(self.entity_description.key) if status else None
        # The frame reports null when it cannot tell, which is unknown rather than off
        return value if isinstance(value, bool) else None
