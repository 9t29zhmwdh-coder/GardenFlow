const API  = window.location.origin;
const WS   = (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host + "/ws";
const MAX_POINTS = 60;

const TRANSLATIONS = {
  en: {
    live: "Live", disconnected: "Disconnected",
    zones: "ZONES", sensors: "SENSORS", rules: "RULES", refresh: "Refresh",
    waitingSensors: "Waiting for sensor data. Start",
    waitingSensorsSuffix: "to simulate data.",
    manualPump: "Manual pump:", stop: "Stop",
    automationRules: "Automation Rules",
    noRules: "No rules yet.",
    confirmDeleteRule: "Delete rule?",
    newRule: "New rule", editRule: "Edit rule", edit: "Edit", save: "Save", cancel: "Cancel",
    ruleName: "Name", when: "When", addCondition: "+ Condition", logicAnd: "all conditions (AND)",
    logicOr: "any condition (OR)", then: "Then", zone: "Zone", durationMin: "Run for (minutes)",
    message: "Alert text", cooldownHours: "Then pause this rule for (hours)",
    actionTypes: { activate_pump: "Start pump", deactivate_pump: "Stop pump", send_alert: "Send alert" },
    errNameRequired: "Give the rule a name.", errZoneRequired: "Every condition and the action need a zone.",
    errThreshold: "Every condition needs a number.", errSave: "Could not save the rule:", dismiss: "Dismiss",
    sensorTypes: { moisture: "Moisture", temperature: "Temperature", humidity: "Humidity", light: "Light" },
  },
  de: {
    live: "Live", disconnected: "Getrennt",
    zones: "ZONEN", sensors: "SENSOREN", rules: "REGELN", refresh: "Aktualisieren",
    waitingSensors: "Warte auf Sensordaten. Starte",
    waitingSensorsSuffix: "um Daten zu simulieren.",
    manualPump: "Pumpe manuell:", stop: "Stop",
    automationRules: "Automatisierungsregeln",
    noRules: "Noch keine Regeln.",
    confirmDeleteRule: "Regel löschen?",
    newRule: "Neue Regel", editRule: "Regel bearbeiten", edit: "Bearbeiten", save: "Speichern", cancel: "Abbrechen",
    ruleName: "Name", when: "Wenn", addCondition: "+ Bedingung", logicAnd: "alle Bedingungen (UND)",
    logicOr: "eine der Bedingungen (ODER)", then: "Dann", zone: "Zone", durationMin: "Laufzeit (Minuten)",
    message: "Alarmtext", cooldownHours: "Danach Regel pausieren für (Stunden)",
    actionTypes: { activate_pump: "Pumpe starten", deactivate_pump: "Pumpe stoppen", send_alert: "Alarm senden" },
    errNameRequired: "Gib der Regel einen Namen.", errZoneRequired: "Jede Bedingung und die Aktion brauchen eine Zone.",
    errThreshold: "Jede Bedingung braucht eine Zahl.", errSave: "Regel konnte nicht gespeichert werden:", dismiss: "Ausblenden",
    sensorTypes: { moisture: "Feuchte", temperature: "Temperatur", humidity: "Luftf.", light: "Licht" },
  },
};

// Chart.js instances live outside Alpine's reactive state on purpose: Alpine
// wraps x-data in a Proxy for reactivity, and Chart.js instances contain
// circular internal references (canvas/scale/plugin cross-links) that blow
// the stack when Alpine tries to deeply proxy-wrap them ("Maximum call stack
// size exceeded"), breaking every re-render on the page, including things
// unrelated to charts like the language toggle.
const charts = {};    // { "zone1.moisture": Chart }

const SENSOR_TYPES = ["moisture", "temperature", "humidity", "light"];
const OPERATORS = ["<", "<=", ">", ">=", "=="];
const ACTION_TYPES = ["activate_pump", "deactivate_pump", "send_alert"];

// An explicit choice wins; otherwise follow the browser's language.
function initialLang() {
  const stored = localStorage.getItem("gardenflow_lang");
  if (stored === "en" || stored === "de") return stored;
  return (navigator.language || "en").toLowerCase().startsWith("de") ? "de" : "en";
}

function blankCondition(zone) {
  return { sensor_type: "moisture", zone, operator: "<", threshold: 30 };
}

// The form edits minutes and hours; the API stores seconds.
function ruleToForm(rule) {
  return {
    id: rule.id,
    name: rule.name,
    enabled: rule.enabled,
    condition_logic: rule.condition_logic,
    conditions: rule.conditions.map(c => ({ ...c })),
    action: {
      type: rule.action.type,
      zone: rule.action.zone,
      minutes: rule.action.duration_seconds ? rule.action.duration_seconds / 60 : null,
      message: rule.action.message || "",
    },
    cooldownHours: rule.cooldown_seconds / 3600,
  };
}

function formToRule(form) {
  const pump = form.action.type === "activate_pump";
  return {
    name: form.name.trim(),
    enabled: form.enabled,
    condition_logic: form.condition_logic,
    conditions: form.conditions.map(c => ({ ...c, zone: c.zone.trim(), threshold: Number(c.threshold) })),
    action: {
      type: form.action.type,
      zone: form.action.zone.trim(),
      duration_seconds: pump && form.action.minutes ? Math.round(form.action.minutes * 60) : null,
      message: form.action.type === "send_alert" ? form.action.message : null,
    },
    cooldown_seconds: Math.round(Number(form.cooldownHours || 0) * 3600),
  };
}

document.addEventListener("alpine:init", () => {
  Alpine.data("gardenflow", () => ({
    connected: false,
    ws: null,
    sensors: {},   // { "zone1.moisture": { value, unit, zone, ts } }
    rules: [],
    zones: [],
    lang: initialLang(),
    alerts: [],       // alerts from rules, newest first, until dismissed
    ruleForm: null,   // the rule being created or edited, null when the editor is closed
    ruleError: "",
    SENSOR_TYPES, OPERATORS, ACTION_TYPES,

    // ---- i18n ----
    t(key) {
      return TRANSLATIONS[this.lang][key] ?? key;
    },
    toggleLang() {
      this.lang = this.lang === "en" ? "de" : "en";
      localStorage.setItem("gardenflow_lang", this.lang);
    },

    // ---- Lifecycle ----
    async init() {
      await this.loadRules();
      await this.loadSensors();
      this.connectWS();
      setInterval(() => this.connectWS(), 5000);
    },

    async loadSensors() {
      const res = await fetch(`${API}/api/sensors`);
      const data = await res.json();
      data.forEach(s => this.handleSensor({
        zone: s.zone, sensor_type: s.sensor_type, value: s.value, unit: s.unit, timestamp: s.timestamp,
      }));
    },

    connectWS() {
      if (this.ws && this.ws.readyState <= 1) return;
      const ws = new WebSocket(WS);
      ws.onopen  = () => { this.connected = true; };
      ws.onclose = () => { this.connected = false; this.ws = null; };
      ws.onerror = () => { this.connected = false; };
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === "sensor") this.handleSensor(msg);
        if (msg.type === "alert") this.alerts.unshift({ ...msg, key: msg.timestamp + msg.zone });
      };
      this.ws = ws;
    },

    handleSensor(msg) {
      const key = `${msg.zone}.${msg.sensor_type}`;
      this.sensors[key] = { value: msg.value, unit: msg.unit, zone: msg.zone, type: msg.sensor_type, ts: msg.timestamp };
      this.zones = [...new Set(Object.values(this.sensors).map(s => s.zone))].sort();
      this.$nextTick(() => this.pushChart(key, msg.value));
    },

    zoneSensors(zone) {
      return Object.values(this.sensors).filter(s => s.zone === zone);
    },

    // ---- Charts ----
    pushChart(key, value) {
      const canvas = document.getElementById("chart-" + key);
      if (!canvas) return;
      if (!charts[key]) {
        charts[key] = new Chart(canvas, {
          type: "line",
          data: { labels: [], datasets: [{ data: [], borderColor: "#52b788", backgroundColor: "rgba(82,183,136,.12)", fill: true, tension: 0.35, pointRadius: 0 }] },
          options: {
            animation: false,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { grid: { color: "#eee" } } },
            responsive: true, maintainAspectRatio: false,
          },
        });
      }
      const chart = charts[key];
      const now = new Date().toLocaleTimeString();
      chart.data.labels.push(now);
      chart.data.datasets[0].data.push(value);
      if (chart.data.labels.length > MAX_POINTS) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
      }
      chart.update("none");
    },

    label(type) {
      return TRANSLATIONS[this.lang].sensorTypes[type] ?? type;
    },

    // ---- Manual pump ----
    async pumpOn(zone, duration = 10) {
      await fetch(`${API}/api/actuators/${zone}/pump`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "on", duration }),
      });
    },
    async pumpOff(zone) {
      await fetch(`${API}/api/actuators/${zone}/pump`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "off" }),
      });
    },

    // ---- Rules ----
    async loadRules() {
      const res = await fetch(`${API}/api/rules`);
      this.rules = await res.json();
    },
    async toggleRule(rule) {
      rule.enabled = !rule.enabled;
      await fetch(`${API}/api/rules/${rule.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formToRule({ ...ruleToForm(rule), enabled: rule.enabled })),
      });
    },
    async deleteRule(id) {
      if (!confirm(this.t("confirmDeleteRule"))) return;
      await fetch(`${API}/api/rules/${id}`, { method: "DELETE" });
      await this.loadRules();
    },

    // ---- Rule editor ----
    newRule() {
      const zone = this.zones[0] || "";
      this.ruleError = "";
      this.ruleForm = ruleToForm({
        name: "", enabled: true, condition_logic: "AND",
        conditions: [blankCondition(zone)],
        action: { type: "activate_pump", zone, duration_seconds: 300 },
        cooldown_seconds: 6 * 3600,
      });
    },
    editRule(rule) {
      this.ruleError = "";
      this.ruleForm = ruleToForm(rule);
    },
    addCondition() {
      this.ruleForm.conditions.push(blankCondition(this.ruleForm.action.zone));
    },
    removeCondition(index) {
      this.ruleForm.conditions.splice(index, 1);
    },
    ruleFormProblem() {
      const f = this.ruleForm;
      if (!f.name.trim()) return this.t("errNameRequired");
      if (!f.action.zone.trim() || f.conditions.some(c => !c.zone.trim())) return this.t("errZoneRequired");
      if (f.conditions.some(c => c.threshold === "" || Number.isNaN(Number(c.threshold)))) return this.t("errThreshold");
      return "";
    },
    async saveRule() {
      this.ruleError = this.ruleFormProblem();
      if (this.ruleError) return;
      const id = this.ruleForm.id;
      const res = await fetch(id ? `${API}/api/rules/${id}` : `${API}/api/rules`, {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formToRule(this.ruleForm)),
      });
      if (!res.ok) {
        this.ruleError = `${this.t("errSave")} ${await apiErrorText(res)}`;
        return;
      }
      this.ruleForm = null;
      await this.loadRules();
    },
    actionLabel(type) {
      return TRANSLATIONS[this.lang].actionTypes[type] ?? type;
    },

    ruleConditionSummary(rule) {
      return rule.conditions.map(c =>
        `${c.zone}/${c.sensor_type} ${c.operator} ${c.threshold}`
      ).join(` ${rule.condition_logic} `);
    },
  }));
});

async function apiErrorText(res) {
  try {
    const body = await res.json();
    if (Array.isArray(body.detail)) return body.detail.map(d => `${d.loc.slice(1).join(".")}: ${d.msg}`).join("; ");
    return body.detail || res.statusText;
  } catch {
    return `${res.status} ${res.statusText}`;
  }
}
