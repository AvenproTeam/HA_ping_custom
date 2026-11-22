"""Data update coordinator for the GC-6612Pro Ping integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_PING_COUNT,
    DEFAULT_PING_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PING_INTERVAL,
    PING_TIMEOUT,
)
from .ping_util import HostLookupError, PingStats, ping

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

    async def _async_update_data(self) -> PingResult:
        """Ping the host with the GC-6612Pro compatible echo request."""
        try:
            stats: PingStats = await self.hass.async_add_executor_job(
                ping, self.host, self.count, PING_TIMEOUT, PING_INTERVAL
            )
        except HostLookupError:
            _LOGGER.debug("Could not resolve host %s", self.host)
            return PingResult(is_alive=False)
        except PermissionError as err:
            raise UpdateFailed(
                "Home Assistant is not allowed to open raw ICMP sockets; "
                "it must run as root (Home Assistant OS does)"
            ) from err
        except OSError as err:
            raise UpdateFailed(f"Error pinging {self.host}: {err}") from err

        if not stats.rtts:
            return PingResult(
                is_alive=False, ip_address=stats.address, packet_loss=100.0
            )

        rtts = stats.rtts
        return PingResult(
            is_alive=True,
            ip_address=stats.address,
            latency_ms=round(sum(rtts) / len(rtts), 2),
            latency_min_ms=round(min(rtts), 2),
            latency_max_ms=round(max(rtts), 2),
            packet_loss=round((1 - len(rtts) / stats.sent) * 100, 1),
        )
