import asyncio

import pytest

from conftest import FakeResponse, FakeSession
from xcomfort.xcomfortAPI import ConfigEntryAuthFailed, ConfigEntryNotReady


def run(coro):
    return asyncio.run(coro)


def reply_with(api, reply):
    """Make api.query return reply for every call."""

    async def fake_query(method, params=None):
        return reply

    api.query = fake_query
    return api


# --- Controller replies -------------------------------------------------------

@pytest.mark.parametrize("reply, expected", [
    ({"status": "ok"}, True),
    ({"status": "error"}, False),
    ([{}], False),  # query() fallback when the SHC cannot be reached
    ({}, False),
])
def test_switch_reports_success_from_status(make_api, reply, expected):
    api = reply_with(make_api(), reply)
    assert run(api.switch("dev", "on")) is expected


def test_switch_does_not_raise_when_shc_unreachable(make_api):
    api = reply_with(make_api(), [{}])
    assert run(api.switch("dev", "off")) is False


@pytest.mark.parametrize("reply, expected", [
    ({"status": "ok"}, True),
    ([{}], False),
])
def test_scene_reports_success_from_status(make_api, reply, expected):
    api = reply_with(make_api(), reply)
    assert run(api.scene("scene1")) is expected


def test_set_heatingmode_does_not_raise_when_shc_unreachable(make_api):
    api = reply_with(make_api(), [{}])
    api.heating_status = {"zone1": {"heating": False, "setpoint": 20.0}}
    assert run(api.set_heatingmode("zone1", True)) is False
    assert api.heating_status["zone1"]["heating"] is False


def test_set_temperature_does_not_raise_when_shc_unreachable(make_api):
    api = reply_with(make_api(), [{}])
    api.heating_status = {"zone1": {"heating": True, "setpoint": 20.0}}
    assert run(api.set_temperture("zone1", 21.5)) is False
    assert api.heating_status["zone1"]["setpoint"] == 20.0


def test_set_temperature_updates_setpoint_on_success(make_api):
    api = reply_with(make_api(), {"status": "ok"})
    api.heating_status = {"zone1": {"heating": True, "setpoint": 20.0}}
    assert run(api.set_temperture("zone1", 21.5)) is True
    assert api.heating_status["zone1"]["setpoint"] == 21.5


# --- Connection handling ------------------------------------------------------

def test_query_returns_empty_result_on_connection_error(make_api):
    api = make_api(FakeSession(post_error=True))
    assert run(api.query("Diagnostics/getPhysicalDevices")) == [{}]


def test_connect_401_raises_auth_failed(make_api):
    session = FakeSession(get_response=FakeResponse(status=401))
    with pytest.raises(ConfigEntryAuthFailed):
        run(make_api(session).connect())


def test_connect_without_cookie_raises_not_ready(make_api):
    session = FakeSession(get_response=FakeResponse(status=200, headers={}))
    with pytest.raises(ConfigEntryNotReady):
        run(make_api(session).connect())


def test_connect_stores_session_cookie(make_api):
    cookie = "JSESSIONID=abc123; Path=/; HttpOnly; End"
    session = FakeSession(get_response=FakeResponse(
        status=200, headers={"Set-Cookie": cookie}))
    api = make_api(session)
    run(api.connect())
    assert api.is_connected is True
    assert api.sessionID.startswith("JSESSIONID=abc123")


def test_connect_other_error_raises_not_ready(make_api):
    session = FakeSession(get_response=FakeResponse(status=503))
    with pytest.raises(ConfigEntryNotReady):
        run(make_api(session).connect())


# --- Battery devices ----------------------------------------------------------

def test_battery_devices_skip_mains_children_and_unpowered(make_api):
    api = make_api()
    api.physical_devices = {
        "battery-button": {"deviceUid": "battery-button", "powered": "Battery",
                           "poweredId": "2", "name": "Button"},
        "mains-dimmer": {"deviceUid": "mains-dimmer", "powered": "Mains",
                         "poweredId": "6", "name": "Dimmer"},
        "channel": {"deviceUid": "channel", "parentId": "battery-button",
                    "powered": "Battery", "poweredId": "2", "name": "Channel 2"},
        "unpowered": {"deviceUid": "unpowered", "name": "Old"},
    }
    assert list(api.get_battery_devices()) == ["battery-button"]


def test_battery_status_is_empty_when_missing(make_api):
    api = make_api()
    api.system_states = {}
    assert api.get_battery_status() == {}
