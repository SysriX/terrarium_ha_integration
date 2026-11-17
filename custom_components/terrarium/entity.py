"""Base entity for terrarium compartments."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SIGNAL_UPDATE
from .manager import TerrariumManager, label_of


def compartment_entities(mgr: TerrariumManager, classes: list[type]) -> list[Entity]:
    out = []
    for enc in mgr.enclosures:
        for comp in enc["compartments"]:
            out.extend(cls(mgr, enc, comp) for cls in classes)
    return out


class CompartmentEntity(Entity):
    """Entity bound to one compartment."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    platform_name: str = ""
    key: str = ""

    def __init__(self, mgr: TerrariumManager, enc: dict, comp: dict) -> None:
        self.mgr = mgr
        self.comp_id = comp["id"]
        label = label_of(enc, comp)
        self._attr_unique_id = f"{comp['id']}_{self.key}"
        self._attr_translation_key = self.key
        self.entity_id = f"{self.platform_name}.terrarium_{label.replace('.', '_')}_{self.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, comp["id"])})

    @property
    def comp(self) -> dict | None:
        return self.mgr.find(self.comp_id)[1]

    @property
    def live(self) -> dict:
        return self.mgr.live.get(self.comp_id, {})

    @property
    def available(self) -> bool:
        return self.comp is not None

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self.async_write_ha_state))
