/* Terrarium card + panel for Home Assistant – https://github.com/SysriX/terrarium_ha_integration */
(() => {
const VERSION = "1.2.0";
if (customElements.get("terrarium-card")) return;

/* ------------------------------------------------------------------ texts */
const TEXTS = {
  de: {
    title: "Terrarien", enclosure: "Anlage", new_enclosure: "Neue Anlage", add_enclosure: "Anlage anlegen",
    empty: "Noch keine Terrarienanlage angelegt.", empty_hint: "Lege eine Anlage mit Gesamtbreite und -höhe an und teile sie in einzelne Terrarien auf – nebeneinander, übereinander, in beliebiger Größe.",
    no_rights: "Nur Administratoren können Anlagen anlegen.",
    back: "Zurück", settings: "Einstellungen", edit: "Bearbeiten", save: "Speichern", cancel: "Abbrechen", delete: "Löschen",
    saved: "Gespeichert", saving: "Speichere …",
    status_ok: "OK", status_pending: "Abweichung", status_alarm: "Alarm", status_offline: "Keine Daten", status_not_configured: "Nicht eingerichtet",
    p_temp_low: "zu kalt", p_temp_high: "zu warm", p_hum_low: "zu trocken", p_hum_high: "zu feucht", p_offline: "Sensor liefert keine Werte",
    temperature: "Temperatur", humidity: "Luftfeuchtigkeit", day: "Tag", night: "Nacht", day_values: "Tagwerte", night_values: "Nachtwerte",
    target: "Soll", since: "seit", last24: "Letzte 24 Stunden", sensors: "Sensoren", devices: "Geräte", no_devices: "Keine Geräte zugeordnet – in den Einstellungen hinzufügen.",
    problems: "Meldungen", all_good: "Alles im grünen Bereich.", not_configured_hint: "Noch keine Sensoren gewählt – in den Einstellungen festlegen.",
    // enclosure editor
    enc_edit: "Anlage bearbeiten", enc_new: "Neue Anlage", number: "Nummer", name: "Name", width: "Breite", height: "Höhe", depth: "Tiefe",
    color: "Gehäuse", c_wood: "Holz", c_black: "Schwarz", c_white: "Weiß", c_grey: "Grau",
    size_total: "Gesamtmaße (cm)", layout: "Aufteilung", add_comp: "Terrarium hinzufügen", grid: "Raster erzeugen", rows: "Zeilen", cols: "Spalten", gap: "Abstand",
    snap: "Einrasten", compartments: "Terrarien", selected: "Ausgewähltes Terrarium", remove: "Entfernen", pos_x: "Links (X)", pos_y: "Oben (Y)",
    none_selected: "Ein Terrarium in der Zeichnung antippen, um es zu verschieben oder zu bearbeiten. Ziehen = verschieben, Ecke unten rechts = Größe.",
    numbering_hint: "Nummerierung automatisch von oben nach unten, links nach rechts.",
    confirm_grid: "Vorhandene Aufteilung durch ein Raster ersetzen?", confirm_delete_enc: "Anlage {nr} mit allen Terrarien und Einstellungen löschen?",
    no_space: "Kein freier Platz mehr – erst ein Terrarium verkleinern.",
    err_layout_overlap: "Terrarien überlappen sich: {d}", err_layout_out_of_bounds: "Terrarium ragt über die Anlage hinaus: {d}",
    err_layout_comp_size: "Ungültige Größe: {d}", err_layout_size: "Ungültige Gesamtmaße.", err_layout_nr_taken: "Die Nummer {d} ist schon vergeben.",
    // compartment settings
    comp_settings: "Einstellungen Terrarium {label}", general: "Allgemein", animal: "Tier / Art", look: "Aussehen im Modell",
    substrate: "Bodengrund", decor: "Einrichtung", background: "Rückwand",
    s_soil: "Erde", s_sand: "Sand", s_bark: "Rinde", s_moss: "Moos", s_gravel: "Kies", s_water: "Wasserteil", s_none: "Keiner",
    d_plants: "Pflanzen", d_stones: "Steine", d_branches: "Äste", d_mixed: "Gemischt", d_none: "Leer",
    b_rock: "Fels", b_cork: "Kork", b_plain: "Schlicht", b_jungle: "Dschungel",
    temp_sensors: "Temperatursensoren", hum_sensors: "Feuchtigkeitssensoren", sensors_hint: "Mehrere Sensoren = Mittelwert.",
    add_sensor: "Sensor hinzufügen …", min: "Minimum", max: "Maximum", hyst: "Hysterese",
    night_enabled: "Eigene Nachtwerte", night_from: "Nacht von", night_to: "bis", night_hint: "Leere Felder = Tagwerte gelten weiter.",
    notifications: "Push-Meldungen", notify_enabled: "Meldungen senden", targets: "Empfänger", add_target: "Empfänger hinzufügen …",
    delay: "Verzögerung (Min.)", delay_hint: "Erst melden, wenn der Wert so lange außerhalb liegt.", repeat: "Wiederholen (Min., 0 = nie)",
    notify_clear: "Entwarnung senden", notify_offline: "Melden, wenn Sensoren ausfallen", notify_persistent: "Zusätzlich als HA-Benachrichtigung",
    test_notify: "Testmeldung senden", test_sent: "Testmeldung gesendet.", test_failed: "Nicht erreichbar: {d}", no_targets: "Keine Empfänger gewählt.",
    devices_hint: "Geräte, die in der Detailansicht von Hand geschaltet werden können.", add_device: "Gerät hinzufügen", entity: "Entität",
    kind: "Art", k_light: "Licht", k_heat: "Wärme", k_uv: "UV", k_ventilation: "Lüftung", k_rain: "Beregnung", k_fogger: "Nebler", k_pump: "Pumpe", k_other: "Sonstiges",
    planned: "Geplant", planned_hint: "Diese Automationen folgen in einer späteren Version.",
    m_light: "Lichtsteuerung (Zeiten, Sonnenauf-/-untergang)", m_ventilation: "Lüftungssteuerung", m_rain: "Beregnung / Regensimulation",
    model_show: "Modell anzeigen", model_hide: "Nur Liste",
    tab_climate: "Klima & Meldungen", tab_light: "Licht", tab_rain: "Bewässerung", tab_vent: "Lüftung",
    light: "Leuchte", light_auto: "Lichtautomatik", light_hint: "Jede Leuchte hat eigene Profile mit Zeiten. Ein Profil gilt an den gewählten Tagen (und optional nur in einer Saison); mehrere aktive Profile ergänzen sich.",
    light_type: "Lichtquelle", socket: "Steckdose / Entität", auto_this: "Automatik für diese Leuchte", overheat: "Überhitzungsschutz", off_above: "Aus über",
    restrike_hint: "Wiederzündsperre: nach dem Ausschalten frühestens nach {m} min wieder einschalten.", profiles: "Leuchtprofile",
    add_light: "Leuchte hinzufügen", profile_name: "Profilname", season: "Nur in Saison", windows: "Leuchtzeiten", vent_windows: "Dauerbetrieb (von – bis)",
    runs: "Beregnungen", vent_runs: "Intervall-Läufe", from: "von", until: "bis", at: "um", duration_s: "Dauer (Sek.)", add_window: "Zeitraum",
    add_run: "Lauf", add_profile: "Profil hinzufügen", ts_time: "Uhrzeit", ts_sunrise: "Sonnenaufgang", ts_sunset: "Sonnenuntergang", minutes_short: "Min.",
    days: "Mo,Di,Mi,Do,Fr,Sa,So", manual_duration: "Dauer von Hand (Sek.)", max_duration: "Höchstdauer (Sek.)", min_pause: "Mindestpause (Min.)",
    rain_auto: "Bewässerungsautomatik", rain_times: "Beregnungszeiten", hum_rules: "Abhängig von der Luftfeuchtigkeit",
    hum_start: "Beregnen, wenn die Luftfeuchtigkeit unter einen Wert fällt", hum_block: "Nicht beregnen, wenn die Luftfeuchtigkeit über einem Wert liegt",
    hum_rules_hint: "Beide Regeln sind unabhängig voneinander ein- und ausschaltbar. Die Sperre gilt für geplante Beregnungen, nicht für „Jetzt beregnen“.",
    below: "unter", above: "über", min_run: "Mindestlaufzeit (Min.)", vent_auto: "Lüftungsautomatik", vent_times: "Zeiten",
    vent_rules: "Abhängig von Temperatur und Luftfeuchtigkeit", vent_temp: "Einschalten, wenn die Temperatur über einem Wert liegt",
    vent_hum: "Einschalten, wenn die Luftfeuchtigkeit über einem Wert liegt", apply_template: "Vorlage anwenden", apply: "Anwenden",
    save_as_template: "Als Vorlage speichern", template_name: "Name der Vorlage:", template_saved: "Vorlage gespeichert.", template_applied: "Vorlage übernommen – zum Übernehmen speichern.",
    group: "Gruppe", group_banner: "Gruppe „{n}“: gilt gemeinsam für {m}. Änderungen hier gelten für alle Terrarien der Gruppe.",
    light_sources: "Lichtquellen", light_sources_hint: "Die Lichtquellen stehen bei jeder Leuchte zur Auswahl. Eigene können hinzugefügt werden.",
    add_light_type: "Lichtquelle hinzufügen", category: "Art", watt: "Leistung (W)", restrike: "Wiederzündsperre (Min.)", color: "Lichtfarbe im Modell",
    restrike_info: "HID-Lampen brauchen nach dem Ausschalten eine Abkühlzeit, bevor sie wieder zünden. Die Automatik wartet so lange.",
    cat_led: "LED", cat_hid: "HID", cat_pl: "P&L (Pflanzen)", cat_ph: "Power & Heat", cat_night: "Nacht-LED", cat_uv: "UV", cat_other: "Sonstiges",
    templates: "Vorlagen", templates_hint: "Vorlagen für Licht, Bewässerung und Lüftung. Eine Vorlage je Art kann als Standard für neue Terrarien gelten; in den Einstellungen jedes Terrariums lassen sich Vorlagen anwenden.",
    add_template: "Neue Vorlage", default_new: "Standard für neue Terrarien", default_new_short: "Standard",
    groups: "Gruppen", groups_hint: "Terrarien, die gemeinsam geschaltet werden (gemeinsame Beleuchtung, Bewässerung oder Lüftung). Je Art kann ein Terrarium nur in einer Gruppe sein.",
    add_group: "Neue Gruppe", members: "Terrarien", group_settings_hint: "Die gemeinsamen Einstellungen (Leuchten, Zeiten …) bearbeitest du in den Einstellungen eines beliebigen Mitglieds. Eine neue Gruppe übernimmt die Einstellungen des ersten Mitglieds.",
    confirm_delete: "Wirklich löschen?", confirm_delete_group: "Gruppe auflösen? Jedes Terrarium behält eine Kopie der Einstellungen (Steckdosen nur das erste).",
    err_layout_group_members: "Eine Gruppe braucht mindestens 2 Terrarien.", err_layout_type_in_use: "Die Lichtquelle wird noch verwendet.",
    tomorrow: "morgen", auto_on: "Auto", auto_off: "Hand", together_with: "gemeinsam: {m}", no_socket: "keine Steckdose", until_t: "bis", from_t: "ab",
    restrike_short: "Sperre bis", overheat_short: "Überhitzung", manual_only: "nur von Hand", rain_stop: "Stopp", rain_now: "Jetzt beregnen",
    state: "Zustand", rain_running: "läuft bis {t}", next_run: "Nächste", last_run: "Zuletzt", note: "Hinweis", rain_blocked: "gesperrt – Luftfeuchte zu hoch",
    ventilation: "Lüfter", next_change: "Wechsel", log: "Schaltprotokoll", skipped: "übersprungen", p_day: "Tag",
    db_ok: "Datenbank verbunden", db_local: "Nur lokal gespeichert", db_error: "Datenbank-Fehler – lokal gesichert",
    on: "An", off: "Aus", unavailable: "nicht verfügbar", required_num: "Bitte eine Zahl eingeben.",
  },
  en: {
    title: "Terrariums", enclosure: "Enclosure", new_enclosure: "New enclosure", add_enclosure: "Add enclosure",
    empty: "No terrarium enclosure yet.", empty_hint: "Create an enclosure with total width and height and split it into single terrariums – side by side, stacked, any size.",
    no_rights: "Only administrators can add enclosures.",
    back: "Back", settings: "Settings", edit: "Edit", save: "Save", cancel: "Cancel", delete: "Delete",
    saved: "Saved", saving: "Saving …",
    status_ok: "OK", status_pending: "Deviation", status_alarm: "Alarm", status_offline: "No data", status_not_configured: "Not configured",
    p_temp_low: "too cold", p_temp_high: "too warm", p_hum_low: "too dry", p_hum_high: "too humid", p_offline: "sensor delivers no values",
    temperature: "Temperature", humidity: "Humidity", day: "Day", night: "Night", day_values: "Day values", night_values: "Night values",
    target: "Target", since: "since", last24: "Last 24 hours", sensors: "Sensors", devices: "Devices", no_devices: "No devices assigned – add them in the settings.",
    problems: "Notices", all_good: "Everything in range.", not_configured_hint: "No sensors selected yet – choose them in the settings.",
    enc_edit: "Edit enclosure", enc_new: "New enclosure", number: "Number", name: "Name", width: "Width", height: "Height", depth: "Depth",
    color: "Cabinet", c_wood: "Wood", c_black: "Black", c_white: "White", c_grey: "Grey",
    size_total: "Overall size (cm)", layout: "Layout", add_comp: "Add terrarium", grid: "Create grid", rows: "Rows", cols: "Columns", gap: "Gap",
    snap: "Snap", compartments: "Terrariums", selected: "Selected terrarium", remove: "Remove", pos_x: "Left (X)", pos_y: "Top (Y)",
    none_selected: "Tap a terrarium in the drawing to move or edit it. Drag = move, bottom right corner = resize.",
    numbering_hint: "Numbered automatically top to bottom, left to right.",
    confirm_grid: "Replace the current layout with a grid?", confirm_delete_enc: "Delete enclosure {nr} with all terrariums and settings?",
    no_space: "No free space left – make a terrarium smaller first.",
    err_layout_overlap: "Terrariums overlap: {d}", err_layout_out_of_bounds: "Terrarium exceeds the enclosure: {d}",
    err_layout_comp_size: "Invalid size: {d}", err_layout_size: "Invalid overall size.", err_layout_nr_taken: "Number {d} is already used.",
    comp_settings: "Settings terrarium {label}", general: "General", animal: "Animal / species", look: "Look in the model",
    substrate: "Substrate", decor: "Decoration", background: "Back wall",
    s_soil: "Soil", s_sand: "Sand", s_bark: "Bark", s_moss: "Moss", s_gravel: "Gravel", s_water: "Water part", s_none: "None",
    d_plants: "Plants", d_stones: "Stones", d_branches: "Branches", d_mixed: "Mixed", d_none: "Empty",
    b_rock: "Rock", b_cork: "Cork", b_plain: "Plain", b_jungle: "Jungle",
    temp_sensors: "Temperature sensors", hum_sensors: "Humidity sensors", sensors_hint: "Several sensors = average.",
    add_sensor: "Add sensor …", min: "Minimum", max: "Maximum", hyst: "Hysteresis",
    night_enabled: "Own night values", night_from: "Night from", night_to: "until", night_hint: "Empty fields = day values apply.",
    notifications: "Push notifications", notify_enabled: "Send notifications", targets: "Recipients", add_target: "Add recipient …",
    delay: "Delay (min)", delay_hint: "Only notify when the value stays out of range this long.", repeat: "Repeat (min, 0 = never)",
    notify_clear: "Send all-clear", notify_offline: "Notify when sensors fail", notify_persistent: "Also as HA notification",
    test_notify: "Send test message", test_sent: "Test message sent.", test_failed: "Not reachable: {d}", no_targets: "No recipients selected.",
    devices_hint: "Devices that can be switched by hand in the detail view.", add_device: "Add device", entity: "Entity",
    kind: "Kind", k_light: "Light", k_heat: "Heat", k_uv: "UV", k_ventilation: "Ventilation", k_rain: "Rain", k_fogger: "Fogger", k_pump: "Pump", k_other: "Other",
    planned: "Planned", planned_hint: "These automations follow in a later version.",
    m_light: "Light control (times, sunrise/sunset)", m_ventilation: "Ventilation control", m_rain: "Rain simulation",
    model_show: "Show model", model_hide: "List only",
    tab_climate: "Climate & notifications", tab_light: "Light", tab_rain: "Rain", tab_vent: "Ventilation",
    light: "Light", light_auto: "Light automation", light_hint: "Every light has its own profiles with times. A profile applies on the chosen days (and optionally only in a season); several active profiles add up.",
    light_type: "Light source", socket: "Socket / entity", auto_this: "Automation for this light", overheat: "Overheat protection", off_above: "Off above",
    restrike_hint: "Restrike lock: after switching off, switch on again after {m} min at the earliest.", profiles: "Light profiles",
    add_light: "Add light", profile_name: "Profile name", season: "Only in season", windows: "Light times", vent_windows: "Continuous (from – until)",
    runs: "Rain runs", vent_runs: "Interval runs", from: "from", until: "until", at: "at", duration_s: "Duration (s)", add_window: "Period",
    add_run: "Run", add_profile: "Add profile", ts_time: "Time", ts_sunrise: "Sunrise", ts_sunset: "Sunset", minutes_short: "min",
    days: "Mo,Tu,We,Th,Fr,Sa,Su", manual_duration: "Duration by hand (s)", max_duration: "Maximum duration (s)", min_pause: "Minimum pause (min)",
    rain_auto: "Rain automation", rain_times: "Rain times", hum_rules: "Depending on humidity",
    hum_start: "Rain when the humidity falls below a value", hum_block: "Do not rain when the humidity is above a value",
    hum_rules_hint: "Both rules can be switched on and off independently. The block applies to scheduled runs, not to “Rain now”.",
    below: "below", above: "above", min_run: "Minimum run time (min)", vent_auto: "Ventilation automation", vent_times: "Times",
    vent_rules: "Depending on temperature and humidity", vent_temp: "Switch on when the temperature is above a value",
    vent_hum: "Switch on when the humidity is above a value", apply_template: "Apply template", apply: "Apply",
    save_as_template: "Save as template", template_name: "Template name:", template_saved: "Template saved.", template_applied: "Template applied – save to keep it.",
    group: "Group", group_banner: "Group “{n}”: shared by {m}. Changes here apply to all terrariums of the group.",
    light_sources: "Light sources", light_sources_hint: "The light sources can be chosen for every light. You can add your own.",
    add_light_type: "Add light source", category: "Kind", watt: "Power (W)", restrike: "Restrike lock (min)", color: "Light colour in the model",
    restrike_info: "HID lamps need to cool down after switching off before they ignite again. The automation waits that long.",
    cat_led: "LED", cat_hid: "HID", cat_pl: "P&L (plants)", cat_ph: "Power & Heat", cat_night: "Night LED", cat_uv: "UV", cat_other: "Other",
    templates: "Templates", templates_hint: "Templates for light, rain and ventilation. One template per kind can be the default for new terrariums; templates can be applied in the settings of every terrarium.",
    add_template: "New template", default_new: "Default for new terrariums", default_new_short: "Default",
    groups: "Groups", groups_hint: "Terrariums switched together (shared lighting, rain or ventilation). Per kind a terrarium can be in one group only.",
    add_group: "New group", members: "Terrariums", group_settings_hint: "The shared settings (lights, times …) are edited in the settings of any member. A new group takes the settings of its first member.",
    confirm_delete: "Really delete?", confirm_delete_group: "Dissolve the group? Every terrarium keeps a copy of the settings (sockets only the first one).",
    err_layout_group_members: "A group needs at least 2 terrariums.", err_layout_type_in_use: "The light source is still in use.",
    tomorrow: "tomorrow", auto_on: "Auto", auto_off: "Manual", together_with: "shared: {m}", no_socket: "no socket", until_t: "until", from_t: "from",
    restrike_short: "Locked until", overheat_short: "overheating", manual_only: "by hand only", rain_stop: "Stop", rain_now: "Rain now",
    state: "State", rain_running: "running until {t}", next_run: "Next", last_run: "Last", note: "Note", rain_blocked: "blocked – humidity too high",
    ventilation: "Fan", next_change: "change", log: "Switching log", skipped: "skipped", p_day: "Day",
    db_ok: "Database connected", db_local: "Stored locally only", db_error: "Database error – saved locally",
    on: "On", off: "Off", unavailable: "unavailable", required_num: "Please enter a number.",
  },
};

const STATUS_COLOR = { ok: "#43a047", pending: "#f9a825", alarm: "#e53935", offline: "#8c919a", not_configured: "#6b7280" };
const CABINET = {
  wood: ["#9a6a3f", "#6f4627", "#b47d4c"], black: ["#2c2d31", "#17181a", "#45474c"],
  white: ["#ecebe7", "#c9c5bd", "#ffffff"], grey: ["#80858b", "#5c6066", "#9da2a8"],
};
const SUBSTRATE = { soil: "#5b3d27", sand: "#d6b57a", bark: "#7b4a27", moss: "#4c7a33", gravel: "#9b968d", water: "#3b7ea8", none: null };
const BACKDROP = { rock: ["#7a736a", "#4d4842"], cork: ["#a2714a", "#6b4529"], plain: ["#3d434a", "#2a2e33"], jungle: ["#2f5d38", "#1b3a22"] };
const KIND_ICON = {
  light: "mdi:lightbulb", heat: "mdi:radiator", uv: "mdi:white-balance-sunny", ventilation: "mdi:fan",
  rain: "mdi:weather-pouring", fogger: "mdi:weather-fog", pump: "mdi:pump", other: "mdi:power-plug",
};
const DEVICE_KINDS = Object.keys(KIND_ICON);

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = (v) => (v === null || v === undefined || v === "" || isNaN(Number(v)) ? null : Number(v));
const fmt = (v, d = 1) => (v === null || v === undefined ? "–" : Number(v).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d }));
const clone = (o) => JSON.parse(JSON.stringify(o));
const isOn = (s) => ["on", "open", "heat", "cool", "auto", "heat_cool", "dry", "fan_only", "playing"].includes(s);
let UID = 0;

