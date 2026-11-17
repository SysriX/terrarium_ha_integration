"""Config flow: one hub entry (panel + database); enclosures are managed in the Terrarium panel/card."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.selector import (
    BooleanSelector, IconSelector, TextSelector, TextSelectorConfig, TextSelectorType,
)

from .const import (
    CONF_DB_URL, CONF_PANEL_ADMIN, CONF_PANEL_ICON, CONF_PANEL_SHOW, CONF_PANEL_TITLE, DEFAULT_PANEL_ICON,
    DEFAULT_PANEL_TITLE, DOMAIN,
)


def _schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_PANEL_SHOW, default=values.get(CONF_PANEL_SHOW, True)): BooleanSelector(),
        vol.Required(CONF_PANEL_TITLE, default=values.get(CONF_PANEL_TITLE, DEFAULT_PANEL_TITLE)): TextSelector(),
        vol.Required(CONF_PANEL_ICON, default=values.get(CONF_PANEL_ICON, DEFAULT_PANEL_ICON)): IconSelector(),
        vol.Required(CONF_PANEL_ADMIN, default=values.get(CONF_PANEL_ADMIN, False)): BooleanSelector(),
        vol.Optional(CONF_DB_URL, description={"suggested_value": values.get(CONF_DB_URL, "")}):
            TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
    })


async def _check_db(hass: HomeAssistant, url: str) -> str | None:
    """None = OK (or no database), otherwise an error key."""
    url = (url or "").strip()
    if not url:
        return None
    if not url.startswith(("mysql://", "mysql+", "mariadb://", "mariadb+", "sqlite://")):
        return "db_url_invalid"
    from .db import TerrariumDB  # noqa: PLC0415 - sqlalchemy only when needed

    db = TerrariumDB(url)
    try:
        await hass.async_add_executor_job(db.connect)
        await hass.async_add_executor_job(db.ping)
    except Exception:  # noqa: BLE001
        return "db_connect"
    finally:
        await hass.async_add_executor_job(db.close)
    return None


class TerrariumConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        errors = {}
        if user_input is not None:
            err = await _check_db(self.hass, user_input.get(CONF_DB_URL, ""))
            if err:
                errors[CONF_DB_URL] = err
            else:
                return self.async_create_entry(title="Terrarium", data=user_input)
        return self.async_show_form(step_id="user", data_schema=_schema(user_input or {}), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> TerrariumOptionsFlow:
        return TerrariumOptionsFlow()


class TerrariumOptionsFlow(OptionsFlowWithReload):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors = {}
        if user_input is not None:
            user_input.setdefault(CONF_DB_URL, "")
            err = await _check_db(self.hass, user_input[CONF_DB_URL])
            if err:
                errors[CONF_DB_URL] = err
            else:
                return self.async_create_entry(data=user_input)
        values = {**self.config_entry.data, **self.config_entry.options, **(user_input or {})}
        return self.async_show_form(step_id="init", data_schema=_schema(values), errors=errors)
