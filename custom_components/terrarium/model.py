"""Data model: validation/normalization of enclosures, terrariums, lights, rain, ventilation, groups,
templates and light types. No Home Assistant imports (testable on its own)."""
from __future__ import annotations

import copy
import uuid
from datetime import time
from typing import Any

from .const import (
    DEFAULT_COMPARTMENT, DEFAULT_ENCLOSURE, DEFAULT_LIGHT, DEFAULT_LIGHT_TYPES, DEFAULT_RAIN, DEFAULT_VENT,
    DEVICE_KINDS, ENCLOSURE_COLORS, KINDS, LIGHT_CATEGORIES, LOOK_BACKGROUNDS, LOOK_DECOR, LOOK_SUBSTRATES,
)
from .schedule import norm_time

EPS = 0.01


def new_id() -> str:
    return uuid.uuid4().hex[:10]


def num(value: Any) -> float | None:
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
        return {k: (merge_known(v, src[k]) if k in src else copy.deepcopy(v)) for k, v in default.items()}
    if isinstance(default, list):
        return copy.deepcopy(incoming) if isinstance(incoming, list) else copy.deepcopy(default)
    if isinstance(default, bool):
        return bool(incoming) if incoming is not None else default
    if isinstance(default, (int, float)):
        n = num(incoming)
        return n if n is not None else default
    if default is None:
        return num(incoming)
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


def entity_list(value: Any) -> list[str]:
    out: list[str] = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, str) and "." in item and item.strip() not in out:
            out.append(item.strip())
    return out


def entity(value: Any) -> str:
    v = str(value or "").strip()
    return v if "." in v else ""


def parse_time(value: Any) -> time | None:
    try:
        parts = str(value).split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError, TypeError):
        return None


def _md(value: Any, default: str) -> str:
    try:
        m, d = (int(x) for x in str(value).split("-"))
        if 1 <= m <= 12 and 1 <= d <= 31:
            return f"{m:02d}-{d:02d}"
    except (TypeError, ValueError):
        pass
    return default


# ------------------------------------------------------------------ profiles
def sanitize_profile(p: Any) -> dict:
    p = p if isinstance(p, dict) else {}
    season = p.get("season") if isinstance(p.get("season"), dict) else {}
    days = sorted({int(d) for d in (p.get("days") or []) if str(d).isdigit() and 0 <= int(d) <= 6})
    windows = []
    for w in p.get("windows") or []:
        if isinstance(w, dict):
            windows.append({"on": norm_time(w.get("on")), "off": norm_time(w.get("off"))})
    runs = []
    for r in p.get("runs") or []:
        if isinstance(r, dict):
            dur = num(r.get("duration"))
            runs.append({"at": norm_time(r.get("at")), "duration": max(1, int(dur if dur is not None else 30))})
    return {
        "id": str(p.get("id") or new_id()),
        "name": str(p.get("name") or ""),
        "enabled": bool(p.get("enabled", True)),
        "days": days,
        "season": {"enabled": bool(season.get("enabled")), "from": _md(season.get("from"), "03-01"),
                   "to": _md(season.get("to"), "10-31")},
        "windows": windows,
        "runs": runs,
    }


def sanitize_profiles(value: Any) -> list[dict]:
    return [sanitize_profile(p) for p in (value if isinstance(value, list) else [])]


def sanitize_light(light: Any, keep_entity: bool = True) -> dict:
    out = merge_known(DEFAULT_LIGHT, light if isinstance(light, dict) else {})
    out["id"] = str(out["id"] or new_id())
    out["entity_id"] = entity(out["entity_id"]) if keep_entity else ""
    out["profiles"] = sanitize_profiles((light or {}).get("profiles"))
    return out


def sanitize_lights(value: Any, keep_entity: bool = True) -> list[dict]:
    return [sanitize_light(x, keep_entity) for x in (value if isinstance(value, list) else []) if isinstance(x, dict)]