function rng(seedStr) {
  let h = 2166136261;
  for (const ch of String(seedStr)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); }
  return () => { h = Math.imul(h ^ (h >>> 15), 2246822507); h = Math.imul(h ^ (h >>> 13), 3266489909); h ^= h >>> 16; return (h >>> 0) / 4294967296; };
}

function sortComps(comps) {
  return [...comps].sort((a, b) => (Math.round(a.y * 10) - Math.round(b.y * 10)) || (Math.round(a.x * 10) - Math.round(b.x * 10)));
}

function overlaps(a, b) {
  const e = 0.01;
  return a.x < b.x + b.width - e && b.x < a.x + a.width - e && a.y < b.y + b.height - e && b.y < a.y + a.height - e;
}

/* ------------------------------------------------------------------ model drawing */
function compartmentArt(comp, w, h, uid, opts) {
  const r = rng(comp.id || comp.label || "x");
  const look = comp.look || {};
  const bd = BACKDROP[look.background] || BACKDROP.rock;
  const sub = SUBSTRATE[look.substrate] === undefined ? SUBSTRATE.soil : SUBSTRATE[look.substrate];
  const s = Math.min(w, h);
  const devs = [...((comp.live && comp.live.devices) || [])];
  const A = comp.auto || {};
  for (const l of (A.light?.lights || [])) devs.push({ kind: l.category === "night" ? "night" : l.category === "ph" ? "heat" : "light", state: l.state, color: l.color });
  if (A.rain?.running_until) devs.push({ kind: "rain", state: "on" });
  const nightOn = devs.some((d) => d.kind === "night" && isOn(d.state));
  const lightOn = devs.some((d) => ["light", "uv"].includes(d.kind) && isOn(d.state));
  const heatOn = devs.some((d) => d.kind === "heat" && isOn(d.state));
  const rainOn = devs.some((d) => ["rain", "fogger"].includes(d.kind) && isOn(d.state));
  const subH = sub ? h * 0.17 : 0;
  const ground = h - subH;
  let out = `<rect width="${w}" height="${h}" fill="url(#bd${uid}_${esc(look.background || "rock")})"/>`;
  // back wall texture
  const blobs = look.background === "plain" ? 0 : 7;
  for (let i = 0; i < blobs; i++) {
    const cx = r() * w, cy = r() * ground, rx = s * (0.08 + r() * 0.16), ry = rx * (0.5 + r() * 0.4);
    out += `<ellipse cx="${cx.toFixed(2)}" cy="${cy.toFixed(2)}" rx="${rx.toFixed(2)}" ry="${ry.toFixed(2)}" fill="${bd[1]}" opacity="${(0.25 + r() * 0.3).toFixed(2)}"/>`;
  }
  if (look.background === "jungle") {
    for (let i = 0; i < 5; i++) {
      const x = r() * w;
      out += `<path d="M${x.toFixed(2)} 0 q ${(s * 0.05).toFixed(2)} ${(h * 0.25).toFixed(2)} ${(-s * 0.02).toFixed(2)} ${(h * (0.35 + r() * 0.3)).toFixed(2)}" stroke="#3f7a3c" stroke-width="${(s * 0.012).toFixed(2)}" fill="none" opacity=".7"/>`;
    }
  }
  if (nightOn && !lightOn) out += `<rect width="${w}" height="${h}" fill="#0b1a3a" opacity=".45"/><rect width="${w}" height="${h}" fill="url(#ng${uid})"/>`;
  if (lightOn) out += `<rect width="${w}" height="${h}" fill="url(#lg${uid})"/>`;
  if (heatOn) out += `<ellipse cx="${(w * 0.75).toFixed(2)}" cy="0" rx="${(s * 0.35).toFixed(2)}" ry="${(s * 0.35).toFixed(2)}" fill="url(#ht${uid})"/>`;
  // decor
  const decor = look.decor || "plants";
  const plants = decor === "plants" || decor === "mixed";
  const stones = decor === "stones" || decor === "mixed";
  const branches = decor === "branches" || decor === "mixed";
  if (branches) {
    const y1 = ground - h * (0.05 + r() * 0.1), y2 = h * (0.25 + r() * 0.2);
    out += `<path d="M${(w * 0.05).toFixed(2)} ${y1.toFixed(2)} Q ${(w * 0.45).toFixed(2)} ${(y2 + h * 0.15).toFixed(2)} ${(w * 0.92).toFixed(2)} ${y2.toFixed(2)}" stroke="#5a3a22" stroke-width="${(s * 0.05).toFixed(2)}" stroke-linecap="round" fill="none"/>`;
    out += `<path d="M${(w * 0.55).toFixed(2)} ${(y2 + h * 0.08).toFixed(2)} l ${(w * 0.08).toFixed(2)} ${(-h * 0.14).toFixed(2)}" stroke="#5a3a22" stroke-width="${(s * 0.025).toFixed(2)}" stroke-linecap="round"/>`;
  }
  if (plants) {
    const n = Math.max(2, Math.round(w / s * 2.5));
    for (let i = 0; i < n; i++) {
      const x = (i + 0.3 + r() * 0.4) * (w / n);
      const ph = h * (0.25 + r() * 0.35);
      const lean = (r() - 0.5) * s * 0.25;
      const green = ["#4f9a3c", "#3d8a34", "#6bb04a", "#2f7a3a"][Math.floor(r() * 4)];
      out += `<path d="M${x.toFixed(2)} ${ground.toFixed(2)} q ${(lean * 0.4).toFixed(2)} ${(-ph * 0.5).toFixed(2)} ${lean.toFixed(2)} ${(-ph).toFixed(2)}" stroke="${green}" stroke-width="${(s * 0.012).toFixed(2)}" fill="none"/>`;
      const leaves = 3 + Math.floor(r() * 3);
      for (let j = 1; j <= leaves; j++) {
        const t = j / (leaves + 0.5);
        const lx = x + lean * t * t, ly = ground - ph * t;
        const side = j % 2 ? 1 : -1;
        const lr = s * (0.05 + r() * 0.04);
        out += `<ellipse cx="${(lx + side * lr * 0.8).toFixed(2)}" cy="${ly.toFixed(2)}" rx="${lr.toFixed(2)}" ry="${(lr * 0.42).toFixed(2)}" fill="${green}" transform="rotate(${side * -25} ${lx.toFixed(2)} ${ly.toFixed(2)})"/>`;
      }
    }
  }
  if (stones) {
    const n = 2 + Math.floor(r() * 3);
    for (let i = 0; i < n; i++) {
      const rx = s * (0.08 + r() * 0.1), x = r() * w;
      out += `<ellipse cx="${x.toFixed(2)}" cy="${(ground + subH * 0.1).toFixed(2)}" rx="${rx.toFixed(2)}" ry="${(rx * 0.6).toFixed(2)}" fill="${["#8d8a84", "#6f6c67", "#a39f97"][i % 3]}"/>`;
    }
  }
  // substrate
  if (sub) {
    let d = `M0 ${ground.toFixed(2)}`;
    const steps = 6;
    for (let i = 1; i <= steps; i++) {
      d += ` Q ${((i - 0.5) * w / steps).toFixed(2)} ${(ground - subH * (0.15 + r() * 0.35)).toFixed(2)} ${(i * w / steps).toFixed(2)} ${ground.toFixed(2)}`;
    }
    d += ` L ${w} ${h} L 0 ${h} Z`;
    out += `<path d="${d}" fill="${sub}"/>`;
    if (look.substrate === "water") out += `<rect y="${ground.toFixed(2)}" width="${w}" height="${(subH * 0.12).toFixed(2)}" fill="#9fd3f2" opacity=".55"/>`;
    for (let i = 0; i < 14; i++) out += `<circle cx="${(r() * w).toFixed(2)}" cy="${(ground + subH * (0.3 + r() * 0.6)).toFixed(2)}" r="${(s * 0.008).toFixed(2)}" fill="#000" opacity=".18"/>`;
  }
  if (rainOn) {
    for (let i = 0; i < 18; i++) {
      const x = r() * w, y = r() * ground * 0.85;
      out += `<line x1="${x.toFixed(2)}" y1="${y.toFixed(2)}" x2="${(x - s * 0.015).toFixed(2)}" y2="${(y + s * 0.07).toFixed(2)}" stroke="#bfe3ff" stroke-width="${(s * 0.008).toFixed(2)}" opacity=".8"/>`;
    }
  }
  // ventilation grille on top
  const vh = Math.min(h * 0.06, 3);
  out += `<rect width="${w}" height="${vh}" fill="#1d1f22" opacity=".85"/>`;
  for (let x = vh; x < w - vh; x += vh * 0.9) out += `<line x1="${x.toFixed(2)}" y1="${(vh * 0.25).toFixed(2)}" x2="${x.toFixed(2)}" y2="${(vh * 0.75).toFixed(2)}" stroke="#555a60" stroke-width="${(vh * 0.18).toFixed(2)}"/>`;
  // glass + doors
  out += `<rect width="${w}" height="${h}" fill="url(#gl${uid})"/>`;
  out += `<path d="M${(w * 0.08).toFixed(2)} ${h.toFixed(2)} L ${(w * 0.32).toFixed(2)} 0 L ${(w * 0.38).toFixed(2)} 0 L ${(w * 0.14).toFixed(2)} ${h.toFixed(2)} Z" fill="#fff" opacity=".06"/>`;
  if (w > h * 0.55) {
    const handleH = Math.min(h * 0.18, 8), hw = Math.max(s * 0.012, 0.4);
    out += `<line x1="${w / 2}" y1="${vh}" x2="${w / 2}" y2="${h}" stroke="#c9d2da" stroke-width="${(s * 0.008).toFixed(2)}" opacity=".55"/>`;
    out += `<rect x="${(w / 2 - hw * 3).toFixed(2)}" y="${(h / 2 - handleH / 2).toFixed(2)}" width="${hw}" height="${handleH.toFixed(2)}" rx="${hw / 2}" fill="#d7dde2" opacity=".75"/>`;
    out += `<rect x="${(w / 2 + hw * 2).toFixed(2)}" y="${(h / 2 - handleH / 2).toFixed(2)}" width="${hw}" height="${handleH.toFixed(2)}" rx="${hw / 2}" fill="#d7dde2" opacity=".75"/>`;
  }
  return out;
}

function svgDefs(uid, color) {
  const cab = CABINET[color] || CABINET.wood;
  let defs = `<linearGradient id="cab${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${cab[2]}"/><stop offset=".55" stop-color="${cab[0]}"/><stop offset="1" stop-color="${cab[1]}"/></linearGradient>`;
  defs += `<linearGradient id="gl${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".45" stop-color="#fff" stop-opacity=".03"/><stop offset="1" stop-color="#fff" stop-opacity=".1"/></linearGradient>`;
  defs += `<radialGradient id="lg${uid}" cx=".5" cy="0" r=".9"><stop offset="0" stop-color="#fff3c4" stop-opacity=".55"/><stop offset="1" stop-color="#fff3c4" stop-opacity="0"/></radialGradient>`;
  defs += `<radialGradient id="ng${uid}" cx=".5" cy="0" r=".9"><stop offset="0" stop-color="#7fa8ff" stop-opacity=".45"/><stop offset="1" stop-color="#7fa8ff" stop-opacity="0"/></radialGradient>`;
  defs += `<radialGradient id="ht${uid}"><stop offset="0" stop-color="#ff8a3d" stop-opacity=".55"/><stop offset="1" stop-color="#ff8a3d" stop-opacity="0"/></radialGradient>`;
  for (const [k, c] of Object.entries(BACKDROP)) defs += `<linearGradient id="bd${uid}_${k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c[0]}"/><stop offset="1" stop-color="${c[1]}"/></linearGradient>`;
  return defs;
}

/** Front view of a whole enclosure. opts: {highlight, values, labels, onlyComp} */
function enclosureSVG(enc, opts = {}) {
  const uid = `t${++UID}`;
  let comps = enc.compartments || [];
  let W = enc.width, H = enc.height, ox = 0, oy = 0;
  if (opts.onlyComp) { // close-up of a single compartment
    const c = opts.onlyComp; comps = [c]; W = c.width; H = c.height; ox = c.x; oy = c.y;
  }
  const f = Math.max(W, H) * 0.035, base = opts.onlyComp ? f : f * 1.6;
  const VW = W + 2 * f, VH = H + 2 * f + base;
  let body = `<defs>${svgDefs(uid, enc.color)}<filter id="sh${uid}" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="${(f * 0.4).toFixed(2)}" stdDeviation="${(f * 0.5).toFixed(2)}" flood-opacity=".45"/></filter></defs>`;
  body += `<rect x="0" y="0" width="${VW}" height="${H + 2 * f}" rx="${(f * 0.6).toFixed(2)}" fill="url(#cab${uid})" filter="url(#sh${uid})"/>`;
  if (!opts.onlyComp) {
    body += `<rect x="${(f * 0.6).toFixed(2)}" y="${(H + 2 * f).toFixed(2)}" width="${(VW - f * 1.2).toFixed(2)}" height="${(base * 0.55).toFixed(2)}" fill="url(#cab${uid})" opacity=".85"/>`;
    body += `<rect x="${(f * 0.9).toFixed(2)}" y="${(H + 2 * f + base * 0.55).toFixed(2)}" width="${(f * 1.4).toFixed(2)}" height="${(base * 0.45).toFixed(2)}" fill="#111" opacity=".6"/>`;
    body += `<rect x="${(VW - f * 2.3).toFixed(2)}" y="${(H + 2 * f + base * 0.55).toFixed(2)}" width="${(f * 1.4).toFixed(2)}" height="${(base * 0.45).toFixed(2)}" fill="#111" opacity=".6"/>`;
  }
  for (const c of comps) {
    const x = f + c.x - ox, y = f + c.y - oy, w = c.width, h = c.height;
    const st = (c.live && c.live.status) || "not_configured";
    const dim = opts.highlight && opts.highlight !== c.id;
    const s = Math.min(w, h);
    body += `<g transform="translate(${x.toFixed(2)} ${y.toFixed(2)})" class="comp${dim ? " dim" : ""}" data-act="open" data-comp="${esc(c.id)}">`;
    body += `<clipPath id="cl${uid}_${esc(c.id)}"><rect width="${w}" height="${h}" rx="${(f * 0.15).toFixed(2)}"/></clipPath>`;
    body += `<g clip-path="url(#cl${uid}_${esc(c.id)})">${compartmentArt(c, w, h, uid, opts)}</g>`;
    const sw = Math.max(f * 0.22, s * 0.012);
    body += `<rect x="${(sw / 2).toFixed(2)}" y="${(sw / 2).toFixed(2)}" width="${(w - sw).toFixed(2)}" height="${(h - sw).toFixed(2)}" rx="${(f * 0.15).toFixed(2)}" fill="none" stroke="${STATUS_COLOR[st]}" stroke-width="${sw.toFixed(2)}" opacity="${st === "ok" ? 0.75 : 1}" ${st === "alarm" ? 'class="blink"' : ""}/>`;
    if (opts.highlight === c.id) body += `<rect x="${(-sw).toFixed(2)}" y="${(-sw).toFixed(2)}" width="${(w + 2 * sw).toFixed(2)}" height="${(h + 2 * sw).toFixed(2)}" rx="${(f * 0.25).toFixed(2)}" fill="none" stroke="var(--primary-color,#03a9f4)" stroke-width="${(sw * 1.3).toFixed(2)}"/>`;
    if (opts.labels !== false) {
      const fs = Math.max(Math.min(s * 0.14, Math.max(W, H) * 0.045), 1.5);
      const lab = c.label || "";
      const bw = fs * (0.75 + lab.length * 0.62);
      body += `<rect x="${(fs * 0.4).toFixed(2)}" y="${(fs * 0.6).toFixed(2)}" width="${bw.toFixed(2)}" height="${(fs * 1.35).toFixed(2)}" rx="${(fs * 0.3).toFixed(2)}" fill="rgba(0,0,0,.6)"/>`;
      body += `<text x="${(fs * 0.4 + bw / 2).toFixed(2)}" y="${(fs * 1.62).toFixed(2)}" font-size="${fs.toFixed(2)}" font-weight="700" fill="#fff" text-anchor="middle">${esc(lab)}</text>`;
      if (opts.values !== false && c.live && (c.live.temperature !== null && c.live.temperature !== undefined || c.live.humidity !== null && c.live.humidity !== undefined)) {
        const vfs = fs * 0.95;
        const parts = [];
        if (c.live.temperature !== null && c.live.temperature !== undefined) parts.push(`${fmt(c.live.temperature)}°`);
        if (c.live.humidity !== null && c.live.humidity !== undefined) parts.push(`${fmt(c.live.humidity, 0)}%`);
        const txt = parts.join("  ");
        const tw = vfs * (0.6 + txt.length * 0.56);
        const ty = h - vfs * 0.6;
        body += `<rect x="${(w / 2 - tw / 2).toFixed(2)}" y="${(ty - vfs * 1.1).toFixed(2)}" width="${tw.toFixed(2)}" height="${(vfs * 1.45).toFixed(2)}" rx="${(vfs * 0.35).toFixed(2)}" fill="rgba(0,0,0,.6)"/>`;
        body += `<text x="${(w / 2).toFixed(2)}" y="${(ty - vfs * 0.05).toFixed(2)}" font-size="${vfs.toFixed(2)}" font-weight="600" fill="#fff" text-anchor="middle">${esc(txt)}</text>`;
      }
    }
    body += `</g>`;
  }
  return `<svg class="model" viewBox="0 0 ${VW.toFixed(2)} ${VH.toFixed(2)}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">${body}</svg>`;
}

