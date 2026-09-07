###Version 1.3.5
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
import json
import logging
import asyncio


_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN

# Device types the SHC reports that map straight onto a numeric sensor, as
# type substring -> (device class, state class, unit, icon, display precision).
# A device class already implies an icon and a precision, so those two are only
# spelled out for the type that has no device class.
#
# WheelSensor is the adjustment wheel on a room thermostat: it reports how far
# the wheel has been turned, so the value is a relative offset in degrees
# (-3.1 as readily as 3.1) rather than an absolute temperature. It gets no
# device class for that reason.
SENSOR_TYPES = {
    "HumiditySensor": (SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, None, None),
    "EnergyConsumptionMeter": (SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, UnitOfEnergy.KILO_WATT_HOUR, None, None),
    "PowerConsumptionMeter": (SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, UnitOfPower.WATT, None, None),
    "WheelSensor": (None, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "mdi:knob", 1),
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    i = 0
    for device in coordinator.data:
        if device['type'].find("Temp") >= 0:
            # The channel suffix is kept. A room thermostat exposes both a
            # TemperatureSensor "(temperature)" and a WheelSensor "(adjustment)"
            # under one device name, so stripping it off the reading left the two
            # entities telling apart only by the wheel having a suffix. The SHC
            # emits both suffixes in English whatever its display language.
            async_add_entities([xcTemperature(coordinator, i, device['id'], device['name'])])
        else:
            for type_name, config in SENSOR_TYPES.items():
                if device['type'].find(type_name) >= 0:
                    async_add_entities([xcSensor(coordinator, i, device['id'],
                                                 device['name'], *config)])
                    break
        i += 1

class xcTemperature(SensorEntity):

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, id, unique_name, name ):
        self.id = id
        self._name = name
        self._unique_id = unique_name
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        self.temp_set = ''
        self.temp_pos = ''
        _LOGGER.debug("xcTemperature.init() %s",name)

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def native_value(self):
        try:
            return float(self.coordinator.data[self.id]['value'])
        except (IndexError, KeyError, TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self):
        stats_id = str(self._unique_id).replace('xCo','hdm:xComfort Adapter')
        try:
            self.last_message_time = self.coordinator.xc.log_stats[stats_id]['lastMsgTimeStamp']
        except:
            self.messages_per_day = '0'
        else:
            self.messages_per_day = self.coordinator.xc.log_stats[stats_id]['msgsPerDay']
            stats_id = stats_id.replace('_u0','_vp')
            try:
                self.temp_pos = self.coordinator.xc.log_stats[stats_id]['eventLog']
                stats_id = stats_id.replace('_vp','_ta')
                self.temp_set = self.coordinator.xc.log_stats[stats_id]['eventLog']
            except:
                self.temp_set = ''
                self.temp_pos = ''

        if self.temp_set == '':
            return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time}
        else:
            return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time, "Set Temperature": self.temp_set, "Position:": self.temp_pos}

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    #async def async_update(self):
    #    await self.coordinator.async_request_refresh()


class xcSensor(SensorEntity):
    """A read-only numeric device the SHC exposes as a plain value."""

    def __init__(self, coordinator, id, unique_name, name, device_class, state_class,
                 unit, icon, precision):
        self.id = id
        self._name = name
        self._unique_id = unique_name
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_suggested_display_precision = precision
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        _LOGGER.debug("xcSensor.init() %s", self._name)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        try:
            return float(self.coordinator.data[self.id]['value'])
        except (IndexError, KeyError, TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self):
        stats_id = str(self._unique_id).replace('xCo','hdm:xComfort Adapter')
        try:
            self.last_message_time = self.coordinator.xc.log_stats[stats_id]['lastMsgTimeStamp']
        except:
            self.last_message_time = ''
            self.messages_per_day = ''
        else:
            self.messages_per_day = self.coordinator.xc.log_stats[stats_id]['msgsPerDay']
        return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time}

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
