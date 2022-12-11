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
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
import functools as ft

from . import CONF_INVERT_LOGIC, DEFAULT_INVERT_LOGIC

_LOGGER = logging.getLogger(__name__)

CONF_PORTS = "ports"

_SENSORS_SCHEMA = vol.Schema({cv.positive_int: cv.string})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORTS): _SENSORS_SCHEMA,
    vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
})


async def setup_switch(address, port, name, invert_logic, hass):
    """Set up a switch."""
    new_switch = RemoteRPiGPIOSwitch(name, address, port, invert_logic, hass)
    await new_switch.setup_switch()
    return new_switch


async def async_setup_platform(hass: HomeAssistant,
                               config,
                               async_add_entities,
                               discovery_info=None):
    """Set up the Remote Raspberry PI GPIO devices."""
    address = config[CONF_HOST]
    invert_logic = config[CONF_INVERT_LOGIC]
    ports = config[CONF_PORTS]

    devices = []
    for port, name in ports.items():
        try:

            new_switch = await setup_switch(address, port, name, invert_logic, hass)
            devices.append(new_switch)
        except (ValueError, IndexError, KeyError, OSError):
            return

    await async_add_entities(devices)


class RemoteRPiGPIOSwitch(SwitchEntity):
    """Representation of a Remote Raspberry Pi GPIO."""

    def __init__(self, name: str, address: str, port: int, invert_logic: bool,
                 hass: HomeAssistant):
        """Initialize the pin."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._state = STATE_UNKNOWN
        self._address = address
        self._port = port
        self._invert_logic = invert_logic
        self._hass = hass

    async def setup_switch(self):
        """create a switch"""
        self._switch = None
        try:
            _LOGGER.debug(
                "setting up output %s on %s port %s %s",
                self._name,
                self._address,
                self._port,
                "inverted" if self._invert_logic else "",
            )
            self._switch: LED = await self._hass.async_add_executor_job(
                ft.partial(LED.__init__,
                           self._port,
                           active_high=not self._invert_logic,
                           pin_factory=PiGPIOFactory(self._address)))
            self._state = STATE_ON if self._switch.is_lit else STATE_OFF
        except Exception:
            _LOGGER.exception("failed to connect {}".format(str(self)))
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
        return self.is_connected and self._state == STATE_ON

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.change_state(True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.change_state(False)

    async def change_state(self, on=True):
        """change the state"""
        _LOGGER.debug("turn %s switch %s %s", "on" if on else "off", self._name,
                      self._port)
        try:
            await self.ensure_connected()
            self._state = STATE_ON if on else STATE_OFF
            await self._hass.async_add_executor_job(
                (self._switch.on if on else self._switch.off))
        except GPIOZeroError:
            _LOGGER.exception("failed to change state of the switch, gpio error")
            self._switch = None
            self._state = STATE_UNAVAILABLE
        except Exception:
            _LOGGER.exception("failed to change state of the switch")
            self._switch = None
            self._state = STATE_UNAVAILABLE
        self.schedule_update_ha_state()

    @property
    def is_connected(self):
        """is the switch connected"""
        return self._switch is not None

    async def ensure_connected(self):
        """make sure we got an active connection"""
        if not self.is_connected:
            await self.setup_switch()
        if not self.is_connected:
            # still not connected
            raise Exception("{} not connected".format(str(self)))

    def __str__(self) -> str:
        return "remote_gpio switch {} on {} pin {}".format(self._name, self._address,
                                                           self._port)

    def __repr__(self) -> str:
        return "RemoteRPiGPIOSwitch(\"{}\",\"{}\",{},{})".format(
            self._name, self._address, self._port,
            "True" if self._invert_logic else "False")
