"""
Support for controlling GPIO pins of a Raspberry Pi.
Fork of remote_rpi_gpio (https://www.home-assistant.io/integrations/remote_rpi_gpio/)
as there the status is currently always inverted (https://github.com/home-assistant/core/issues/24571)

"""
import homeassistant.loader as loader
import logging


_LOGGER = logging.getLogger(__name__)

CONF_BOUNCETIME = "bouncetime"
CONF_INVERT_LOGIC = "invert_logic"
CONF_PULL_MODE = "pull_mode"

DEFAULT_BOUNCETIME = 50
DEFAULT_INVERT_LOGIC = False
DEFAULT_PULL_MODE = "UP"


# The domain of your component. Should be equal to the name of your component.
DOMAIN = 'remote_gpio'

# List of integration names (string) your integration depends upon.
DEPENDENCIES = []

log = logging.getLogger(DOMAIN)


def setup(hass, config):
    """Set up remote_gpio_custom."""
    try:
        log.info("loading {} completed.".format(DOMAIN))
        return True
    except:  # noqa
        log.exception("failed to initialize {}".format(DOMAIN))
        return False
