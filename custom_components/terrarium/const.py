"""Constants for the Terrarium integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "terrarium"
VERSION = "1.0.0"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH]

STORE_VERSION = 1
SIGNAL_UPDATE = f"{DOMAIN}_update"
EVENT_ALARM = f"{DOMAIN}_alarm"

STATIC_URL = "/terrarium_static"
CARD_FILE = "terrarium-card.js"
PANEL_URL = "terrarium"
PANEL_ELEMENT = "terrarium-panel"

CONF_PANEL_SHOW = "panel_show"
CONF_PANEL_TITLE = "panel_title"
CONF_PANEL_ICON = "panel_icon"
CONF_PANEL_ADMIN = "panel_admin"

DEFAULT_PANEL_TITLE = "Terrarien"
DEFAULT_PANEL_ICON = "mdi:turtle"

# Problem keys
P_TEMP_LOW = "temp_low"
P_TEMP_HIGH = "temp_high"
P_HUM_LOW = "hum_low"
P_HUM_HIGH = "hum_high"
P_OFFLINE = "offline"
PROBLEMS = [P_TEMP_LOW, P_TEMP_HIGH, P_HUM_LOW, P_HUM_HIGH, P_OFFLINE]

# Status of a compartment
S_OK = "ok"
S_PENDING = "pending"
S_ALARM = "alarm"
S_OFFLINE = "offline"
S_NOT_CONFIGURED = "not_configured"
STATUSES = [S_OK, S_PENDING, S_ALARM, S_OFFLINE, S_NOT_CONFIGURED]

DEVICE_KINDS = ["light", "heat", "uv", "ventilation", "rain", "fogger", "pump", "other"]

DEFAULT_COMPARTMENT: dict = {
    "name": "",
    "animal": "",
    "depth": None,
    "climate": {
        "temp_sensors": [],
        "hum_sensors": [],
        "temp_min": None,
        "temp_max": None,
        "hum_min": None,
        "hum_max": None,
        "night": {
            "enabled": False,
            "start": "21:00",
            "end": "07:00",
            "temp_min": None,
            "temp_max": None,
            "hum_min": None,
            "hum_max": None,
        },
        "delay": 10,
        "temp_hyst": 0.5,
        "hum_hyst": 3.0,
    },
    "notify": {
        "enabled": True,
        "targets": [],
        "clear": True,
        "offline": True,
        "repeat": 0,
        "persistent": False,
    },
    "devices": [],
    "look": {
        "substrate": "soil",
        "decor": "plants",
        "background": "rock",
    },
    # reserved for later modules (light schedule, ventilation, rain simulation, …)
    "light": {},
    "ventilation": {},
    "rain": {},
}

DEFAULT_ENCLOSURE: dict = {
    "name": "",
    "nr": 1,
    "width": 100.0,
    "height": 100.0,
    "depth": 50.0,
    "color": "wood",
    "compartments": [],
}

LOOK_SUBSTRATES = ["soil", "sand", "bark", "moss", "gravel", "water", "none"]
LOOK_DECOR = ["plants", "stones", "branches", "mixed", "none"]
LOOK_BACKGROUNDS = ["rock", "cork", "plain", "jungle"]
ENCLOSURE_COLORS = ["wood", "black", "white", "grey"]
