from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, OptionsFlowWithReload
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.util.network import is_ip_address

from .const import DOMAIN, CONF_HOST, CONF_PING_COUNT, DEFAULT_NAME


def _clean(user_input):
    user_input[CONF_HOST] = user_input[CONF_HOST].strip()
    return user_input


class PingCustomConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }),
            )

        user_input = _clean(user_input)

        if not is_ip_address(user_input[CONF_HOST]):
            return self.async_show_form(
                step_id="user",
                errors={"base": "invalid_ip"},
                data_schema=vol.Schema({
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }),
            )

        self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})

        return self.async_create_entry(
            title=user_input[CONF_NAME],
            data={CONF_HOST: user_input[CONF_HOST]},
            options={CONF_HOST: user_input[CONF_HOST], CONF_PING_COUNT: 1},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PingOptionsFlow(config_entry)


class PingOptionsFlow(OptionsFlowWithReload):
    def __init__(self, entry):
        super().__init__(entry)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            user_input = _clean(user_input)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_HOST,
                    default=self.config_entry.options[CONF_HOST],
                ): str,
                vol.Optional(
                    CONF_PING_COUNT,
                    default=self.config_entry.options[CONF_PING_COUNT],
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=100,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }),
        )
