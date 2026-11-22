"""Latency and packet loss sensors for the GC-6612Pro Ping integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import PingConfigEntry, PingCoordinator, PingResult
from .entity import PingEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class PingSensorEntityDescription(SensorEntityDescription):
    """Describes a ping sensor."""

    value_fn: Callable[[PingResult], float | None]


SENSORS: tuple[PingSensorEntityDescription, ...] = (
    PingSensorEntityDescription(
        key="latency",
        translation_key="latency",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.latency_ms,
    ),
    PingSensorEntityDescription(
        key="packet_loss",
        translation_key="packet_loss",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=0,
        value_fn=lambda data: data.packet_loss,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PingConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the ping sensors."""
    async_add_entities(
        PingSensor(entry.runtime_data, description) for description in SENSORS
    )


class PingSensor(PingEntity, SensorEntity):
    """A numeric ping statistic."""

    entity_description: PingSensorEntityDescription

    def __init__(
        self, coordinator: PingCoordinator, description: PingSensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
