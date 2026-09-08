# Eaton xComfort SHC integration for Home Assistant

Brings the devices on your Eaton xComfort system into Home Assistant as lights, switches, covers,
climate and sensor entities.

## What the Smart Home Controller does

xComfort devices talk to each other over Eaton's own radio protocol, which Home Assistant cannot
speak. The Smart Home Controller (SHC) is the bridge between the two: it is the hub your xComfort
devices are paired with, and it exposes them on your local network through an HTTP API.

This integration is the Home Assistant end of that bridge. It signs in to the SHC at its address on
your LAN, reads the devices in the zone you configure and mirrors them as Home Assistant entities,
so the lights, blinds, thermostats and sensors you would otherwise operate from the xComfort app
become ordinary HA entities on your dashboards and in your automations. Commands travel back the
same path: Home Assistant to the SHC, and the SHC out to the device over radio.

Everything stays on your own network - no Eaton cloud account is involved.

## Configuration

Only devices from one SHC zone are added to Home Assistant. For zone 1 use `hz_1`, for zone 2 use
`hz_2`, and so on. You can create a root zone on the controller that contains all your devices and
add that one to get everything.

Set the language of your Smart Home Controller to English. Some state descriptions are language
dependent and this integration only understands the English values.

See the [README](https://github.com/SEspe/xcomfort) for the full device list and setup details.
