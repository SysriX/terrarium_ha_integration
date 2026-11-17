"""WebSocket API used by the terrarium card / panel."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_UPDATE
from .manager import LayoutError, TerrariumManager


def _mgr(hass: HomeAssistant) -> TerrariumManager | None:
    return hass.data.get(DOMAIN, {}).get("manager")


def _not_loaded(connection, msg) -> None:
    connection.send_error(msg["id"], "not_loaded", "Terrarium integration is not set up")


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (ws_get, ws_subscribe, ws_save_enclosure, ws_delete_enclosure,
                    ws_save_compartment, ws_test_notify, ws_notify_targets):
        websocket_api.async_register_command(hass, handler)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/get"})
@callback
def ws_get(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    mgr = _mgr(hass)
    if mgr is None:
        return _not_loaded(connection, msg)
    connection.send_result(msg["id"], mgr.snapshot())


@websocket_api.websocket_command({vol.Required("type"): "terrarium/subscribe"})
@callback
def ws_subscribe(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    mgr = _mgr(hass)
    if mgr is None:
        return _not_loaded(connection, msg)

    @callback
    def forward() -> None:
        current = _mgr(hass)
        if current is not None:
            connection.send_message(websocket_api.event_message(msg["id"], current.snapshot()))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(hass, SIGNAL_UPDATE, forward)
    connection.send_result(msg["id"])
    forward()


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/save_enclosure",
    vol.Required("enclosure"): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save_enclosure(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    mgr = _mgr(hass)
    if mgr is None:
        return _not_loaded(connection, msg)
    try:
        enc, changed = await mgr.async_save_enclosure(msg["enclosure"])
    except LayoutError as err:
        connection.send_error(msg["id"], f"layout_{err.args[0]}", err.args[1] if len(err.args) > 1 else "")
        return
    connection.send_result(msg["id"], {"id": enc["id"], "reload": changed})
    if changed:
        hass.config_entries.async_schedule_reload(mgr.entry.entry_id)


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/delete_enclosure",
    vol.Required("enclosure_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete_enclosure(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    mgr = _mgr(hass)
    if mgr is None:
        return _not_loaded(connection, msg)
    await mgr.async_delete_enclosure(msg["enclosure_id"])
    connection.send_result(msg["id"])
    hass.config_entries.async_schedule_reload(mgr.entry.entry_id)


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/save_compartment",
    vol.Required("compartment_id"): str,
    vol.Required("settings"): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save_compartment(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    mgr = _mgr(hass)
    if mgr is None:
        return _not_loaded(connection, msg)
    try:
        await mgr.async_save_compartment(msg["compartment_id"], msg["settings"])
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Compartment not found")
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/test_notify",
    vol.Required("compartment_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_test_notify(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    mgr = _mgr(hass)
    if mgr is None:
        return _not_loaded(connection, msg)
    try:
        failed = await mgr.async_test_notify(msg["compartment_id"])
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Compartment not found")
        return
    connection.send_result(msg["id"], {"failed": failed})


@websocket_api.websocket_command({vol.Required("type"): "terrarium/notify_targets"})
@callback
def ws_notify_targets(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Notify services (legacy) and notify entities."""
    targets = []
    for service in sorted(hass.services.async_services_for_domain("notify")):
        if service in ("send_message", "persistent_notification"):
            continue
        targets.append({"id": f"notify.{service}", "name": service, "type": "service"})
    for state in hass.states.async_all("notify"):
        targets.append({"id": state.entity_id, "name": state.attributes.get("friendly_name", state.entity_id),
                        "type": "entity"})
    connection.send_result(msg["id"], {"targets": targets})
