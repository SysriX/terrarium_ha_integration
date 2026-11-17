"""Terrarium manager: data, climate evaluation, notifications, automation and persistence."""
from __future__ import annotations

import copy
import logging
from datetime import datetime, timedelta

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.util import dt as dt_util

from .automation import Automation
from .const import (
    DOMAIN, EVENT_ALARM, KINDS, P_HUM_HIGH, P_HUM_LOW, P_OFFLINE, P_TEMP_HIGH, P_TEMP_LOW, S_ALARM,
    S_NOT_CONFIGURED, S_OFFLINE, S_OK, S_PENDING, SIGNAL_UPDATE,
)
from .model import (
    LayoutError, apply_template, deep_update, default_light_types, kind_config_of, normalize_enclosure, num,
    parse_time, sanitize_compartment_settings, sanitize_group, sanitize_kind_config, sanitize_light_type,
    sanitize_template,
)
from .persist import Persistence

_LOGGER = logging.getLogger(__name__)

# entity keys per platform (used for renaming entity ids after renumbering)
COMP_ENTITY_KEYS = {
    "sensor": ["temperature", "humidity", "status"],
    "binary_sensor": ["problem"],
    "switch": ["cfg_notify", "cfg_light_auto", "cfg_rain_auto", "cfg_vent_auto"],
    "button": ["rain_now"],
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
        "group": "Gruppe",
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
        "group": "Group",
    },
}


def label_of(enc: dict, comp: dict) -> str:
    return f"{enc['nr']}.{comp['nr']}"


