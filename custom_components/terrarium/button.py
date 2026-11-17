"""Button per terrarium with rain: rain now (manual run with the set duration)."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import CompartmentEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    mgr = entry.runtime_data
    async_add_entities([RainNowButton(mgr, enc, comp) for enc in mgr.enclosures for comp in enc["compartments"]
                        if mgr.features(comp)["rain"]])


class RainNowButton(CompartmentEntity, ButtonEntity):
    platform_name = "button"
    key = "rain_now"
    _attr_icon = "mdi:weather-pouring"

    async def async_press(self) -> None:
        self.mgr.rain_now(self.comp_id)
