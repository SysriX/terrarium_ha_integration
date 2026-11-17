"""Terrarium manager: storage, climate evaluation and notifications."""
from __future__ import annotations

import copy
import logging
import uuid
from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_COMPARTMENT, DEFAULT_ENCLOSURE, DEVICE_KINDS, DOMAIN, ENCLOSURE_COLORS, EVENT_ALARM,
    LOOK_BACKGROUNDS, LOOK_DECOR, LOOK_SUBSTRATES, P_HUM_HIGH, P_HUM_LOW, P_OFFLINE, P_TEMP_HIGH,
    P_TEMP_LOW, S_ALARM, S_NOT_CONFIGURED, S_OFFLINE, S_OK, S_PENDING, SIGNAL_UPDATE, STORE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

EPS = 0.01

# entity keys per platform (used for renaming entity ids after renumbering)
COMP_ENTITY_KEYS = {
    "sensor": ["temperature", "humidity", "status"],
    "binary_sensor": ["problem"],
    "switch": ["cfg_notify"],
}

TEXTS = {
    "de": {
        P_TEMP_LOW: "Temperatur zu niedrig: {value} °C (min. {limit} °C)",
        P_TEMP_HIGH: "Temperatur zu hoch: {value} °C (max. {limit} °C)",
        P_HUM_LOW: "Luftfeuchtigkeit zu niedrig: {value} % (min. {limit} %)",
        P_HUM_HIGH: "Luftfeuchtigkeit zu hoch: {value} % (max. {limit} %)",
        P_OFFLINE: "Sensor liefert keine Werte",
        "clear": "Wieder in Ordnung: {what}",
        "repeat": "Weiterhin: ",
        "test": "Testmeldung – Benachrichtigungen funktionieren.",
        "title": "Terrarium {label}",
    },
    "en": {
        P_TEMP_LOW: "Temperature too low: {value} °C (min. {limit} °C)",
        P_TEMP_HIGH: "Temperature too high: {value} °C (max. {limit} °C)",
        P_HUM_LOW: "Humidity too low: {value} % (min. {limit} %)",
        P_HUM_HIGH: "Humidity too high: {value} % (max. {limit} %)",
        P_OFFLINE: "Sensor delivers no values",
        "clear": "Back to normal: {what}",
        "repeat": "Still: ",
        "test": "Test message – notifications are working.",
        "title": "Terrarium {label}",
    },
}


