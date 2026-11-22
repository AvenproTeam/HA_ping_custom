"""Connectivity binary sensor for the GC-6612Pro Ping integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    ATTR_IP_ADDRESS,
    ATTR_LATENCY_MAX_MS,
    ATTR_LATENCY_MIN_MS,
    ATTR_LATENCY_MS,
    ATTR_PACKET_LOSS,
)
from .coordinator import PingConfigEntry, PingCoordinator
from .entity import PingEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PingConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the connectivity binary sensor."""
    async_add_entities([PingBinarySensor(entry.runtime_data)])


class PingBinarySensor(PingEntity, BinarySensorEntity):
    """Reports whether the host answers ICMP echo requests."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_name = None  # Use the device name

    def __init__(self, coordinator: PingCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, "connectivity")

    @property
    def is_on(self) -> bool:
        """Return true if the host is reachable."""
        return self.coordinator.data.is_alive

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return ping statistics."""
        data = self.coordinator.data
        return {
            ATTR_IP_ADDRESS: data.ip_address,
            ATTR_LATENCY_MS: data.latency_ms,
            ATTR_LATENCY_MIN_MS: data.latency_min_ms,
            ATTR_LATENCY_MAX_MS: data.latency_max_ms,
            ATTR_PACKET_LOSS: data.packet_loss,
        }
