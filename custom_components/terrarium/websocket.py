"""WebSocket API used by the terrarium card / panel."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_UPDATE
from .model import LayoutError
from .manager import TerrariumManager


def _mgr(hass: HomeAssistant) -> TerrariumManager | None:
    return hass.data.get(DOMAIN, {}).get("manager")


def _not_loaded(connection, msg) -> None:
    connection.send_error(msg["id"], "not_loaded", "Terrarium integration is not set up")


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (ws_get, ws_subscribe, ws_save_enclosure, ws_delete_enclosure, ws_save_compartment,
                    ws_test_notify, ws_notify_targets, ws_save_group, ws_delete_group, ws_save_template,
                    ws_delete_template, ws_apply_template, ws_save_light_type, ws_delete_light_type, ws_rain,
                    ws_events):
        websocket_api.async_register_command(hass, handler)


def _reload(hass: HomeAssistant, mgr: TerrariumManager, changed: bool) -> None:
    if changed:
        hass.config_entries.async_schedule_reload(mgr.entry.entry_id)


async def _run(hass, connection, msg, func) -> None:
    """Run a manager call with common error handling. func(mgr) -> (result, reload)."""
    mgr = _mgr(hass)
    if mgr is None:
        return _not_loaded(connection, msg)
    try:
        result, changed = await func(mgr)
    except LayoutError as err:
        connection.send_error(msg["id"], f"layout_{err.args[0]}", err.args[1] if len(err.args) > 1 else "")
        return
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Not found")
        return
    connection.send_result(msg["id"], {**(result or {}), "reload": changed})
    _reload(hass, mgr, changed)


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


@websocket_api.websocket_command({vol.Required("type"): "terrarium/save_enclosure", vol.Required("enclosure"): dict})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save_enclosure(hass, connection, msg) -> None:
    async def f(mgr):
        enc, changed = await mgr.async_save_enclosure(msg["enclosure"])
        return {"id": enc["id"]}, changed
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/delete_enclosure", vol.Required("enclosure_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete_enclosure(hass, connection, msg) -> None:
    async def f(mgr):
        await mgr.async_delete_enclosure(msg["enclosure_id"])
        return {}, True
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/save_compartment",
    vol.Required("compartment_id"): str,
    vol.Required("settings"): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save_compartment(hass, connection, msg) -> None:
    async def f(mgr):
        return {}, await mgr.async_save_compartment(msg["compartment_id"], msg["settings"])
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/test_notify", vol.Required("compartment_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_test_notify(hass, connection, msg) -> None:
    async def f(mgr):
        return {"failed": await mgr.async_test_notify(msg["compartment_id"])}, False
    await _run(hass, connection, msg, f)


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


@websocket_api.websocket_command({vol.Required("type"): "terrarium/save_group", vol.Required("group"): dict})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save_group(hass, connection, msg) -> None:
    async def f(mgr):
        return {}, await mgr.async_save_group(msg["group"])
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/delete_group", vol.Required("group_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete_group(hass, connection, msg) -> None:
    async def f(mgr):
        return {}, await mgr.async_delete_group(msg["group_id"])
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/save_template", vol.Required("template"): dict})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save_template(hass, connection, msg) -> None:
    async def f(mgr):
        tpl = await mgr.async_save_template(msg["template"])
        return {"id": tpl["id"]}, False
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/delete_template", vol.Required("template_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete_template(hass, connection, msg) -> None:
    async def f(mgr):
        await mgr.async_delete_template(msg["template_id"])
        return {}, False
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/apply_template",
    vol.Required("compartment_id"): str,
    vol.Required("template_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_apply_template(hass, connection, msg) -> None:
    async def f(mgr):
        return {}, await mgr.async_apply_template(msg["compartment_id"], msg["template_id"])
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/save_light_type", vol.Required("light_type"): dict})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save_light_type(hass, connection, msg) -> None:
    async def f(mgr):
        lt = await mgr.async_save_light_type(msg["light_type"])
        return {"id": lt["id"]}, False
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({vol.Required("type"): "terrarium/delete_light_type", vol.Required("type_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete_light_type(hass, connection, msg) -> None:
    async def f(mgr):
        await mgr.async_delete_light_type(msg["type_id"])
        return {}, False
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/rain",
    vol.Required("compartment_id"): str,
    vol.Optional("action", default="start"): vol.In(["start", "stop"]),
    vol.Optional("seconds"): vol.Coerce(float),
})
@websocket_api.async_response
async def ws_rain(hass, connection, msg) -> None:
    """Rain by hand (also for non-admin users, like switching a device)."""
    async def f(mgr):
        if mgr.find(msg["compartment_id"])[1] is None:
            raise KeyError(msg["compartment_id"])
        if msg["action"] == "stop":
            mgr.rain_stop(msg["compartment_id"])
        else:
            mgr.rain_now(msg["compartment_id"], msg.get("seconds"))
        return {}, False
    await _run(hass, connection, msg, f)


@websocket_api.websocket_command({
    vol.Required("type"): "terrarium/events",
    vol.Optional("unit"): str,
    vol.Optional("limit", default=50): vol.All(vol.Coerce(int), vol.Range(min=1, max=500)),
})
@websocket_api.async_response
async def ws_events(hass, connection, msg) -> None:
    async def f(mgr):
        return {"events": await mgr.persist.async_events(msg.get("unit"), msg["limit"])}, False
    await _run(hass, connection, msg, f)