def sanitize_rain(rain: Any, keep_entity: bool = True) -> dict:
    out = merge_known(DEFAULT_RAIN, rain if isinstance(rain, dict) else {})
    out["entity_id"] = entity(out["entity_id"]) if keep_entity else ""
    out["profiles"] = sanitize_profiles((rain or {}).get("profiles"))
    for key in ("manual_duration", "max_duration", "min_pause"):
        out[key] = max(0, int(out[key]))
    out["manual_duration"] = max(1, out["manual_duration"])
    out["max_duration"] = max(5, out["max_duration"])
    out["hum_start"]["duration"] = max(1, int(out["hum_start"]["duration"]))
    out["hum_start"]["min_pause"] = max(0, int(out["hum_start"]["min_pause"]))
    return out


def sanitize_vent(vent: Any, keep_entity: bool = True) -> dict:
    out = merge_known(DEFAULT_VENT, vent if isinstance(vent, dict) else {})
    out["entity_id"] = entity(out["entity_id"]) if keep_entity else ""
    out["profiles"] = sanitize_profiles((vent or {}).get("profiles"))
    out["min_run"] = max(0, int(out["min_run"]))
    out["temp_on"]["hyst"] = max(0.0, out["temp_on"]["hyst"])
    out["hum_on"]["hyst"] = max(0.0, out["hum_on"]["hyst"])
    return out


def sanitize_kind_config(kind: str, cfg: Any, keep_entity: bool = True) -> dict:
    cfg = cfg if isinstance(cfg, dict) else {}
    if kind == "light":
        return {"lights": sanitize_lights(cfg.get("lights"), keep_entity), "light_auto": bool(cfg.get("light_auto", True))}
    if kind == "rain":
        return {"rain": sanitize_rain(cfg.get("rain"), keep_entity)}
    return {"vent": sanitize_vent(cfg.get("vent"), keep_entity)}


def kind_config_of(kind: str, comp: dict) -> dict:
    if kind == "light":
        return {"lights": comp.get("lights", []), "light_auto": comp.get("light_auto", True)}
    return {kind: comp.get(kind, {})}


# ------------------------------------------------------------------ terrarium
def sanitize_compartment_settings(comp: dict) -> dict:
    out = merge_known(DEFAULT_COMPARTMENT, comp)
    clim = out["climate"]
    clim["temp_sensors"] = entity_list(clim["temp_sensors"])
    clim["hum_sensors"] = entity_list(clim["hum_sensors"])
    clim["delay"] = max(0.0, clim["delay"])
    clim["temp_hyst"] = max(0.0, clim["temp_hyst"])
    clim["hum_hyst"] = max(0.0, clim["hum_hyst"])
    for key in ("start", "end"):
        if parse_time(clim["night"][key]) is None:
            clim["night"][key] = DEFAULT_COMPARTMENT["climate"]["night"][key]
    notify = out["notify"]
    notify["targets"] = entity_list(notify["targets"])
    notify["repeat"] = max(0.0, notify["repeat"])
    devices = []
    for dev in comp.get("devices") or []:
        if not isinstance(dev, dict) or not entity(dev.get("entity_id")):
            continue
        kind = dev.get("kind") if dev.get("kind") in DEVICE_KINDS else "other"
        devices.append({"entity_id": entity(dev.get("entity_id")), "kind": kind, "name": str(dev.get("name") or "")})
    out["devices"] = devices
    look = out["look"]
    if look["substrate"] not in LOOK_SUBSTRATES:
        look["substrate"] = "soil"
    if look["decor"] not in LOOK_DECOR:
        look["decor"] = "plants"
    if look["background"] not in LOOK_BACKGROUNDS:
        look["background"] = "rock"
    out["lights"] = sanitize_lights(comp.get("lights"))
    out["rain"] = sanitize_rain(comp.get("rain"))
    out["vent"] = sanitize_vent(comp.get("vent"))
    return out


def number_compartments(comps: list[dict]) -> None:
    """Number top -> bottom, left -> right."""
    order = sorted(comps, key=lambda c: (round(c["y"], 1), round(c["x"], 1)))
    for idx, comp in enumerate(order, start=1):
        comp["nr"] = idx
    comps.sort(key=lambda c: c["nr"])


class LayoutError(ValueError):
    """Invalid input. args[0] = error key, args[1] = details."""


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