def _num(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def merge_known(default: Any, incoming: Any) -> Any:
    """Deep-merge incoming onto default, keeping only keys known in default."""
    if isinstance(default, dict):
        src = incoming if isinstance(incoming, dict) else {}
        out = {}
        for key, dval in default.items():
            if key in src:
                out[key] = merge_known(dval, src[key])
            else:
                out[key] = copy.deepcopy(dval)
        return out
    if isinstance(default, list):
        return copy.deepcopy(incoming) if isinstance(incoming, list) else copy.deepcopy(default)
    if isinstance(default, bool):
        return bool(incoming) if incoming is not None else default
    if isinstance(default, (int, float)) and not isinstance(default, bool):
        n = _num(incoming)
        return n if n is not None else default
    if default is None:
        # numbers that may be empty
        return _num(incoming)
    if isinstance(default, str):
        return str(incoming) if incoming is not None else default
    return incoming


def deep_update(base: dict, upd: dict) -> dict:
    """Recursive merge (dicts merged, everything else replaced)."""
    out = copy.deepcopy(base)
    for key, val in (upd or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_update(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def _entity_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if isinstance(item, str) and "." in item and item not in out:
            out.append(item.strip())
    return out


def sanitize_compartment_settings(comp: dict) -> dict:
    """Normalize the settings part of a compartment (everything except layout)."""
    out = merge_known(DEFAULT_COMPARTMENT, comp)
    # keep reserved module dicts as they are
    for key in ("light", "ventilation", "rain"):
        if isinstance(comp.get(key), dict):
            out[key] = copy.deepcopy(comp[key])
    clim = out["climate"]
    clim["temp_sensors"] = _entity_list(clim["temp_sensors"])
    clim["hum_sensors"] = _entity_list(clim["hum_sensors"])
    clim["delay"] = max(0.0, clim["delay"])
    clim["temp_hyst"] = max(0.0, clim["temp_hyst"])
    clim["hum_hyst"] = max(0.0, clim["hum_hyst"])
    for key in ("start", "end"):
        if _parse_time(clim["night"][key]) is None:
            clim["night"][key] = DEFAULT_COMPARTMENT["climate"]["night"][key]
    notify = out["notify"]
    notify["targets"] = _entity_list(notify["targets"])
    notify["repeat"] = max(0.0, notify["repeat"])
    devices = []
    for dev in comp.get("devices") or []:
        if not isinstance(dev, dict):
            continue
        ent = str(dev.get("entity_id") or "").strip()
        if "." not in ent:
            continue
        kind = dev.get("kind") if dev.get("kind") in DEVICE_KINDS else "other"
        devices.append({"entity_id": ent, "kind": kind, "name": str(dev.get("name") or "")})
    out["devices"] = devices
    look = out["look"]
    if look["substrate"] not in LOOK_SUBSTRATES:
        look["substrate"] = "soil"
    if look["decor"] not in LOOK_DECOR:
        look["decor"] = "plants"
    if look["background"] not in LOOK_BACKGROUNDS:
        look["background"] = "rock"
    return out


def _parse_time(value: Any) -> time | None:
    try:
        parts = str(value).split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError, TypeError):
        return None


def label_of(enc: dict, comp: dict) -> str:
    return f"{enc['nr']}.{comp['nr']}"


def number_compartments(comps: list[dict]) -> None:
    """Number compartments top -> bottom, left -> right."""
    order = sorted(comps, key=lambda c: (round(c["y"], 1), round(c["x"], 1)))
    for idx, comp in enumerate(order, start=1):
        comp["nr"] = idx
    comps.sort(key=lambda c: c["nr"])


class LayoutError(ValueError):
    """Invalid enclosure layout. args[0] = error key, args[1] = details."""


def validate_layout(enc: dict) -> None:
    width, height = enc["width"], enc["height"]
    if width <= 0 or height <= 0:
        raise LayoutError("size", "")
    comps = enc["compartments"]
    for comp in comps:
        if comp["width"] <= 0 or comp["height"] <= 0:
            raise LayoutError("comp_size", comp.get("name") or comp["id"])
        if (comp["x"] < -EPS or comp["y"] < -EPS or comp["x"] + comp["width"] > width + EPS
                or comp["y"] + comp["height"] > height + EPS):
            raise LayoutError("out_of_bounds", comp.get("name") or comp["id"])
    for i, a in enumerate(comps):
        for b in comps[i + 1:]:
            if (a["x"] < b["x"] + b["width"] - EPS and b["x"] < a["x"] + a["width"] - EPS
                    and a["y"] < b["y"] + b["height"] - EPS and b["y"] < a["y"] + a["height"] - EPS):
                raise LayoutError("overlap", f"{a.get('name') or a['id']} / {b.get('name') or b['id']}")


class TerrariumManager:
    """Holds all enclosures and evaluates their climate."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.store: Store = Store(hass, STORE_VERSION, DOMAIN)
        self.enclosures: list[dict] = []
        self.live: dict[str, dict] = {}
        # comp_id -> problem key -> {"since", "active", "last", "value", "limit"}
        # kept in hass.data so a reload (after editing an enclosure) does not re-send active alarms
        self._track: dict[str, dict[str, dict]] = hass.data.setdefault(DOMAIN, {}).setdefault("track", {})
        self._unsub_states = None
        self._unsub_timer = None

    # ------------------------------------------------------------------ storage
    async def async_load(self) -> None:
        data = await self.store.async_load() or {}
        encs = []
        for raw in data.get("enclosures", []):
            try:
                encs.append(self._normalize_enclosure(raw, raw))
            except (LayoutError, KeyError, TypeError) as err:
                _LOGGER.warning("Terrarienanlage verworfen (%s): %s", err, raw.get("name"))
        self.enclosures = sorted(encs, key=lambda e: e["nr"])

    async def async_save(self) -> None:
        await self.store.async_save({"enclosures": self.enclosures})

    # ------------------------------------------------------------------ lookup
    def find(self, comp_id: str) -> tuple[dict, dict] | tuple[None, None]:
        for enc in self.enclosures:
            for comp in enc["compartments"]:
                if comp["id"] == comp_id:
                    return enc, comp
        return None, None

    def enclosure(self, enc_id: str) -> dict | None:
        return next((e for e in self.enclosures if e["id"] == enc_id), None)

    def structure(self) -> set[tuple[str, str]]:
        """Set of (enclosure id, compartment id) incl. enclosure-only rows."""
        out = set()
        for enc in self.enclosures:
            out.add((enc["id"], ""))
            for comp in enc["compartments"]:
                out.add((enc["id"], comp["id"]))
        return out

    # ------------------------------------------------------------------ editing
    def _normalize_enclosure(self, raw: dict, existing: dict | None) -> dict:
        enc = merge_known({k: v for k, v in DEFAULT_ENCLOSURE.items() if k != "compartments"}, raw)
        enc["id"] = str(raw.get("id") or uuid.uuid4().hex[:10])
        enc["nr"] = int(enc["nr"]) if enc["nr"] else 1
        if enc["color"] not in ENCLOSURE_COLORS:
            enc["color"] = "wood"
        old = {c["id"]: c for c in (existing or {}).get("compartments", []) if isinstance(c, dict) and c.get("id")}
        comps = []
        for rc in raw.get("compartments") or []:
            cid = str(rc.get("id") or uuid.uuid4().hex[:10])
            base = old.get(cid, {})
            settings = sanitize_compartment_settings(
                deep_update(base, {k: v for k, v in rc.items() if k in DEFAULT_COMPARTMENT}))
            comp = {
                "id": cid,
                "nr": 0,
                "x": _num(rc.get("x")) or 0.0,
                "y": _num(rc.get("y")) or 0.0,
                "width": _num(rc.get("width")) or 0.0,
                "height": _num(rc.get("height")) or 0.0,
                **settings,
            }
            comps.append(comp)
        enc["compartments"] = comps
        validate_layout(enc)
        number_compartments(comps)
        return enc

    async def async_save_enclosure(self, raw: dict) -> tuple[dict, bool]:
        """Create or update an enclosure. Returns (enclosure, structure_changed)."""
        before = self.structure()
        old_labels = self._labels()
        existing = self.enclosure(raw.get("id")) if raw.get("id") else None
        if existing is None:
            raw = {**raw, "id": None}
            if not raw.get("nr"):
                raw["nr"] = max((e["nr"] for e in self.enclosures), default=0) + 1
        enc = self._normalize_enclosure(raw, existing)
        if any(e["nr"] == enc["nr"] and e["id"] != enc["id"] for e in self.enclosures):
            raise LayoutError("nr_taken", str(enc["nr"]))
        if existing is None:
            self.enclosures.append(enc)
        else:
            self.enclosures[self.enclosures.index(existing)] = enc
        self.enclosures.sort(key=lambda e: e["nr"])
        await self.async_save()
        self._rename_entities(old_labels)
        changed = before != self.structure()
        if not changed:
            self._resubscribe()
            self.evaluate_all()
        return enc, changed

    async def async_delete_enclosure(self, enc_id: str) -> None:
        enc = self.enclosure(enc_id)
        if enc is None:
            return
        self.enclosures.remove(enc)
        for comp in enc["compartments"]:
            self._track.pop(comp["id"], None)
            self.live.pop(comp["id"], None)
        await self.async_save()

    async def async_save_compartment(self, comp_id: str, settings: dict) -> dict:
        enc, comp = self.find(comp_id)
        if comp is None:
            raise KeyError(comp_id)
        merged = sanitize_compartment_settings(deep_update(comp, settings))
        comp.update(merged)
        await self.async_save()
        self._rename_entities({})  # device name follows the compartment name
        self._resubscribe()
        self.evaluate_all()
        return comp

    async def async_set_notify_enabled(self, comp_id: str, enabled: bool) -> None:
        _enc, comp = self.find(comp_id)
        if comp is None:
            return
        comp["notify"]["enabled"] = enabled
        await self.async_save()
        async_dispatcher_send(self.hass, SIGNAL_UPDATE)

    def _labels(self) -> dict[str, str]:
        return {c["id"]: label_of(e, c) for e in self.enclosures for c in e["compartments"]}

    def _rename_entities(self, old_labels: dict[str, str]) -> None:
        """After renumbering: move entity ids that still follow the default pattern."""
        reg = er.async_get(self.hass)
        new_labels = self._labels()
        moves = []  # (temporary id, final id) – two steps, so swapped numbers work
        for cid, old in old_labels.items():
            new = new_labels.get(cid)
            if not new or new == old:
                continue
            for platform, keys in COMP_ENTITY_KEYS.items():
                for key in keys:
                    ent_id = reg.async_get_entity_id(platform, DOMAIN, f"{cid}_{key}")
                    old_id = f"{platform}.terrarium_{old.replace('.', '_')}_{key}"
                    if not ent_id or ent_id != old_id:
                        continue  # renamed by the user: leave it alone
                    tmp_id = f"{platform}.terrarium_renumber_{cid}_{key}"
                    reg.async_update_entity(ent_id, new_entity_id=tmp_id)
                    moves.append((tmp_id, f"{platform}.terrarium_{new.replace('.', '_')}_{key}"))
        for tmp_id, new_id in moves:
            target = new_id if reg.async_get(new_id) is None else new_id + "_2"
            reg.async_update_entity(tmp_id, new_entity_id=target)
        # device names follow the new numbers
        dev_reg = dr.async_get(self.hass)
        for enc in self.enclosures:
            for comp in enc["compartments"]:
                dev = next((d for d in dr.async_entries_for_config_entry(dev_reg, self.entry.entry_id)
                            if (DOMAIN, comp["id"]) in d.identifiers), None)
                name = f"Terrarium {label_of(enc, comp)}" + (f" {comp['name']}" if comp["name"] else "")
                if dev and dev.name != name:
                    dev_reg.async_update_device(dev.id, name=name)

    # ------------------------------------------------------------------ runtime
    async def async_start(self) -> None:
        self._resubscribe()
        self._unsub_timer = async_track_time_interval(self.hass, self._tick, timedelta(seconds=60))
        self.evaluate_all()

    @callback
    def async_unload(self) -> None:
        if self._unsub_states:
            self._unsub_states()
            self._unsub_states = None
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None

    @callback
    def _resubscribe(self) -> None:
        if self._unsub_states:
            self._unsub_states()
            self._unsub_states = None
        watched: set[str] = set()
        for enc in self.enclosures:
            for comp in enc["compartments"]:
                watched.update(comp["climate"]["temp_sensors"])
                watched.update(comp["climate"]["hum_sensors"])
                watched.update(d["entity_id"] for d in comp["devices"])
        if watched:
            self._unsub_states = async_track_state_change_event(self.hass, list(watched), self._state_changed)

    @callback
    def _tick(self, _now: datetime) -> None:
        self.evaluate_all()

    @callback
    def _state_changed(self, _event: Event) -> None:
        self.evaluate_all()

    def _read(self, entity_ids: list[str]) -> tuple[float | None, list[dict]]:
        values, details = [], []
        for ent in entity_ids:
            st = self.hass.states.get(ent)
            val = None
            if st is not None and st.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                val = _num(st.state)
            details.append({"entity_id": ent, "value": val,
                            "name": st.attributes.get("friendly_name", ent) if st else ent})
            if val is not None:
                values.append(val)
        if not values:
            return None, details
        return round(sum(values) / len(values), 2), details

    def _period(self, clim: dict, now: datetime) -> str:
        night = clim["night"]
        if not night["enabled"]:
            return "day"
        start, end = _parse_time(night["start"]), _parse_time(night["end"])
        if start is None or end is None or start == end:
            return "day"
        cur = dt_util.as_local(now).time()
        if start < end:
            return "night" if start <= cur < end else "day"
        return "night" if cur >= start or cur < end else "day"

    def targets(self, clim: dict, period: str) -> dict:
        out = {k: clim[k] for k in ("temp_min", "temp_max", "hum_min", "hum_max")}
        if period == "night":
            for key in out:
                if clim["night"].get(key) is not None:
                    out[key] = clim["night"][key]
        return out

    @callback
    def evaluate_all(self) -> None:
        now = dt_util.utcnow()
        for enc in self.enclosures:
            for comp in enc["compartments"]:
                self._evaluate(enc, comp, now)
        async_dispatcher_send(self.hass, SIGNAL_UPDATE)

    def _evaluate(self, enc: dict, comp: dict, now: datetime) -> None:
        clim = comp["climate"]
        temp, temp_det = self._read(clim["temp_sensors"])
        hum, hum_det = self._read(clim["hum_sensors"])
        period = self._period(clim, now)
        tgt = self.targets(clim, period)
        track = self._track.setdefault(comp["id"], {})
        configured = bool(clim["temp_sensors"] or clim["hum_sensors"])

        conds: dict[str, tuple[bool, float | None, float | None]] = {}
        offline = (bool(clim["temp_sensors"]) and temp is None) or (bool(clim["hum_sensors"]) and hum is None)
        conds[P_OFFLINE] = (offline, None, None)

        def check(key: str, value: float | None, limit: float | None, low: bool, hyst: float, used: bool) -> None:
            if value is None and used:
                return  # no value: keep the current state of this problem (offline is reported separately)
            if value is None or limit is None:
                conds[key] = (False, value, limit)
                return
            current = key in track
            if low:
                bad = value < (limit + hyst if current else limit)
            else:
                bad = value > (limit - hyst if current else limit)
            conds[key] = (bad, value, limit)

        t_used, h_used = bool(clim["temp_sensors"]), bool(clim["hum_sensors"])
        check(P_TEMP_LOW, temp, tgt["temp_min"], True, clim["temp_hyst"], t_used)
        check(P_TEMP_HIGH, temp, tgt["temp_max"], False, clim["temp_hyst"], t_used)
        check(P_HUM_LOW, hum, tgt["hum_min"], True, clim["hum_hyst"], h_used)
        check(P_HUM_HIGH, hum, tgt["hum_max"], False, clim["hum_hyst"], h_used)

        delay = timedelta(minutes=clim["delay"])
        repeat = comp["notify"]["repeat"]
        for key, (bad, value, limit) in conds.items():
            entry = track.get(key)
            if bad:
                if entry is None:
                    entry = track[key] = {"since": now, "active": False, "last": None}
                entry["value"], entry["limit"] = value, limit
                if not entry["active"] and now - entry["since"] >= delay:
                    entry["active"] = True
                    entry["last"] = now
                    self._alert(enc, comp, key, "start", entry)
                elif entry["active"] and repeat > 0 and entry["last"] and now - entry["last"] >= timedelta(minutes=repeat):
                    entry["last"] = now
                    self._alert(enc, comp, key, "repeat", entry)
            elif entry is not None:
                if entry["active"]:
                    self._alert(enc, comp, key, "clear", entry)
                track.pop(key, None)

        active = [k for k, e in track.items() if e["active"]]
        pending = [k for k, e in track.items() if not e["active"]]
        if not configured:
            status = S_NOT_CONFIGURED
        elif P_OFFLINE in active:
            status = S_OFFLINE
        elif active:
            status = S_ALARM
        elif pending:
            status = S_PENDING
        else:
            status = S_OK

        devices = []
        for dev in comp["devices"]:
            st = self.hass.states.get(dev["entity_id"])
            devices.append({**dev, "state": st.state if st else None})

        self.live[comp["id"]] = {
            "temperature": temp,
            "humidity": hum,
            "temp_sensors": temp_det,
            "hum_sensors": hum_det,
            "period": period,
            "targets": tgt,
            "status": status,
            "problems": active,
            "pending": pending,
            "since": {k: e["since"].isoformat() for k, e in track.items()},
            "devices": devices,
        }

    # ------------------------------------------------------------------ notify
    def _lang(self) -> dict:
        lang = (self.hass.config.language or "en").split("-")[0]
        return TEXTS.get(lang, TEXTS["en"])

    def _problem_text(self, key: str, entry: dict) -> str:
        txt = self._lang()[key]
        val = entry.get("value")
        lim = entry.get("limit")
        return txt.format(value=f"{val:.1f}" if isinstance(val, (int, float)) else "–",
                          limit=f"{lim:g}" if isinstance(lim, (int, float)) else "–")

    def _alert(self, enc: dict, comp: dict, key: str, kind: str, entry: dict) -> None:
        label = label_of(enc, comp)
        notify = comp["notify"]
        self.hass.bus.async_fire(EVENT_ALARM, {
            "enclosure": enc["name"], "enclosure_nr": enc["nr"], "compartment": comp["name"],
            "label": label, "compartment_id": comp["id"], "problem": key, "kind": kind,
            "value": entry.get("value"), "limit": entry.get("limit"),
        })
        if not notify["enabled"]:
            return
        if key == P_OFFLINE and not notify["offline"]:
            return
        if kind == "clear" and not notify["clear"]:
            if notify["persistent"]:
                persistent_notification.async_dismiss(self.hass, f"{DOMAIN}_{comp['id']}_{key}")
            return
        texts = self._lang()
        what = self._problem_text(key, entry)
        if kind == "clear":
            message = texts["clear"].format(what=what.split(":")[0])
        elif kind == "repeat":
            message = texts["repeat"] + what
        else:
            message = what
        title = texts["title"].format(label=label) + (f" – {comp['name']}" if comp["name"] else "")
        self.hass.async_create_task(self.async_send(notify["targets"], title, message))
        if notify["persistent"]:
            nid = f"{DOMAIN}_{comp['id']}_{key}"
            if kind == "clear":
                persistent_notification.async_dismiss(self.hass, nid)
            else:
                persistent_notification.async_create(self.hass, message, title, nid)

    async def async_send(self, targets: list[str], title: str, message: str) -> list[str]:
        """Send to notify services and notify entities. Returns failed targets."""
        failed = []
        for target in targets:
            try:
                if self.hass.states.get(target) is not None and target.startswith("notify."):
                    await self.hass.services.async_call(
                        "notify", "send_message", {"entity_id": target, "title": title, "message": message},
                        blocking=True)
                    continue
                service = target.split(".", 1)[1] if target.startswith("notify.") else target
                if self.hass.services.has_service("notify", service):
                    await self.hass.services.async_call(
                        "notify", service, {"title": title, "message": message}, blocking=True)
                else:
                    failed.append(target)
            except Exception as err:  # noqa: BLE001 - a failing target must not stop the others
                _LOGGER.warning("Benachrichtigung an %s fehlgeschlagen: %s", target, err)
                failed.append(target)
        return failed

    async def async_test_notify(self, comp_id: str) -> list[str]:
        enc, comp = self.find(comp_id)
        if comp is None:
            raise KeyError(comp_id)
        texts = self._lang()
        title = texts["title"].format(label=label_of(enc, comp)) + (f" – {comp['name']}" if comp["name"] else "")
        return await self.async_send(comp["notify"]["targets"], title, texts["test"])

    # ------------------------------------------------------------------ snapshot
    def entity_ids(self, comp_id: str) -> dict[str, str | None]:
        reg = er.async_get(self.hass)
        out = {}
        for platform, keys in COMP_ENTITY_KEYS.items():
            for key in keys:
                out[key] = reg.async_get_entity_id(platform, DOMAIN, f"{comp_id}_{key}")
        return out

    def snapshot(self) -> dict:
        encs = []
        for enc in self.enclosures:
            e = copy.deepcopy(enc)
            for comp in e["compartments"]:
                comp["label"] = label_of(enc, comp)
                comp["live"] = self.live.get(comp["id"], {})
                comp["entities"] = self.entity_ids(comp["id"])
            encs.append(e)
        return {"enclosures": encs}
