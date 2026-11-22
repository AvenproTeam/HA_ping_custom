"""Test the config flow."""

from unittest.mock import MagicMock

from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.gc6612pro_ping.const import CONF_PING_COUNT, DOMAIN


async def test_user_flow(hass: HomeAssistant, mock_ping: MagicMock) -> None:
    """Create an entry from the user step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: " 10.0.0.1 ", CONF_NAME: "Switch"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Switch"
    assert result["data"] == {CONF_HOST: "10.0.0.1"}
    assert result["options"] == {CONF_PING_COUNT: 3, CONF_SCAN_INTERVAL: 30}


async def test_user_flow_title_defaults_to_host(
    hass: HomeAssistant, mock_ping: MagicMock
) -> None:
    """Without a name, the host is used as title."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "nas.local"}
    )
    assert result["title"] == "nas.local"


async def test_user_flow_empty_host(hass: HomeAssistant) -> None:
    """A blank host shows an error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "   "}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_HOST: "invalid_host"}


async def test_user_flow_duplicate(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    """The same host cannot be added twice."""
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.10"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: MagicMock
) -> None:
    """Options are stored as integers and applied on reload."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_PING_COUNT: 5.0, CONF_SCAN_INTERVAL: 60.0}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert config_entry.options == {CONF_PING_COUNT: 5, CONF_SCAN_INTERVAL: 60}
    assert config_entry.runtime_data.count == 5


async def test_reconfigure(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_ping: MagicMock
) -> None:
    """The host can be changed without recreating the entry."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await config_entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.20"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert config_entry.data[CONF_HOST] == "192.168.1.20"
    assert config_entry.runtime_data.host == "192.168.1.20"
    assert hass.states.get("binary_sensor.router") is not None
