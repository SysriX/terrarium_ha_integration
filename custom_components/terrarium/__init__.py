"""Terrarium: enclosures made of several compartments with climate monitoring."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.typing import ConfigType

from .const import (
    CARD_FILE, CONF_DB_URL, CONF_PANEL_ADMIN, CONF_PANEL_ICON, CONF_PANEL_SHOW, CONF_PANEL_TITLE, DEFAULT_PANEL_ICON,
    DEFAULT_PANEL_TITLE, DOMAIN, PANEL_ELEMENT, PANEL_URL, PLATFORMS, STATIC_URL, VERSION,
)
from .manager import TerrariumManager, label_of
from .websocket import async_register as async_register_ws

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type TerrariumConfigEntry = ConfigEntry[TerrariumManager]

CARD_URL = f"{STATIC_URL}/{CARD_FILE}?v={VERSION}"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    await hass.http.async_register_static_paths([
        StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "frontend"), False),
    ])
    # card is available on every dashboard without adding a resource
    frontend.add_extra_js_url(hass, CARD_URL)
    async_register_ws(hass)
    return True


def _opt(entry: ConfigEntry, key: str, default):
    return entry.options.get(key, entry.data.get(key, default))


async def async_setup_entry(hass: HomeAssistant, entry: TerrariumConfigEntry) -> bool:
    mgr = TerrariumManager(hass, entry, _opt(entry, CONF_DB_URL, ""))
    await mgr.async_load()
    entry.runtime_data = mgr
    hass.data.setdefault(DOMAIN, {})["manager"] = mgr

    _sync_devices(hass, entry, mgr)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _remove_stale_entities(hass, entry, mgr)
    await mgr.async_start()
    entry.async_on_unload(mgr.async_unload)

    await _async_panel(hass, entry)
    return True


async def _async_panel(hass: HomeAssistant, entry: ConfigEntry | None) -> None:
    """Register/update the sidebar panel. Only touched when its settings change, so reloading the
    entry (e.g. after editing an enclosure) does not throw the user out of the open panel."""
    store = hass.data.setdefault(DOMAIN, {})
    wanted = None
    if entry is not None and _opt(entry, CONF_PANEL_SHOW, True):
        wanted = (_opt(entry, CONF_PANEL_TITLE, DEFAULT_PANEL_TITLE), _opt(entry, CONF_PANEL_ICON, DEFAULT_PANEL_ICON),
                  bool(_opt(entry, CONF_PANEL_ADMIN, False)))
    current = store.get("panel")
    if wanted == current:
        return
    if current is not None:
        frontend.async_remove_panel(hass, PANEL_URL, warn_if_unknown=False)
    if wanted is not None:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_URL,
            webcomponent_name=PANEL_ELEMENT,
            sidebar_title=wanted[0],
            sidebar_icon=wanted[1],
            module_url=CARD_URL,
            require_admin=wanted[2],
            config={},
        )
    store["panel"] = wanted


def _sync_devices(hass: HomeAssistant, entry: ConfigEntry, mgr: TerrariumManager) -> None:
    """Create enclosure/compartment devices and remove leftovers."""
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    keep: set[str] = set()
    for enc in mgr.enclosures:
        ident = f"enc_{enc['id']}"
        keep.add(ident)
        enc_dev = dev_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, ident)},
            name=f"Terrarienanlage {enc['nr']}" + (f" {enc['name']}" if enc["name"] else ""),
            manufacturer="SysriX",
            model=f"{enc['width']:g} × {enc['height']:g} cm",
        )
        for comp in enc["compartments"]:
            keep.add(comp["id"])
            dev_reg.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, comp["id"])},
                name=f"Terrarium {label_of(enc, comp)}" + (f" {comp['name']}" if comp["name"] else ""),
                manufacturer="SysriX",
                model=f"{comp['width']:g} × {comp['height']:g} cm",
                via_device_id=enc_dev.id,
            )
    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        idents = {i[1] for i in device.identifiers if i[0] == DOMAIN}
        if idents and not idents & keep:
            for ent in er.async_entries_for_device(ent_reg, device.id, include_disabled_entities=True):
                ent_reg.async_remove(ent.entity_id)
            dev_reg.async_remove_device(device.id)


def _remove_stale_entities(hass: HomeAssistant, entry: ConfigEntry, mgr: TerrariumManager) -> None:
    """Remove entities of features that are no longer configured (e.g. ventilation socket removed)."""
    keep = {f"enc_{e['id']}_problems" for e in mgr.enclosures}
    for enc in mgr.enclosures:
        for comp in enc["compartments"]:
            keep.update(f"{comp['id']}_{k}" for k in ("temperature", "humidity", "status", "problem", "cfg_notify"))
            feats = mgr.features(comp)
            keep.update(f"{comp['id']}_cfg_{kind}_auto" for kind, on in feats.items() if on)
            if feats["rain"]:
                keep.add(f"{comp['id']}_rain_now")
    ent_reg = er.async_get(hass)
    for ent in er.async_entries_for_config_entry(ent_reg, entry.entry_id):
        if ent.unique_id not in keep:
            ent_reg.async_remove(ent.entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: TerrariumConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data.get(DOMAIN, {}).pop("manager", None)
    return ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await _async_panel(hass, None)
