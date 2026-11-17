"""Problem binary sensor per compartment."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import S_ALARM, S_OFFLINE
from .entity import CompartmentEntity, compartment_entities


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities(compartment_entities(entry.runtime_data, [ProblemSensor]))


class ProblemSensor(CompartmentEntity, BinarySensorEntity):
    platform_name = "binary_sensor"
    key = "problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        return self.live.get("status") in (S_ALARM, S_OFFLINE)

    @property
    def extra_state_attributes(self):
        return {"problems": self.live.get("problems", [])}
