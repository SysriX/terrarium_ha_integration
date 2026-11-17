"""Sensors: temperature, humidity and status per compartment, problems per enclosure."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, S_ALARM, S_OFFLINE, SIGNAL_UPDATE, STATUSES
from .entity import CompartmentEntity, compartment_entities
from .manager import TerrariumManager, label_of


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    mgr: TerrariumManager = entry.runtime_data
    entities = [EnclosureProblemsSensor(mgr, enc) for enc in mgr.enclosures]
    entities += compartment_entities(mgr, [TemperatureSensor, HumiditySensor, StatusSensor])
    async_add_entities(entities)


class TemperatureSensor(CompartmentEntity, SensorEntity):
    platform_name = "sensor"
    key = "temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1

    @property
    def native_value(self):
        return self.live.get("temperature")

    @property
    def extra_state_attributes(self):
        tgt = self.live.get("targets", {})
        return {"min": tgt.get("temp_min"), "max": tgt.get("temp_max"),
                "sensors": [s["entity_id"] for s in self.live.get("temp_sensors", [])]}


class HumiditySensor(CompartmentEntity, SensorEntity):
    platform_name = "sensor"
    key = "humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_suggested_display_precision = 0

    @property
    def native_value(self):
        return self.live.get("humidity")

    @property
    def extra_state_attributes(self):
        tgt = self.live.get("targets", {})
        return {"min": tgt.get("hum_min"), "max": tgt.get("hum_max"),
                "sensors": [s["entity_id"] for s in self.live.get("hum_sensors", [])]}


class StatusSensor(CompartmentEntity, SensorEntity):
    platform_name = "sensor"
    key = "status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATUSES

    @property
    def native_value(self):
        return self.live.get("status")

    @property
    def extra_state_attributes(self):
        live = self.live
        comp = self.comp or {}
        return {
            "problems": live.get("problems", []),
            "pending": live.get("pending", []),
            "period": live.get("period"),
            "targets": live.get("targets", {}),
            "animal": comp.get("animal"),
            "compartment_name": comp.get("name"),
        }


class EnclosureProblemsSensor(SensorEntity):
    """Number of compartments of an enclosure with an active problem."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_translation_key = "problems"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, mgr: TerrariumManager, enc: dict) -> None:
        self.mgr = mgr
        self.enc_id = enc["id"]
        self._attr_unique_id = f"enc_{enc['id']}_problems"
        self.entity_id = f"sensor.terrarium_{enc['nr']}_problems"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, f"enc_{enc['id']}")})

    @property
    def native_value(self):
        enc = self.mgr.enclosure(self.enc_id)
        if enc is None:
            return None
        return sum(1 for c in enc["compartments"]
                   if self.mgr.live.get(c["id"], {}).get("status") in (S_ALARM, S_OFFLINE))

    @property
    def extra_state_attributes(self):
        enc = self.mgr.enclosure(self.enc_id)
        if enc is None:
            return {}
        return {"compartments": {label_of(enc, c): self.mgr.live.get(c["id"], {}).get("status")
                                 for c in enc["compartments"]}}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self.async_write_ha_state))
