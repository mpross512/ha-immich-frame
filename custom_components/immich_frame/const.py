from homeassistant.const import CONF_HOST

DOMAIN = "immich_frame"
PLATFORMS = ["button", "light"]
DEFAULT_PORT = 53287
COMMAND_TIMEOUT = 10

BUTTON_COMMANDS = (
    ("next", "Next photo"),
    ("previous", "Previous photo"),
    ("pause", "Pause slideshow")
)

BRIGHTNESS_COMMAND = "brightness"
