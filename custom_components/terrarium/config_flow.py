"""Config flow: one hub entry; enclosures are managed in the Terrarium panel/card."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers.selector import BooleanSelector, IconSelector, TextSelector

from .const import (
    CONF_PANEL_ADMIN, CONF_PANEL_ICON, CONF_PANEL_SHOW, CONF_PANEL_TITLE, DEFAULT_PANEL_ICON,
    DEFAULT_PANEL_TITLE, DOMAIN,
)


def _schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_PANEL_SHOW, default=values.get(CONF_PANEL_SHOW, True)): BooleanSelector(),
        vol.Required(CONF_PANEL_TITLE, default=values.get(CONF_PANEL_TITLE, DEFAULT_PANEL_TITLE)): TextSelector(),
        vol.Required(CONF_PANEL_ICON, default=values.get(CONF_PANEL_ICON, DEFAULT_PANEL_ICON)): IconSelector(),
        vol.Required(CONF_PANEL_ADMIN, default=values.get(CONF_PANEL_ADMIN, False)): BooleanSelector(),
    })


class TerrariumConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="Terrarium", data=user_input)
        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> TerrariumOptionsFlow:
        return TerrariumOptionsFlow()


class TerrariumOptionsFlow(OptionsFlowWithReload):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init", data_schema=_schema({**self.config_entry.data, **self.config_entry.options}))
