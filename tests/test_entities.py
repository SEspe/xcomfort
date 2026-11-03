import asyncio
import types

import pytest

from xcomfort import binary_sensor, light


class FakeXC:
    """Records the state values the entities send to the SHC."""

    def __init__(self, switch_ok=True):
        self.switch_ok = switch_ok
        self.sent = []

    async def switch(self, dev_id, state):
        self.sent.append(state)
        return self.switch_ok


def make_coordinator(value, xc=None):
    return types.SimpleNamespace(
        xc=xc or FakeXC(),
        data=[{"id": "dev1", "value": value}],
        last_update_success=True,
    )


def make_dimmer(xc):
    coordinator = make_coordinator("0", xc)
    entity = light.xcLight(coordinator, 0, "xCo1", "Dimmer", "DimActuator")
    entity.async_write_ha_state = lambda: None
    return entity


# --- Dimmer brightness --------------------------------------------------------

@pytest.mark.parametrize("ha_brightness, sent", [
    (1, "1"),      # 1/255 used to round down to 0, which switches the dimmer off
    (2, "1"),
    (3, "1"),
    (128, "50"),
    (255, "100"),
])
def test_dimmer_turn_on_sends_percentage(ha_brightness, sent):
    xc = FakeXC()
    entity = make_dimmer(xc)
    asyncio.run(entity.async_turn_on(brightness=ha_brightness))
    assert xc.sent == [sent]


def test_dimmer_turn_on_without_brightness_is_full():
    xc = FakeXC()
    asyncio.run(make_dimmer(xc).async_turn_on())
    assert xc.sent == ["100"]


def test_dimmer_never_sends_zero_on_turn_on():
    xc = FakeXC()
    entity = make_dimmer(xc)
    for ha_brightness in range(1, 256):
        asyncio.run(entity.async_turn_on(brightness=ha_brightness))
    assert "0" not in xc.sent


def test_dimmer_turn_off_sends_zero():
    xc = FakeXC()
    entity = make_dimmer(xc)
    asyncio.run(entity.async_turn_off())
    assert xc.sent == ["0"]


def test_dimmer_failed_switch_does_not_update_state():
    xc = FakeXC(switch_ok=False)
    coordinator = make_coordinator("0", xc)
    entity = light.xcLight(coordinator, 0, "xCo1", "Dimmer", "DimActuator")
    entity.async_write_ha_state = lambda: None
    asyncio.run(entity.async_turn_on(brightness=128))
    assert coordinator.data[0]["value"] == "0"


# --- Binary sensor ------------------------------------------------------------

@pytest.mark.parametrize("value, expected", [
    ("ON", True),
    ("OPEN", True),
    ("MOTION", True),
    ("OFF", False),
    ("CLOSE", False),
    ("CLOSED", False),
    ("NO MOTION", False),  # contains "MOTION"; must not read as on
    ("  on ", True),
    ("garbage", None),
])
def test_binary_sensor_maps_shc_values(value, expected):
    sensor = binary_sensor.xcBinarySensor(make_coordinator(value), 0, "xCo1", "Door", None)
    assert sensor.is_on is expected


def test_binary_sensor_unknown_when_id_missing():
    sensor = binary_sensor.xcBinarySensor(make_coordinator("ON"), 5, "xCo1", "Door", None)
    assert sensor.is_on is None