/* ------------------------------------------------------------------ gauges & charts */
function arc(cx, cy, r, a0, a1) {
  const p = (a) => [cx + r * Math.cos(a), cy - r * Math.sin(a)];
  const [x0, y0] = p(a0), [x1, y1] = p(a1);
  const large = Math.abs(a1 - a0) > Math.PI ? 1 : 0;
  return `M${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${large} ${a0 > a1 ? 1 : 0} ${x1.toFixed(2)} ${y1.toFixed(2)}`;
}

function gaugeSVG(value, lo, hi, rmin, rmax, unit, color, dec) {
  const ang = (v) => Math.PI * (1 - (Math.min(Math.max(v, rmin), rmax) - rmin) / (rmax - rmin));
  let s = `<svg class="gauge" viewBox="0 0 120 74" xmlns="http://www.w3.org/2000/svg">`;
  s += `<path d="${arc(60, 62, 48, Math.PI, 0)}" stroke="var(--divider-color,#3a3f45)" stroke-width="10" fill="none" stroke-linecap="round"/>`;
  if (lo !== null || hi !== null) {
    const a0 = ang(lo !== null ? lo : rmin), a1 = ang(hi !== null ? hi : rmax);
    s += `<path d="${arc(60, 62, 48, a0, a1)}" stroke="#43a047" stroke-opacity=".55" stroke-width="10" fill="none"/>`;
  }
  if (value !== null && value !== undefined) {
    const a = ang(value);
    s += `<circle cx="${(60 + 48 * Math.cos(a)).toFixed(2)}" cy="${(62 - 48 * Math.sin(a)).toFixed(2)}" r="7" fill="${color}" stroke="var(--card-background-color,#1c1c1c)" stroke-width="2.5"/>`;
  }
  s += `<text x="60" y="56" text-anchor="middle" font-size="19" font-weight="700" fill="var(--primary-text-color,#e1e1e1)">${value === null || value === undefined ? "–" : fmt(value, dec)}<tspan font-size="11" font-weight="500" dx="1">${unit}</tspan></text>`;
  s += `<text x="12" y="73" font-size="8" fill="var(--secondary-text-color,#9aa0a6)" text-anchor="middle">${rmin}</text><text x="108" y="73" font-size="8" fill="var(--secondary-text-color,#9aa0a6)" text-anchor="middle">${rmax}</text>`;
  return s + `</svg>`;
}

function chartSVG(points, lo, hi, unit, color, startMs, endMs) {
  const W = 560, H = 120, pl = 32, pr = 8, pt = 6, pb = 16;
  if (!points || points.length < 2) {
    return `<svg class="chart" viewBox="0 0 ${W} ${H}"><text x="${W / 2}" y="${H / 2}" text-anchor="middle" font-size="10" fill="var(--secondary-text-color,#9aa0a6)">–</text></svg>`;
  }
  let vmin = Math.min(...points.map((p) => p.v)), vmax = Math.max(...points.map((p) => p.v));
  if (lo !== null) vmin = Math.min(vmin, lo); if (hi !== null) vmax = Math.max(vmax, hi);
  const pad = Math.max((vmax - vmin) * 0.12, 0.5); vmin -= pad; vmax += pad;
  const X = (t) => pl + (t - startMs) / (endMs - startMs) * (W - pl - pr);
  const Y = (v) => pt + (1 - (v - vmin) / (vmax - vmin)) * (H - pt - pb);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
  if (lo !== null || hi !== null) {
    const y0 = Y(hi !== null ? hi : vmax), y1 = Y(lo !== null ? lo : vmin);
    s += `<rect x="${pl}" y="${y0.toFixed(1)}" width="${W - pl - pr}" height="${(y1 - y0).toFixed(1)}" fill="#43a047" opacity=".14"/>`;
  }
  for (const v of [vmin + pad, vmax - pad]) s += `<text x="${pl - 4}" y="${(Y(v) + 3).toFixed(1)}" font-size="8.5" text-anchor="end" fill="var(--secondary-text-color,#9aa0a6)">${fmt(v, unit === "%" ? 0 : 1)}</text>`;
  const hrs = [-24, -18, -12, -6, 0];
  for (const hr of hrs) {
    const x = X(endMs + hr * 3600000);
    s += `<line x1="${x.toFixed(1)}" y1="${pt}" x2="${x.toFixed(1)}" y2="${H - pb}" stroke="var(--divider-color,#3a3f45)" stroke-width=".5"/>`;
    s += `<text x="${x.toFixed(1)}" y="${H - 4}" font-size="8.5" text-anchor="middle" fill="var(--secondary-text-color,#9aa0a6)">${hr === 0 ? "0" : hr + "h"}</text>`;
  }
  let d = "";
  points.forEach((p, i) => { d += `${i ? "L" : "M"}${X(p.t).toFixed(1)} ${Y(p.v).toFixed(1)} `; });
  d += `L${X(endMs).toFixed(1)} ${Y(points[points.length - 1].v).toFixed(1)}`;
  s += `<path d="${d}" fill="none" stroke="${color}" stroke-width="1.6" stroke-linejoin="round"/>`;
  return s + `</svg>`;
}

/* ------------------------------------------------------------------ styles */
const STYLE = `
:host { display:block; --tc-gap:12px; --tc-muted: var(--secondary-text-color, #9aa0a6); -webkit-tap-highlight-color: transparent; }
* { box-sizing: border-box; }
.wrap { container-type: inline-size; padding: 12px; color: var(--primary-text-color, #e1e1e1); font-family: var(--paper-font-body1_-_font-family, inherit); }
.panel .wrap { padding: 16px; max-width: 1600px; margin: 0 auto; }
h2 { font-size: 1.25rem; margin: 0; font-weight: 600; }
h3 { font-size: 1rem; margin: 0 0 8px; font-weight: 600; }
.muted { color: var(--tc-muted); }
.small { font-size: .85rem; }
.row { display:flex; align-items:center; gap:8px; }
.spacer { flex:1; }
.head .hd { min-width: 0; flex: 0 1 auto; }
.head { display:flex; align-items:center; gap:10px; margin-bottom: 12px; flex-wrap: wrap; }
button.b { font: inherit; cursor:pointer; border:1px solid var(--divider-color, #3a3f45); background: var(--secondary-background-color, #2a2d31);
  color: var(--primary-text-color, #e1e1e1); border-radius: 10px; padding: 7px 12px; display:inline-flex; gap:6px; align-items:center; }
button.b:hover { border-color: var(--primary-color, #03a9f4); }
button.b.pri { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); border-color: transparent; }
button.b.warn { color: #ef5350; }
button.b[disabled] { opacity:.5; cursor: default; }
button.ic { background:none; border:none; color: inherit; cursor:pointer; padding:6px; border-radius: 50%; display:inline-flex; }
button.ic:hover { background: rgba(127,127,127,.15); }
ha-icon { --mdc-icon-size: 20px; }
.grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(min(380px, 100%), 1fr)); gap: var(--tc-gap); }
.ell { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.tile { background: var(--card-background-color, #1f2124); border: 1px solid var(--divider-color, #33373c); border-radius: 14px; padding: 12px; display:flex; flex-direction:column; gap:10px; }
.card-mode .tile { background: rgba(127,127,127,.06); }
.tile .th { display:flex; align-items:center; gap:6px; min-width:0; }
.tile .th .tn { flex: 1 1 auto; min-width: 70px; }
.tile .th .ic { flex: none; }
.nr { font-weight:700; background: rgba(127,127,127,.18); border-radius: 8px; padding: 2px 8px; font-variant-numeric: tabular-nums; }
.chip { white-space:nowrap; display:inline-flex; align-items:center; gap:5px; border-radius: 999px; padding: 2px 9px; font-size: .8rem; font-weight:600; color:#fff; }
.model { width:100%; height:auto; display:block; max-height: 420px; }
.model .comp { cursor:pointer; transition: opacity .2s; }
.model .comp.dim { opacity:.35; }
.blink { animation: blink 1.4s infinite; }
@keyframes blink { 50% { opacity:.25; } }
.list { display:flex; flex-direction:column; gap:4px; }
.li { display:grid; grid-template-columns: auto minmax(0,1fr) auto auto auto; gap:6px 10px; align-items:center; padding: 6px 8px; border-radius: 10px; cursor:pointer; }
.qd { grid-column: 2 / -1; display:flex; flex-wrap:wrap; gap:6px; }
.qb { width:40px; height:40px; border-radius: 10px; border:1px solid var(--divider-color, #3a3f45); background: rgba(127,127,127,.08); color: inherit; display:inline-flex; align-items:center; justify-content:center; cursor:pointer; padding:0; }
.qb.on { border-color:#f9a825; background: rgba(249,168,37,.18); color:#f9a825; }
.qb.na { opacity:.4; }
.dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.val { font-variant-numeric: tabular-nums; min-width: 52px; text-align:right; }
.add-tile { align-items:center; justify-content:center; min-height: 200px; cursor:pointer; border-style: dashed; color: var(--tc-muted); }
.empty { text-align:center; padding: 30px 12px; display:flex; flex-direction:column; gap:12px; align-items:center; }
/* details */
.det { display:grid; grid-template-columns: minmax(260px, 1fr) minmax(300px, 1.1fr); gap: var(--tc-gap); }
.det .col { display:flex; flex-direction:column; gap: var(--tc-gap); }
.box { background: var(--card-background-color, #1f2124); border: 1px solid var(--divider-color, #33373c); border-radius: 14px; padding: 12px; }
.card-mode .box { background: rgba(127,127,127,.06); }
.gauges { display:grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.gauge { width:100%; max-width: 230px; display:block; margin: 0 auto; }
.gl { text-align:center; font-size:.85rem; }
.chart { width:100%; height:auto; display:block; }
.devs { display:grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; }
.dev { border:1px solid var(--divider-color, #3a3f45); border-radius: 12px; padding: 10px; cursor:pointer; display:flex; flex-direction:column; gap:4px; background: rgba(127,127,127,.06); }
.dev.on { border-color: #f9a825; background: rgba(249,168,37,.14); }
.dev.busy, .qb.busy { animation: blink .9s infinite; }
.dev .dn { font-weight:600; font-size: .9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.prob { display:flex; align-items:center; gap:8px; padding: 4px 0; }
.locator { max-width: 260px; }
/* forms */
.form { display:flex; flex-direction:column; gap: var(--tc-gap); }
.sec { background: var(--card-background-color, #1f2124); border: 1px solid var(--divider-color, #33373c); border-radius: 14px; padding: 12px 14px; }
.card-mode .sec { background: rgba(127,127,127,.06); }
.fields { display:grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
label.f { display:flex; flex-direction:column; gap:4px; font-size: .8rem; color: var(--tc-muted); }
label.cb { display:flex; align-items:center; gap:8px; font-size:.92rem; cursor:pointer; }
input, select { font: inherit; color: var(--primary-text-color, #e1e1e1); background: var(--input-fill-color, rgba(127,127,127,.12));
  border: 1px solid var(--divider-color, #3a3f45); border-radius: 8px; padding: 7px 9px; width: 100%; min-width: 0; }
input[type=checkbox] { width: 18px; height: 18px; accent-color: var(--primary-color, #03a9f4); }
input:focus, select:focus { outline: 2px solid var(--primary-color, #03a9f4); outline-offset: -1px; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin: 4px 0 8px; }
.ch { display:inline-flex; align-items:center; gap:4px; background: rgba(127,127,127,.16); border-radius: 999px; padding: 3px 4px 3px 10px; font-size: .85rem; }
.ch button { background:none; border:none; color: inherit; cursor:pointer; font-size: 1rem; line-height: 1; padding: 0 4px; }
.ch .v { color: var(--tc-muted); }
.devrow { display:grid; grid-template-columns: 130px 1fr 1fr auto; gap: 8px; align-items:center; margin-bottom: 6px; }
.err { color: #ef5350; font-weight: 600; }
.ok { color: #66bb6a; }
.actions { display:flex; gap:8px; justify-content:flex-end; flex-wrap:wrap; position: sticky; bottom: 0; padding: 10px 0 calc(10px + env(safe-area-inset-bottom, 0px)); background: linear-gradient(transparent, var(--primary-background-color, #111) 35%); }
.card-mode .actions { background: none; position: static; }
.planned { display:flex; flex-direction:column; gap:6px; }
.planned .pl { display:flex; align-items:center; gap:8px; opacity: .7; }
.badge { font-size: .72rem; border:1px solid var(--divider-color,#3a3f45); border-radius: 6px; padding: 1px 6px; color: var(--tc-muted); }
/* layout editor */
.ed { display:grid; grid-template-columns: minmax(260px, 340px) 1fr; gap: var(--tc-gap); }
.edsvg { width:100%; height:auto; max-height: 70vh; display:block; touch-action: none; user-select: none; }
.edsvg .ec { cursor: move; }
.edsvg .eh { cursor: nwse-resize; }
.clist .ci { display:flex; gap:8px; align-items:center; padding: 4px 6px; border-radius: 8px; cursor:pointer; }
.clist .ci.sel { background: rgba(3,169,244,.18); }
.tabs { display:flex; gap:6px; overflow-x:auto; padding: 2px 0 10px; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
.tabs::-webkit-scrollbar { display:none; }
.tab { flex: none; display:inline-flex; align-items:center; gap:6px; font: inherit; color: inherit; background: rgba(127,127,127,.1); border: 1px solid transparent; border-radius: 999px; padding: 7px 12px; cursor:pointer; white-space: nowrap; }
.tab.act { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); }
.sec.inner { background: rgba(127,127,127,.06); margin: 10px 0; }
.sec h3 ha-icon { --mdc-icon-size: 18px; }
button.b.sm { padding: 5px 10px; font-size: .88rem; }
.prof { border:1px solid var(--divider-color, #3a3f45); border-radius: 12px; padding: 10px; margin-bottom: 10px; display:flex; flex-direction:column; gap:6px; }
.prof.off { opacity: .6; }
.ph { display:flex; align-items:center; gap:8px; }
.ph .pn { flex:1; }
.days { display:flex; gap:4px; flex-wrap: wrap; }
.day { font: inherit; font-size: .8rem; min-width: 38px; padding: 6px 4px; border-radius: 8px; border: 1px solid var(--divider-color, #3a3f45); background: none; color: var(--tc-muted); cursor:pointer; }
.day.on { background: rgba(3,169,244,.2); border-color: var(--primary-color, #03a9f4); color: var(--primary-text-color, #e1e1e1); }
.win { display:flex; align-items:flex-end; gap:8px; flex-wrap: wrap; padding: 4px 0; }
.ts { display:grid; grid-template-columns: auto auto; gap:3px 6px; align-items:center; }
.ts > .muted { grid-column: 1 / -1; }
.ts select, .ts input { width:auto; }
.ts .off { display:flex; align-items:center; gap:4px; }
.ts .off input { width: 80px; }
.f.dur input { width: 100px; }
.season input { width: 76px; }
.swatch { width: 14px; height: 14px; border-radius: 50%; display:inline-block; border: 1px solid rgba(0,0,0,.3); flex:none; }
.banner { display:flex; gap:8px; align-items:flex-start; background: rgba(3,169,244,.12); border:1px solid rgba(3,169,244,.4); border-radius: 10px; padding: 8px 10px; margin-bottom: 10px; font-size: .9rem; }
.tplbar { display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin-bottom: 12px; }
.tplbar select { width:auto; max-width: 220px; }
.mlist { display:flex; flex-direction:column; gap:2px; }
.achip { display:inline-flex; align-items:center; gap:4px; font: inherit; font-size:.8rem; border-radius: 999px; padding: 4px 10px; border:1px solid var(--divider-color,#3a3f45); background:none; color: var(--tc-muted); cursor:pointer; }
.achip.on { color: #66bb6a; border-color: rgba(102,187,106,.6); }
.achip ha-icon { --mdc-icon-size: 16px; }
.kv { display:grid; grid-template-columns: auto 1fr; gap: 4px 12px; margin-top: 10px; font-size: .9rem; }
.kv span { color: var(--tc-muted); }
.warnc { color: #f9a825; }
.ev { display:grid; grid-template-columns: 64px 18px 46px 1fr; gap:6px; align-items:center; padding: 2px 0; }
.spin { animation: spin 1.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.adminbar { display:flex; gap:6px; flex-wrap:wrap; align-items:center; }
.dbchip { font-size:.75rem; display:inline-flex; align-items:center; gap:4px; color: var(--tc-muted); }
@media (hover: hover) { .li:hover { background: rgba(127,127,127,.1); } .model .comp:hover { opacity:.92; } .dev:hover, .qb:hover { border-color: var(--primary-color, #03a9f4); } }
/* touch devices (iPhone, iPad): bigger targets, 16px inputs = no zoom on focus */
@media (pointer: coarse) {
  button.b { min-height: 44px; }
  button.ic { min-width: 44px; min-height: 44px; justify-content: center; }
  input, select { font-size: 16px; min-height: 44px; }
  .qb { width: 46px; height: 46px; }
  .li { padding: 10px 8px; }
  .dev { min-height: 76px; }
  label.cb { min-height: 40px; }
  input[type=checkbox] { width: 22px; height: 22px; min-height: 0; }
}
/* layout follows the width of the card/panel, not the screen */
@container (max-width: 860px) {
  .det, .ed { display:flex; flex-direction:column; }
  .det .col, .ed .col { display: contents; }
  .o1{order:1} .o2{order:2} .o3{order:3} .o4{order:4} .o5{order:5} .o6{order:6} .o7{order:7}
  .ed .edbox { order:-1; } .ed .actions { order: 20; }
  .locator { max-width: 240px; }
}
@container (max-width: 520px) {
  .wrap { padding: 8px; }
  .head h2 { font-size: 1.08rem; }
  .head { flex-wrap: nowrap; gap: 6px; }
  .tile, .box, .sec { padding: 10px; border-radius: 12px; }
  .devrow { grid-template-columns: 1fr 1fr; }
  .hide-s { display:none; }
  .li { gap: 6px 8px; }
  .val { min-width: 44px; }
  .gauges { gap: 2px; }
  .devs { grid-template-columns: repeat(auto-fill, minmax(104px, 1fr)); }
  .fields { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
  .tab span { display: none; }
  .tab.act span { display: inline; }
  .ts { flex: 1 1 100%; grid-template-columns: minmax(0,1fr) minmax(0,1fr); }
  .ts select, .ts input { width: 100%; }
  .ev { grid-template-columns: 58px 18px 40px 1fr; }
  .grid { gap: 10px; }
  .add-tile { min-height: 80px; flex-direction: row; }
  .chip { padding: 2px 7px; font-size: .75rem; }
}
`;

