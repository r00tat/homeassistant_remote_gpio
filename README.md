# Home Assistant Raspberry PI Remote GPIO

This is a fork of [remote_rpi_gpio](https://www.home-assistant.io/integrations/remote_rpi_gpio/), as there is a [major open bug](https://github.com/home-assistant/core/issues/24571).
Currently the outputs are always inverted. If you set `invert_logic` the behaviour stays the same as `active_high` ([see `__init__.py`](https://github.com/home-assistant/core/blob/dev/homeassistant/components/remote_rpi_gpio/__init__.py#L29)) and `write_output` ([see `switch.py`](https://github.com/home-assistant/core/blob/dev/homeassistant/components/remote_rpi_gpio/switch.py#L78)) toggles at the same time.

Other changes:

- simplified import structure
- added logging

## Installation

Checkout this git repo inside of the `custom_components` in your config directory.

Configure your switches accordingly:

```yaml
switch:
  - platform: remote_gpio
    host: '192.168.1.123'
    ports:
      17: rpi_switch
```

## Development

Setup your dev environment with:

```bash
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt

```
