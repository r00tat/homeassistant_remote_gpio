"""Allows to configure a switch using RPi GPIO."""
import logging

from gpiozero import LED, GPIOZeroError
from gpiozero.pins.pigpio import PiGPIOFactory
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
    CONF_HOST,
    DEVICE_DEFAULT_NAME,
    STATE_UNKNOWN,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
import homeassistant.helpers.config_validation as cv

from . import CONF_INVERT_LOGIC, DEFAULT_INVERT_LOGIC

_LOGGER = logging.getLogger(__name__)

CONF_PORTS = "ports"

_SENSORS_SCHEMA = vol.Schema({cv.positive_int: cv.string})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORTS): _SENSORS_SCHEMA,
    vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
})


def setup_led(address, port, name, invert_logic=False):
    """set up a led"""
    _LOGGER.debug(
        "setting up output %s on %s port %s %s",
        name,
        address,
        port,
        "inverted" if invert_logic else "",
    )
    led = LED(port, active_high=not invert_logic, pin_factory=PiGPIOFactory(address))
    return led


def setup_switch(address, port, name, invert_logic=False):
    """Set up a switch."""
    new_switch = RemoteRPiGPIOSwitch(name, address, port, invert_logic)
    return new_switch


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Remote Raspberry PI GPIO devices."""
    address = config[CONF_HOST]
    invert_logic = config[CONF_INVERT_LOGIC]
    ports = config[CONF_PORTS]

    devices = []
    for port, name in ports.items():
        try:

            new_switch = setup_switch(address, port, name, invert_logic)
            devices.append(new_switch)
        except (ValueError, IndexError, KeyError, OSError):
            return

    add_entities(devices)


class RemoteRPiGPIOSwitch(SwitchEntity):
    """Representation of a Remote Raspberry Pi GPIO."""

    def __init__(self, name, address, port, invert_logic):
        """Initialize the pin."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._state = STATE_UNKNOWN
        self._address = address
        self._port = port
        self._invert_logic = invert_logic
        self.setup_switch()

    def setup_switch(self):
        """create a switch"""
        self._switch = None
        try:
            self._switch = setup_led(self._address, self._port, self._name,
                                     self._invert_logic)
            self._state = STATE_UNKNOWN
        except Exception as err:
            _LOGGER.exception("failed to connect switch", err)
            self._state = STATE_UNAVAILABLE

        return self._switch

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
        return self._state == STATE_ON

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self.change_state(True)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.change_state(False)

    def change_state(self, on=True):
        """change the state"""
        _LOGGER.debug("turn %s switch %s %s", "on" if on else "off", self._name,
                      self._switch.pin)
        try:
            self.ensure_connected()
            self._state = STATE_ON if on else STATE_OFF
            if on:
                self._switch.on()
            else:
                self._switch.off()
            self.schedule_update_ha_state()
        except GPIOZeroError:
            _LOGGER.exception("failed to change state of the switch, gpio error")
            self._switch = None
            self._state = STATE_UNAVAILABLE
        except Exception:
            _LOGGER.exception("failed to change state of the switch")

    @property
    def is_connected(self):
        """is the switch connected"""
        return self._switch is not None

    def ensure_connected(self):
        """make sure we got an active connection"""
        if not self.is_connected:
            self.setup_switch()
