[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/docs/faq/custom_repositories)
# Eaton xComfort SHC integration for Home Assistant
This is a custom component integrating the Eaton xComfort smart home system with Home Assistant.

It continues [plamish/xcomfort](https://github.com/plamish/xcomfort), which has been dormant since
June 2025. See [FORK.md](FORK.md) for how this repository is organised.

### What the Smart Home Controller does
xComfort devices talk to each other over Eaton's own radio protocol, which Home Assistant cannot
speak. The Smart Home Controller (SHC) is the bridge between the two: it is the hub your xComfort
devices are paired with, and it exposes them on your local network through an HTTP API.

This integration is the Home Assistant end of that bridge. It signs in to the SHC at its address on
your LAN, reads the devices in the zone you configure and mirrors them as Home Assistant entities,
so the lights, blinds, thermostats and sensors you would otherwise operate from the xComfort app
become ordinary HA entities on your dashboards and in your automations. Commands travel back the
same path: Home Assistant to the SHC, and the SHC out to the device over radio.

Everything stays on your own network - no Eaton cloud account is involved.

### Requirements :
- [xComfort Smart Home Controller](https://www.eaton.com/bg/en-gb/catalog/residential/xcomfort-smart-home-controller.html)
- [Home Assistant](https://www.home-assistant.io)

 > It is recommended to set the language of your Smart Home Controller to english as some state descriptions are language dependent and this integration only supports the english values

### Installation:
Add this repository to [HACS](https://hacs.xyz/docs/setup/download "HACS") as a custom repository:
three-dot menu -> Custom repositories -> `https://github.com/SEspe/xcomfort`, category
**Integration**. Then install it and restart Home Assistant.

### Configuration

Please note only devices from one SHC zone will be added to HA. For zone 1 use hz_1, for 2 use hz_2, etc.

To find zone number log into SHC via web console using this address http://ip_address_of_your_integration/system/console/config, go to Configuration Status -> Home Devices and use search function to search for 'hz_'. Number following hz_ is the zone number.

 > You can create a root zone that will contain all your devices. Add this one in HA to get all devices!

### Supported devices

| xComfort device | Appears in Home Assistant as |
| --- | --- |
| Dimming actuators | Light, with brightness |
| Light actuators | Light |
| Switch actuators | Switch |
| Shutter actuators | Cover |
| Scenes | Button |
| Radiator thermostats | Climate |
| Temperature sensors | Sensor, temperature |
| Humidity sensors | Sensor, humidity |
| Energy metering on actuators | Sensor, energy - feeds the energy dashboard |
| Power metering on actuators | Sensor, power |
| Room thermostat adjustment wheel | Sensor, the wheel offset in degrees |
| Binary inputs | Binary sensor - assign a device class in the entity settings |
| Motion sensors | Binary sensor, motion |

Battery level is not available. The SHC does not report a battery field for any device, through
either of the API calls this integration uses, so it cannot be surfaced as an entity.

If a device of yours does not appear, call the `xcomfort.save_status_files` action. It writes
`xcomfort_devices` and `xcomfort_log_stats` into your config directory, which together show every
device the controller reports and what type string it uses. Attach both to an issue.

The integration polls updates from xComfort SHC to Home Assistant with user defined frequency.

### xComfort to MQTT broker
For instant, push based updates from xComfort SHC to Home Assistant you can try AppDaemon based [xcomfort2mqtt](https://github.com/plamish/xcomfort2mqtt "xcomfort2mqtt") . This can be useful if you want to trigger  Home Assistant automations from your xComfort devices

### Help and new ideas
For help or questions, open an [issue](https://github.com/SEspe/xcomfort/issues).
