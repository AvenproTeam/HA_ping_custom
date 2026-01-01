from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlowWithReload
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.util.network import is_ip_address

from .const import DOMAIN, CONF_HOST, DEFAULT_NAME, CONF_PING_COUNT, DEFAULT_PING_COUNT

_LOGGER = logging.getLogger(__name__)


def _clean_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Clean up the user input."""
    user_input[CONF_HOST] = user_input[CONF_HOST].strip()
    # Ensure ping count has a sensible default
    user_input.setdefault(CONF_PING_COUNT, DEFAULT_PING_COUNT)
    return user_input


class PingCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for GC-6612Pro Ping integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            # Show the form for entering host and optional name
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST): str,
                        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    }
                ),
            )
        
        user_input = _clean_user_input(user_input)
        # Basic validation: ensure host is not empty. Accept hostnames and IPs.
        if not user_input[CONF_HOST]:
            self.async_abort(reason="invalid_host")

        self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
        return self.async_create_entry(
            title=user_input.get(CONF_NAME, user_input[CONF_HOST]),
            data={CONF_HOST: user_input[CONF_HOST]},
            options={CONF_PING_COUNT: user_input.get(CONF_PING_COUNT, DEFAULT_PING_COUNT)},
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowWithReload:
        """Create the options flow for a config entry."""
        # Pass the current config entry into the options flow handler so it has access to data/options
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(OptionsFlowWithReload):
    """Handle an options flow for Ping."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=_clean_user_input(user_input))

        # Use options with fallbacks to data/defaults to avoid KeyError
        host_default = self.config_entry.options.get(CONF_HOST, self.config_entry.data.get(CONF_HOST, ""))
        ping_count_default = self.config_entry.options.get(CONF_PING_COUNT, DEFAULT_PING_COUNT)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=host_default): str,
                    vol.Optional(CONF_PING_COUNT, default=ping_count_default): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=1, max=100, mode=selector.NumberSelectorMode.BOX)
                    ),
                }
            ),
        )