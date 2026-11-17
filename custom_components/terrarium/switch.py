"""Switch per compartment: notifications on/off."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import CompartmentEntity, compartment_entities


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities(compartment_entities(entry.runtime_data, [NotifySwitch]))


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
