const domain = "lk_systems_webserver";

const labels = {
  en: {
    title: "Floor Heating", connected: "Connected", degraded: "Connection degraded",
    offline: "Disconnected", last: "Last successful read", unknown: "Unknown",
    system: "System", normal: "Normal", holiday: "Holiday", setback: "Setback",
    clock: "LK clock", sync: "Sync clock", apply: "Apply mode", end: "Holiday end date",
    pump: "Pump relay", boiler: "Boiler relay", on: "On", off: "Off",
    measured: "Room temperature", target: "Target temperature", heat: "Heating",
    idle: "Idle", battery: "Battery", radio: "Radio link quality", settings: "Room settings",
    schedule: "Weekly program", manual: "Temporary manual override", save: "Save",
    noRooms: "No active thermostats.", noData: "Waiting for LK Webserver data.",
    waiting: "Saving…", saved: "Saved and verified.", error: "The operation failed.",
    dayHelp: "Enter start and end for each economy period. Leave both blank to remove a period. Use 24:00 for midnight at the end of a day.",
    holidayHelp: "Select a date 1–99 days from today. This mode affects all rooms.",
    setbackHelp: "Use each room's setback temperature until normal mode is restored.",
    days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    comfort_deg: ["Comfort temperature", "Normal target when the weekly program is active."],
    economy_deg: ["Economy temperature", "Target during scheduled economy periods."],
    adaptive_enable: ["Adaptive start", "May start heating early to reach Comfort temperature at the scheduled time."],
    holiday_deg: ["Holiday temperature", "Target for this room while system Holiday mode is active."],
    setback_deg: ["Setback temperature", "Target for this room while system Setback mode is active."],
    backlight_enable: ["Backlight", "Illuminates the thermostat display on a button press."],
    keylock_enable: ["Key lock", "Locks the physical thermostat buttons."],
    restrict_deg_min: ["Minimum room target", "Lower limit for the room temperature setting."],
    restrict_deg_max: ["Maximum room target", "Upper limit for the room temperature setting."],
    fireplace_hours: ["Fireplace duration (h)", "Keeps the floor warm for a set time. Enter 0 to turn it off."],
    fireplace_level: ["Fireplace heating level (%)", "Heating level used while Fireplace is active."],
    bypass_mode: ["Bypass", "Can open this circuit to maintain water flow when other circuits are closed."],
    bypassOptions: ["Off", "Continuous", "Timed"],
  },
  fi: {
    title: "Lattialämmitys", connected: "Yhteys kunnossa", degraded: "Yhteyshäiriö",
    offline: "Ei yhteyttä", last: "Viimeisin onnistunut luku", unknown: "Ei tiedossa",
    system: "Järjestelmä", normal: "Normaali", holiday: "Loma", setback: "Pudotus",
    clock: "LK:n kello", sync: "Synkronoi kello", apply: "Ota tila käyttöön", end: "Loman päättymispäivä",
    pump: "Pumpun rele", boiler: "Kattilan rele", on: "Päällä", off: "Pois",
    measured: "Huonelämpötila", target: "Tavoitelämpötila", heat: "Lämmittää",
    idle: "Ei lämmityspyyntöä", battery: "Paristo", radio: "Radiolinkin laatu", settings: "Huoneen asetukset",
    schedule: "Viikko-ohjelma", manual: "Tilapäinen käsisäätö", save: "Tallenna",
    noRooms: "Ei aktiivisia termostaatteja.", noData: "Odotetaan LK Webserverin tietoja.",
    waiting: "Tallennetaan…", saved: "Tallennettu ja tarkistettu.", error: "Toiminto epäonnistui.",
    dayHelp: "Anna säästöjakson alku ja loppu. Tyhjennä molemmat kentät poistaaksesi jakson. Vuorokauden loppu merkitään 24.00.",
    holidayHelp: "Valitse päivä 1–99 päivän päähän. Tila vaikuttaa kaikkiin huoneisiin.",
    setbackHelp: "Käyttää huoneiden pudotuslämpötiloja, kunnes normaalitila palautetaan.",
    days: ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai", "Lauantai", "Sunnuntai"],
    comfort_deg: ["Mukavuuslämpötila", "Tavallinen tavoite viikko-ohjelman ollessa käytössä."],
    economy_deg: ["Säästölämpötila", "Tavoite ajastettujen säästöjaksojen aikana."],
    adaptive_enable: ["Mukautuva käynnistys", "Voi aloittaa lämmityksen etukäteen, jotta mukavuuslämpötila saavutetaan ajallaan."],
    holiday_deg: ["Lomalämpötila", "Huoneen tavoite järjestelmän lomatilan aikana."],
    setback_deg: ["Pudotuslämpötila", "Huoneen tavoite keskitetyn lämpötilan pudotuksen aikana."],
    backlight_enable: ["Taustavalo", "Valaisee termostaatin näytön painiketta painettaessa."],
    keylock_enable: ["Näppäinlukko", "Lukitsee seinätermostaatin painikkeet."],
    restrict_deg_min: ["Tavoitelämpötilan alaraja", "Huoneen tavoitelämpötilan pienin sallittu asetus."],
    restrict_deg_max: ["Tavoitelämpötilan yläraja", "Huoneen tavoitelämpötilan suurin sallittu asetus."],
    fireplace_hours: ["Takkatoiminnon kesto (h)", "Pitää lattian lämpimänä valitun ajan. Arvo 0 kytkee toiminnon pois."],
    fireplace_level: ["Takkatoiminnon lämmitystaso (%)", "Lämmitystaso takkatoiminnon aikana."],
    bypass_mode: ["Ohitus", "Voi avata tämän piirin virtauksen ylläpitämiseksi muiden piirien sulkeutuessa."],
    bypassOptions: ["Pois", "Jatkuva", "Ajastettu"],
  },
};

