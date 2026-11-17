"""Time profiles for light, rain and ventilation (no Home Assistant imports – testable on its own).

A *profile* is::

    {"id", "name", "enabled": bool,
     "days": [0..6]            # Monday = 0; empty = every day
     "season": {"enabled": bool, "from": "MM-DD", "to": "MM-DD"},   # may wrap the year end
     "windows": [{"on": TIME, "off": TIME}],       # light / ventilation: on between
     "runs":    [{"at": TIME, "duration": seconds}] # rain / ventilation: timed runs
    }

TIME is ``{"type": "time"|"sunrise"|"sunset", "time": "HH:MM", "offset": minutes}``.
A window whose end is before its start runs over midnight and belongs to the start day.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Callable, Iterable

# sun(kind, day) -> local aware datetime or None ("sunrise" / "sunset")
SunFunc = Callable[[str, date], "datetime | None"]


def parse_hm(value) -> time | None:
    try:
        h, m = str(value).split(":")[:2]
        return time(int(h), int(m))
    except (ValueError, TypeError):
        return None


def norm_time(spec) -> dict:
    """Normalize a TIME spec (also accepts plain 'HH:MM')."""
    if isinstance(spec, str):
        spec = {"type": "time", "time": spec}
    if not isinstance(spec, dict):
        spec = {}
    kind = spec.get("type") if spec.get("type") in ("time", "sunrise", "sunset") else "time"
    hm = spec.get("time") if parse_hm(spec.get("time")) else "08:00"
    try:
        off = int(float(spec.get("offset") or 0))
    except (TypeError, ValueError):
        off = 0
    return {"type": kind, "time": hm, "offset": max(-720, min(720, off))}


def resolve(spec: dict, day: date, tz, sun: SunFunc | None) -> datetime | None:
    spec = norm_time(spec)
    if spec["type"] == "time":
        t = parse_hm(spec["time"])
        return datetime.combine(day, t, tzinfo=tz)
    if sun is None:
        return None
    base = sun(spec["type"], day)
    if base is None:
        return None
    return base + timedelta(minutes=spec["offset"])


def in_season(profile: dict, day: date) -> bool:
    season = profile.get("season") or {}
    if not season.get("enabled"):
        return True
    try:
        fm, fd = (int(x) for x in str(season.get("from")).split("-"))
        tm, td = (int(x) for x in str(season.get("to")).split("-"))
    except (ValueError, TypeError):
        return True
    cur = (day.month, day.day)
    start, end = (fm, fd), (tm, td)
    if start <= end:
        return start <= cur <= end
    return cur >= start or cur <= end


def day_ok(profile: dict, day: date) -> bool:
    if not profile.get("enabled", True):
        return False
    days = profile.get("days") or []
    if days and day.weekday() not in days:
        return False
    return in_season(profile, day)


def windows_of_day(profiles: Iterable[dict], day: date, tz, sun: SunFunc | None) -> list[tuple[datetime, datetime]]:
    """All on-windows that START on `day` (an end before the start = next day)."""
    out = []
    for prof in profiles:
        if not day_ok(prof, day):
            continue
        for win in prof.get("windows") or []:
            on = resolve(win.get("on"), day, tz, sun)
            off = resolve(win.get("off"), day, tz, sun)
            if on is None or off is None:
                continue
            if off <= on:
                off = resolve(win.get("off"), day + timedelta(days=1), tz, sun)
                if off is None:
                    continue
            out.append((on, off))
    return out


def is_on(profiles: list[dict], now: datetime, sun: SunFunc | None) -> bool:
    tz = now.tzinfo
    for day in (now.date() - timedelta(days=1), now.date()):
        for on, off in windows_of_day(profiles, day, tz, sun):
            if on <= now < off:
                return True
    return False


def next_change(profiles: list[dict], now: datetime, sun: SunFunc | None, days: int = 8) -> datetime | None:
    """Next moment the on/off state of the windows changes (None = never within `days`)."""
    tz = now.tzinfo
    edges = set()
    for i in range(-1, days):
        for on, off in windows_of_day(profiles, now.date() + timedelta(days=i), tz, sun):
            edges.add(on)
            edges.add(off)
    cur = is_on(profiles, now, sun)
    for edge in sorted(e for e in edges if e > now):
        if is_on(profiles, edge, sun) != cur:
            return edge
    return None


def runs_of_day(profiles: Iterable[dict], day: date, tz, sun: SunFunc | None) -> list[tuple[datetime, float, str]]:
    """(start, duration seconds, profile name) of all timed runs on `day`."""
    out = []
    for prof in profiles:
        if not day_ok(prof, day):
            continue
        for run in prof.get("runs") or []:
            at = resolve(run.get("at"), day, tz, sun)
            if at is None:
                continue
            try:
                dur = max(1.0, float(run.get("duration") or 0))
            except (TypeError, ValueError):
                dur = 30.0
            out.append((at, dur, prof.get("name") or ""))
    return sorted(out, key=lambda r: r[0])


def runs_due(profiles: list[dict], since: datetime, now: datetime, sun: SunFunc | None) -> list[tuple[datetime, float, str]]:
    """Runs with since < start <= now."""
    tz = now.tzinfo
    out = []
    day = since.date()
    while day <= now.date():
        out += [r for r in runs_of_day(profiles, day, tz, sun) if since < r[0] <= now]
        day += timedelta(days=1)
    return out


def next_run(profiles: list[dict], now: datetime, sun: SunFunc | None, days: int = 8) -> tuple[datetime, float] | None:
    tz = now.tzinfo
    for i in range(days):
        for at, dur, _name in runs_of_day(profiles, now.date() + timedelta(days=i), tz, sun):
            if at > now:
                return at, dur
    return None


def active_run(profiles: list[dict], now: datetime, sun: SunFunc | None) -> tuple[datetime, float] | None:
    """A timed run that is going on right now (start <= now < start + duration)."""
    tz = now.tzinfo
    for day in (now.date() - timedelta(days=1), now.date()):
        for at, dur, _name in runs_of_day(profiles, day, tz, sun):
            if at <= now < at + timedelta(seconds=dur):
                return at, dur
    return None
