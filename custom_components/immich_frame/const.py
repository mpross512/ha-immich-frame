from homeassistant.const import CONF_HOST

DOMAIN = "immich_frame"
PLATFORMS = ["binary_sensor", "button", "light", "media_player", "sensor"]
DEFAULT_PORT = 53287
COMMAND_TIMEOUT = 10

BRIGHTNESS_COMMAND = "brightness"

# A negative brightness hands the display back to the device's own setting
SYSTEM_BRIGHTNESS_QUERY = "value=-1"
EFFECT_SYSTEM_BRIGHTNESS = "System brightness"

# key, name
BUTTON_COMMANDS = (
    ("settings", "Open settings"),
)

# Buttons replaced by the Slideshow media player. Their registry entries are cleared out on
# setup, so an upgraded install is not left with entities that no longer do anything.
REMOVED_BUTTON_KEYS = ("next", "pause", "previous")
RELOAD_COMMAND = "reload"
STATUS_COMMAND = "status"

# The frame answers a command before it has taken effect
STATUS_REFRESH_DELAY = 1.5

COORDINATOR = "coordinator"