def normalize_enclosure(raw: dict, existing: dict | None, new_comp_defaults: dict | None = None) -> dict:
    """new_comp_defaults: settings applied to terrariums that did not exist before (templates)."""
    enc = merge_known({k: v for k, v in DEFAULT_ENCLOSURE.items() if k != "compartments"}, raw)
    enc["id"] = str(raw.get("id") or new_id())
    enc["nr"] = int(enc["nr"]) if enc["nr"] else 1
    if enc["color"] not in ENCLOSURE_COLORS:
        enc["color"] = "wood"
    old = {c["id"]: c for c in (existing or {}).get("compartments", []) if isinstance(c, dict) and c.get("id")}
    comps = []
    for rc in raw.get("compartments") or []:
        cid = str(rc.get("id") or "")
        base = old.get(cid)
        if base is None:  # new terrarium: fresh id + template defaults
            cid = new_id()
            base = copy.deepcopy(new_comp_defaults or {})
        settings = sanitize_compartment_settings(deep_update(base, {k: v for k, v in rc.items() if k in DEFAULT_COMPARTMENT}))
        comps.append({
            "id": cid, "nr": 0,
            "x": num(rc.get("x")) or 0.0, "y": num(rc.get("y")) or 0.0,
            "width": num(rc.get("width")) or 0.0, "height": num(rc.get("height")) or 0.0,
            **settings,
        })
    enc["compartments"] = comps
    validate_layout(enc)
    number_compartments(comps)
    return enc


# ------------------------------------------------------------------ groups, templates, light types
def sanitize_group(raw: dict, valid_comp_ids: set[str]) -> dict:
    kind = raw.get("kind") if raw.get("kind") in KINDS else None
    if kind is None:
        raise LayoutError("group_kind", str(raw.get("kind")))
    members = [m for m in entity_list_ids(raw.get("members")) if m in valid_comp_ids]
    if len(members) < 2:
        raise LayoutError("group_members", "")
    return {
        "id": str(raw.get("id") or new_id()),
        "kind": kind,
        "name": str(raw.get("name") or ""),
        "members": members,
        "config": sanitize_kind_config(kind, raw.get("config")),
    }


def entity_list_ids(value: Any) -> list[str]:
    out: list[str] = []
    for v in value if isinstance(value, list) else []:
        if isinstance(v, str) and v and v not in out:
            out.append(v)
    return out


def sanitize_template(raw: dict) -> dict:
    kind = raw.get("kind") if raw.get("kind") in KINDS else None
    if kind is None:
        raise LayoutError("template_kind", str(raw.get("kind")))
    return {
        "id": str(raw.get("id") or new_id()),
        "kind": kind,
        "name": str(raw.get("name") or "") or kind,
        "default_new": bool(raw.get("default_new")),
        "config": sanitize_kind_config(kind, raw.get("config"), keep_entity=False),
    }


def sanitize_light_type(raw: dict) -> dict:
    cat = raw.get("category") if raw.get("category") in LIGHT_CATEGORIES else "other"
    color = str(raw.get("color") or "#fff6e0")
    if not (color.startswith("#") and len(color) in (4, 7)):
        color = "#fff6e0"
    return {
        "id": str(raw.get("id") or new_id()),
        "name": str(raw.get("name") or "") or "Licht",
        "category": cat,
        "watt": max(0.0, num(raw.get("watt")) or 0.0),
        "restrike_min": max(0.0, num(raw.get("restrike_min")) or 0.0),
        "color": color,
    }


def default_light_types() -> list[dict]:
    return [sanitize_light_type(t) for t in DEFAULT_LIGHT_TYPES]


def apply_template(kind: str, current: dict, template: dict) -> dict:
    """Return the kind config after applying a template; entities of the current config are kept."""
    tcfg = copy.deepcopy(template.get("config") or {})
    if kind == "light":
        old = list(current.get("lights") or [])
        lights = []
        for tl in tcfg.get("lights") or []:
            match = next((o for o in old if o.get("type_id") == tl.get("type_id") and o.get("entity_id")), None)
            if match:
                old.remove(match)
            lights.append(sanitize_light({**tl, "id": new_id(), "entity_id": match["entity_id"] if match else ""}))
        return {"lights": lights, "light_auto": tcfg.get("light_auto", True)}
    cur = current.get(kind) or {}
    cfg = tcfg.get(kind) or {}
    cfg["entity_id"] = cur.get("entity_id", "")
    for prof in cfg.get("profiles") or []:
        prof["id"] = new_id()
    return sanitize_kind_config(kind, {kind: cfg})
