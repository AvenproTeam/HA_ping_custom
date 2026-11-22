"""Fixtures for testing."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.gc6612pro_ping.const import CONF_PING_COUNT, DOMAIN
from custom_components.gc6612pro_ping.ping_util import PingStats


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    return


@pytest.fixture
def mock_ping() -> Generator[MagicMock]:
    """Patch the ping routine so no real packets are sent."""
    with patch(
        "custom_components.gc6612pro_ping.coordinator.ping",
        return_value=PingStats("192.168.1.10", 3, [1.0, 2.0, 3.0]),
    ) as mock:
        yield mock


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Return a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Router",
        data={CONF_HOST: "192.168.1.10"},
        options={CONF_PING_COUNT: 3, CONF_SCAN_INTERVAL: 30},
    )
