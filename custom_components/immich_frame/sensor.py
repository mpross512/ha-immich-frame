"""Sensor platform for Immich Frame."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ImmichFrameCoordinator
from .entity import ImmichFrameEntity, get_coordinator

# Keyed by the field name in the frame's status report.
# Uptime restarts from zero when the app does, which makes a crash or restart visible.
SENSORS = (
    SensorEntityDescription(
        key="uptimeSeconds",
        name="Uptime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for frames that report their status."""
    coordinator = get_coordinator(hass, config_entry)
    if not coordinator.supports_status:
        return

    async_add_entities(
        ImmichFrameSensor(coordinator, config_entry, description)
        for description in SENSORS
    )


class ImmichFrameSensor(ImmichFrameEntity, SensorEntity):
    """Immich Frame sensor entity."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: ImmichFrameCoordinator,
        config_entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            name=description.name,
            key=description.key,
        )
        self.entity_description = description

    @property
    def native_value(self) -> int | float | None:
        status = self.status
        if not status:
            return None
        value = status.get(self.entity_description.key)
        return value if isinstance(value, (int, float)) else None
