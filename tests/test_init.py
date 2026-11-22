"""Test setup and entities."""

from unittest.mock import AsyncMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from icmplib import Host, NameLookupError, SocketPermissionError
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_reachable(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: AsyncMock
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
    assert mock_ping.call_args.kwargs["count"] == 3

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.NOT_LOADED


async def test_unreachable(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: AsyncMock
) -> None:
    """Host without replies is off."""
    mock_ping.return_value = Host("192.168.1.10", 3, [])
    await _setup(hass, config_entry)

    state = hass.states.get("binary_sensor.router")
    assert state.state == STATE_OFF
    assert state.attributes["latency_ms"] is None
    assert hass.states.get("sensor.router_packet_loss").state == "100.0"


async def test_dns_failure_is_off(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: AsyncMock
) -> None:
    """Unresolvable hostname is reported as unreachable, not as an error."""
    mock_ping.side_effect = NameLookupError("nope.local")
    await _setup(hass, config_entry)
    assert hass.states.get("binary_sensor.router").state == STATE_OFF


async def test_unprivileged_fallback(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: AsyncMock
) -> None:
    """Falls back to unprivileged sockets when raw sockets are not allowed."""
    host = mock_ping.return_value
    mock_ping.side_effect = [SocketPermissionError(True), host]
    await _setup(hass, config_entry)

    assert hass.states.get("binary_sensor.router").state == STATE_ON
    assert mock_ping.call_args_list[0].kwargs["privileged"] is True
    assert mock_ping.call_args_list[1].kwargs["privileged"] is False


async def test_no_icmp_permission(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: AsyncMock
) -> None:
    """Setup is retried when ICMP sockets cannot be opened at all."""
    mock_ping.side_effect = SocketPermissionError(False)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
