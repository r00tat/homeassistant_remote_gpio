"""Allows to configure a switch using RPi GPIO."""
import logging

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_HOST, DEVICE_DEFAULT_NAME
import homeassistant.helpers.config_validation as cv

from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory

from . import CONF_INVERT_LOGIC, DEFAULT_INVERT_LOGIC, DOMAIN

_LOGGER = logging.getLogger("{}.{}".format(DOMAIN, __name__))

CONF_PORTS = "ports"

_SENSORS_SCHEMA = vol.Schema({cv.positive_int: cv.string})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORTS): _SENSORS_SCHEMA,
        vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Remote Raspberry PI GPIO devices."""
    address = config[CONF_HOST]
    invert_logic = config[CONF_INVERT_LOGIC]
    ports = config[CONF_PORTS]

    devices = []
    for port, name in ports.items():
        try:
            _LOGGER.info("setting up output on %s port %s %s", address, port, "inverted" if invert_logic else "")
            led = LED(port, active_high=not invert_logic, pin_factory=PiGPIOFactory(address))
        except (ValueError, IndexError, KeyError, OSError):
            return
        new_switch = RemoteRPiGPIOSwitch(name, led, invert_logic)
        devices.append(new_switch)

    add_entities(devices)

class RemoteRPiGPIOSwitch(SwitchEntity):
    """Representation of a Remtoe Raspberry Pi GPIO."""

    def __init__(self, name, led, invert_logic):
        """Initialize the pin."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._state = False
        self._invert_logic = invert_logic
        self._switch = led

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def assumed_state(self):
        """If unable to access real state of the entity."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.info("turn on switch %s %s", self._name, self._switch.pin)
        self._state = True
        self._switch.on()
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.info("turn off switch %s %s", self._name, self._switch.pin)
        self._state = False
        self._switch.off()
        self.schedule_update_ha_state()
