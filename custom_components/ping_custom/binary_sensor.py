# custom_components/ping_custom/binary_sensor.py
"""Binary sensor platform for ping_custom."""

from __future__ import annotations

import logging
from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST
from .ping_util import ping

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ping binary sensor from a config entry."""
    host = entry.data[CONF_HOST]
    name = entry.title  # This is the name you typed in the UI

    async_add_entities([PingBinarySensor(host, name, entry.entry_id)])


class PingBinarySensor(BinarySensorEntity):
    """Representation of a host reachability sensor using ICMP ping."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True

    def __init__(self, host: str, name: str, entry_id: str) -> None:
        """Initialize the sensor."""
        self._host = host
        self._attr_name = name
        self.entity_id = f"binary_sensor.ping_{host.replace('.', '_')}"
        self._attr_unique_id = f"{entry_id}_{host.replace('.', '_')}"
        self._is_on = False
        self._latency: float | None = None

    @property
    def is_on(self) -> bool:
        """Return True if the host is reachable."""
        return self._is_on

    @property
    def extra_state_attributes(self) -> dict[str, float | None]:
        """Return latency as extra attribute."""
        return {"latency_ms": self._latency}

    def update(self) -> None:
        """Update the sensor state by performing a ping."""
        success, latency = ping(self._host, timeout=2)
        self._is_on = bool(success)
        self._latency = latency if success else None