const settings = [
  ["comfort_deg", "temperature"], ["economy_deg", "temperature"],
  ["adaptive_enable", "toggle"], ["holiday_deg", "temperature"],
  ["setback_deg", "temperature"], ["backlight_enable", "toggle"],
  ["keylock_enable", "toggle"], ["restrict_deg_min", "temperature"],
  ["restrict_deg_max", "temperature"], ["fireplace_hours", "hours"],
  ["fireplace_level", "power"], ["bypass_mode", "bypass"],
];

const escapeHTML = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[char]);
const formatTime = (minutes) => [Math.floor(minutes / 60), minutes % 60]
  .map((n) => String(n).padStart(2, "0")).join(":");
function parseTime(value) {
  const match = /^(\d{1,2})[:.](\d{2})$/.exec(value.trim());
  if (!match || Number(match[2]) > 59 || Number(match[1]) * 60 + Number(match[2]) > 1440) {
    throw new Error("Invalid time");
  }
  return Number(match[1]) * 60 + Number(match[2]);
}

class LKFloorHeating extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode: "open"});
    this.data = {};
    this.open = new Set();
    this.dirty = new Set();
    this.busy = false;
    this.message = "";
    this.shadowRoot.addEventListener("submit", (event) => this.submit(event));
    this.shadowRoot.addEventListener("input", (event) => {
      if (event.target.form) this.dirty.add(event.target.form.dataset.id);
    });
    this.shadowRoot.addEventListener("change", (event) => {
      const select = event.target;
      const form = select.form;
      if (form?.dataset.action !== "system_mode" || select.name !== "value") return;
      const holiday = select.value === "1";
      const end = form.elements.namedItem("end");
      end.disabled = !holiday;
      end.required = holiday;
      end.closest("label").hidden = !holiday;
      form.querySelector("[data-holiday-help]").hidden = !holiday;
      form.querySelector("[data-setback-help]").hidden = select.value !== "2";
    });
    this.shadowRoot.addEventListener("click", (event) => {
      const help = event.target.closest("[data-help]");
      if (help) {
        const text = help.nextElementSibling;
        text.hidden = !text.hidden;
        help.setAttribute("aria-expanded", String(!text.hidden));
      }
      if (event.target.closest("[data-menu]")) {
        this.dispatchEvent(new CustomEvent("hass-toggle-menu", {bubbles: true, composed: true}));
      }
    });
    this.shadowRoot.addEventListener("toggle", (event) => this.toggle(event), true);
  }

  set hass(hass) {
    const oldLanguage = this.language;
    this._hass = hass;
    if (oldLanguage !== this.language && !this.busy) this.render();
  }

  get language() {
    return (this._hass?.locale?.language ?? this._hass?.language ?? "en").startsWith("fi") ? "fi" : "en";
  }

  get t() { return labels[this.language]; }

  connectedCallback() {
    this.render();
    this.refresh();
    this.timer = setInterval(() => this.refresh(), 5000);
  }

  disconnectedCallback() { clearInterval(this.timer); }

  async refresh() {
    if (!this._hass || this.busy || this.dirty.size || this.shadowRoot.activeElement?.matches("input, select")) return;
    try {
      const data = await this._hass.callWS({type: domain + "/state"});
      if (!this.busy && !this.dirty.size && JSON.stringify(data) !== JSON.stringify(this.data)) {
        this.data = data;
        this.render();
      }
    } catch {
      // Home Assistant will reconnect its websocket and the next refresh can recover.
    }
  }

  async toggle(event) {
    const details = event.target;
    const key = details.dataset?.key;
    if (!key || !details.isConnected) return;
    if (!details.open) {
      this.open.delete(key);
      return;
    }
    if (this.open.has(key)) return;
    this.open.add(key);
    await this.send(details.dataset.entry, "details", {tid: Number(details.dataset.tid)}, false);
  }

  async send(entry, action, args, notify = true) {
    if (this.busy) return;
    this.busy = true;
    if (notify) {
      this.message = this.t.waiting;
      const status = this.shadowRoot.querySelector("[role=status]");
      if (status) status.textContent = this.message;
    }
    try {
      this.data[entry] = await this._hass.callWS({
        type: domain + "/action", entry, action, args,
      });
      if (notify) this.message = this.t.saved;
    } catch (error) {
      this.message = this.language === "fi" ? this.t.error : (error.message || this.t.error);
    } finally {
      this.busy = false;
      this.render();
    }
  }

  async submit(event) {
    event.preventDefault();
    const form = event.target;
    const {entry, action, tid, key, day, id} = form.dataset;
    const values = new FormData(form);
    const args = {};
    if (tid) args.tid = Number(tid);
    if (key) args.key = key;
    if (day !== undefined) {
      args.day = Number(day);
      try {
        args.periods = [0, 1, 2].flatMap((i) => {
          const start = values.get("start" + i), end = values.get("end" + i);
          return start || end ? [[parseTime(start), parseTime(end)]] : [];
        });
      } catch {
        this.message = this.t.dayHelp;
        this.shadowRoot.querySelector("[role=status]").textContent = this.message;
        return;
      }
    }
    if (values.has("value")) args.value = Number(values.get("value"));
    if (action === "week_enabled") args.value = Boolean(args.value);
    if (values.has("end")) args.end = values.get("end");
    this.dirty.delete(id);
    await this.send(entry, action, args);
  }

  form(entry, action, content, params = {}) {
    const attributes = Object.entries(params).map(([key, value]) =>
      ' data-' + key + '="' + escapeHTML(value) + '"').join("");
    const id = [entry, action, ...Object.values(params)].join("_");
    return '<form data-id="' + escapeHTML(id) + '" data-entry="' + escapeHTML(entry)
      + '" data-action="' + action + '"' + attributes + ">" + content + "</form>";
  }

  choices(options, value) {
    return options.map((label, i) => '<option value="' + i + '"' + (Number(value) === i ? " selected" : "") + ">"
      + escapeHTML(label) + "</option>").join("");
  }

  roomSetting(entry, tid, details, key, kind) {
    const [label, help] = this.t[key];
    const raw = details[key];
    if (raw === undefined) return "";
    let control;
    if (kind === "toggle" || kind === "bypass") {
      const options = kind === "toggle" ? [this.t.off, this.t.on] : this.t.bypassOptions;
      control = '<select name="value" aria-label="' + escapeHTML(label) + '">' + this.choices(options, raw) + "</select>";
    } else {
      const [minimum, maximum, step, divisor] = {
        temperature: [7, 40, 0.5, 100], hours: [0, 99, 1, 1], power: [5, 100, 1, 100],
      }[kind];
      control = '<input name="value" type="number" required aria-label="' + escapeHTML(label)
        + '" min="' + minimum + '" max="' + maximum + '" step="' + step
        + '" value="' + Number(raw) / divisor + '">';
    }
    return this.form(entry, "setting", '<span>' + label
      + ' <button type="button" data-help aria-expanded="false" aria-label="' + escapeHTML(label)
      + '">ⓘ</button><span class="muted help" hidden>' + escapeHTML(help)
      + '</span></span>' + control + '<button>' + this.t.save + '</button>', {tid, key});
  }

  schedule(entry, tid, details) {
    const t = this.t;
    const enabled = this.form(entry, "week_enabled", '<label>' + t.schedule
      + ' <select name="value">' + this.choices([t.off, t.on], details.week_program_enable)
      + '</select></label><button>' + t.save + '</button>', {tid});
    const week = details.week_program;
    if (!Array.isArray(week) || week.length !== 42) return enabled;
    return enabled + '<p class="muted">' + t.dayHelp + '</p><div class="week">'
      + t.days.map((name, day) => {
        const rows = [0, 1, 2].map((period) => {
          const index = day * 6 + period * 2;
          const start = Number(week[index]), end = Number(week[index + 1]);
          return '<div class="period"><input aria-label="' + (period + 1) + ' start" name="start' + period
            + '" placeholder="HH:MM" value="' + (start < end ? formatTime(start) : "")
            + '"><input aria-label="' + (period + 1) + ' end" name="end' + period
            + '" placeholder="HH:MM" value="' + (start < end ? formatTime(end) : "") + '"></div>';
        }).join("");
        return this.form(entry, "day", '<strong>' + name + '</strong>' + rows
          + '<button>' + t.save + '</button>', {tid, day});
      }).join("") + "</div>";
  }

  room(entry, tid, room) {
    const t = this.t, details = room.details, key = entry + "-" + tid;
    const showTemp = (value) => Number(value).toLocaleString(this.language, {minimumFractionDigits: 1, maximumFractionDigits: 1}) + " °C";
    const target = this.form(entry, "target", '<label>' + t.target
      + ' <input name="value" type="number" required step="0.5" min="7" max="40" value="'
      + Number(room.target) + '"></label><button>' + t.save + '</button>', {tid});
    return '<article><h2>' + escapeHTML(room.name) + '</h2><div class="reading">' + showTemp(room.current)
      + '</div><p>' + t.measured + ' · ' + (room.heating ? t.heat : t.idle) + '</p>' + target
      + '<p class="muted">' + t.battery + ' ' + escapeHTML(details.battery ?? "—")
      + (details.battery === undefined ? "" : " %") + ' · ' + t.radio + ' ' + escapeHTML(details.link_quality ?? "—")
      + '</p>' + (details.operation_mode === "1" && details.week_program_enable === "1" ? '<p>' + t.manual + '</p>' : '')
      + '<details data-key="' + escapeHTML(key) + '" data-entry="' + escapeHTML(entry) + '" data-tid="' + tid
      + '"' + (this.open.has(key) ? ' open' : '') + '><summary>⚙ ' + t.settings + '</summary>'
      + (details.week_program_enable === undefined ? '<p>' + t.unknown + '</p>'
      : settings.map(([field, kind]) => this.roomSetting(entry, tid, details, field, kind)).join("")
        + this.schedule(entry, tid, details))
      + '</details></article>';
  }

  system(entry, system) {
    const t = this.t;
    const date = system.date;
    const dateText = Array.isArray(date) && date.length >= 5
      ? date.slice(0, 3).map((v) => String(v).padStart(2, "0")).join("-") + " "
        + date.slice(3, 5).map((v) => String(v).padStart(2, "0")).join(":")
      : t.unknown;
    const relay = (value) => value === "1" ? t.on : value === "0" ? t.off : t.unknown;
    const holiday = Number(system.override_web) === 1;
    const setback = Number(system.override_web) === 2;
    const mode = this.form(entry, "system_mode", '<label>' + t.system + ' <select name="value">'
      + this.choices([t.normal, t.holiday, t.setback], system.override_web)
      + '</select></label><label' + (holiday ? '' : ' hidden') + '>' + t.end
      + ' <input type="date" name="end"' + (holiday ? ' required' : ' disabled') + '></label>'
      + '<button>' + t.apply + '</button>'
      + '<p class="muted mode-help" data-holiday-help' + (holiday ? '' : ' hidden') + '>' + t.holidayHelp + '</p>'
      + '<p class="muted mode-help" data-setback-help' + (setback ? '' : ' hidden') + '>' + t.setbackHelp + '</p>');
    const clock = this.form(entry, "sync_clock", '<button>' + t.sync + '</button>');
    return '<article><h2>' + t.system + '</h2><p>' + t.clock + ' · ' + escapeHTML(dateText)
      + '</p><p>' + t.pump + ' · ' + relay(system.pump_state) + ' · ' + t.boiler + ' · ' + relay(system.boiler_state)
      + '</p>' + mode + clock + '</article>';
  }

  render() {
    const t = this.t;
    const entries = Object.entries(this.data).map(([entry, data]) => {
      const status = !data.last_success || data.failures >= 3 ? t.offline : data.failures ? t.degraded : t.connected;
      const last = data.last_success ? new Date(data.last_success).toLocaleTimeString(this.language) : t.unknown;
      return '<section><p class="connection"><strong>' + status + '</strong> · ' + t.last + ' '
        + escapeHTML(last) + '</p>' + this.system(entry, data.system) + '<div class="rooms">'
        + (Object.entries(data.rooms).map(([tid, room]) => this.room(entry, tid, room)).join("")
          || '<p>' + t.noRooms + '</p>') + '</div></section>';
    }).join("");
    this.shadowRoot.innerHTML = '<style>'
      + ':host{display:block;color:var(--primary-text-color);background:var(--primary-background-color);min-height:100%;font:inherit}'
      + 'main{max-width:1200px;margin:auto;padding:20px}header{display:flex;align-items:center;gap:12px}'
      + 'h1,h2,p{margin:0 0 12px}.connection{margin-bottom:16px}.reading{font-size:2rem;font-weight:650}'
      + 'article{border:1px solid var(--divider-color,#8885);border-radius:14px;padding:16px;margin-bottom:14px;background:var(--card-background-color)}'
      + '.rooms,.week{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:12px}'
      + 'form{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:8px 0}.week form{display:grid;border:1px solid var(--divider-color,#8885);border-radius:8px;padding:8px}'
      + '.mode-help{flex-basis:100%;margin:0}'
      + 'input,select,button{font:inherit;color:inherit;background:var(--secondary-background-color);border:1px solid var(--divider-color,#8888);border-radius:6px;padding:6px}'
      + 'button,summary{cursor:pointer}input[type=number]{width:5.2rem}.period{display:flex;gap:8px}.period input{width:5.3rem}'
      + '.muted{color:var(--secondary-text-color);font-size:.9em}details{margin-top:12px}.help:not([hidden]){display:block}'
      + '</style><main><header><button data-menu aria-label="Menu">☰</button><h1>' + t.title + '</h1></header>'
      + '<p role="status">' + escapeHTML(this.message) + '</p>' + (entries || '<p>' + t.noData + '</p>') + '</main>';
  }
}

if (!customElements.get("lk-systems-webserver")) {
  customElements.define("lk-systems-webserver", LKFloorHeating);
}

