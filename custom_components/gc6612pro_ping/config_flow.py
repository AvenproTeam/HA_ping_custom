"""Config flow for the GC-6612Pro Ping integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_PING_COUNT,
    DEFAULT_PING_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_PING_COUNT,
    MAX_SCAN_INTERVAL,
    MIN_PING_COUNT,
    MIN_SCAN_INTERVAL,
)

HOST_SCHEMA = vol.Schema({vol.Required(CONF_HOST): selector.TextSelector()})

USER_SCHEMA = HOST_SCHEMA.extend({vol.Optional(CONF_NAME): selector.TextSelector()})

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PING_COUNT): vol.All(
            selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_PING_COUNT,
                    max=MAX_PING_COUNT,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Coerce(int),
        ),
        vol.Required(CONF_SCAN_INTERVAL): vol.All(
            selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="s",
                )
            ),
            vol.Coerce(int),
        ),
    }
)

DEFAULT_OPTIONS = {
    CONF_PING_COUNT: DEFAULT_PING_COUNT,
    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
}


class PingConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for GC-6612Pro Ping."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the host to monitor."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if not host:
                errors[CONF_HOST] = "invalid_host"
            else:
                self._async_abort_entries_match({CONF_HOST: host})
                name = (user_input.get(CONF_NAME) or "").strip() or host
                return self.async_create_entry(
                    title=name,
                    data={CONF_HOST: host},
                    options=DEFAULT_OPTIONS,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(USER_SCHEMA, user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the monitored host of an existing entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if not host:
                errors[CONF_HOST] = "invalid_host"
            elif any(
                other.data.get(CONF_HOST) == host
                for other in self._async_current_entries(include_ignore=False)
                if other.entry_id != entry.entry_id
            ):
                return self.async_abort(reason="already_configured")
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_HOST: host}
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                HOST_SCHEMA, user_input or entry.data
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> PingOptionsFlow:
        """Create the options flow."""
        return PingOptionsFlow()


class PingOptionsFlow(OptionsFlowWithReload):
    """Options: number of echo requests and polling interval."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, {**DEFAULT_OPTIONS, **self.config_entry.options}
            ),
        )
