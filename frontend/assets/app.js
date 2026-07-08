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
    noRules: "No rules yet. Create one via",
    confirmDeleteRule: "Delete rule?",
    sensorTypes: { moisture: "Moisture", temperature: "Temperature", humidity: "Humidity", light: "Light" },
  },
  de: {
    live: "Live", disconnected: "Getrennt",
    zones: "ZONEN", sensors: "SENSOREN", rules: "REGELN", refresh: "Aktualisieren",
    waitingSensors: "Warte auf Sensordaten. Starte",
    waitingSensorsSuffix: "um Daten zu simulieren.",
    manualPump: "Pumpe manuell:", stop: "Stop",
    automationRules: "Automatisierungsregeln",
    noRules: "Keine Regeln vorhanden. Erstelle eine via",
    confirmDeleteRule: "Regel löschen?",
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

document.addEventListener("alpine:init", () => {
  Alpine.data("gardenflow", () => ({
    connected: false,
    ws: null,
    sensors: {},   // { "zone1.moisture": { value, unit, zone, ts } }
    rules: [],
    zones: [],
    lang: localStorage.getItem("gardenflow_lang") || "en",

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
        body: JSON.stringify(rule),
      });
    },
    async deleteRule(id) {
      if (!confirm(this.t("confirmDeleteRule"))) return;
      await fetch(`${API}/api/rules/${id}`, { method: "DELETE" });
      await this.loadRules();
    },

    ruleConditionSummary(rule) {
      return rule.conditions.map(c =>
        `${c.zone}/${c.sensor_type} ${c.operator} ${c.threshold}`
      ).join(` ${rule.condition_logic} `);
    },
  }));
});
