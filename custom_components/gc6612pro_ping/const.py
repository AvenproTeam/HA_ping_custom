"""Constants for the GC-6612Pro Ping integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "gc6612pro_ping"

CONF_PING_COUNT: Final = "ping_count"

DEFAULT_PING_COUNT: Final = 3
MIN_PING_COUNT: Final = 1
MAX_PING_COUNT: Final = 20

DEFAULT_SCAN_INTERVAL: Final = 30  # seconds
MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 3600

# Seconds to wait for each echo reply and between consecutive echo requests.
PING_TIMEOUT: Final = 2
PING_INTERVAL: Final = 0.2

ATTR_LATENCY_MS: Final = "latency_ms"
ATTR_LATENCY_MIN_MS: Final = "latency_min_ms"
ATTR_LATENCY_MAX_MS: Final = "latency_max_ms"
ATTR_PACKET_LOSS: Final = "packet_loss"
ATTR_IP_ADDRESS: Final = "ip_address"
