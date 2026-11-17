"""Light, rain and ventilation automation.

A *unit* is what is switched together: a group (several terrariums share the system) or a single terrarium.
Switching works on edges: a command is only sent when the wanted state changes (schedule boundary,
condition, settings changed, start). So switching by hand holds until the next scheduled change.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.sun import get_astral_event_date
from homeassistant.util import dt as dt_util

from . import schedule as sch

_LOGGER = logging.getLogger(__name__)

ON_STATES = ("on", "open", "opening", "heat", "cool", "auto", "heat_cool", "dry", "fan_only")
MISSED_GRACE = timedelta(minutes=2)

T = {
    "de": {"schedule": "Zeitplan", "manual": "Von Hand", "overheat": "Überhitzung {v:.1f} °C",
           "restrike": "Wiederzündsperre bis {t}", "hum_low": "Luftfeuchte {v:.0f} % < {l:g} %",
           "blocked": "nicht beregnet: Luftfeuchte {v:.0f} % > {l:g} %", "pause": "nicht beregnet: Pause",
           "safety": "Sicherheitsabschaltung", "max": "Höchstdauer erreicht", "end": "Laufzeit beendet",
           "temp_high": "Temperatur {v:.1f} °C > {l:g} °C", "hum_high": "Luftfeuchte {v:.0f} % > {l:g} %",
           "min_run": "Mindestlaufzeit", "off": "aus", "auto_off": "Automatik aus", "start": "Start"},
    "en": {"schedule": "Schedule", "manual": "By hand", "overheat": "Overheating {v:.1f} °C",
           "restrike": "Restrike lock until {t}", "hum_low": "Humidity {v:.0f} % < {l:g} %",
           "blocked": "no rain: humidity {v:.0f} % > {l:g} %", "pause": "no rain: pause",
           "safety": "Safety switch-off", "max": "Maximum run time reached", "end": "Run finished",
           "temp_high": "Temperature {v:.1f} °C > {l:g} °C", "hum_high": "Humidity {v:.0f} % > {l:g} %",
           "min_run": "Minimum run time", "off": "off", "auto_off": "Automation off", "start": "Start"},
}


def _hash(obj: Any) -> str:
    return hashlib.md5(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class Automation:
    def __init__(self, mgr) -> None:
        self.mgr = mgr
        self.hass: HomeAssistant = mgr.hass
        # kept in hass.data: an entry reload (after saving a group, …) must not forget restrike locks,
        # running rain or the last wanted state (manual switching stays until the next scheduled change)
        store = self.hass.data.setdefault("terrarium", {})
        self.rt: dict[str, dict] = store.setdefault("auto_rt", {})
        self.info: dict[str, dict] = {}
        self._last_off: dict[str, datetime] = store.setdefault("last_off", {})
        self._sun_cache: dict[tuple[str, date], datetime | None] = {}
        self._started = False

    # ------------------------------------------------------------ helpers
    def t(self, key: str, **kw) -> str:
        lang = (self.hass.config.language or "en").split("-")[0]
        txt = T.get(lang, T["en"])[key]
        return txt.format(**kw) if kw else txt

    def sun(self, kind: str, day: date) -> datetime | None:
        key = (kind, day)
        if key not in self._sun_cache:
            ev = get_astral_event_date(self.hass, kind, day)
            self._sun_cache[key] = dt_util.as_local(ev) if ev else None
            if len(self._sun_cache) > 200:
                self._sun_cache.clear()
        return self._sun_cache[key]

    def state(self, entity_id: str) -> str | None:
        st = self.hass.states.get(entity_id) if entity_id else None
        return st.state if st else None

    def is_on(self, entity_id: str) -> bool | None:
        st = self.state(entity_id)
        if st is None or st in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        return st in ON_STATES

    def climate(self, members: list[tuple[dict, dict]]) -> tuple[float | None, float | None]:
        temps = [self.mgr.live.get(c["id"], {}).get("temperature") for _e, c in members]
        hums = [self.mgr.live.get(c["id"], {}).get("humidity") for _e, c in members]
        temps = [v for v in temps if v is not None]
        hums = [v for v in hums if v is not None]
        return (sum(temps) / len(temps) if temps else None, sum(hums) / len(hums) if hums else None)

    async def _switch(self, entity_id: str, on: bool, unit: dict, kind: str, reason: str) -> None:
        domain = entity_id.split(".")[0]
        try:
            if domain == "valve":
                await self.hass.services.async_call("valve", "open_valve" if on else "close_valve",
                                                    {"entity_id": entity_id}, blocking=True)
            elif domain in ("script", "scene") and on:
                await self.hass.services.async_call(domain, "turn_on", {"entity_id": entity_id}, blocking=True)
            else:
                await self.hass.services.async_call("homeassistant", "turn_on" if on else "turn_off",
                                                    {"entity_id": entity_id}, blocking=True)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Terrarium %s: %s konnte nicht geschaltet werden: %s", unit["name"], entity_id, err)
            reason = f"{reason} – Fehler: {err}"
        self.mgr.persist.log(unit["name"], kind, entity_id, "on" if on else "off", reason)

    def switch(self, entity_id: str, on: bool, unit: dict, kind: str, reason: str) -> None:
        self.hass.async_create_task(self._switch(entity_id, on, unit, kind, reason))

    # ------------------------------------------------------------ events from manager
    @callback
    def on_state(self, event: Event) -> None:
        ent = event.data.get("entity_id")
        old, new = event.data.get("old_state"), event.data.get("new_state")
        was_on = old is not None and old.state in ON_STATES
        now_on = new is not None and new.state in ON_STATES
        if was_on and not now_on:
            self._last_off[ent] = dt_util.utcnow()
        if now_on and not was_on:
            # rain switched on from somewhere else -> make sure it stops after the maximum time
            for unit in self.mgr.units():
                if unit["kind"] == "rain" and unit["cfg"]["rain"].get("entity_id") == ent:
                    rt = self.rt.setdefault(unit["id"], {})
                    if not rt.get("until"):
                        dur = unit["cfg"]["rain"]["max_duration"]
                        self._arm_rain(unit, rt, dt_util.utcnow() + timedelta(seconds=dur), self.t("max"))

    # ------------------------------------------------------------ main loop
    @callback
    def tick(self) -> None:
        now = dt_util.now()
        live_units = set()
        for unit in self.mgr.units():
            live_units.add(unit["id"])
            rt = self.rt.setdefault(unit["id"], {})
            h = _hash(unit["cfg"])
            if rt.get("hash") != h:  # settings changed -> apply schedule again
                rt["hash"] = h
                rt["desired"] = {}
            try:
                if unit["kind"] == "light":
                    self._lights(unit, rt, now)
                elif unit["kind"] == "rain":
                    self._rain(unit, rt, now)
                else:
                    self._vent(unit, rt, now)
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Terrarium: Fehler in der Automatik für %s", unit["name"])
        for gone in set(self.rt) - live_units:
            cancel = self.rt[gone].get("cancel")
            if cancel:
                cancel()
            self.rt.pop(gone, None)
            self.info.pop(gone, None)
        self._started = True

    def _edge(self, unit: dict, rt: dict, key: str, entity_id: str, desired: bool, reason: str, kind: str) -> None:
        prev = rt["desired"].get(key)
        if prev == desired:
            return
        rt["desired"][key] = desired
        cur = self.is_on(entity_id)
        if cur is None or cur != desired:
            self.switch(entity_id, desired, unit, kind, reason)

    # ------------------------------------------------------------ light
    def _lights(self, unit: dict, rt: dict, now: datetime) -> None:
        cfg = unit["cfg"]
        temp, _hum = self.climate(unit["members"])
        hot = rt.setdefault("hot", {})
        infos = []
        for light in cfg["lights"]:
            key, ent = light["id"], light["entity_id"]
            ltype = self.mgr.light_type(light["type_id"]) or {}
            sched = sch.is_on(light["profiles"], now, self.sun)
            desired, reason = sched, self.t("schedule")
            oh = light["overheat"]
            if oh["enabled"] and temp is not None:
                if temp > oh["above"]:
                    hot[key] = True
                elif temp < oh["above"] - oh["hyst"]:
                    hot[key] = False
                if hot.get(key) and desired:
                    desired, reason = False, self.t("overheat", v=temp)
            locked_until = None
            restrike = float(ltype.get("restrike_min") or 0)
            if restrike and ent in self._last_off:
                lu = self._last_off[ent] + timedelta(minutes=restrike)
                if lu > dt_util.utcnow():
                    locked_until = lu
            auto = bool(cfg["light_auto"] and light["enabled"] and ent)
            if auto:
                if desired and locked_until and rt["desired"].get(key) is not True and not self.is_on(ent):
                    reason = self.t("restrike", t=dt_util.as_local(locked_until).strftime("%H:%M"))
                else:
                    self._edge(unit, rt, key, ent, desired, reason, "light")
            nxt = sch.next_change(light["profiles"], now, self.sun) if light["profiles"] else None
            infos.append({
                "id": key, "name": light["name"] or ltype.get("name") or ent, "type_id": light["type_id"],
                "category": ltype.get("category", "other"), "color": ltype.get("color"), "watt": ltype.get("watt"),
                "entity_id": ent, "state": self.state(ent), "auto": auto, "scheduled": sched, "desired": desired,
                "reason": reason, "next": _iso(nxt), "locked_until": _iso(locked_until), "overheat": bool(hot.get(key)),
            })
        self.info[unit["id"]] = {"auto": cfg["light_auto"], "lights": infos, "unit": unit["name"],
                                 "temperature": temp}

    # ------------------------------------------------------------ rain
    def _arm_rain(self, unit: dict, rt: dict, until: datetime, reason_end: str) -> None:
        if rt.get("cancel"):
            rt["cancel"]()
        rt["until"] = until
        ent = unit["cfg"]["rain"]["entity_id"]
        uid = unit["id"]

        @callback
        def _end(_now) -> None:
            r = self.rt.get(uid, {})
            r["until"], r["cancel"] = None, None
            current = next((u for u in self.mgr.units() if u["id"] == uid), unit)
            self.switch(ent, False, current, "rain", reason_end)
            self.mgr.notify_update()

        rt["cancel"] = async_call_later(self.hass, max(1.0, (until - dt_util.utcnow()).total_seconds()), _end)

    def start_rain(self, unit: dict, seconds: float, reason: str) -> None:
        rain = unit["cfg"]["rain"]
        ent = rain["entity_id"]
        if not ent:
            return
        rt = self.rt.setdefault(unit["id"], {})
        seconds = min(float(seconds), float(rain["max_duration"]))
        now = dt_util.utcnow()
        rt["last_rain"] = now
        self._arm_rain(unit, rt, now + timedelta(seconds=seconds), self.t("end"))
        self.switch(ent, True, unit, "rain", f"{reason} ({seconds:g} s)")
        self.mgr.notify_update()

    def stop_rain(self, unit: dict, reason: str) -> None:
        rt = self.rt.setdefault(unit["id"], {})
        if rt.get("cancel"):
            rt["cancel"]()
        rt["until"], rt["cancel"] = None, None
        if unit["cfg"]["rain"]["entity_id"]:
            self.switch(unit["cfg"]["rain"]["entity_id"], False, unit, "rain", reason)
        self.mgr.notify_update()

    def _rain(self, unit: dict, rt: dict, now: datetime) -> None:
        rain = unit["cfg"]["rain"]
        ent = rain["entity_id"]
        _temp, hum = self.climate(unit["members"])
        utcnow = dt_util.utcnow()
        if not ent:
            self.info[unit["id"]] = {"configured": False, "unit": unit["name"]}
            return
        if "last_check" not in rt:
            rt["last_check"] = now
            if self.is_on(ent) and not rt.get("until"):  # after a restart: never leave the water running
                self.switch(ent, False, unit, "rain", self.t("safety"))
        running = bool(rt.get("until") and rt["until"] > utcnow)
        if running and not rt.get("cancel"):  # after a reload: set the switch-off timer again
            self._arm_rain(unit, rt, rt["until"], self.t("end"))
        elif rt.get("until") and not running and not rt.get("cancel"):
            rt["until"] = None
            if self.is_on(ent):
                self.switch(ent, False, unit, "rain", self.t("end"))
        blocked = bool(rain["hum_block"]["enabled"] and hum is not None and hum > rain["hum_block"]["above"])
        last = rt.get("last_rain")
        pause_ok = not (rain["min_pause"] and last and utcnow - last < timedelta(minutes=rain["min_pause"]))
        if rain["enabled"]:
            for at, dur, name in sch.runs_due(rain["profiles"], rt["last_check"], now, self.sun):
                if now - at > MISSED_GRACE or running:
                    continue
                if blocked:
                    self.mgr.persist.log(unit["name"], "rain", ent, "skip",
                                         self.t("blocked", v=hum, l=rain["hum_block"]["above"]))
                    continue
                if not pause_ok:
                    self.mgr.persist.log(unit["name"], "rain", ent, "skip", self.t("pause"))
                    continue
                self.start_rain(unit, dur, f"{self.t('schedule')} {name}".strip())
                running, pause_ok = True, False
            hs = rain["hum_start"]
            if (hs["enabled"] and not running and pause_ok and hum is not None and hum < hs["below"]
                    and not (last and utcnow - last < timedelta(minutes=hs["min_pause"]))):
                self.start_rain(unit, hs["duration"], self.t("hum_low", v=hum, l=hs["below"]))
                running = True
        rt["last_check"] = now
        nxt = sch.next_run(rain["profiles"], now, self.sun) if rain["enabled"] else None
        self.info[unit["id"]] = {
            "configured": True, "unit": unit["name"], "auto": rain["enabled"], "entity_id": ent,
            "state": self.state(ent), "running_until": _iso(rt.get("until")) if running else None,
            "next_run": _iso(nxt[0]) if nxt else None, "next_duration": nxt[1] if nxt else None,
            "last_run": _iso(rt.get("last_rain")), "blocked": blocked, "humidity": hum,
            "manual_duration": rain["manual_duration"],
        }

    # ------------------------------------------------------------ ventilation
    def _vent(self, unit: dict, rt: dict, now: datetime) -> None:
        vent = unit["cfg"]["vent"]
        ent = vent["entity_id"]
        if not ent:
            self.info[unit["id"]] = {"configured": False, "unit": unit["name"]}
            return
        temp, hum = self.climate(unit["members"])
        sched = sch.is_on(vent["profiles"], now, self.sun) or sch.active_run(vent["profiles"], now, self.sun) is not None
        reasons = []
        to, ho = vent["temp_on"], vent["hum_on"]
        if to["enabled"] and temp is not None:
            if temp > to["above"]:
                rt["t_hot"] = True
            elif temp < to["above"] - to["hyst"]:
                rt["t_hot"] = False
        else:
            rt["t_hot"] = False
        if ho["enabled"] and hum is not None:
            if hum > ho["above"]:
                rt["h_high"] = True
            elif hum < ho["above"] - ho["hyst"]:
                rt["h_high"] = False
        else:
            rt["h_high"] = False
        cond = bool(rt.get("t_hot") or rt.get("h_high"))
        if rt.get("t_hot"):
            reasons.append(self.t("temp_high", v=temp, l=to["above"]))
        if rt.get("h_high"):
            reasons.append(self.t("hum_high", v=hum, l=ho["above"]))
        if cond:
            rt.setdefault("cond_since", now)
        elif rt.get("cond_since"):
            if now - rt["cond_since"] < timedelta(minutes=vent["min_run"]):
                cond = True
                reasons.append(self.t("min_run"))
            else:
                rt["cond_since"] = None
        if sched:
            reasons.insert(0, self.t("schedule"))
        desired = sched or cond
        reason = ", ".join(reasons) if desired else self.t("off")
        if vent["enabled"]:
            self._edge(unit, rt, "vent", ent, desired, reason, "vent")
        nxt = sch.next_change(vent["profiles"], now, self.sun) if vent["profiles"] else None
        nrun = sch.next_run(vent["profiles"], now, self.sun) if vent["profiles"] else None
        self.info[unit["id"]] = {
            "configured": True, "unit": unit["name"], "auto": vent["enabled"], "entity_id": ent,
            "state": self.state(ent), "desired": desired, "reason": reason,
            "next": _iso(min([x for x in (nxt, nrun[0] if nrun else None) if x], default=None)),
            "temperature": temp, "humidity": hum,
        }