/* ------------------------------------------------------------------ main view */
class TerrariumView extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._data = null;
    this._view = { name: "overview" };
    this._hist = {};
    this._targets = null;
    this._msg = "";
    this._busy = {};
    try { this._modelPref = JSON.parse(localStorage.getItem("terrarium-model") || "{}"); } catch (e) { this._modelPref = {}; }
    this._root = this.shadowRoot;
    this._root.addEventListener("click", (e) => this._click(e));
    this._root.addEventListener("input", (e) => this._input(e));
    this._root.addEventListener("change", (e) => this._change(e));
  }

  setConfig(config) { this._config = config || {}; this._initialRoute = false; }
  getCardSize() { return 8; }
  static getStubConfig() { return {}; }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) { this._subscribe(); this._render(); }
  }
  get hass() { return this._hass; }

  connectedCallback() { if (this._hass && !this._unsub) this._subscribe(); }
  disconnectedCallback() {
    if (this._unsub) { this._unsub.then((u) => u && u()).catch(() => {}); this._unsub = null; }
    clearInterval(this._histTimer);
  }

  get lang() { const l = (this._hass && (this._hass.locale?.language || this._hass.language)) || "en"; return TEXTS[l.split("-")[0]] ? l.split("-")[0] : "en"; }
  t(key, vars) { let s = (TEXTS[this.lang][key] ?? TEXTS.en[key] ?? key); if (vars) for (const [k, v] of Object.entries(vars)) s = s.replace(`{${k}}`, v); return s; }
  get admin() { return !!(this._hass && this._hass.user && this._hass.user.is_admin); }
  get isPanel() { return false; }

  _subscribe() {
    if (!this._hass || this._unsub) return;
    this._unsub = this._hass.connection.subscribeMessage((data) => this._onData(data), { type: "terrarium/subscribe" })
      .catch((err) => { this._error = err.message || String(err); this._unsub = null; this._render(); });
  }

  _onData(data) {
    this._data = data;
    // a switched device reported its new state -> stop the "busy" blink
    for (const [ent, prev] of Object.entries(this._busy)) if (this._devState(ent) !== prev) delete this._busy[ent];
    this._error = null;
    if (!this._initialRoute) {
      this._initialRoute = true;
      if (this._config.compartment) {
        const c = this._allComps().find((x) => x.label === String(this._config.compartment));
        if (c) this._view = { name: "details", comp: c.id };
      }
    }
    if (["overview", "details"].includes(this._view.name) || (["ltypes", "tpls", "groups"].includes(this._view.name) && !this._view.draft)) this._render();
  }

  _devState(ent) {
    for (const e of (this._data?.enclosures || [])) for (const c of e.compartments) for (const d of (c.live?.devices || [])) if (d.entity_id === ent) return d.state;
    const s = this._hass && this._hass.states[ent];
    return s ? s.state : null;
  }

  _modelShown(encId) {
    if (encId in this._modelPref) return this._modelPref[encId];
    const w = this.getBoundingClientRect().width || window.innerWidth;
    return w >= 560; // phones: compact list first, model on demand
  }

  _quickButtons(c) {
    const A = c.auto || {};
    const devs = [];
    for (const l of (A.light?.lights || [])) if (l.entity_id) devs.push({ entity_id: l.entity_id, kind: l.category === "night" ? "night" : "light", name: l.name, color: l.color });
    let rain = "";
    if (A.rain?.configured) {
      const running = !!A.rain.running_until, ent = A.rain.entity_id;
      rain = `<button class="qb ${running || isOn(this._devState(ent)) ? "on" : ""} ${this._busy[ent] !== undefined ? "busy" : ""}" data-act="${running ? "rain-stop" : "rain-now"}" data-comp="${esc(c.id)}" data-ent="${esc(ent)}" title="${this.t(running ? "rain_stop" : "rain_now")}" aria-label="${this.t("rain_now")}"><ha-icon icon="mdi:weather-pouring"></ha-icon></button>`;
    }
    if (A.vent?.configured) devs.push({ entity_id: A.vent.entity_id, kind: "ventilation", name: this.t("ventilation") });
    const auto = new Set(devs.map((d) => d.entity_id));
    for (const d of (c.live?.devices || c.devices || [])) if (!auto.has(d.entity_id) && d.entity_id !== A.rain?.entity_id) devs.push(d);
    if (!devs.length && !rain) return "";
    return `<div class="qd">${rain}${devs.map((d) => {
      const st = this._devState(d.entity_id), on = isOn(st), na = st === null || st === "unavailable";
      const s = this._hass.states[d.entity_id];
      const name = d.name || (s && s.attributes.friendly_name) || d.entity_id;
      return `<button class="qb ${on ? "on" : ""} ${na ? "na" : ""} ${this._busy[d.entity_id] !== undefined ? "busy" : ""}" data-act="toggle" data-ent="${esc(d.entity_id)}" title="${esc(name)}: ${on ? this.t("on") : this.t("off")}" aria-label="${esc(name)}"><ha-icon icon="${d.kind === "night" ? "mdi:weather-night" : KIND_ICON[d.kind] || KIND_ICON.other}" ${on && d.color ? `style="color:${esc(d.color)}"` : ""}></ha-icon></button>`;
    }).join("")}</div>`;
  }

  _encs() {
    const encs = (this._data && this._data.enclosures) || [];
    if (this._config.enclosure !== undefined && this._config.enclosure !== null) return encs.filter((e) => String(e.nr) === String(this._config.enclosure));
    return encs;
  }
  _allComps() { return ((this._data && this._data.enclosures) || []).flatMap((e) => e.compartments.map((c) => ({ ...c, _enc: e }))); }
  _find(id) { for (const e of (this._data?.enclosures || [])) for (const c of e.compartments) if (c.id === id) return [e, c]; return [null, null]; }

  /* -------------------------------------------------------- rendering */
  _render() {
    if (!this._hass) return;
    let html;
    if (this._error) html = `<div class="wrap"><p class="err">${esc(this._error)}</p></div>`;
    else if (!this._data) html = `<div class="wrap"><p class="muted">…</p></div>`;
    else {
      switch (this._view.name) {
        case "details": html = this._renderDetails(); break;
        case "comp": html = this._renderCompSettings(); break;
        case "enc": html = this._renderEncEditor(); break;
        case "ltypes": html = this._renderLightTypes(); break;
        case "tpls": html = this._renderTemplates(); break;
        case "tpl": html = this._renderTemplateEdit(); break;
        case "groups": html = this._renderGroups(); break;
        default: html = this._renderOverview();
      }
    }
    const shell = this.isPanel ? this._panelShell(html) : `<ha-card class="card-mode">${html}</ha-card>`;
    this._root.innerHTML = `<style>${STYLE}</style>${shell}`;
    if (this._view.name === "enc") this._bindEditor();
    if (this._view.name === "details") { this._loadHistory(); const [, cc] = this._find(this._view.comp); if (cc && this._root.getElementById("evlog")) this._loadEvents(cc); }
  }

  _panelShell(html) { return `<div class="panel">${html}</div>`; }

  _statusChip(st) { return `<span class="chip" style="background:${STATUS_COLOR[st] || STATUS_COLOR.not_configured}">${esc(this.t("status_" + (st || "not_configured")))}</span>`; }

  _renderOverview() {
    const encs = this._encs();
    let h = `<div class="wrap">`;
    const showHead = !this.isPanel || this._config.title;
    const adm = this.admin && !this._config.enclosure;
    if (showHead || adm) {
      h += `<div class="head">${showHead ? `<h2>${esc(this._config.title || this.t("title"))}</h2>` : ""}<span class="spacer"></span>`;
      if (adm) {
        const db = this._data?.db || {};
        const dbk = db.status === "ok" ? "db_ok" : db.status === "off" ? "db_local" : "db_error";
        h += `<span class="dbchip" title="${esc(this.t(dbk) + (db.error ? ": " + db.error : ""))}"><ha-icon icon="${db.status === "ok" ? "mdi:database-check" : db.status === "off" ? "mdi:database-off-outline" : "mdi:database-alert"}" style="--mdc-icon-size:18px;color:${db.status === "ok" ? "#66bb6a" : db.status === "off" ? "inherit" : "#f9a825"}"></ha-icon></span>`;
        h += `<div class="adminbar"><button class="b sm" data-act="light-types" title="${this.t("light_sources")}"><ha-icon icon="mdi:lightbulb-group-outline"></ha-icon><span class="hide-s">${this.t("light_sources")}</span></button>`;
        h += `<button class="b sm" data-act="templates" title="${this.t("templates")}"><ha-icon icon="mdi:file-document-multiple-outline"></ha-icon><span class="hide-s">${this.t("templates")}</span></button>`;
        h += `<button class="b sm" data-act="groups" title="${this.t("groups")}"><ha-icon icon="mdi:link-variant"></ha-icon><span class="hide-s">${this.t("groups")}</span></button></div>`;
      }
      h += `</div>`;
    }
    if (!encs.length) {
      h += `<div class="empty"><ha-icon icon="mdi:turtle" style="--mdc-icon-size:48px"></ha-icon><div><b>${this.t("empty")}</b></div><div class="muted">${this.t("empty_hint")}</div>`;
      h += this.admin ? `<button class="b pri" data-act="enc-new"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_enclosure")}</button>` : `<div class="muted">${this.t("no_rights")}</div>`;
      return h + `</div></div>`;
    }
    h += `<div class="grid">`;
    for (const enc of encs) {
      const comps = enc.compartments;
      const bad = comps.filter((c) => ["alarm", "offline"].includes(c.live?.status)).length;
      const pend = comps.filter((c) => c.live?.status === "pending").length;
      h += `<div class="tile"><div class="th"><span class="nr">${enc.nr}</span><b class="ell tn">${esc(enc.name || this.t("enclosure") + " " + enc.nr)}</b>`;
      h += `<span class="muted small hide-s" style="white-space:nowrap">${enc.width}×${enc.height} cm</span>`;
      if (bad) h += `<span class="chip" style="background:${STATUS_COLOR.alarm}">${bad} × ${this.t("status_alarm")}</span>`;
      else if (pend) h += `<span class="chip" style="background:${STATUS_COLOR.pending}">${pend} × ${this.t("status_pending")}</span>`;
      const shown = this._modelShown(enc.id);
      if (comps.length) h += `<button class="ic" data-act="model" data-enc="${esc(enc.id)}" title="${this.t(shown ? "model_hide" : "model_show")}"><ha-icon icon="${shown ? "mdi:view-list" : "mdi:image-outline"}"></ha-icon></button>`;
      if (this.admin) h += `<button class="ic" data-act="enc-edit" data-enc="${esc(enc.id)}" title="${this.t("edit")}"><ha-icon icon="mdi:pencil-ruler"></ha-icon></button>`;
      h += `</div>${comps.length ? (shown ? enclosureSVG(enc) : "") : `<div class="muted small">${this.t("none_selected")}</div>`}<div class="list">`;
      for (const c of comps) {
        const L = c.live || {};
        h += `<div class="li" data-act="open" data-comp="${esc(c.id)}"><span class="nr">${esc(c.label)}</span>`;
        h += `<span class="ell">${esc(c.name || "–")}${c.animal ? ` <span class="muted small hide-s">· ${esc(c.animal)}</span>` : ""}</span>`;
        h += `<span class="val">${L.temperature !== null && L.temperature !== undefined ? fmt(L.temperature) + " °C" : "–"}</span>`;
        h += `<span class="val">${L.humidity !== null && L.humidity !== undefined ? fmt(L.humidity, 0) + " %" : "–"}</span>`;
        h += `<span class="dot" style="background:${STATUS_COLOR[L.status || "not_configured"]}" title="${esc(this.t("status_" + (L.status || "not_configured")))}"></span>`;
        h += this._quickButtons(c) + `</div>`;
      }
      h += `</div></div>`;
    }
    if (this.admin && this._config.enclosure === undefined) h += `<div class="tile add-tile" data-act="enc-new"><ha-icon icon="mdi:plus-box-multiple-outline" style="--mdc-icon-size:36px"></ha-icon>${this.t("new_enclosure")}</div>`;
    return h + `</div></div>`;
  }

  _renderDetails() {
    const [enc, c] = this._find(this._view.comp);
    if (!c) { this._view = { name: "overview" }; return this._renderOverview(); }
    const L = c.live || {};
    const tg = L.targets || {};
    const st = L.status || "not_configured";
    let h = `<div class="wrap"><div class="head"><button class="ic" data-act="back" title="${this.t("back")}"><ha-icon icon="mdi:arrow-left"></ha-icon></button>`;
    h += `<span class="nr">${esc(c.label)}</span><div class="hd"><h2 class="ell">${esc(c.name || this.t("enclosure") + " " + c.label)}</h2>${c.animal ? `<div class="muted small ell">${esc(c.animal)}</div>` : ""}</div>`;
    h += this._statusChip(st) + `<span class="spacer"></span>`;
    if (this.admin) h += `<button class="b" data-act="comp-settings" data-comp="${esc(c.id)}" title="${this.t("settings")}"><ha-icon icon="mdi:cog"></ha-icon><span class="hide-s">${this.t("settings")}</span></button>`;
    h += `</div><div class="det"><div class="col"><div class="box o4">${enclosureSVG(enc, { onlyComp: { ...c }, labels: false })}</div>`;
    if (enc.compartments.length > 1) h += `<div class="box o6"><div class="muted small" style="margin-bottom:6px">${esc(enc.name || this.t("enclosure") + " " + enc.nr)}</div><div class="locator">${enclosureSVG(enc, { highlight: c.id, values: false })}</div></div>`;
    h += `</div><div class="col">`;
    // gauges
    const period = L.period === "night" ? this.t("night_values") : this.t("day_values");
    const tcol = STATUS_COLOR[(L.problems || []).concat(L.pending || []).some((p) => p.startsWith("temp")) ? (L.problems || []).some((p) => p.startsWith("temp")) ? "alarm" : "pending" : "ok"];
    const hcol = STATUS_COLOR[(L.problems || []).concat(L.pending || []).some((p) => p.startsWith("hum")) ? (L.problems || []).some((p) => p.startsWith("hum")) ? "alarm" : "pending" : "ok"];
    h += `<div class="box o1"><div class="row" style="margin-bottom:6px"><h3 style="margin:0">${this.t("temperature")} & ${this.t("humidity")}</h3><span class="spacer"></span><span class="muted small"><ha-icon icon="${L.period === "night" ? "mdi:weather-night" : "mdi:weather-sunny"}" style="--mdc-icon-size:16px"></ha-icon> ${period}</span></div><div class="gauges">`;
    const tmin = Math.min(15, (tg.temp_min ?? 15) - 5), tmax = Math.max(40, (tg.temp_max ?? 40) + 5);
    h += `<div>${gaugeSVG(L.temperature, num(tg.temp_min), num(tg.temp_max), Math.floor(tmin / 5) * 5, Math.ceil(tmax / 5) * 5, "°C", tcol, 1)}<div class="gl">${this.t("temperature")}<br><span class="muted">${this.t("target")} ${this._range(tg.temp_min, tg.temp_max, "°C")}</span></div></div>`;
    h += `<div>${gaugeSVG(L.humidity, num(tg.hum_min), num(tg.hum_max), 0, 100, "%", hcol, 0)}<div class="gl">${this.t("humidity")}<br><span class="muted">${this.t("target")} ${this._range(tg.hum_min, tg.hum_max, "%")}</span></div></div>`;
    h += `</div></div>`;
    // problems
    h += `<div class="box o3"><h3>${this.t("problems")}</h3>`;
    if (st === "not_configured") h += `<div class="muted">${this.t("not_configured_hint")}</div>`;
    else if (!(L.problems || []).length && !(L.pending || []).length) h += `<div class="ok">${this.t("all_good")}</div>`;
    for (const p of (L.problems || [])) h += `<div class="prob"><span class="dot" style="background:${STATUS_COLOR.alarm}"></span>${esc(this.t("p_" + p))}<span class="muted small">${this._since(L.since?.[p])}</span></div>`;
    for (const p of (L.pending || [])) h += `<div class="prob"><span class="dot" style="background:${STATUS_COLOR.pending}"></span>${esc(this.t("p_" + p))}<span class="muted small">${this._since(L.since?.[p])}</span></div>`;
    h += `</div>`;
    // automation: light, rain, ventilation
    h += this._autoBoxes(c);
    // devices
    h += `<div class="box o2"><h3>${this.t("devices")}</h3>`;
    const devs = L.devices || c.devices || [];
    if (!devs.length) h += `<div class="muted small">${this.t("no_devices")}</div>`;
    else {
      h += `<div class="devs">`;
      for (const d of devs) {
        const s = this._hass.states[d.entity_id];
        const state = this._devState(d.entity_id);
        const on = isOn(state);
        const name = d.name || (s && s.attributes.friendly_name) || d.entity_id;
        h += `<div class="dev ${on ? "on" : ""} ${this._busy[d.entity_id] !== undefined ? "busy" : ""}" role="button" data-act="toggle" data-ent="${esc(d.entity_id)}"><ha-icon icon="${KIND_ICON[d.kind] || KIND_ICON.other}" style="color:${on ? "#f9a825" : "inherit"}"></ha-icon>`;
        h += `<span class="dn">${esc(name)}</span><span class="muted small">${state === null || state === "unavailable" ? this.t("unavailable") : on ? this.t("on") : this.t("off")}</span></div>`;
      }
      h += `</div>`;
    }
    h += `</div>`;
    // history
    h += `<div class="box o5"><h3>${this.t("last24")}</h3><div class="muted small">${this.t("temperature")}</div><div id="ch-t">${this._chart(c, "temperature")}</div>`;
    h += `<div class="muted small" style="margin-top:6px">${this.t("humidity")}</div><div id="ch-h">${this._chart(c, "humidity")}</div></div>`;
    // sensors
    const sens = [...(L.temp_sensors || []).map((s) => ({ ...s, u: "°C" })), ...(L.hum_sensors || []).map((s) => ({ ...s, u: "%" }))];
    if (sens.length) {
      h += `<div class="box o7"><h3>${this.t("sensors")}</h3>`;
      for (const s of sens) h += `<div class="row small" style="padding:3px 0"><span>${esc(s.name)}</span><span class="spacer"></span><span class="val">${s.value === null ? this.t("unavailable") : fmt(s.value, s.u === "%" ? 0 : 1) + " " + s.u}</span></div>`;
      h += `</div>`;
    }
    return h + `</div></div></div>`;
  }

  _range(lo, hi, u) {
    if (lo === null && hi === null || lo === undefined && hi === undefined) return "–";
    return `${lo ?? "…"}–${hi ?? "…"} ${u}`;
  }
  _since(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return `${this.t("since")} ${d.toLocaleTimeString(this.lang, { hour: "2-digit", minute: "2-digit" })}`;
  }

  _chart(c, key) {
    const hist = this._hist[c.id];
    const tg = c.live?.targets || {};
    const end = Date.now(), start = end - 24 * 3600000;
    if (!hist) return chartSVG(null);
    if (key === "temperature") return chartSVG(hist.temperature, num(tg.temp_min), num(tg.temp_max), "°C", "#ff8a65", start, end);
    return chartSVG(hist.humidity, num(tg.hum_min), num(tg.hum_max), "%", "#4fc3f7", start, end);
  }

  async _loadHistory() {
    const [, c] = this._find(this._view.comp);
    if (!c) return;
    const cached = this._hist[c.id];
    if (cached && Date.now() - cached.at < 5 * 60000) return;
    const ids = [c.entities?.temperature, c.entities?.humidity].filter(Boolean);
    if (!ids.length) return;
    this._hist[c.id] = { at: Date.now(), temperature: cached?.temperature, humidity: cached?.humidity };
    try {
      const end = new Date(), start = new Date(end.getTime() - 24 * 3600000);
      const res = await this._hass.callWS({ type: "history/history_during_period", start_time: start.toISOString(), end_time: end.toISOString(),
        entity_ids: ids, minimal_response: true, no_attributes: true, significant_changes_only: false });
      const conv = (arr) => (arr || []).map((p) => ({ t: (p.lu ?? p.lc ?? (Date.parse(p.last_updated || p.last_changed) / 1000)) * 1000, v: Number(p.s ?? p.state) })).filter((p) => !isNaN(p.v));
      this._hist[c.id] = { at: Date.now(), temperature: conv(res[c.entities.temperature]), humidity: conv(res[c.entities.humidity]) };
      if (this._view.name === "details" && this._view.comp === c.id) {
        const t = this._root.getElementById("ch-t"), hh = this._root.getElementById("ch-h");
        if (t) t.innerHTML = this._chart(c, "temperature");
        if (hh) hh.innerHTML = this._chart(c, "humidity");
      }
    } catch (e) { /* history not available */ }
  }

  /* -------------------------------------------------------- compartment settings (tabs) */
  _openCompSettings(id, tab) {
    const [enc, c] = this._find(id);
    if (!c) return;
    this._view = { name: "comp", comp: id, tab: tab || this._view.tab || "general", label: c.label, enc: enc.id,
      groups: c.groups || {},
      draft: clone({ name: c.name, animal: c.animal, depth: c.depth, climate: c.climate, notify: c.notify, devices: c.devices, look: c.look,
        lights: c.lights || [], light_auto: c.light_auto !== false, rain: c.rain || {}, vent: c.vent || {} }) };
    this._msg = "";
    this._loadTargets();
    this._render();
  }

  _loadTargets() {
    if (!this._targets) this._hass.callWS({ type: "terrarium/notify_targets" }).then((r) => { this._targets = r.targets; if (["comp"].includes(this._view.name)) this._render(); }).catch(() => { this._targets = []; });
  }

  _entityOptions(kind) {
    const st = this._hass.states;
    const ids = Object.keys(st).filter((id) => {
      const s = st[id], dc = s.attributes.device_class, u = s.attributes.unit_of_measurement;
      if (kind === "temperature") return id.startsWith("sensor.") && (dc === "temperature" || u === "°C" || u === "°F");
      if (kind === "humidity") return id.startsWith("sensor.") && (dc === "humidity" || (u === "%" && /hum|feucht/i.test(id)));
      if (kind === "device") return /^(light|switch|fan|input_boolean|climate|humidifier|valve|cover|script|automation)\./.test(id);
      if (kind === "switch") return /^(light|switch|input_boolean|valve|fan)\./.test(id);
      return false;
    }).filter((id) => !id.startsWith("sensor.terrarium_") && !id.startsWith("switch.terrarium_"));
    return ids.sort().map((id) => `<option value="${esc(id)}">${esc(st[id].attributes.friendly_name || "")}</option>`).join("");
  }

  _numField(path, label, val, step = "0.1", extra = "") {
    return `<label class="f">${label}<input type="number" inputmode="decimal" step="${step}" data-path="${path}" data-type="num" value="${val ?? ""}" ${extra}></label>`;
  }
  _txt(path, label, val, extra = "") { return `<label class="f">${label}<input data-path="${path}" value="${esc(val ?? "")}" ${extra}></label>`; }
  _sel(path, label, val, opts, rerender) {
    return `<label class="f">${label}<select data-path="${path}" ${rerender ? 'data-rr="1"' : ""}>${opts.map(([v, l]) => `<option value="${esc(v)}" ${v === val ? "selected" : ""}>${esc(l)}</option>`).join("")}</select></label>`;
  }
  _cb(path, label, val, rerender) { return `<label class="cb"><input type="checkbox" data-path="${path}" data-type="bool" ${rerender ? 'data-rr="1"' : ""} ${val ? "checked" : ""}>${label}</label>`; }

  _sensorChips(path, list) {
    return `<div class="chips">${list.map((id, i) => {
      const s = this._hass.states[id];
      const v = s ? `${s.state}${s.attributes.unit_of_measurement ? " " + s.attributes.unit_of_measurement : ""}` : this.t("unavailable");
      return `<span class="ch">${esc((s && s.attributes.friendly_name) || id)} <span class="v">${esc(v)}</span><button data-act="chip-del" data-path="${path}" data-i="${i}">×</button></span>`;
    }).join("")}</div>`;
  }

  _entityField(path, label, val, list) {
    const s = val && this._hass.states[val];
    const st = val ? (s ? `${s.attributes.friendly_name || val}: ${s.state}` : this.t("unavailable")) : "";
    return `<label class="f">${label}<input list="${list}" data-path="${path}" value="${esc(val || "")}" placeholder="switch.…" autocomplete="off" autocapitalize="off" spellcheck="false"><span class="muted small">${esc(st)}</span></label>`;
  }

  _tabs(tabs, cur) {
    return `<div class="tabs" role="tablist">${tabs.map(([k, ic, l]) => `<button class="tab ${k === cur ? "act" : ""}" data-act="tab" data-tab="${k}" role="tab"><ha-icon icon="${ic}"></ha-icon><span>${esc(l)}</span></button>`).join("")}</div>`;
  }

  /* time spec: fixed time or sunrise/sunset +- minutes */
  _timeSpec(path, spec, label) {
    spec = spec || { type: "time", time: "08:00", offset: 0 };
    let h = `<div class="ts"><span class="muted small">${label}</span><select data-path="${path}.type" data-rr="1">`;
    for (const k of ["time", "sunrise", "sunset"]) h += `<option value="${k}" ${spec.type === k ? "selected" : ""}>${this.t("ts_" + k)}</option>`;
    h += `</select>`;
    if (spec.type === "time") h += `<input type="time" data-path="${path}.time" value="${esc(spec.time || "08:00")}">`;
    else h += `<span class="off"><input type="number" inputmode="numeric" step="5" data-path="${path}.offset" data-type="num" value="${spec.offset ?? 0}"><span class="muted small">${this.t("minutes_short")}</span></span>`;
    return h + `</div>`;
  }

  _days(path, days) {
    const names = this.t("days").split(",");
    return `<div class="days">${names.map((n, i) => `<button class="day ${!days.length || days.includes(i) ? "on" : ""}" data-act="day" data-path="${path}" data-d="${i}">${n}</button>`).join("")}</div>`;
  }

  /* profile list; mode: "windows" (light), "runs" (rain), "both" (ventilation) */
  _profilesEditor(path, profiles, mode) {
    let h = `<div class="profiles">`;
    profiles.forEach((p, i) => {
      const pp = `${path}.${i}`;
      h += `<div class="prof ${p.enabled ? "" : "off"}"><div class="ph">${this._cb(`${pp}.enabled`, "", p.enabled, true)}<input class="pn" data-path="${pp}.name" value="${esc(p.name || "")}" placeholder="${this.t("profile_name")}">`;
      h += `<button class="ic" data-act="arr-del" data-path="${path}" data-i="${i}" title="${this.t("remove")}"><ha-icon icon="mdi:delete"></ha-icon></button></div>`;
      h += this._days(`${pp}.days`, p.days || []);
      h += `<div class="row" style="flex-wrap:wrap;gap:10px;margin:6px 0">${this._cb(`${pp}.season.enabled`, this.t("season"), p.season?.enabled, true)}`;
      if (p.season?.enabled) h += `<span class="season"><input data-path="${pp}.season.from" value="${esc(p.season.from)}" placeholder="MM-TT" inputmode="numeric"> – <input data-path="${pp}.season.to" value="${esc(p.season.to)}" placeholder="MM-TT" inputmode="numeric"></span>`;
      h += `</div>`;
      if (mode !== "runs") {
        h += `<div class="muted small">${this.t(mode === "both" ? "vent_windows" : "windows")}</div>`;
        (p.windows || []).forEach((w, j) => {
          h += `<div class="win">${this._timeSpec(`${pp}.windows.${j}.on`, w.on, this.t("from"))}${this._timeSpec(`${pp}.windows.${j}.off`, w.off, this.t("until"))}<button class="ic" data-act="arr-del" data-path="${pp}.windows" data-i="${j}"><ha-icon icon="mdi:close"></ha-icon></button></div>`;
        });
        h += `<button class="b sm" data-act="arr-add" data-path="${pp}.windows" data-tpl="window"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_window")}</button>`;
      }
      if (mode !== "windows") {
        h += `<div class="muted small" style="margin-top:8px">${this.t(mode === "both" ? "vent_runs" : "runs")}</div>`;
        (p.runs || []).forEach((r, j) => {
          h += `<div class="win">${this._timeSpec(`${pp}.runs.${j}.at`, r.at, this.t("at"))}<label class="f dur">${this.t("duration_s")}<input type="number" inputmode="numeric" min="1" step="1" data-path="${pp}.runs.${j}.duration" data-type="num" value="${r.duration ?? 30}"></label><button class="ic" data-act="arr-del" data-path="${pp}.runs" data-i="${j}"><ha-icon icon="mdi:close"></ha-icon></button></div>`;
        });
        h += `<button class="b sm" data-act="arr-add" data-path="${pp}.runs" data-tpl="run"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_run")}</button>`;
      }
      h += `</div>`;
    });
    h += `<button class="b" data-act="arr-add" data-path="${path}" data-tpl="${mode === "runs" ? "profile_runs" : "profile"}"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_profile")}</button></div>`;
    return h;
  }

  _lightTypeOptions() {
    return (this._data?.light_types || []).map((t) => [t.id, `${t.name}${t.watt ? ` (${t.watt} W)` : ""}`]);
  }

  _lightsEditor(prefix, d, withEntity) {
    let h = this._cb(`${prefix}light_auto`, this.t("light_auto"), d.light_auto !== false);
    h += `<div class="muted small" style="margin:6px 0 10px">${this.t("light_hint")}</div>`;
    (d.lights || []).forEach((l, i) => {
      const p = `${prefix}lights.${i}`;
      const lt = (this._data?.light_types || []).find((t) => t.id === l.type_id);
      h += `<div class="sec inner"><div class="row" style="margin-bottom:8px"><span class="swatch" style="background:${esc(lt?.color || "#888")}"></span><b class="ell">${esc(l.name || lt?.name || this.t("light"))}</b><span class="spacer"></span>`;
      h += `<button class="ic" data-act="arr-del" data-path="${prefix}lights" data-i="${i}" title="${this.t("remove")}"><ha-icon icon="mdi:delete"></ha-icon></button></div><div class="fields">`;
      h += this._sel(`${p}.type_id`, this.t("light_type"), l.type_id, this._lightTypeOptions(), true);
      h += this._txt(`${p}.name`, this.t("name"), l.name, `placeholder="${esc(lt?.name || "")}"`);
      if (withEntity) h += this._entityField(`${p}.entity_id`, this.t("socket"), l.entity_id, "dl-sw");
      h += `</div><div class="row" style="flex-wrap:wrap;gap:14px;margin:8px 0">${this._cb(`${p}.enabled`, this.t("auto_this"), l.enabled)}${this._cb(`${p}.overheat.enabled`, this.t("overheat"), l.overheat?.enabled, true)}</div>`;
      if (l.overheat?.enabled) h += `<div class="fields">${this._numField(`${p}.overheat.above`, this.t("off_above") + " °C", l.overheat.above)}${this._numField(`${p}.overheat.hyst`, this.t("hyst") + " °C", l.overheat.hyst)}</div>`;
      if (lt?.restrike_min) h += `<div class="muted small" style="margin:4px 0">${this.t("restrike_hint", { m: lt.restrike_min })}</div>`;
      h += `<div class="muted small" style="margin:10px 0 4px">${this.t("profiles")}</div>${this._profilesEditor(`${p}.profiles`, l.profiles || [], "windows")}</div>`;
    });
    h += `<button class="b" data-act="arr-add" data-path="${prefix}lights" data-tpl="light"><ha-icon icon="mdi:lightbulb-on-outline"></ha-icon>${this.t("add_light")}</button>`;
    return h;
  }

  _rainEditor(prefix, r, withEntity) {
    const p = `${prefix}rain`;
    let h = `<div class="fields">`;
    if (withEntity) h += this._entityField(`${p}.entity_id`, this.t("socket"), r.entity_id, "dl-sw");
    h += this._numField(`${p}.manual_duration`, this.t("manual_duration"), r.manual_duration, "1", 'min="1"');
    h += this._numField(`${p}.max_duration`, this.t("max_duration"), r.max_duration, "1", 'min="5"');
    h += this._numField(`${p}.min_pause`, this.t("min_pause"), r.min_pause, "1", 'min="0"');
    h += `</div><div style="margin:10px 0">${this._cb(`${p}.enabled`, this.t("rain_auto"), r.enabled !== false)}</div>`;
    h += `<div class="sec inner"><h3>${this.t("rain_times")}</h3>${this._profilesEditor(`${p}.profiles`, r.profiles || [], "runs")}</div>`;
    h += `<div class="sec inner"><h3>${this.t("hum_rules")}</h3>${this._cb(`${p}.hum_start.enabled`, this.t("hum_start"), r.hum_start?.enabled, true)}`;
    if (r.hum_start?.enabled) h += `<div class="fields" style="margin:6px 0 10px">${this._numField(`${p}.hum_start.below`, this.t("below") + " %", r.hum_start.below, "1")}${this._numField(`${p}.hum_start.duration`, this.t("duration_s"), r.hum_start.duration, "1")}${this._numField(`${p}.hum_start.min_pause`, this.t("min_pause"), r.hum_start.min_pause, "1")}</div>`;
    h += this._cb(`${p}.hum_block.enabled`, this.t("hum_block"), r.hum_block?.enabled, true);
    if (r.hum_block?.enabled) h += `<div class="fields" style="margin-top:6px">${this._numField(`${p}.hum_block.above`, this.t("above") + " %", r.hum_block.above, "1")}</div>`;
    h += `<div class="muted small" style="margin-top:8px">${this.t("hum_rules_hint")}</div></div>`;
    return h;
  }

  _ventEditor(prefix, v, withEntity) {
    const p = `${prefix}vent`;
    let h = `<div class="fields">`;
    if (withEntity) h += this._entityField(`${p}.entity_id`, this.t("socket"), v.entity_id, "dl-sw");
    h += this._numField(`${p}.min_run`, this.t("min_run"), v.min_run, "1", 'min="0"');
    h += `</div><div style="margin:10px 0">${this._cb(`${p}.enabled`, this.t("vent_auto"), v.enabled !== false)}</div>`;
    h += `<div class="sec inner"><h3>${this.t("vent_times")}</h3>${this._profilesEditor(`${p}.profiles`, v.profiles || [], "both")}</div>`;
    h += `<div class="sec inner"><h3>${this.t("vent_rules")}</h3>${this._cb(`${p}.temp_on.enabled`, this.t("vent_temp"), v.temp_on?.enabled, true)}`;
    if (v.temp_on?.enabled) h += `<div class="fields" style="margin:6px 0 10px">${this._numField(`${p}.temp_on.above`, this.t("above") + " °C", v.temp_on.above)}${this._numField(`${p}.temp_on.hyst`, this.t("hyst") + " °C", v.temp_on.hyst)}</div>`;
    h += this._cb(`${p}.hum_on.enabled`, this.t("vent_hum"), v.hum_on?.enabled, true);
    if (v.hum_on?.enabled) h += `<div class="fields" style="margin-top:6px">${this._numField(`${p}.hum_on.above`, this.t("above") + " %", v.hum_on.above, "1")}${this._numField(`${p}.hum_on.hyst`, this.t("hyst") + " %", v.hum_on.hyst, "1")}</div>`;
    return h + `</div>`;
  }

  _templateBar(kind) {
    const tpls = (this._data?.templates || []).filter((t) => t.kind === kind);
    let h = `<div class="tplbar">`;
    if (tpls.length) h += `<select id="tplsel"><option value="">${this.t("apply_template")} …</option>${tpls.map((t) => `<option value="${esc(t.id)}">${esc(t.name)}</option>`).join("")}</select><button class="b sm" data-act="tpl-apply" data-kind="${kind}">${this.t("apply")}</button>`;
    h += `<button class="b sm" data-act="tpl-from" data-kind="${kind}"><ha-icon icon="mdi:content-save-outline"></ha-icon>${this.t("save_as_template")}</button></div>`;
    return h;
  }

  _groupBanner(kind) {
    const g = this._view.groups?.[kind];
    if (!g) return "";
    return `<div class="banner"><ha-icon icon="mdi:link-variant"></ha-icon><div>${this.t("group_banner", { n: esc(g.name || this.t("group")), m: g.members.join(", ") })}</div></div>`;
  }

  _renderCompSettings() {
    const v = this._view, d = v.draft, cl = d.climate, n = cl.night, no = d.notify;
    let h = `<div class="wrap"><div class="head"><button class="ic" data-act="comp-cancel" title="${this.t("back")}"><ha-icon icon="mdi:arrow-left"></ha-icon></button><h2 class="ell">${esc(this.t("comp_settings", { label: v.label }))}</h2></div>`;
    h += this._tabs([["general", "mdi:information-outline", this.t("general")], ["climate", "mdi:thermometer", this.t("tab_climate")], ["light", "mdi:lightbulb-on-outline", this.t("tab_light")],
      ["rain", "mdi:weather-pouring", this.t("tab_rain")], ["vent", "mdi:fan", this.t("tab_vent")], ["devices", "mdi:toggle-switch-outline", this.t("devices")]], v.tab);
    h += `<div class="form">`;
    h += `<datalist id="dl-temp">${this._entityOptions("temperature")}</datalist><datalist id="dl-hum">${this._entityOptions("humidity")}</datalist><datalist id="dl-dev">${this._entityOptions("device")}</datalist><datalist id="dl-sw">${this._entityOptions("switch")}</datalist>`;
    if (v.tab === "general") {
      h += `<div class="sec"><h3>${this.t("general")}</h3><div class="fields">${this._txt("name", this.t("name"), d.name)}${this._txt("animal", this.t("animal"), d.animal)}${this._numField("depth", this.t("depth") + " (cm)", d.depth, "1")}</div></div>`;
      h += `<div class="sec"><h3>${this.t("look")}</h3><div class="fields">`;
      h += this._sel("look.substrate", this.t("substrate"), d.look.substrate, ["soil", "sand", "bark", "moss", "gravel", "water", "none"].map((k) => [k, this.t("s_" + k)]));
      h += this._sel("look.decor", this.t("decor"), d.look.decor, ["plants", "stones", "branches", "mixed", "none"].map((k) => [k, this.t("d_" + k)]));
      h += this._sel("look.background", this.t("background"), d.look.background, ["rock", "cork", "plain", "jungle"].map((k) => [k, this.t("b_" + k)]));
      h += `</div></div>`;
    }
    if (v.tab === "climate") {
      h += `<div class="sec"><h3><ha-icon icon="mdi:thermometer"></ha-icon> ${this.t("temperature")}</h3><div class="muted small">${this.t("temp_sensors")} – ${this.t("sensors_hint")}</div>`;
      h += this._sensorChips("climate.temp_sensors", cl.temp_sensors);
      h += `<input list="dl-temp" placeholder="${this.t("add_sensor")}" data-add="climate.temp_sensors" autocomplete="off" autocapitalize="off"><div class="fields" style="margin-top:10px">`;
      h += this._numField("climate.temp_min", this.t("min") + " °C", cl.temp_min) + this._numField("climate.temp_max", this.t("max") + " °C", cl.temp_max) + this._numField("climate.temp_hyst", this.t("hyst") + " °C", cl.temp_hyst);
      h += `</div></div>`;
      h += `<div class="sec"><h3><ha-icon icon="mdi:water-percent"></ha-icon> ${this.t("humidity")}</h3><div class="muted small">${this.t("hum_sensors")} – ${this.t("sensors_hint")}</div>`;
      h += this._sensorChips("climate.hum_sensors", cl.hum_sensors);
      h += `<input list="dl-hum" placeholder="${this.t("add_sensor")}" data-add="climate.hum_sensors" autocomplete="off" autocapitalize="off"><div class="fields" style="margin-top:10px">`;
      h += this._numField("climate.hum_min", this.t("min") + " %", cl.hum_min, "1") + this._numField("climate.hum_max", this.t("max") + " %", cl.hum_max, "1") + this._numField("climate.hum_hyst", this.t("hyst") + " %", cl.hum_hyst, "0.5");
      h += `</div></div>`;
      h += `<div class="sec"><h3><ha-icon icon="mdi:weather-night"></ha-icon> ${this.t("night_values")}</h3>${this._cb("climate.night.enabled", this.t("night_enabled"), n.enabled, true)}`;
      if (n.enabled) {
        h += `<div class="fields" style="margin-top:10px"><label class="f">${this.t("night_from")}<input type="time" data-path="climate.night.start" value="${esc(n.start)}"></label><label class="f">${this.t("night_to")}<input type="time" data-path="climate.night.end" value="${esc(n.end)}"></label>`;
        h += this._numField("climate.night.temp_min", this.t("min") + " °C", n.temp_min) + this._numField("climate.night.temp_max", this.t("max") + " °C", n.temp_max);
        h += this._numField("climate.night.hum_min", this.t("min") + " %", n.hum_min, "1") + this._numField("climate.night.hum_max", this.t("max") + " %", n.hum_max, "1");
        h += `</div><div class="muted small" style="margin-top:6px">${this.t("night_hint")}</div>`;
      }
      h += `</div>`;
      h += `<div class="sec"><h3><ha-icon icon="mdi:bell-ring"></ha-icon> ${this.t("notifications")}</h3>${this._cb("notify.enabled", this.t("notify_enabled"), no.enabled)}`;
      h += `<div class="muted small" style="margin-top:8px">${this.t("targets")}</div><div class="chips">${no.targets.map((id, i) => {
        const tt = (this._targets || []).find((x) => x.id === id);
        return `<span class="ch">${esc(tt ? tt.name : id)}<button data-act="chip-del" data-path="notify.targets" data-i="${i}">×</button></span>`;
      }).join("")}</div>`;
      h += `<select data-add="notify.targets"><option value="">${this.t("add_target")}</option>${(this._targets || []).filter((x) => !no.targets.includes(x.id)).map((x) => `<option value="${esc(x.id)}">${esc(x.name)} (${esc(x.id)})</option>`).join("")}</select>`;
      h += `<div class="fields" style="margin-top:10px">${this._numField("climate.delay", this.t("delay"), cl.delay, "1", 'min="0"')}${this._numField("notify.repeat", this.t("repeat"), no.repeat, "1", 'min="0"')}</div>`;
      h += `<div class="muted small" style="margin:4px 0 8px">${this.t("delay_hint")}</div>`;
      h += `<div class="row" style="flex-wrap:wrap;gap:14px">${this._cb("notify.clear", this.t("notify_clear"), no.clear)}${this._cb("notify.offline", this.t("notify_offline"), no.offline)}${this._cb("notify.persistent", this.t("notify_persistent"), no.persistent)}</div>`;
      h += `<div class="row" style="margin-top:10px"><button class="b" data-act="test-notify"><ha-icon icon="mdi:send"></ha-icon>${this.t("test_notify")}</button><span id="tn" class="small"></span></div></div>`;
    }
    if (v.tab === "light") h += `<div class="sec">${this._groupBanner("light")}${this._templateBar("light")}${this._lightsEditor("", d, true)}</div>`;
    if (v.tab === "rain") h += `<div class="sec">${this._groupBanner("rain")}${this._templateBar("rain")}${this._rainEditor("", d.rain, true)}</div>`;
    if (v.tab === "vent") h += `<div class="sec">${this._groupBanner("vent")}${this._templateBar("vent")}${this._ventEditor("", d.vent, true)}</div>`;
    if (v.tab === "devices") {
      h += `<div class="sec"><h3><ha-icon icon="mdi:toggle-switch"></ha-icon> ${this.t("devices")}</h3><div class="muted small" style="margin-bottom:8px">${this.t("devices_hint")}</div>`;
      d.devices.forEach((dev, i) => {
        h += `<div class="devrow"><select data-path="devices.${i}.kind">${DEVICE_KINDS.map((k) => `<option value="${k}" ${k === dev.kind ? "selected" : ""}>${esc(this.t("k_" + k))}</option>`).join("")}</select>`;
        h += `<input list="dl-dev" data-path="devices.${i}.entity_id" value="${esc(dev.entity_id)}" placeholder="${this.t("entity")}" autocomplete="off" autocapitalize="off"><input data-path="devices.${i}.name" value="${esc(dev.name)}" placeholder="${this.t("name")}">`;
        h += `<button class="ic" data-act="arr-del" data-path="devices" data-i="${i}"><ha-icon icon="mdi:delete"></ha-icon></button></div>`;
      });
      h += `<button class="b" data-act="arr-add" data-path="devices" data-tpl="device"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_device")}</button></div>`;
    }
    h += `<div class="actions"><span id="msg" class="${this._msgErr ? "err" : "ok"}">${esc(this._msg)}</span><span class="spacer"></span><button class="b" data-act="comp-cancel">${this.t("cancel")}</button><button class="b pri" data-act="comp-save"><ha-icon icon="mdi:content-save"></ha-icon>${this.t("save")}</button></div>`;
    return h + `</div></div>`;
  }

  _newObj(tpl) {
    const T = (s) => ({ type: "time", time: s, offset: 0 });
    const lt = (this._data?.light_types || [])[0];
    switch (tpl) {
      case "light": return { id: "", name: "", type_id: lt ? lt.id : "", entity_id: "", enabled: true, overheat: { enabled: false, above: 40, hyst: 2 },
        profiles: [{ name: this.t("p_day"), enabled: true, days: [], season: { enabled: false, from: "03-01", to: "10-31" }, windows: [{ on: T("08:00"), off: T("20:00") }], runs: [] }] };
      case "profile": return { name: "", enabled: true, days: [], season: { enabled: false, from: "03-01", to: "10-31" }, windows: [{ on: T("08:00"), off: T("20:00") }], runs: [] };
      case "profile_runs": return { name: "", enabled: true, days: [], season: { enabled: false, from: "03-01", to: "10-31" }, windows: [], runs: [{ at: T("08:00"), duration: 30 }] };
      case "window": return { on: T("08:00"), off: T("20:00") };
      case "run": return { at: T("12:00"), duration: 30 };
      case "device": return { entity_id: "", kind: "light", name: "" };
      default: return {};
    }
  }

  /* client-side template application (reviewed by the user, then saved) */
  _applyTemplateToDraft(kind, tplId, draft, prefix) {
    const tpl = (this._data?.templates || []).find((t) => t.id === tplId);
    if (!tpl) return;
    const target = prefix ? this._getPath(draft, prefix.replace(/\.$/, "")) : draft;
    const cfg = clone(tpl.config || {});
    if (kind === "light") {
      const old = [...(target.lights || [])];
      target.lights = (cfg.lights || []).map((l) => {
        const i = old.findIndex((o) => o.type_id === l.type_id && o.entity_id);
        const ent = i >= 0 ? old.splice(i, 1)[0].entity_id : "";
        return { ...l, id: "", entity_id: ent };
      });
      target.light_auto = cfg.light_auto !== false;
    } else {
      const ent = target[kind]?.entity_id || "";
      target[kind] = { ...(cfg[kind] || {}), entity_id: ent };
    }
  }

  /* -------------------------------------------------------- central pages: light sources, templates, groups */
  _renderAdminHead(title, back = "back") {
    return `<div class="head"><button class="ic" data-act="${back}" title="${this.t("back")}"><ha-icon icon="mdi:arrow-left"></ha-icon></button><h2 class="ell">${esc(title)}</h2></div>`;
  }

  _renderLightTypes() {
    const v = this._view;
    let h = `<div class="wrap">${this._renderAdminHead(this.t("light_sources"))}<div class="form">`;
    h += `<div class="sec"><div class="muted small" style="margin-bottom:10px">${this.t("light_sources_hint")}</div><div class="list">`;
    for (const t of (this._data?.light_types || [])) {
      h += `<div class="li" data-act="lt-edit" data-id="${esc(t.id)}"><span class="swatch" style="background:${esc(t.color)}"></span><span class="ell">${esc(t.name)} <span class="muted small">· ${esc(this.t("cat_" + t.category))}</span></span><span class="val">${t.watt ? t.watt + " W" : ""}</span><span class="muted small">${t.restrike_min ? "⏱ " + t.restrike_min + " min" : ""}</span><ha-icon icon="mdi:chevron-right"></ha-icon></div>`;
    }
    h += `</div><button class="b" data-act="lt-new" style="margin-top:10px"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_light_type")}</button></div>`;
    if (v.draft) {
      const d = v.draft;
      h += `<div class="sec" id="edsec"><h3>${d.id ? this.t("edit") : this.t("add_light_type")}</h3><div class="fields">`;
      h += this._txt("name", this.t("name"), d.name);
      h += this._sel("category", this.t("category"), d.category, ["led", "hid", "pl", "ph", "night", "uv", "other"].map((k) => [k, this.t("cat_" + k)]));
      h += this._numField("watt", this.t("watt"), d.watt, "1");
      h += this._numField("restrike_min", this.t("restrike"), d.restrike_min, "1");
      h += `<label class="f">${this.t("color")}<input type="color" data-path="color" value="${esc(d.color || "#fff6e0")}"></label>`;
      h += `</div><div class="muted small" style="margin-top:6px">${this.t("restrike_info")}</div>`;
      h += `<div class="actions"><span id="msg" class="${this._msgErr ? "err" : "ok"}">${esc(this._msg)}</span><span class="spacer"></span>${d.id ? `<button class="b warn" data-act="lt-del">${this.t("delete")}</button>` : ""}<button class="b" data-act="lt-cancel">${this.t("cancel")}</button><button class="b pri" data-act="lt-save">${this.t("save")}</button></div></div>`;
    }
    return h + `</div></div>`;
  }

  _renderTemplates() {
    const v = this._view;
    let h = `<div class="wrap">${this._renderAdminHead(this.t("templates"))}<div class="form">`;
    h += `<div class="muted small">${this.t("templates_hint")}</div>`;
    for (const [kind, ic] of [["light", "mdi:lightbulb-on-outline"], ["rain", "mdi:weather-pouring"], ["vent", "mdi:fan"]]) {
      const list = (this._data?.templates || []).filter((t) => t.kind === kind);
      h += `<div class="sec"><h3><ha-icon icon="${ic}"></ha-icon> ${this.t("tab_" + kind)}</h3><div class="list">`;
      for (const t of list) h += `<div class="li" data-act="tpl-edit" data-id="${esc(t.id)}"><ha-icon icon="${ic}"></ha-icon><span class="ell">${esc(t.name)}</span>${t.default_new ? `<span class="badge">${this.t("default_new_short")}</span>` : "<span></span>"}<span></span><ha-icon icon="mdi:chevron-right"></ha-icon></div>`;
      if (!list.length) h += `<div class="muted small">–</div>`;
      h += `</div><button class="b sm" data-act="tpl-new" data-kind="${kind}" style="margin-top:8px"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_template")}</button></div>`;
    }
    return h + `</div></div>`;
  }

  _renderTemplateEdit() {
    const v = this._view, d = v.draft;
    let h = `<div class="wrap">${this._renderAdminHead(d.id ? d.name : this.t("add_template"), "tpl-back")}<div class="form"><div class="sec"><div class="fields">`;
    h += this._txt("name", this.t("name"), d.name);
    h += `</div><div style="margin-top:10px">${this._cb("default_new", this.t("default_new"), d.default_new)}</div></div>`;
    h += `<div class="sec">`;
    if (d.kind === "light") h += this._lightsEditor("config.", d.config, false);
    if (d.kind === "rain") h += this._rainEditor("config.", d.config.rain, false);
    if (d.kind === "vent") h += this._ventEditor("config.", d.config.vent, false);
    h += `</div><div class="actions"><span id="msg" class="${this._msgErr ? "err" : "ok"}">${esc(this._msg)}</span><span class="spacer"></span>${d.id ? `<button class="b warn" data-act="tpl-del">${this.t("delete")}</button>` : ""}<button class="b" data-act="tpl-back">${this.t("cancel")}</button><button class="b pri" data-act="tpl-save">${this.t("save")}</button></div>`;
    return h + `</div></div>`;
  }

  _renderGroups() {
    const v = this._view;
    const comps = this._allComps();
    let h = `<div class="wrap">${this._renderAdminHead(this.t("groups"))}<div class="form"><div class="muted small">${this.t("groups_hint")}</div>`;
    for (const [kind, ic] of [["light", "mdi:lightbulb-group-outline"], ["rain", "mdi:weather-pouring"], ["vent", "mdi:fan"]]) {
      const list = (this._data?.groups || []).filter((g) => g.kind === kind);
      h += `<div class="sec"><h3><ha-icon icon="${ic}"></ha-icon> ${this.t("tab_" + kind)}</h3><div class="list">`;
      for (const g of list) h += `<div class="li" data-act="grp-edit" data-id="${esc(g.id)}"><ha-icon icon="mdi:link-variant"></ha-icon><span class="ell">${esc(g.name || this.t("group"))}</span><span class="muted small">${esc(g.member_labels.join(", "))}</span><span></span><ha-icon icon="mdi:chevron-right"></ha-icon></div>`;
      if (!list.length) h += `<div class="muted small">–</div>`;
      h += `</div><button class="b sm" data-act="grp-new" data-kind="${kind}" style="margin-top:8px"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_group")}</button></div>`;
    }
    if (v.draft) {
      const d = v.draft;
      h += `<div class="sec" id="edsec"><h3>${this.t("tab_" + d.kind)} – ${d.id ? this.t("edit") : this.t("add_group")}</h3><div class="fields">${this._txt("name", this.t("name"), d.name)}</div>`;
      h += `<div class="muted small" style="margin:10px 0 4px">${this.t("members")}</div><div class="mlist">`;
      for (const c of comps) {
        const other = (this._data?.groups || []).find((g) => g.kind === d.kind && g.id !== d.id && g.members.includes(c.id));
        h += `<label class="cb"><input type="checkbox" data-act="grp-member" data-id="${esc(c.id)}" ${d.members.includes(c.id) ? "checked" : ""}><span class="nr">${esc(c.label)}</span>${esc(c.name || "")}${other ? ` <span class="muted small">(${esc(other.name || this.t("group"))})</span>` : ""}</label>`;
      }
      h += `</div><div class="muted small" style="margin-top:8px">${this.t("group_settings_hint")}</div>`;
      h += `<div class="actions"><span id="msg" class="${this._msgErr ? "err" : "ok"}">${esc(this._msg)}</span><span class="spacer"></span>${d.id ? `<button class="b warn" data-act="grp-del">${this.t("delete")}</button>` : ""}<button class="b" data-act="grp-cancel">${this.t("cancel")}</button><button class="b pri" data-act="grp-save">${this.t("save")}</button></div></div>`;
    }
    return h + `</div></div>`;
  }

  _scrollEd() { requestAnimationFrame(() => { const e = this._root.getElementById("edsec"); if (e) e.scrollIntoView({ behavior: "smooth", block: "start" }); }); }

  async _ws(msg, okView) {
    this._setMsg(this.t("saving"), false);
    try {
      const r = await this._hass.callWS(msg);
      if (okView) { this._view = okView; this._msg = ""; this._render(); }
      return r;
    } catch (err) {
      const key = "err_" + (err.code || "");
      this._setMsg(TEXTS.en[key] ? this.t(key, { d: err.message || "" }) : (err.message || String(err)), true);
      return null;
    }
  }

  _clickAdmin(act, el, e) {
    const v = this._view;
    switch (act) {
      case "tab": v.tab = el.dataset.tab; this._render(); return true;
      case "arr-add": { const list = this._getPath(v.draft, el.dataset.path); list.push(this._newObj(el.dataset.tpl)); this._render(); return true; }
      case "arr-del": { const list = this._getPath(v.draft, el.dataset.path); list.splice(Number(el.dataset.i), 1); this._render(); return true; }
      case "day": {
        const days = this._getPath(v.draft, el.dataset.path), d = Number(el.dataset.d);
        let set = days.length ? [...days] : [0, 1, 2, 3, 4, 5, 6];
        set = set.includes(d) ? set.filter((x) => x !== d) : [...set, d].sort();
        if (!set.length) set = [d];
        days.splice(0, days.length, ...(set.length === 7 ? [] : set));
        this._render();
        return true;
      }
      case "tpl-apply": {
        const sel = this._root.getElementById("tplsel");
        if (!sel || !sel.value) return true;
        this._applyTemplateToDraft(el.dataset.kind, sel.value, v.draft, "");
        this._msg = this.t("template_applied"); this._msgErr = false;
        this._render();
        return true;
      }
      case "tpl-from": {
        const name = prompt(this.t("template_name"), "");
        if (!name) return true;
        const kind = el.dataset.kind;
        const cfg = kind === "light" ? { lights: clone(v.draft.lights), light_auto: v.draft.light_auto } : { [kind]: clone(v.draft[kind]) };
        this._hass.callWS({ type: "terrarium/save_template", template: { kind, name, config: cfg } })
          .then(() => this._setMsg(this.t("template_saved"), false)).catch((err) => this._setMsg(err.message || String(err), true));
        return true;
      }
      // light sources
      case "light-types": this._view = { name: "ltypes" }; this._render(); return true;
      case "lt-new": v.draft = { id: "", name: "", category: "led", watt: 0, restrike_min: 0, color: "#fff6e0" }; this._msg = ""; this._render(); this._scrollEd(); return true;
      case "lt-edit": v.draft = clone((this._data.light_types || []).find((t) => t.id === el.dataset.id)); this._msg = ""; this._render(); this._scrollEd(); return true;
      case "lt-cancel": v.draft = null; this._render(); return true;
      case "lt-save": { const d = { ...v.draft }; if (!d.id) delete d.id; this._ws({ type: "terrarium/save_light_type", light_type: d }, { name: "ltypes" }); return true; }
      case "lt-del": if (confirm(this.t("confirm_delete"))) this._ws({ type: "terrarium/delete_light_type", type_id: v.draft.id }, { name: "ltypes" }); return true;
      // templates
      case "templates": this._view = { name: "tpls" }; this._render(); return true;
      case "tpl-new": {
        const kind = el.dataset.kind;
        const config = kind === "light" ? { lights: [this._newObj("light")], light_auto: true } : kind === "rain"
          ? { rain: { enabled: true, profiles: [this._newObj("profile_runs")], manual_duration: 30, max_duration: 600, min_pause: 0, hum_start: { enabled: false, below: 60, duration: 30, min_pause: 60 }, hum_block: { enabled: false, above: 90 } } }
          : { vent: { enabled: true, profiles: [], min_run: 5, temp_on: { enabled: false, above: 32, hyst: 1 }, hum_on: { enabled: false, above: 90, hyst: 5 } } };
        this._view = { name: "tpl", draft: { id: "", kind, name: "", default_new: false, config } }; this._msg = ""; this._render(); return true;
      }
      case "tpl-edit": this._view = { name: "tpl", draft: clone((this._data.templates || []).find((t) => t.id === el.dataset.id)) }; this._msg = ""; this._render(); return true;
      case "tpl-back": this._view = { name: "tpls" }; this._render(); return true;
      case "tpl-save": { const d = clone(v.draft); if (!d.id) delete d.id; this._ws({ type: "terrarium/save_template", template: d }, { name: "tpls" }); return true; }
      case "tpl-del": if (confirm(this.t("confirm_delete"))) this._ws({ type: "terrarium/delete_template", template_id: v.draft.id }, { name: "tpls" }); return true;
      // groups
      case "groups": this._view = { name: "groups" }; this._render(); return true;
      case "grp-new": v.draft = { id: "", kind: el.dataset.kind, name: "", members: [] }; this._msg = ""; this._render(); this._scrollEd(); return true;
      case "grp-edit": { const g = (this._data.groups || []).find((x) => x.id === el.dataset.id); v.draft = { id: g.id, kind: g.kind, name: g.name, members: [...g.members] }; this._msg = ""; this._render(); this._scrollEd(); return true; }
      case "grp-cancel": v.draft = null; this._render(); return true;
      case "grp-member": {
        const id = el.dataset.id;
        v.draft.members = el.checked ? [...new Set([...v.draft.members, id])] : v.draft.members.filter((m) => m !== id);
        return true;
      }
      case "grp-save": {
        if (v.draft.members.length < 2) { this._setMsg(this.t("err_layout_group_members"), true); return true; }
        const d = { ...v.draft }; if (!d.id) delete d.id;
        this._ws({ type: "terrarium/save_group", group: d }, { name: "groups" }); return true;
      }
      case "grp-del": if (confirm(this.t("confirm_delete_group"))) this._ws({ type: "terrarium/delete_group", group_id: v.draft.id }, { name: "groups" }); return true;
      // rain by hand
      case "rain-now": e.stopPropagation(); this._busy[el.dataset.ent] = this._devState(el.dataset.ent); el.classList.add("busy");
        this._hass.callWS({ type: "terrarium/rain", compartment_id: el.dataset.comp, action: "start" }); return true;
      case "rain-stop": e.stopPropagation(); this._hass.callWS({ type: "terrarium/rain", compartment_id: el.dataset.comp, action: "stop" }); return true;
      case "auto-toggle": e.stopPropagation(); if (el.dataset.ent) this._hass.callService("switch", "toggle", { entity_id: el.dataset.ent }); return true;
    }
    return false;
  }

  _time(iso) {
    if (!iso) return "";
    const d = new Date(iso), now = new Date();
    const hm = d.toLocaleTimeString(this.lang, { hour: "2-digit", minute: "2-digit" });
    if (d.toDateString() === now.toDateString()) return hm;
    const tomorrow = new Date(now.getTime() + 86400000);
    if (d.toDateString() === tomorrow.toDateString()) return `${this.t("tomorrow")} ${hm}`;
    return `${d.toLocaleDateString(this.lang, { weekday: "short" })} ${hm}`;
  }

  _autoChip(c, kind, on) {
    const ent = c.entities?.[`cfg_${kind}_auto`];
    if (!ent) return "";
    return `<button class="achip ${on ? "on" : ""}" data-act="auto-toggle" data-ent="${esc(ent)}" title="${this.t(kind + "_auto")}"><ha-icon icon="mdi:${on ? "robot" : "robot-off"}"></ha-icon><span>${on ? this.t("auto_on") : this.t("auto_off")}</span></button>`;
  }

  _groupNote(c, kind) {
    const g = c.groups?.[kind];
    return g ? `<div class="muted small" style="margin:-4px 0 8px"><ha-icon icon="mdi:link-variant" style="--mdc-icon-size:14px"></ha-icon> ${esc(this.t("together_with", { m: g.members.join(", ") }))}</div>` : "";
  }

  _autoBoxes(c) {
    const A = c.auto || {};
    let h = "";
    const L = A.light || {};
    if ((L.lights || []).length) {
      h += `<div class="box o2"><div class="row" style="margin-bottom:8px"><h3 style="margin:0">${this.t("tab_light")}</h3><span class="spacer"></span>${this._autoChip(c, "light", L.auto)}</div>${this._groupNote(c, "light")}<div class="devs">`;
      for (const l of L.lights) {
        const on = isOn(this._devState(l.entity_id) ?? l.state);
        const na = !l.entity_id || l.state === null || l.state === "unavailable";
        let sub = na ? this.t(l.entity_id ? "unavailable" : "no_socket") : on ? this.t("on") : this.t("off");
        if (l.next && l.auto) sub += ` · ${on ? this.t("until_t") : this.t("from_t")} ${this._time(l.next)}`;
        if (l.locked_until) sub = `${this.t("restrike_short")} ${this._time(l.locked_until)}`;
        if (l.overheat) sub += ` · ${this.t("overheat_short")}`;
        h += `<div class="dev ${on ? "on" : ""} ${this._busy[l.entity_id] !== undefined ? "busy" : ""}" role="button" ${l.entity_id ? `data-act="toggle" data-ent="${esc(l.entity_id)}"` : ""}>`;
        h += `<ha-icon icon="${l.category === "night" ? "mdi:weather-night" : l.category === "hid" ? "mdi:lightbulb-on" : "mdi:lightbulb"}" style="color:${on ? esc(l.color || "#f9a825") : "inherit"}"></ha-icon>`;
        h += `<span class="dn">${esc(l.name)}</span><span class="muted small">${esc(sub)}</span>${!l.auto ? `<span class="muted small">${this.t("manual_only")}</span>` : ""}</div>`;
      }
      h += `</div></div>`;
    }
    const R = A.rain || {};
    if (R.configured) {
      const ent = R.entity_id, running = !!R.running_until;
      h += `<div class="box o2"><div class="row" style="margin-bottom:8px"><h3 style="margin:0">${this.t("tab_rain")}</h3><span class="spacer"></span>${this._autoChip(c, "rain", R.auto)}</div>${this._groupNote(c, "rain")}`;
      h += `<div class="row" style="flex-wrap:wrap;gap:8px">`;
      h += running ? `<button class="b warn" data-act="rain-stop" data-comp="${esc(c.id)}"><ha-icon icon="mdi:stop"></ha-icon>${this.t("rain_stop")}</button>`
        : `<button class="b pri ${this._busy[ent] !== undefined ? "busy" : ""}" data-act="rain-now" data-comp="${esc(c.id)}" data-ent="${esc(ent)}"><ha-icon icon="mdi:weather-pouring"></ha-icon>${this.t("rain_now")} (${R.manual_duration} s)</button>`;
      h += `</div><div class="kv">`;
      h += `<span>${this.t("state")}</span><b>${running ? this.t("rain_running", { t: this._time(R.running_until) }) : isOn(R.state) ? this.t("on") : this.t("off")}</b>`;
      if (R.next_run && R.auto) h += `<span>${this.t("next_run")}</span><b>${this._time(R.next_run)} (${R.next_duration} s)</b>`;
      if (R.last_run) h += `<span>${this.t("last_run")}</span><b>${this._time(R.last_run)}</b>`;
      if (R.blocked) h += `<span>${this.t("note")}</span><b class="warnc">${this.t("rain_blocked")}</b>`;
      h += `</div></div>`;
    }
    const V = A.vent || {};
    if (V.configured) {
      const on = isOn(this._devState(V.entity_id) ?? V.state);
      h += `<div class="box o2"><div class="row" style="margin-bottom:8px"><h3 style="margin:0">${this.t("tab_vent")}</h3><span class="spacer"></span>${this._autoChip(c, "vent", V.auto)}</div>${this._groupNote(c, "vent")}<div class="devs">`;
      h += `<div class="dev ${on ? "on" : ""} ${this._busy[V.entity_id] !== undefined ? "busy" : ""}" role="button" data-act="toggle" data-ent="${esc(V.entity_id)}"><ha-icon icon="mdi:fan" ${on ? 'class="spin"' : ""}></ha-icon><span class="dn">${this.t("ventilation")}</span><span class="muted small">${on ? this.t("on") : this.t("off")}${V.next && V.auto ? ` · ${this.t("next_change")} ${this._time(V.next)}` : ""}</span></div></div>`;
      if (V.auto && V.reason) h += `<div class="muted small" style="margin-top:6px">${esc(V.reason)}</div>`;
      h += `</div>`;
    }
    if (h) h += `<div class="box o6"><h3>${this.t("log")}</h3><div id="evlog" class="muted small">…</div></div>`;
    return h;
  }

  async _loadEvents(c) {
    const units = new Set([c.label, ...Object.values(c.groups || {}).map((g) => g.name || g.members.join(", "))]);
    try {
      const r = await this._hass.callWS({ type: "terrarium/events", limit: 120 });
      const rows = (r.events || []).filter((e) => units.has(e.unit)).slice(0, 12);
      const el = this._root.getElementById("evlog");
      if (!el) return;
      el.innerHTML = rows.length ? rows.map((e) => `<div class="ev"><span>${esc(this._time(e.ts))}</span><ha-icon icon="${e.kind === "rain" ? "mdi:weather-pouring" : e.kind === "vent" ? "mdi:fan" : "mdi:lightbulb"}" style="--mdc-icon-size:16px"></ha-icon><b>${esc(e.action === "on" ? this.t("on") : e.action === "off" ? this.t("off") : this.t("skipped"))}</b><span class="ell">${esc(e.reason)}</span></div>`).join("") : "–";
    } catch (e) { /* ignore */ }
  }

  _setPath(obj, path, value) {
    const parts = path.split(".");
    let o = obj;
    for (let i = 0; i < parts.length - 1; i++) o = o[parts[i]];
    o[parts[parts.length - 1]] = value;
  }
  _getPath(obj, path) { return path.split(".").reduce((o, k) => (o ? o[k] : undefined), obj); }

  /* -------------------------------------------------------- enclosure editor */
  _openEncEditor(id) {
    let draft;
    if (id) {
      const enc = this._data.enclosures.find((e) => e.id === id);
      draft = clone({ id: enc.id, nr: enc.nr, name: enc.name, width: enc.width, height: enc.height, depth: enc.depth, color: enc.color,
        compartments: enc.compartments.map((c) => ({ id: c.id, name: c.name, x: c.x, y: c.y, width: c.width, height: c.height, depth: c.depth, look: c.look, live: c.live })) });
    } else {
      const nr = Math.max(0, ...this._data.enclosures.map((e) => e.nr)) + 1;
      draft = { id: null, nr, name: "", width: 120, height: 150, depth: 60, color: "wood", compartments: [] };
      draft.compartments = this._gridComps(draft, 2, 2, 0);
    }
    this._view = { name: "enc", draft, sel: null, snap: 5, rows: 2, cols: 2, gap: 0 };
    this._msg = ""; this._msgErr = false;
    this._render();
  }

  _gridComps(d, rows, cols, gap) {
    const out = [];
    const w = (d.width - gap * (cols - 1)) / cols, h = (d.height - gap * (rows - 1)) / rows;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      out.push({ id: `new${Math.random().toString(16).slice(2, 10)}`, name: "", x: +(c * (w + gap)).toFixed(1), y: +(r * (h + gap)).toFixed(1), width: +w.toFixed(1), height: +h.toFixed(1), depth: null, _new: true });
    }
    return out;
  }

  _labelsFor(d) {
    const map = {};
    sortComps(d.compartments).forEach((c, i) => { map[c.id] = `${d.nr}.${i + 1}`; });
    return map;
  }

  _editorProblems(d) {
    const bad = new Set();
    for (const c of d.compartments) {
      if (c.x < -0.01 || c.y < -0.01 || c.x + c.width > d.width + 0.01 || c.y + c.height > d.height + 0.01 || c.width <= 0 || c.height <= 0) bad.add(c.id);
    }
    for (let i = 0; i < d.compartments.length; i++) for (let j = i + 1; j < d.compartments.length; j++) {
      if (overlaps(d.compartments[i], d.compartments[j])) { bad.add(d.compartments[i].id); bad.add(d.compartments[j].id); }
    }
    return bad;
  }

  _editorSVGInner() {
    const v = this._view, d = v.draft;
    const W = d.width, H = d.height, cab = CABINET[d.color] || CABINET.wood;
    const labels = this._labelsFor(d), bad = this._editorProblems(d);
    const m = Math.max(W, H);
    let s = `<rect x="${-m * 0.03}" y="${-m * 0.03}" width="${W + m * 0.06}" height="${H + m * 0.06}" rx="${m * 0.015}" fill="${cab[0]}"/>`;
    s += `<rect x="0" y="0" width="${W}" height="${H}" fill="#15171a"/>`;
    for (let x = 10; x < W; x += 10) s += `<line x1="${x}" y1="0" x2="${x}" y2="${H}" stroke="#2c3036" stroke-width="${m * 0.002}"/>`;
    for (let y = 10; y < H; y += 10) s += `<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="#2c3036" stroke-width="${m * 0.002}"/>`;
    // selected one last, so it and its resize handle are on top
    for (const c of [...d.compartments].sort((a, b) => (a.id === v.sel) - (b.id === v.sel))) {
      const sel = v.sel === c.id, isBad = bad.has(c.id);
      const fs = Math.max(Math.min(c.width, c.height) * 0.16, m * 0.018);
      s += `<g class="ec" data-c="${esc(c.id)}"><rect x="${c.x}" y="${c.y}" width="${c.width}" height="${c.height}" fill="${isBad ? "rgba(229,57,53,.35)" : sel ? "rgba(3,169,244,.35)" : "rgba(120,170,120,.28)"}" stroke="${isBad ? "#e53935" : sel ? "#03a9f4" : "#9ccc9c"}" stroke-width="${m * (sel ? 0.006 : 0.004)}"/>`;
      s += `<text x="${c.x + c.width / 2}" y="${c.y + c.height / 2}" font-size="${fs}" fill="#fff" text-anchor="middle" font-weight="700" pointer-events="none">${esc(labels[c.id])}</text>`;
      s += `<text x="${c.x + c.width / 2}" y="${c.y + c.height / 2 + fs * 1.05}" font-size="${fs * 0.6}" fill="#cfd8dc" text-anchor="middle" pointer-events="none">${esc(c.name || "")} ${c.width.toFixed(0)}×${c.height.toFixed(0)}</text></g>`;
      if (sel) {
        const hs = m * (matchMedia("(pointer: coarse)").matches ? 0.07 : 0.035);
        s += `<rect class="eh" data-c="${esc(c.id)}" data-h="1" x="${c.x + c.width - hs}" y="${c.y + c.height - hs}" width="${hs}" height="${hs}" fill="#03a9f4" stroke="#fff" stroke-width="${m * 0.003}"/>`;
      }
    }
    return s;
  }

  _renderEncEditor() {
    const v = this._view, d = v.draft;
    const sel = d.compartments.find((c) => c.id === v.sel);
    const labels = this._labelsFor(d);
    const m = Math.max(d.width, d.height), pad = m * 0.05;
    let h = `<div class="wrap"><div class="head"><button class="ic" data-act="enc-cancel" title="${this.t("back")}"><ha-icon icon="mdi:arrow-left"></ha-icon></button><h2>${d.id ? this.t("enc_edit") : this.t("enc_new")}</h2></div><div class="ed"><div class="form">`;
    h += `<div class="sec"><h3>${this.t("enclosure")}</h3><div class="fields">`;
    h += `<label class="f">${this.t("number")}<input type="number" min="1" step="1" data-e="nr" value="${d.nr}"></label><label class="f">${this.t("name")}<input data-e="name" value="${esc(d.name)}"></label>`;
    h += `<label class="f">${this.t("color")}<select data-e="color">${["wood", "black", "white", "grey"].map((k) => `<option value="${k}" ${d.color === k ? "selected" : ""}>${this.t("c_" + k)}</option>`).join("")}</select></label>`;
    h += `</div><div class="muted small" style="margin:10px 0 4px">${this.t("size_total")}</div><div class="fields">`;
    h += `<label class="f">${this.t("width")}<input type="number" min="1" step="1" data-e="width" value="${d.width}"></label><label class="f">${this.t("height")}<input type="number" min="1" step="1" data-e="height" value="${d.height}"></label><label class="f">${this.t("depth")}<input type="number" min="0" step="1" data-e="depth" value="${d.depth ?? ""}"></label>`;
    h += `</div></div>`;
    h += `<div class="sec"><h3>${this.t("layout")}</h3><div class="fields"><label class="f">${this.t("rows")}<input type="number" min="1" max="12" data-g="rows" value="${v.rows}"></label><label class="f">${this.t("cols")}<input type="number" min="1" max="12" data-g="cols" value="${v.cols}"></label><label class="f">${this.t("gap")} (cm)<input type="number" min="0" step="0.5" data-g="gap" value="${v.gap}"></label></div>`;
    h += `<div class="row" style="margin-top:10px;flex-wrap:wrap"><button class="b" data-act="enc-grid"><ha-icon icon="mdi:grid"></ha-icon>${this.t("grid")}</button><button class="b" data-act="enc-add"><ha-icon icon="mdi:plus"></ha-icon>${this.t("add_comp")}</button></div>`;
    h += `<div class="fields" style="margin-top:10px"><label class="f">${this.t("snap")}<select data-g="snap">${[0.5, 1, 2.5, 5, 10].map((s) => `<option value="${s}" ${v.snap === s ? "selected" : ""}>${s} cm</option>`).join("")}</select></label></div></div>`;
    h += `<div class="sec"><h3>${this.t("selected")}</h3><div id="selbox">${this._selBox(sel, labels)}</div></div>`;
    h += `<div class="sec"><h3>${this.t("compartments")}</h3><div class="muted small" style="margin-bottom:6px">${this.t("numbering_hint")}</div><div class="clist" id="clist">${this._compList(d, labels)}</div></div>`;
    h += `</div><div class="col"><div class="box edbox"><svg class="edsvg" id="edsvg" viewBox="${-pad} ${-pad} ${d.width + 2 * pad} ${d.height + 2 * pad}" xmlns="http://www.w3.org/2000/svg"><g id="lay">${this._editorSVGInner()}</g></svg></div>`;
    h += `<div class="actions">${d.id ? `<button class="b warn" data-act="enc-delete"><ha-icon icon="mdi:delete"></ha-icon>${this.t("delete")}</button>` : ""}<span id="msg" class="${this._msgErr ? "err" : "ok"}">${esc(this._msg)}</span><span class="spacer"></span><button class="b" data-act="enc-cancel">${this.t("cancel")}</button><button class="b pri" data-act="enc-save"><ha-icon icon="mdi:content-save"></ha-icon>${this.t("save")}</button></div></div>`;
    return h + `</div></div>`;
  }

  _selBox(sel, labels) {
    if (!sel) return `<div class="muted small">${this.t("none_selected")}</div>`;
    let h = `<div class="row" style="margin-bottom:8px"><span class="nr">${esc(labels[sel.id])}</span><span class="spacer"></span><button class="b warn" data-act="enc-remove"><ha-icon icon="mdi:delete"></ha-icon>${this.t("remove")}</button></div><div class="fields">`;
    h += `<label class="f">${this.t("name")}<input data-s="name" value="${esc(sel.name || "")}"></label>`;
    for (const [k, l] of [["x", this.t("pos_x")], ["y", this.t("pos_y")], ["width", this.t("width")], ["height", this.t("height")], ["depth", this.t("depth")]]) {
      h += `<label class="f">${l} (cm)<input type="number" step="0.5" min="0" data-s="${k}" value="${sel[k] ?? ""}"></label>`;
    }
    return h + `</div>`;
  }

  _compList(d, labels) {
    const bad = this._editorProblems(d);
    return sortComps(d.compartments).map((c) => `<div class="ci ${this._view.sel === c.id ? "sel" : ""}" data-act="enc-sel" data-c="${esc(c.id)}"><span class="nr">${esc(labels[c.id])}</span><span>${esc(c.name || "–")}</span><span class="spacer"></span><span class="muted small">${c.width.toFixed(1).replace(/\.0$/, "")}×${c.height.toFixed(1).replace(/\.0$/, "")} @ ${c.x.toFixed(1).replace(/\.0$/, "")}/${c.y.toFixed(1).replace(/\.0$/, "")}</span>${bad.has(c.id) ? `<ha-icon icon="mdi:alert" style="color:#e53935"></ha-icon>` : ""}</div>`).join("");
  }

  _refreshEditor(full) {
    const lay = this._root.getElementById("lay");
    if (lay) lay.innerHTML = this._editorSVGInner();
    const d = this._view.draft, labels = this._labelsFor(d);
    const cl = this._root.getElementById("clist");
    if (cl) cl.innerHTML = this._compList(d, labels);
    if (full) {
      const sb = this._root.getElementById("selbox");
      if (sb) sb.innerHTML = this._selBox(d.compartments.find((c) => c.id === this._view.sel), labels);
    }
  }

  _bindEditor() {
    const svg = this._root.getElementById("edsvg");
    if (!svg) return;
    const pt = (e) => { const p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY; return p.matrixTransform(svg.getScreenCTM().inverse()); };
    svg.addEventListener("pointerdown", (e) => {
      const el = e.target.closest("[data-c]");
      const v = this._view;
      if (!el) { if (v.sel) { v.sel = null; this._refreshEditor(true); } return; }
      const c = v.draft.compartments.find((x) => x.id === el.dataset.c);
      if (!c) return;
      const selChanged = v.sel !== c.id;
      v.sel = c.id;
      this._drag = { mode: el.dataset.h ? "resize" : "move", start: pt(e), orig: { ...c }, c, moved: false };
      svg.setPointerCapture(e.pointerId);
      if (selChanged) this._refreshEditor(true);
      e.preventDefault();
    });
    svg.addEventListener("pointermove", (e) => {
      const g = this._drag;
      if (!g) return;
      const d = this._view.draft, snap = this._view.snap || 1;
      const p = pt(e), dx = p.x - g.start.x, dy = p.y - g.start.y;
      const sn = (val) => Math.round(val / snap) * snap;
      if (g.mode === "move") {
        g.c.x = Math.min(Math.max(0, sn(g.orig.x + dx)), Math.max(0, d.width - g.c.width));
        g.c.y = Math.min(Math.max(0, sn(g.orig.y + dy)), Math.max(0, d.height - g.c.height));
      } else {
        g.c.width = Math.min(Math.max(snap, sn(g.orig.width + dx)), d.width - g.c.x);
        g.c.height = Math.min(Math.max(snap, sn(g.orig.height + dy)), d.height - g.c.y);
      }
      g.moved = true;
      this._refreshEditor(false);
    });
    const end = () => { if (this._drag) { const moved = this._drag.moved; this._drag = null; if (moved) this._refreshEditor(true); } };
    svg.addEventListener("pointerup", end);
    svg.addEventListener("pointercancel", end);
  }

  _freeSpot(d) {
    const snap = this._view.snap || 1;
    const sizes = [[Math.min(d.width / 2, 60), Math.min(d.height / 2, 50)], [d.width / 3, d.height / 3], [d.width / 4, d.height / 4], [20, 20], [10, 10], [5, 5]];
    for (let [w, h] of sizes) {
      w = Math.max(snap, Math.round(w / snap) * snap); h = Math.max(snap, Math.round(h / snap) * snap);
      for (let y = 0; y + h <= d.height + 0.01; y += snap) for (let x = 0; x + w <= d.width + 0.01; x += snap) {
        const cand = { x, y, width: w, height: h };
        if (!d.compartments.some((c) => overlaps(c, cand))) return cand;
      }
    }
    return null;
  }

  async _saveEnclosure() {
    const d = this._view.draft;
    const bad = this._editorProblems(d);
    if (bad.size) { const lb = this._labelsFor(d); this._setMsg(this.t("err_layout_overlap", { d: [...bad].map((id) => lb[id]).join(", ") }), true); return; }
    const payload = {
      id: d.id || undefined, nr: d.nr, name: d.name, width: d.width, height: d.height, depth: d.depth, color: d.color,
      compartments: d.compartments.map((c) => ({ id: c._new ? undefined : c.id, name: c.name || "", x: c.x, y: c.y, width: c.width, height: c.height, depth: c.depth })),
    };
    if (!payload.id) delete payload.id;
    this._setMsg(this.t("saving"), false);
    try {
      await this._hass.callWS({ type: "terrarium/save_enclosure", enclosure: payload });
      this._view = { name: "overview" };
      this._msg = "";
      this._render();
    } catch (err) {
      const key = "err_" + (err.code || "");
      this._setMsg(TEXTS.en[key] ? this.t(key, { d: err.message || "" }) : (err.message || String(err)), true);
    }
  }

  _setMsg(text, isErr) {
    this._msg = text; this._msgErr = isErr;
    const el = this._root.getElementById("msg");
    if (el) { el.textContent = text; el.className = isErr ? "err" : "ok"; }
  }

  /* -------------------------------------------------------- events */
  _click(e) {
    const el = e.target.closest("[data-act]");
    if (!el) return;
    const act = el.dataset.act, v = this._view;
    if (this._clickAdmin(act, el, e)) return;
    switch (act) {
      case "open": {
        if (v.name === "enc") return;
        this._view = { name: "details", comp: el.dataset.comp };
        this._render();
        break;
      }
      case "back": this._view = { name: "overview" }; this._render(); break;
      case "model": {
        e.stopPropagation();
        this._modelPref[el.dataset.enc] = !this._modelShown(el.dataset.enc);
        try { localStorage.setItem("terrarium-model", JSON.stringify(this._modelPref)); } catch (err) { /* private mode */ }
        this._render();
        break;
      }
      case "toggle": {
        e.stopPropagation();
        const ent = el.dataset.ent, domain = ent.split(".")[0];
        this._busy[ent] = this._devState(ent);
        el.classList.add("busy");
        setTimeout(() => { if (this._busy[ent] !== undefined) { delete this._busy[ent]; if (["overview", "details"].includes(this._view.name)) this._render(); } }, 6000);
        if (domain === "script") this._hass.callService("script", "turn_on", { entity_id: ent });
        else if (domain === "automation") this._hass.callService("automation", "trigger", { entity_id: ent });
        else this._hass.callService("homeassistant", "toggle", { entity_id: ent });
        break;
      }
      case "comp-settings": this._openCompSettings(el.dataset.comp); break;
      case "comp-cancel": this._view = { name: "details", comp: v.comp }; this._render(); break;
      case "comp-save": this._saveComp(); break;
      case "chip-del": {
        const list = this._getPath(v.draft, el.dataset.path);
        list.splice(Number(el.dataset.i), 1);
        this._render();
        break;
      }
      case "dev-add": v.draft.devices.push({ entity_id: "", kind: "light", name: "" }); this._render(); break;
      case "dev-del": v.draft.devices.splice(Number(el.dataset.i), 1); this._render(); break;
      case "test-notify": this._testNotify(); break;
      case "enc-new": this._openEncEditor(null); break;
      case "enc-edit": e.stopPropagation(); this._openEncEditor(el.dataset.enc); break;
      case "enc-cancel": this._view = { name: "overview" }; this._render(); break;
      case "enc-save": this._saveEnclosure(); break;
      case "enc-sel": v.sel = el.dataset.c; this._refreshEditor(true); break;
      case "enc-grid": {
        if (v.draft.compartments.length && !confirm(this.t("confirm_grid"))) return;
        v.draft.compartments = this._gridComps(v.draft, Math.max(1, v.rows | 0), Math.max(1, v.cols | 0), Math.max(0, Number(v.gap) || 0));
        v.sel = null; this._refreshEditor(true);
        break;
      }
      case "enc-add": {
        const spot = this._freeSpot(v.draft);
        if (!spot) { this._setMsg(this.t("no_space"), true); return; }
        const c = { id: `new${Math.random().toString(16).slice(2, 10)}`, name: "", depth: null, _new: true, ...spot };
        v.draft.compartments.push(c); v.sel = c.id; this._refreshEditor(true);
        break;
      }
      case "enc-remove": {
        v.draft.compartments = v.draft.compartments.filter((c) => c.id !== v.sel);
        v.sel = null; this._refreshEditor(true);
        break;
      }
      case "enc-delete": {
        if (!confirm(this.t("confirm_delete_enc", { nr: v.draft.nr }))) return;
        this._hass.callWS({ type: "terrarium/delete_enclosure", enclosure_id: v.draft.id }).then(() => { this._view = { name: "overview" }; this._render(); })
          .catch((err) => this._setMsg(err.message || String(err), true));
        break;
      }
    }
  }

  _input(e) {
    const el = e.target, v = this._view;
    if (v.name === "comp" && el.dataset.add && el.tagName === "INPUT" && this._hass.states[el.value.trim()]) {
      const list = this._getPath(v.draft, el.dataset.add), val = el.value.trim();
      if (!list.includes(val)) list.push(val);
      this._render();
      return;
    }
    if (v.draft && v.name !== "enc" && el.dataset.path && el.type !== "checkbox" && el.tagName !== "SELECT") {
      this._setPath(v.draft, el.dataset.path, el.dataset.type === "num" ? num(el.value) : el.value);
    }
    if (v.name === "enc") {
      if (el.dataset.e) {
        const k = el.dataset.e;
        v.draft[k] = ["nr", "width", "height", "depth"].includes(k) ? num(el.value) : el.value;
        if (["width", "height"].includes(k) && v.draft[k] > 0) {
          const svg = this._root.getElementById("edsvg"), m = Math.max(v.draft.width, v.draft.height), pad = m * 0.05;
          if (svg) svg.setAttribute("viewBox", `${-pad} ${-pad} ${v.draft.width + 2 * pad} ${v.draft.height + 2 * pad}`);
        }
        if (v.draft.width > 0 && v.draft.height > 0) this._refreshEditor(false);
      } else if (el.dataset.g && el.tagName !== "SELECT") {
        v[el.dataset.g] = num(el.value) ?? 0;
      } else if (el.dataset.s) {
        const c = v.draft.compartments.find((x) => x.id === v.sel);
        if (!c) return;
        const k = el.dataset.s;
        if (k === "name") c.name = el.value;
        else { const n = num(el.value); if (k === "depth") c.depth = n; else if (n !== null) c[k] = n; }
        this._refreshEditor(false);
      }
    }
  }

  _change(e) {
    const el = e.target, v = this._view;
    if (v.name === "comp") {
      if (el.dataset.add) {
        const val = el.value.trim();
        if (val && (this._hass.states[val] || el.dataset.add === "notify.targets")) {
          const list = this._getPath(v.draft, el.dataset.add);
          if (!list.includes(val)) list.push(val);
          this._render();
        }
        return;
      }
    }
    if (v.draft && v.name !== "enc" && el.dataset.path) {
      if (el.type === "checkbox") this._setPath(v.draft, el.dataset.path, el.checked);
      else if (el.tagName === "SELECT") this._setPath(v.draft, el.dataset.path, el.value);
      else return;
      if (el.dataset.rr) this._render();
    }
    if (v.name === "enc") {
      if (el.dataset.g === "snap") v.snap = Number(el.value);
      if (el.dataset.e === "color") { v.draft.color = el.value; this._refreshEditor(false); }
    }
  }

  async _saveComp() {
    const v = this._view;
    const d = clone(v.draft);
    d.devices = d.devices.filter((x) => x.entity_id && x.entity_id.includes("."));
    // shared (group) parts are only sent when they belong to this terrarium's own tab or the group
    this._setMsg(this.t("saving"), false);
    try {
      await this._hass.callWS({ type: "terrarium/save_compartment", compartment_id: v.comp, settings: d });
      this._view = { name: "details", comp: v.comp };
      this._msg = "";
      this._render();
    } catch (err) { this._setMsg(err.message || String(err), true); }
  }

  async _testNotify() {
    const v = this._view, out = this._root.getElementById("tn");
    if (!v.draft.notify.targets.length) { if (out) { out.textContent = this.t("no_targets"); out.className = "small err"; } return; }
    try {
      // save first so the test uses the current recipients
      const d = clone(v.draft); d.devices = d.devices.filter((x) => x.entity_id && x.entity_id.includes("."));
      await this._hass.callWS({ type: "terrarium/save_compartment", compartment_id: v.comp, settings: d });
      const r = await this._hass.callWS({ type: "terrarium/test_notify", compartment_id: v.comp });
      if (out) { out.textContent = r.failed && r.failed.length ? this.t("test_failed", { d: r.failed.join(", ") }) : this.t("test_sent"); out.className = r.failed && r.failed.length ? "small err" : "small ok"; }
    } catch (err) { if (out) { out.textContent = err.message || String(err); out.className = "small err"; } }
  }
}

