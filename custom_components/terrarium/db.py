"""MariaDB storage for Terrarium (synchronous, runs in the executor; no Home Assistant imports).

Every object is stored as a JSON document in its own table, plus readable key columns:

    tr_enclosure   enclosures with their terrariums (layout, climate, notifications, lights, rain, ventilation)
    tr_group       terrariums switched together (kind light / rain / vent) and their shared settings
    tr_template    templates for light / rain / vent
    tr_light_type  light sources (catalogue: LED, HID 35–150 W, P&L, Power & Heat, night LED, own ones)
    tr_setting     global settings
    tr_event       switching log (what was switched when and why)
    tr_meta        schema version

Works with MariaDB / MySQL (``mysql://user:pass@host/terrarium?charset=utf8mb4``) and – for tests – SQLite.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import (
    BigInteger, Column, DateTime, Integer, MetaData, String, Table, Text, create_engine, delete, insert, select,
    update,
)
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import Engine, make_url

SCHEMA_VERSION = 1

LongText = Text().with_variant(mysql.LONGTEXT(), "mysql", "mariadb")
TABLE_KW = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mariadb_engine": "InnoDB", "mariadb_charset": "utf8mb4"}

md = MetaData()


def _doc_table(name: str, *extra: Column) -> Table:
    return Table(
        name, md,
        Column("id", String(40), primary_key=True),
        *extra,
        Column("name", String(120), nullable=False, default=""),
        Column("data", LongText, nullable=False),
        Column("updated_at", DateTime, nullable=False),
        **TABLE_KW,
    )


t_meta = Table("tr_meta", md, Column("key", String(64), primary_key=True), Column("value", Text), **TABLE_KW)
t_enclosure = _doc_table("tr_enclosure", Column("nr", Integer, nullable=False, default=0))
t_group = _doc_table("tr_group", Column("kind", String(16), nullable=False, default=""))
t_template = _doc_table("tr_template", Column("kind", String(16), nullable=False, default=""))
t_light_type = _doc_table("tr_light_type", Column("category", String(24), nullable=False, default=""))
t_setting = Table("tr_setting", md, Column("key", String(64), primary_key=True), Column("data", LongText, nullable=False),
                  Column("updated_at", DateTime, nullable=False), **TABLE_KW)
t_event = Table(
    "tr_event", md,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("ts", DateTime, nullable=False, index=True),
    Column("unit", String(80), nullable=False, default=""),
    Column("kind", String(16), nullable=False, default=""),
    Column("entity_id", String(255), nullable=False, default=""),
    Column("action", String(16), nullable=False, default=""),
    Column("reason", String(255), nullable=False, default=""),
    **TABLE_KW,
)

# collection name -> (table, extra key column name or None)
COLLECTIONS = {
    "enclosures": (t_enclosure, "nr"),
    "groups": (t_group, "kind"),
    "templates": (t_template, "kind"),
    "light_types": (t_light_type, "category"),
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def redact(url: str) -> str:
    try:
        return make_url(url).render_as_string(hide_password=True)
    except Exception:  # noqa: BLE001
        return "?"


class TerrariumDB:
    def __init__(self, url: str) -> None:
        self.url = url
        self.engine: Engine | None = None

    # ------------------------------------------------------------ connection
    def connect(self) -> None:
        u = make_url(self.url)
        kw: dict[str, Any] = {"pool_pre_ping": True, "future": True}
        if u.get_backend_name() in ("mysql", "mariadb"):
            kw.update(pool_recycle=1800, pool_size=2, max_overflow=3, connect_args={"connect_timeout": 10})
        self.engine = create_engine(u, **kw)
        md.create_all(self.engine)
        with self.engine.begin() as c:
            if c.execute(select(t_meta.c.value).where(t_meta.c.key == "schema_version")).scalar() is None:
                c.execute(insert(t_meta).values(key="schema_version", value=str(SCHEMA_VERSION)))

    def close(self) -> None:
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None

    def ping(self) -> None:
        with self.engine.connect() as c:
            c.execute(select(1))

    # ------------------------------------------------------------ documents
    def is_empty(self) -> bool:
        with self.engine.connect() as c:
            for table, _key in COLLECTIONS.values():
                if c.execute(select(table.c.id).limit(1)).first() is not None:
                    return False
            return c.execute(select(t_setting.c.key).limit(1)).first() is None

    def load_all(self) -> dict:
        out: dict[str, Any] = {}
        with self.engine.connect() as c:
            for coll, (table, _key) in COLLECTIONS.items():
                out[coll] = [json.loads(r.data) for r in c.execute(select(table.c.data))]
            out["settings"] = {r.key: json.loads(r.data) for r in c.execute(select(t_setting.c.key, t_setting.c.data))}
        return out

    def sync(self, state: dict) -> int:
        """Write the complete state: upsert changed documents, delete removed ones. Returns changed rows."""
        changed = 0
        now = _now()
        with self.engine.begin() as c:
            for coll, (table, key) in COLLECTIONS.items():
                docs = {str(d["id"]): d for d in state.get(coll, []) if isinstance(d, dict) and d.get("id")}
                have = {r.id: r.data for r in c.execute(select(table.c.id, table.c.data))}
                for doc_id, doc in docs.items():
                    data = json.dumps(doc, ensure_ascii=False, sort_keys=True)
                    vals = {"name": str(doc.get("name") or "")[:120], "data": data, "updated_at": now}
                    if key:
                        vals[key] = doc.get(key) if key == "nr" else str(doc.get(key) or "")
                        if key == "nr":
                            vals[key] = int(doc.get("nr") or 0)
                    if doc_id not in have:
                        c.execute(insert(table).values(id=doc_id, **vals))
                        changed += 1
                    elif have[doc_id] != data:
                        c.execute(update(table).where(table.c.id == doc_id).values(**vals))
                        changed += 1
                gone = set(have) - set(docs)
                if gone:
                    c.execute(delete(table).where(table.c.id.in_(gone)))
                    changed += len(gone)
            settings = state.get("settings") or {}
            have = {r.key: r.data for r in c.execute(select(t_setting.c.key, t_setting.c.data))}
            for k, v in settings.items():
                data = json.dumps(v, ensure_ascii=False, sort_keys=True)
                if k not in have:
                    c.execute(insert(t_setting).values(key=k, data=data, updated_at=now))
                    changed += 1
                elif have[k] != data:
                    c.execute(update(t_setting).where(t_setting.c.key == k).values(data=data, updated_at=now))
                    changed += 1
        return changed

    # ------------------------------------------------------------ log
    def log_events(self, rows: list[dict]) -> None:
        if not rows:
            return
        with self.engine.begin() as c:
            c.execute(insert(t_event), [{
                "ts": r["ts"], "unit": str(r.get("unit", ""))[:80], "kind": str(r.get("kind", ""))[:16],
                "entity_id": str(r.get("entity_id", ""))[:255], "action": str(r.get("action", ""))[:16],
                "reason": str(r.get("reason", ""))[:255],
            } for r in rows])

    def events(self, unit: str | None = None, limit: int = 100) -> list[dict]:
        q = select(t_event).order_by(t_event.c.ts.desc(), t_event.c.id.desc()).limit(limit)
        if unit:
            q = q.where(t_event.c.unit == unit)
        with self.engine.connect() as c:
            return [{"ts": r.ts.replace(tzinfo=timezone.utc).isoformat(), "unit": r.unit, "kind": r.kind,
                     "entity_id": r.entity_id, "action": r.action, "reason": r.reason}
                    for r in c.execute(q)]

    def prune_events(self, days: int = 90) -> None:
        with self.engine.begin() as c:
            c.execute(delete(t_event).where(t_event.c.ts < _now() - timedelta(days=days)))
