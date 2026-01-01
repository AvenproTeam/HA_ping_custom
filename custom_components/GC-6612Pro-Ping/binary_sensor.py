from __future__ import annotations

import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN
from .ping_util import ping

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    host = entry.data[CONF_HOST]
    name = entry.title
    count = entry.options.get("ping_count", 1)

    async_add_entities([PingBinarySensor(host, name, entry.entry_id, count)])


class PingBinarySensor(BinarySensorEntity):
    """Connectivity binary sensor"""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True

    def __init__(self, host: str, name: str, entry_id: str, count: int):
        self._host = host
        self._attr_name = name
        self.entity_id = f"binary_sensor.ping_{host.replace('.', '_')}"
        self._attr_unique_id = f"{entry_id}_{host.replace('.', '_')}"
        self._count = count

        self._is_on = False
        self._latency = None

    @property
    def is_on(self):
        return self._is_on

    @property
    def extra_state_attributes(self):
        return {"latency_ms": self._latency}

    async def async_update(self):
        """Perform ping in executor to avoid blocking."""
        success, latency = await self.hass.async_add_executor_job(
            ping, self._host, 2, self._count
        )
        self._is_on = success
        self._latency = latency if success else None