class TerrariumCard extends TerrariumView {}

class TerrariumPanel extends TerrariumView {
  get isPanel() { return true; }
  set narrow(v) { this._narrow = v; }
  set panel(p) { this._panelCfg = p; }
  set route(r) {}
  _panelShell(html) {
    const title = (this._panelCfg && this._panelCfg.title) || this.t("title");
    return `<style>.top{display:flex;align-items:center;gap:4px;height:56px;padding:0 8px;background:var(--app-header-background-color,var(--primary-color));color:var(--app-header-text-color,#fff);position:sticky;top:0;z-index:2}
      .top .t{font-size:20px;margin-left:8px} :host{background:var(--primary-background-color);min-height:100vh;display:block}</style>
      <div class="top"><ha-menu-button id="menu"></ha-menu-button><span class="t">${esc(title)}</span></div><div class="panel">${html}</div>`;
  }
  _render() {
    super._render();
    const mb = this._root.getElementById("menu");
    if (mb) { mb.hass = this._hass; mb.narrow = this._narrow; }
  }
}

customElements.define("terrarium-card", TerrariumCard);
customElements.define("terrarium-panel", TerrariumPanel);

window.customCards = window.customCards || [];
window.customCards.push({ type: "terrarium-card", name: "Terrarium", description: "Overview, model, details and settings of your terrariums", preview: false });
console.info(`%c TERRARIUM %c ${VERSION} `, "background:#43a047;color:#fff;border-radius:3px 0 0 3px", "background:#2a2d31;color:#fff;border-radius:0 3px 3px 0");

// for tests / other cards
window.TerrariumModel = { enclosureSVG, gaugeSVG };
})();
