"""Persistence: MariaDB (main storage) + local cache in .storage (fallback when the database is not reachable)."""
from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timezone

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORE_VERSION
from .db import TerrariumDB, redact

_LOGGER = logging.getLogger(__name__)

EMPTY_STATE = {"enclosures": [], "groups": [], "templates": [], "light_types": [], "settings": {}}


class Persistence:
    def __init__(self, hass: HomeAssistant, db_url: str) -> None:
        self.hass = hass
        self.db_url = (db_url or "").strip()
        self.store: Store = Store(hass, STORE_VERSION, DOMAIN)
        self.db: TerrariumDB | None = None
        self.status = "off" if not self.db_url else "connecting"
        self.error = ""
        self.dirty = False
        self._events: deque = deque(maxlen=500)     # not yet written to the database
        self._recent: deque = deque(maxlen=300)     # for the UI when there is no database

    @property
    def db_info(self) -> dict:
        return {"status": self.status, "error": self.error, "url": redact(self.db_url) if self.db_url else "",
                "dirty": self.dirty}

    async def _connect(self) -> bool:
        if not self.db_url:
            return False
        if self.db is not None:
            return True
        db = TerrariumDB(self.db_url)
        try:
            await self.hass.async_add_executor_job(db.connect)
        except Exception as err:  # noqa: BLE001
            self.status, self.error = "error", str(err).split("\n")[0][:300]
            _LOGGER.warning("Terrarium-Datenbank %s nicht erreichbar: %s", redact(self.db_url), self.error)
            return False
        self.db = db
        return True

    async def async_load(self) -> dict:
        cache = await self.store.async_load() or {}
        state = cache.get("state")
        if state is None:  # cache of version 1.x: only enclosures
            state = {"enclosures": cache.get("enclosures", [])}
        state = {**EMPTY_STATE, **state}
        self.dirty = bool(cache.get("dirty"))
        if await self._connect():
            try:
                empty = await self.hass.async_add_executor_job(self.db.is_empty)
                if empty or self.dirty:
                    # first start with the database (migration) or changes made while it was offline
                    await self.hass.async_add_executor_job(self.db.sync, state)
                    _LOGGER.info("Terrarium: lokale Daten in die Datenbank übernommen")
                else:
                    state = {**EMPTY_STATE, **await self.hass.async_add_executor_job(self.db.load_all)}
                self.status, self.error, self.dirty = "ok", "", False
            except Exception as err:  # noqa: BLE001
                self.status, self.error = "error", str(err).split("\n")[0][:300]
                self.dirty = True
                _LOGGER.warning("Terrarium-Datenbank: Laden fehlgeschlagen, nutze lokalen Stand: %s", self.error)
        elif self.db_url:
            self.dirty = True
        await self.store.async_save({"state": state, "dirty": self.dirty})
        return state

    async def async_save(self, state: dict) -> None:
        if self.db_url:
            ok = False
            if await self._connect():
                try:
                    await self.hass.async_add_executor_job(self.db.sync, state)
                    ok = True
                    self.status, self.error = "ok", ""
                except Exception as err:  # noqa: BLE001
                    self.status, self.error = "error", str(err).split("\n")[0][:300]
                    _LOGGER.warning("Terrarium-Datenbank: Speichern fehlgeschlagen (lokal gesichert): %s", self.error)
            self.dirty = not ok
        await self.store.async_save({"state": state, "dirty": self.dirty})

    async def async_retry(self, state: dict) -> None:
        """Called periodically: write pending changes and events when the database is back."""
        if not self.db_url:
            return
        if self.dirty:
            await self.async_save(state)
        await self.async_flush()

    # ------------------------------------------------------------ switching log
    def log(self, unit: str, kind: str, entity_id: str, action: str, reason: str) -> None:
        row = {"ts": datetime.now(timezone.utc).replace(tzinfo=None), "unit": unit, "kind": kind,
               "entity_id": entity_id, "action": action, "reason": reason}
        self._recent.appendleft(row)
        if self.db_url:
            self._events.append(row)

    async def async_flush(self) -> None:
        if not self._events or not await self._connect():
            return
        rows = list(self._events)
        try:
            await self.hass.async_add_executor_job(self.db.log_events, rows)
            for _ in rows:
                self._events.popleft()
        except Exception as err:  # noqa: BLE001
            self.status, self.error = "error", str(err).split("\n")[0][:300]

    async def async_events(self, unit: str | None, limit: int) -> list[dict]:
        if self.db is not None and self.status == "ok":
            await self.async_flush()
            try:
                return await self.hass.async_add_executor_job(self.db.events, unit, limit)
            except Exception:  # noqa: BLE001
                pass
        rows = [r for r in self._recent if not unit or r["unit"] == unit][:limit]
        return [{**r, "ts": r["ts"].replace(tzinfo=timezone.utc).isoformat()} for r in rows]

    async def async_prune(self) -> None:
        if self.db is not None:
            try:
                await self.hass.async_add_executor_job(self.db.prune_events, 90)
            except Exception:  # noqa: BLE001
                pass

    async def async_close(self) -> None:
        await self.async_flush()
        if self.db is not None:
            await self.hass.async_add_executor_job(self.db.close)
            self.db = None

    async def async_test(self, url: str) -> str | None:
        """Try a database URL. Returns None when OK, otherwise the error text."""
        db = TerrariumDB(url)
        try:
            await self.hass.async_add_executor_job(db.connect)
            await self.hass.async_add_executor_job(db.ping)
            return None
        except Exception as err:  # noqa: BLE001
            return str(err).split("\n")[0][:300]
        finally:
            await self.hass.async_add_executor_job(db.close)
