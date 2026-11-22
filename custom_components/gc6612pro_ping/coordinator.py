"""Data update coordinator for the GC-6612Pro Ping integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from icmplib import (
    ICMPLibError,
    NameLookupError,
    SocketPermissionError,
    async_ping,
)

from .const import (
    CONF_PING_COUNT,
    DEFAULT_PING_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PING_INTERVAL,
    PING_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

type PingConfigEntry = ConfigEntry[PingCoordinator]


@dataclass(frozen=True, slots=True)
class PingResult:
    """Result of one ping round."""

    is_alive: bool
    ip_address: str | None = None
    latency_ms: float | None = None
    latency_min_ms: float | None = None
    latency_max_ms: float | None = None
    packet_loss: float | None = None


class PingCoordinator(DataUpdateCoordinator[PingResult]):
    """Ping a host periodically and share the result with all entities."""

    config_entry: PingConfigEntry

    def __init__(self, hass: HomeAssistant, entry: PingConfigEntry) -> None:
        """Initialize the coordinator."""
        self.host: str = entry.data[CONF_HOST]
        self.count: int = int(entry.options.get(CONF_PING_COUNT, DEFAULT_PING_COUNT))
        # Raw (privileged) sockets work on HA OS / containers running as root.
        # Fall back to unprivileged datagram ICMP sockets otherwise.
        self._privileged = True
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {self.host}",
            update_interval=timedelta(
                seconds=int(
                    entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                )
            ),
        )

    async def _ping(self):
        return await async_ping(
            self.host,
            count=self.count,
            interval=PING_INTERVAL,
            timeout=PING_TIMEOUT,
            privileged=self._privileged,
        )

    async def _async_update_data(self) -> PingResult:
        """Ping the host."""
        try:
            try:
                host = await self._ping()
            except SocketPermissionError:
                if not self._privileged:
                    raise
                _LOGGER.debug(
                    "No permission for raw ICMP sockets, using unprivileged mode"
                )
                self._privileged = False
                host = await self._ping()
        except NameLookupError:
            _LOGGER.debug("Could not resolve host %s", self.host)
            return PingResult(is_alive=False)
        except SocketPermissionError as err:
            raise UpdateFailed(
                "Home Assistant is not allowed to open ICMP sockets; "
                "run it as root or allow unprivileged ping (net.ipv4.ping_group_range)"
            ) from err
        except ICMPLibError as err:
            raise UpdateFailed(f"Error pinging {self.host}: {err}") from err

        if not host.is_alive:
            return PingResult(
                is_alive=False, ip_address=host.address, packet_loss=100.0
            )

        return PingResult(
            is_alive=True,
            ip_address=host.address,
            latency_ms=round(host.avg_rtt, 2),
            latency_min_ms=round(host.min_rtt, 2),
            latency_max_ms=round(host.max_rtt, 2),
            packet_loss=round(host.packet_loss * 100, 1),
        )
