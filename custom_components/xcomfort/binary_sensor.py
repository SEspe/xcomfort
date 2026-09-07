###Version 1.3.9
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
import logging

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

# The SHC reports these device types as plain strings in the "value" field.
# They are compared exactly rather than with find(), because "NO MOTION"
# contains "MOTION" and a substring test would invert the motion sensors.
ON_STATES = ("ON", "OPEN", "MOTION")
OFF_STATES = ("OFF", "CLOSE", "CLOSED", "NO MOTION")


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    i = 0
    for device in coordinator.data:
        if device['type'].find("BinaryMotionSensor") >= 0:
            async_add_entities([xcBinarySensor(coordinator, i, device['id'], device['name'],
                                               BinarySensorDeviceClass.MOTION)])
        elif device['type'].find("BinaryInput") >= 0:
            # A binary input can be wired to a door contact, a window contact or
            # anything else, and the SHC does not say which, so it gets no device
            # class and the user can assign one in Home Assistant.
            async_add_entities([xcBinarySensor(coordinator, i, device['id'], device['name'], None)])
        i += 1


class xcBinarySensor(BinarySensorEntity):

    def __init__(self, coordinator, id, unique_name, name, device_class):
        self.id = id
        self._name = name
        self._unique_id = unique_name
        self._device_class = device_class
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        _LOGGER.debug("xcBinarySensor.init() %s", self._name)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_class(self):
        return self._device_class

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def is_on(self):
        try:
            value = str(self.coordinator.data[self.id]['value']).strip().upper()
        except (IndexError, KeyError, TypeError):
            return None
        if value in ON_STATES:
            return True
        if value in OFF_STATES:
            return False
        # Logged at debug because the coordinator refreshes every few seconds.
        _LOGGER.debug("xcBinarySensor %s: unrecognised value %s", self._name, value)
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
