"""Switches per terrarium: notifications on/off, light/rain/ventilation automation on/off."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import KINDS
from .entity import CompartmentEntity, compartment_entities


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    mgr = entry.runtime_data
    entities = compartment_entities(mgr, [NotifySwitch])
    for enc in mgr.enclosures:
        for comp in enc["compartments"]:
            features = mgr.features(comp)
            entities += [AutoSwitch(mgr, enc, comp, kind) for kind in KINDS if features[kind]]
    async_add_entities(entities)


class NotifySwitch(CompartmentEntity, SwitchEntity):
    platform_name = "switch"
    key = "cfg_notify"
    _attr_entity_category = EntityCategory.CONFIG

    @property
    def is_on(self):
        comp = self.comp
        return bool(comp and comp["notify"]["enabled"])

    async def async_turn_on(self, **kwargs) -> None:
        await self.mgr.async_set_notify_enabled(self.comp_id, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.mgr.async_set_notify_enabled(self.comp_id, False)


class AutoSwitch(CompartmentEntity, SwitchEntity):
    """Light / rain / ventilation automation of the terrarium (or of its group)."""

    platform_name = "switch"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, mgr, enc: dict, comp: dict, kind: str) -> None:
        self.kind = kind
        self.key = f"cfg_{kind}_auto"
        self._attr_icon = {"light": "mdi:lightbulb-auto", "rain": "mdi:weather-pouring", "vent": "mdi:fan-auto"}[kind]
        super().__init__(mgr, enc, comp)

    @property
    def is_on(self):
        comp = self.comp
        if comp is None:
            return False
        cfg = self.mgr.effective(comp, self.kind)
        return bool(cfg["light_auto"] if self.kind == "light" else cfg[self.kind]["enabled"])

    @property
    def extra_state_attributes(self):
        comp = self.comp
        grp = self.mgr.group_of(self.comp_id, self.kind) if comp else None
        return {"group": grp["name"] if grp else None}

    async def async_turn_on(self, **kwargs) -> None:
        await self.mgr.async_set_auto(self.comp_id, self.kind, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.mgr.async_set_auto(self.comp_id, self.kind, False)
