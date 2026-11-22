"""Test setup and entities."""

from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.gc6612pro_ping.ping_util import HostLookupError, PingStats


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_reachable(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: MagicMock
) -> None:
    """Reachable host exposes state, attributes and sensors."""
    await _setup(hass, config_entry)
    assert config_entry.state is ConfigEntryState.LOADED

    state = hass.states.get("binary_sensor.router")
    assert state.state == STATE_ON
    assert state.attributes["latency_ms"] == 2.0
    assert state.attributes["latency_min_ms"] == 1.0
    assert state.attributes["latency_max_ms"] == 3.0
    assert state.attributes["packet_loss"] == 0.0
    assert state.attributes["ip_address"] == "192.168.1.10"

    assert hass.states.get("sensor.router_latency").state == "2.0"
    assert hass.states.get("sensor.router_packet_loss").state == "0.0"
    host, count, *_ = mock_ping.call_args.args
    assert (host, count) == ("192.168.1.10", 3)

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.NOT_LOADED


async def test_partial_loss(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: MagicMock
) -> None:
    """One reply out of three is reachable with 66.7 % loss."""
    mock_ping.return_value = PingStats("192.168.1.10", 3, [4.0])
    await _setup(hass, config_entry)
    assert hass.states.get("binary_sensor.router").state == STATE_ON
    assert hass.states.get("sensor.router_packet_loss").state == "66.7"


async def test_unreachable(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: MagicMock
) -> None:
    """Host without replies is off."""
    mock_ping.return_value = PingStats("192.168.1.10", 3, [])
    await _setup(hass, config_entry)

    state = hass.states.get("binary_sensor.router")
    assert state.state == STATE_OFF
    assert state.attributes["latency_ms"] is None
    assert hass.states.get("sensor.router_packet_loss").state == "100.0"


async def test_dns_failure_is_off(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: MagicMock
) -> None:
    """Unresolvable hostname is reported as unreachable, not as an error."""
    mock_ping.side_effect = HostLookupError("nope.local")
    await _setup(hass, config_entry)
    assert hass.states.get("binary_sensor.router").state == STATE_OFF


async def test_no_raw_socket_permission(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: MagicMock
) -> None:
    """Setup is retried when raw ICMP sockets cannot be opened."""
    mock_ping.side_effect = PermissionError(1, "Operation not permitted")
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
