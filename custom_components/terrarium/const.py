"""Constants for the Terrarium integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "terrarium"
VERSION = "1.2.0"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.BUTTON]

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
CONF_DB_URL = "db_url"

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
    # automation – may be overridden by a group of the same kind (see GROUP_KINDS)
    "lights": [],
    "light_auto": True,
    "rain": {},
    "vent": {},
}

KINDS = ["light", "rain", "vent"]

DEFAULT_RAIN: dict = {
    "entity_id": "",
    "enabled": True,
    "profiles": [],
    "manual_duration": 30,     # s, "rain now"
    "max_duration": 600,       # s, safety limit per run
    "min_pause": 0,            # min between two runs (all reasons)
    "hum_start": {"enabled": False, "below": 60.0, "duration": 30, "min_pause": 60},
    "hum_block": {"enabled": False, "above": 90.0},
}

DEFAULT_VENT: dict = {
    "entity_id": "",
    "enabled": True,
    "profiles": [],
    "temp_on": {"enabled": False, "above": 32.0, "hyst": 1.0},
    "hum_on": {"enabled": False, "above": 90.0, "hyst": 5.0},
    "min_run": 5,              # min, minimum run time after a condition switched it on
}

DEFAULT_LIGHT: dict = {
    "id": "",
    "name": "",
    "type_id": "",
    "entity_id": "",
    "enabled": True,
    "profiles": [],
    "overheat": {"enabled": False, "above": 40.0, "hyst": 2.0},
}

LIGHT_CATEGORIES = ["led", "hid", "pl", "ph", "night", "uv", "other"]

# seeded light catalogue (editable, own ones can be added)
DEFAULT_LIGHT_TYPES: list[dict] = [
    {"id": "led", "name": "LED Ausleuchtung", "category": "led", "watt": 20, "restrike_min": 0, "color": "#fff6e0"},
    {"id": "hid35", "name": "HID 35 W", "category": "hid", "watt": 35, "restrike_min": 10, "color": "#ffe9b0"},
    {"id": "hid70", "name": "HID 70 W", "category": "hid", "watt": 70, "restrike_min": 10, "color": "#ffe9b0"},
    {"id": "hid100", "name": "HID 100 W", "category": "hid", "watt": 100, "restrike_min": 10, "color": "#ffe9b0"},
    {"id": "hid150", "name": "HID 150 W", "category": "hid", "watt": 150, "restrike_min": 10, "color": "#ffe9b0"},
    {"id": "pl", "name": "P&L Leuchte (Pflanzen)", "category": "pl", "watt": 30, "restrike_min": 0, "color": "#f3e8ff"},
    {"id": "ph", "name": "Power & Heat", "category": "ph", "watt": 50, "restrike_min": 0, "color": "#ffcf8a"},
    {"id": "ph_led", "name": "Power & Heat LED", "category": "ph", "watt": 25, "restrike_min": 0, "color": "#ffd99a"},
    {"id": "night", "name": "Nacht-LED (Mondlicht)", "category": "night", "watt": 2, "restrike_min": 0, "color": "#7fa8ff"},
]

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