class TerrariumManager:
    """Holds all data, evaluates climate, runs the automation."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, db_url: str = "") -> None:
        self.hass = hass
        self.entry = entry
        self.persist = Persistence(hass, db_url)
        self.state: dict = {"enclosures": [], "groups": [], "templates": [], "light_types": [], "settings": {}}
        self.live: dict[str, dict] = {}
        # kept in hass.data so a reload (after editing an enclosure) does not re-send active alarms
        self._track: dict[str, dict[str, dict]] = hass.data.setdefault(DOMAIN, {}).setdefault("track", {})
        self.auto = Automation(self)
        self._unsub_states = None
        self._unsub_timer = None
        self._unsub_slow = None

    # ------------------------------------------------------------------ data access
    @property
    def enclosures(self) -> list[dict]:
        return self.state["enclosures"]

    @property
    def groups(self) -> list[dict]:
        return self.state["groups"]

    @property
    def templates(self) -> list[dict]:
        return self.state["templates"]

    @property
    def light_types(self) -> list[dict]:
        return self.state["light_types"]

    def light_type(self, type_id: str) -> dict | None:
        return next((t for t in self.light_types if t["id"] == type_id), None)

    def find(self, comp_id: str) -> tuple[dict, dict] | tuple[None, None]:
        for enc in self.enclosures:
            for comp in enc["compartments"]:
                if comp["id"] == comp_id:
                    return enc, comp
        return None, None

    def enclosure(self, enc_id: str) -> dict | None:
        return next((e for e in self.enclosures if e["id"] == enc_id), None)

    def comp_ids(self) -> set[str]:
        return {c["id"] for e in self.enclosures for c in e["compartments"]}

    def group_of(self, comp_id: str, kind: str) -> dict | None:
        return next((g for g in self.groups if g["kind"] == kind and comp_id in g["members"]), None)

    def effective(self, comp: dict, kind: str) -> dict:
        grp = self.group_of(comp["id"], kind)
        return grp["config"] if grp else kind_config_of(kind, comp)

    def units(self) -> list[dict]:
        """Everything that is switched together: groups + terrariums without a group of that kind."""
        by_id = {c["id"]: (e, c) for e in self.enclosures for c in e["compartments"]}
        out = []
        grouped: dict[str, set[str]] = {k: set() for k in KINDS}
        for grp in self.groups:
            members = [by_id[m] for m in grp["members"] if m in by_id]
            if not members:
                continue
            grouped[grp["kind"]].update(c["id"] for _e, c in members)
            labels = ", ".join(label_of(e, c) for e, c in members)
            out.append({"id": f"g_{grp['id']}_{grp['kind']}", "kind": grp["kind"], "group": grp["id"],
                        "name": grp["name"] or labels, "members": members, "cfg": grp["config"]})
        for e, c in by_id.values():
            for kind in KINDS:
                if c["id"] not in grouped[kind]:
                    out.append({"id": f"c_{c['id']}_{kind}", "kind": kind, "group": None, "name": label_of(e, c),
                                "members": [(e, c)], "cfg": kind_config_of(kind, c)})
        return out

    def unit_of(self, comp_id: str, kind: str) -> dict | None:
        grp = self.group_of(comp_id, kind)
        uid = f"g_{grp['id']}_{kind}" if grp else f"c_{comp_id}_{kind}"
        return next((u for u in self.units() if u["id"] == uid), None)

    def features(self, comp: dict) -> dict[str, bool]:
        """Which automation entities a terrarium gets."""
        return {
            "light": bool(self.effective(comp, "light")["lights"]),
            "rain": bool(self.effective(comp, "rain")["rain"].get("entity_id")),
            "vent": bool(self.effective(comp, "vent")["vent"].get("entity_id")),
        }

    def structure(self) -> set[tuple]:
        """Changes here need a reload (entities/devices come and go)."""
        out = set()
        for enc in self.enclosures:
            out.add((enc["id"], "", ""))
            for comp in enc["compartments"]:
                f = self.features(comp)
                out.add((enc["id"], comp["id"], f"{f['light']}{f['rain']}{f['vent']}"))
        return out

    # ------------------------------------------------------------------ loading / saving
    async def async_load(self) -> None:
        state = await self.persist.async_load()
        encs = []
        for raw in state.get("enclosures", []):
            try:
                encs.append(normalize_enclosure(raw, raw))
            except (LayoutError, KeyError, TypeError) as err:
                _LOGGER.warning("Terrarienanlage verworfen (%s): %s", err, raw.get("name"))
        ids = {c["id"] for e in encs for c in e["compartments"]}
        groups = []
        for raw in state.get("groups", []):
            try:
                groups.append(sanitize_group(raw, ids))
            except LayoutError:
                pass
        templates = []
        for raw in state.get("templates", []):
            try:
                templates.append(sanitize_template(raw))
            except LayoutError:
                pass
        types = [sanitize_light_type(t) for t in state.get("light_types", [])]
        seeded = bool((state.get("settings") or {}).get("light_types_seeded"))
        settings = dict(state.get("settings") or {})
        if not seeded:
            have = {t["id"] for t in types}
            types += [t for t in default_light_types() if t["id"] not in have]
            settings["light_types_seeded"] = True
        self.state = {"enclosures": sorted(encs, key=lambda e: e["nr"]), "groups": groups, "templates": templates,
                      "light_types": types, "settings": settings}
        if not seeded:
            await self.async_save()

    async def async_save(self) -> None:
        await self.persist.async_save(self.state)

    def notify_update(self) -> None:
        async_dispatcher_send(self.hass, SIGNAL_UPDATE)

    def new_comp_defaults(self) -> dict:
        """Settings for new terrariums from templates marked 'default for new terrariums'."""
        out: dict = {}
        for kind in KINDS:
            tpl = next((t for t in self.templates if t["kind"] == kind and t["default_new"]), None)
            if tpl:
                out.update(apply_template(kind, kind_config_of(kind, {}), tpl))
        return out

    async def _after_change(self, old_labels: dict | None = None) -> bool:
        """Save, rename entities, re-evaluate. Returns True when the entry must be reloaded."""
        await self.async_save()
        self._rename_entities(old_labels or {})
        changed = self._structure_before != self.structure()
        if not changed:
            self._resubscribe()
            self.evaluate_all()
        return changed

    def _mark(self) -> dict:
        self._structure_before = self.structure()
        return self._labels()

    # ------------------------------------------------------------------ enclosures
    async def async_save_enclosure(self, raw: dict) -> tuple[dict, bool]:
        old_labels = self._mark()
        existing = self.enclosure(raw.get("id")) if raw.get("id") else None
        if existing is None:
            raw = {**raw, "id": None}
            if not raw.get("nr"):
                raw["nr"] = max((e["nr"] for e in self.enclosures), default=0) + 1
        enc = normalize_enclosure(raw, existing, self.new_comp_defaults())
        if any(e["nr"] == enc["nr"] and e["id"] != enc["id"] for e in self.enclosures):
            raise LayoutError("nr_taken", str(enc["nr"]))
        if existing is None:
            self.enclosures.append(enc)
        else:
            self.enclosures[self.enclosures.index(existing)] = enc
        self.enclosures.sort(key=lambda e: e["nr"])
        self._clean_groups()
        return enc, await self._after_change(old_labels)

    async def async_delete_enclosure(self, enc_id: str) -> None:
        enc = self.enclosure(enc_id)
        if enc is None:
            return
        self.enclosures.remove(enc)
        for comp in enc["compartments"]:
            self._track.pop(comp["id"], None)
            self.live.pop(comp["id"], None)
        self._clean_groups()
        await self.async_save()

    def _clean_groups(self) -> None:
        ids = self.comp_ids()
        for grp in list(self.groups):
            grp["members"] = [m for m in grp["members"] if m in ids]
            if len(grp["members"]) < 2:
                self.groups.remove(grp)

    # ------------------------------------------------------------------ terrarium settings
    async def async_save_compartment(self, comp_id: str, settings: dict) -> bool:
        enc, comp = self.find(comp_id)
        if comp is None:
            raise KeyError(comp_id)
        old_labels = self._mark()
        settings = dict(settings)
        # parts that belong to a group go to the group
        for kind in KINDS:
            keys = ("lights", "light_auto") if kind == "light" else (kind,)
            part = {k: settings.pop(k) for k in keys if k in settings}
            if not part:
                continue
            grp = self.group_of(comp_id, kind)
            if grp:
                grp["config"] = sanitize_kind_config(kind, deep_update(grp["config"], part))
            else:
                settings.update(part)
        comp.update(sanitize_compartment_settings(deep_update(comp, settings)))
        return await self._after_change(old_labels)

    async def async_set_auto(self, comp_id: str, kind: str, enabled: bool) -> None:
        _enc, comp = self.find(comp_id)
        if comp is None:
            return
        grp = self.group_of(comp_id, kind)
        target = grp["config"] if grp else comp
        if kind == "light":
            target["light_auto"] = enabled
        else:
            target[kind]["enabled"] = enabled
        await self.async_save()
        self.evaluate_all()

    async def async_set_notify_enabled(self, comp_id: str, enabled: bool) -> None:
        _enc, comp = self.find(comp_id)
        if comp is None:
            return
        comp["notify"]["enabled"] = enabled
        await self.async_save()
        self.notify_update()

    async def async_apply_template(self, comp_id: str, template_id: str) -> bool:
        _enc, comp = self.find(comp_id)
        tpl = next((t for t in self.templates if t["id"] == template_id), None)
        if comp is None or tpl is None:
            raise KeyError(template_id)
        cfg = apply_template(tpl["kind"], self.effective(comp, tpl["kind"]), tpl)
        return await self.async_save_compartment(comp_id, cfg)

    # ------------------------------------------------------------------ groups / templates / light types
    async def async_save_group(self, raw: dict) -> bool:
        old_labels = self._mark()
        existing = next((g for g in self.groups if g["id"] == raw.get("id")), None)
        if existing and "config" not in raw:
            raw = {**raw, "config": existing["config"]}
        if not existing and not raw.get("config"):
            # new group: start with the settings of the first member
            _e, first = self.find((raw.get("members") or [""])[0])
            if first is not None:
                raw = {**raw, "config": copy.deepcopy(kind_config_of(raw.get("kind"), first))}
        grp = sanitize_group(raw, self.comp_ids())
        for other in self.groups:  # a terrarium is in at most one group per kind
            if other["id"] != grp["id"] and other["kind"] == grp["kind"]:
                other["members"] = [m for m in other["members"] if m not in grp["members"]]
        if existing:
            self.groups[self.groups.index(existing)] = grp
        else:
            self.groups.append(grp)
        self._clean_groups()
        return await self._after_change(old_labels)

    async def async_delete_group(self, group_id: str) -> bool:
        old_labels = self._mark()
        grp = next((g for g in self.groups if g["id"] == group_id), None)
        if grp:
            # members keep a copy of the shared settings; the switch entities stay only with the first
            # member, otherwise the same socket would be switched by several terrariums
            for idx, m in enumerate(grp["members"]):
                _e, comp = self.find(m)
                if comp is None:
                    continue
                cfg = copy.deepcopy(grp["config"])
                if idx:
                    for light in cfg.get("lights", []):
                        light["entity_id"] = ""
                    if grp["kind"] in cfg:
                        cfg[grp["kind"]]["entity_id"] = ""
                comp.update(sanitize_compartment_settings(deep_update(comp, cfg)))
            self.groups.remove(grp)
        return await self._after_change(old_labels)

    async def async_save_template(self, raw: dict) -> dict:
        tpl = sanitize_template(raw)
        if tpl["default_new"]:
            for other in self.templates:
                if other["kind"] == tpl["kind"] and other["id"] != tpl["id"]:
                    other["default_new"] = False
        idx = next((i for i, t in enumerate(self.templates) if t["id"] == tpl["id"]), None)
        if idx is None:
            self.templates.append(tpl)
        else:
            self.templates[idx] = tpl
        await self.async_save()
        self.notify_update()
        return tpl

    async def async_delete_template(self, template_id: str) -> None:
        self.state["templates"] = [t for t in self.templates if t["id"] != template_id]
        await self.async_save()
        self.notify_update()

    async def async_save_light_type(self, raw: dict) -> dict:
        lt = sanitize_light_type(raw)
        idx = next((i for i, t in enumerate(self.light_types) if t["id"] == lt["id"]), None)
        if idx is None:
            self.light_types.append(lt)
        else:
            self.light_types[idx] = lt
        await self.async_save()
        self.evaluate_all()
        return lt

    async def async_delete_light_type(self, type_id: str) -> None:
        used = any(l.get("type_id") == type_id for u in self.units() if u["kind"] == "light" for l in u["cfg"]["lights"])
        if used:
            raise LayoutError("type_in_use", type_id)
        self.state["light_types"] = [t for t in self.light_types if t["id"] != type_id]
        await self.async_save()
        self.notify_update()

    # ------------------------------------------------------------------ rain by hand
    def rain_now(self, comp_id: str, seconds: float | None = None) -> None:
        unit = self.unit_of(comp_id, "rain")
        if unit and unit["cfg"]["rain"].get("entity_id"):
            self.auto.start_rain(unit, seconds or unit["cfg"]["rain"]["manual_duration"], self.auto.t("manual"))

    def rain_stop(self, comp_id: str) -> None:
        unit = self.unit_of(comp_id, "rain")
        if unit:
            self.auto.stop_rain(unit, self.auto.t("manual"))

    # ------------------------------------------------------------------ entity names
    def _labels(self) -> dict[str, str]:
        return {c["id"]: label_of(e, c) for e in self.enclosures for c in e["compartments"]}

    def _rename_entities(self, old_labels: dict[str, str]) -> None:
        """After renumbering: move entity ids that still follow the default pattern (two steps for swaps)."""
        reg = er.async_get(self.hass)
        new_labels = self._labels()
        moves = []
        for cid, old in old_labels.items():
            new = new_labels.get(cid)
            if not new or new == old:
                continue
            for platform, keys in COMP_ENTITY_KEYS.items():
                for key in keys:
                    ent_id = reg.async_get_entity_id(platform, DOMAIN, f"{cid}_{key}")
                    old_id = f"{platform}.terrarium_{old.replace('.', '_')}_{key}"
                    if not ent_id or ent_id != old_id:
                        continue
                    tmp_id = f"{platform}.terrarium_renumber_{cid}_{key}"
                    reg.async_update_entity(ent_id, new_entity_id=tmp_id)
                    moves.append((tmp_id, f"{platform}.terrarium_{new.replace('.', '_')}_{key}"))
        for tmp_id, new_id in moves:
            target = new_id if reg.async_get(new_id) is None else new_id + "_2"
            reg.async_update_entity(tmp_id, new_entity_id=target)
        dev_reg = dr.async_get(self.hass)
        devices = dr.async_entries_for_config_entry(dev_reg, self.entry.entry_id)
        for enc in self.enclosures:
            for comp in enc["compartments"]:
                dev = next((d for d in devices if (DOMAIN, comp["id"]) in d.identifiers), None)
                name = f"Terrarium {label_of(enc, comp)}" + (f" {comp['name']}" if comp["name"] else "")
                if dev and dev.name != name:
                    dev_reg.async_update_device(dev.id, name=name)

    # ------------------------------------------------------------------ runtime
    async def async_start(self) -> None:
        self._structure_before = self.structure()
        self._resubscribe()
        self._unsub_timer = async_track_time_interval(self.hass, self._tick, timedelta(seconds=20))
        self._unsub_slow = async_track_time_interval(self.hass, self._slow, timedelta(minutes=1))
        self.evaluate_all()

    @callback
    def async_unload(self) -> None:
        for name in ("_unsub_states", "_unsub_timer", "_unsub_slow"):
            unsub = getattr(self, name)
            if unsub:
                unsub()
                setattr(self, name, None)
        for rt in self.auto.rt.values():
            if rt.get("cancel"):
                rt["cancel"]()
                rt["cancel"] = None  # "until" stays, the next instance arms the timer again
        self.hass.async_create_task(self.persist.async_close())

    @callback
    def _tick(self, _now: datetime) -> None:
        self.evaluate_all()

    async def _slow(self, now: datetime) -> None:
        await self.persist.async_retry(self.state)
        if now.minute == 7 and now.hour == 3:
            await self.persist.async_prune()

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
        for unit in self.units():
            cfg = unit["cfg"]
            if unit["kind"] == "light":
                watched.update(l["entity_id"] for l in cfg["lights"] if l["entity_id"])
            elif cfg[unit["kind"]].get("entity_id"):
                watched.add(cfg[unit["kind"]]["entity_id"])
        if watched:
            self._unsub_states = async_track_state_change_event(self.hass, list(watched), self._state_changed)

    @callback
    def _state_changed(self, event: Event) -> None:
        self.auto.on_state(event)
        self.evaluate_all()

    def _read(self, entity_ids: list[str]) -> tuple[float | None, list[dict]]:
        values, details = [], []
        for ent in entity_ids:
            st = self.hass.states.get(ent)
            val = None
            if st is not None and st.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                val = num(st.state)
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
        start, end = parse_time(night["start"]), parse_time(night["end"])
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
        self.auto.tick()
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
        labels = self._labels()
        encs = []
        for enc in self.enclosures:
            e = copy.deepcopy(enc)
            for comp in e["compartments"]:
                comp["label"] = label_of(enc, comp)
                comp["live"] = self.live.get(comp["id"], {})
                comp["entities"] = self.entity_ids(comp["id"])
                comp["groups"] = {}
                comp["auto"] = {}
                for kind in KINDS:
                    grp = self.group_of(comp["id"], kind)
                    if grp:
                        comp["groups"][kind] = {"id": grp["id"], "name": grp["name"],
                                                "members": [labels.get(m, "?") for m in grp["members"]]}
                        comp.update(copy.deepcopy(grp["config"]))  # effective settings
                    uid = f"g_{grp['id']}_{kind}" if grp else f"c_{comp['id']}_{kind}"
                    comp["auto"][kind] = self.auto.info.get(uid, {})
            encs.append(e)
        groups = [{**g, "member_labels": [labels.get(m, "?") for m in g["members"]]} for g in self.groups]
        return {"enclosures": encs, "groups": groups, "templates": self.templates, "light_types": self.light_types,
                "db": self.persist.db_info}
