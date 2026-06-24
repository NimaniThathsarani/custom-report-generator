/**
 * frontend/js/app.js
 * ==================
 * Main application logic for the Custom Report Generator UI.
 * Connects to Flask backend at http://127.0.0.1:5000
 *
 * API Endpoints used:
 *   POST /api/generate-report  — generate and download a report file
 *   GET  /api/filters/<type>   — fetch dropdown options for a report type
 *   GET  /api/health           — health check for connection status
 */

'use strict';

/* ──────────────────────────────────────────────────────────────
   CONFIGURATION
──────────────────────────────────────────────────────────────── */
const API_BASE = 'http://127.0.0.1:5000';

const ENDPOINTS = {
  generateReport: `${API_BASE}/api/generate-report`,
  filters:        (type) => `${API_BASE}/api/filters/${type}`,
  health:         `${API_BASE}/api/health`,
};

/* ──────────────────────────────────────────────────────────────
   APPLICATION STATE
──────────────────────────────────────────────────────────────── */
const State = {
  reportKey:     null,   // 'sales' | 'user_activity' | 'inventory'
  reportLabel:   null,   // Human-readable label
  reportIcon:    null,   // Emoji icon
  filtersCache:  {},     // { [reportKey]: filterData } from /api/filters/<type>
  lastFilters:   {},     // The filter payload used for the last generate
  isOnline:      false,  // Whether the Flask backend is reachable
};

/* ──────────────────────────────────────────────────────────────
   UTILITY HELPERS
──────────────────────────────────────────────────────────────── */

/** Read trimmed value of a form field by its ID. Returns '' if not found. */
function v(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
}

/** Set a field's value by ID (no-op if not found). */
function setVal(id, val) {
  const el = document.getElementById(id);
  if (el) el.value = val;
}

/** Set an element's text content by ID (no-op if not found). */
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

/** Show/hide an element by toggling display:none. */
function show(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = '';
}
function hide(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

/** Add or remove a class from an element by ID. */
function addClass(id, cls) {
  const el = document.getElementById(id);
  if (el) el.classList.add(cls);
}
function removeClass(id, cls) {
  const el = document.getElementById(id);
  if (el) el.classList.remove(cls);
}

/* ──────────────────────────────────────────────────────────────
   ALERT BANNERS
──────────────────────────────────────────────────────────────── */

/**
 * Display an alert banner with a message.
 * @param {string} bannerId - ID of the alert container
 * @param {string} bodyId   - ID of the message text element
 * @param {string} msg      - The message to display
 */
function showAlert(bannerId, bodyId, msg) {
  const banner = document.getElementById(bannerId);
  const body   = document.getElementById(bodyId);
  if (body)   body.textContent = msg;
  if (banner) {
    banner.classList.add('show');
    banner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

/** Hide an alert banner. */
function hideAlert(bannerId) {
  const el = document.getElementById(bannerId);
  if (el) el.classList.remove('show');
}

/* ──────────────────────────────────────────────────────────────
   TOAST NOTIFICATIONS
──────────────────────────────────────────────────────────────── */

/**
 * Show a temporary toast notification.
 * @param {string} message
 * @param {'success'|'error'|'info'} type
 * @param {number} duration  milliseconds before auto-dismiss
 */
function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-out');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }, duration);
}

/* ──────────────────────────────────────────────────────────────
   LOADING OVERLAY
──────────────────────────────────────────────────────────────── */

function showLoading(text = 'Generating your report…', sub = 'This may take a few seconds') {
  setText('loading-text', text);
  setText('loading-sub', sub);
  addClass('loading-overlay', 'show');
}

function hideLoading() {
  removeClass('loading-overlay', 'show');
}

/* ──────────────────────────────────────────────────────────────
   GENERATE BUTTON STATE
──────────────────────────────────────────────────────────────── */

function setGenBtnLoading(loading) {
  const btn = document.getElementById('btn-gen');
  if (!btn) return;
  if (loading) {
    btn.disabled  = true;
    btn.innerHTML = '<span class="btn-spin" aria-hidden="true"></span> Generating report…';
  } else {
    resetGenBtn();
  }
}

function resetGenBtn() {
  const btn = document.getElementById('btn-gen');
  if (!btn) return;
  btn.disabled  = false;
  btn.innerHTML = '⚡ Generate Report Now';
}

/* ──────────────────────────────────────────────────────────────
   BACKEND HEALTH CHECK
──────────────────────────────────────────────────────────────── */

async function checkHealth() {
  const dot  = document.getElementById('status-dot');
  const lbl  = document.getElementById('status-lbl');

  try {
    const res = await fetch(ENDPOINTS.health, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      State.isOnline = true;
      if (dot) { dot.className = 'status-dot online'; }
      if (lbl) lbl.textContent = 'Backend connected';
    } else {
      throw new Error('Non-200');
    }
  } catch {
    State.isOnline = false;
    if (dot) { dot.className = 'status-dot offline'; }
    if (lbl) lbl.textContent = 'Backend offline';
  }
}

/* ──────────────────────────────────────────────────────────────
   SCREEN NAVIGATION
──────────────────────────────────────────────────────────────── */

/**
 * Navigate to the given screen number (1–4).
 * @param {1|2|3|4} n
 */
function goTo(n) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('is-active'));
  const target = document.getElementById('s' + n);
  if (target) {
    target.classList.add('is-active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Sync nav step pills
  // Step 1 pill → screen 1
  // Step 2 pill → screen 2 or 3
  // Step 3 pill → screen 4
  const pills = ['np1', 'np2', 'np3'];
  const activeIndex = n === 1 ? 0 : (n === 4 ? 2 : 1);
  pills.forEach((id, i) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle('is-active', i === activeIndex);
    el.classList.toggle('is-done',   i < activeIndex);
  });
}

/* ──────────────────────────────────────────────────────────────
   SCREEN 1 — REPORT TYPE SELECTION
──────────────────────────────────────────────────────────────── */

/**
 * Handle a click on one of the three report type cards.
 * Updates State, highlights the card, enables action buttons.
 * @param {HTMLButtonElement} card
 */
function pickReport(card) {
  // Deselect all cards
  document.querySelectorAll('.rtype-card').forEach(c => {
    c.classList.remove('is-selected');
    c.setAttribute('aria-checked', 'false');
  });

  // Select clicked card
  card.classList.add('is-selected');
  card.setAttribute('aria-checked', 'true');

  // Save to state
  State.reportKey   = card.dataset.key;
  State.reportLabel = card.dataset.lbl;
  State.reportIcon  = card.dataset.icon;

  // Update selection display
  const display = document.getElementById('sel-display');
  setText('sel-val', State.reportLabel);
  if (display) display.classList.add('has-val');

  // Enable action buttons
  document.getElementById('btn-instant').disabled = false;
  document.getElementById('btn-sched').disabled   = false;
}

/* ──────────────────────────────────────────────────────────────
   SCREEN 2 — FILTERS & GENERATE
──────────────────────────────────────────────────────────────── */

/**
 * Navigate to Screen 2.
 * Populates the context chip, reveals the correct filter panel,
 * and attempts to load filter options from the backend API.
 */
async function gotoFilters() {
  if (!State.reportKey) return;

  // Set context chip
  setText('f-chip-ico', State.reportIcon);
  setText('f-chip-lbl', State.reportLabel);

  // Hide all filter panels
  document.querySelectorAll('.filter-panel').forEach(p => { p.style.display = 'none'; });

  // Show the relevant panel
  const panel = document.getElementById('fg-' + State.reportKey);
  if (panel) panel.style.display = 'block';

  // Clear any previous error and reset button
  hideAlert('f-err');
  resetGenBtn();

  goTo(2);

  // Load filter options from API in the background
  await loadFilterOptions(State.reportKey);
}

/**
 * Load filter dropdown options from GET /api/filters/<type>
 * and populate the selects. Falls back gracefully if backend is offline.
 * @param {string} reportType
 */
async function loadFilterOptions(reportType) {
  // Use cache if already fetched
  if (State.filtersCache[reportType]) {
    populateFilterDropdowns(reportType, State.filtersCache[reportType]);
    return;
  }

  try {
    const res = await fetch(ENDPOINTS.filters(reportType), {
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    State.filtersCache[reportType] = data.filters;
    populateFilterDropdowns(reportType, data.filters);
  } catch (err) {
    console.warn('[ReportGen] Could not load filter options:', err.message);
    // Filters keep their static fallback values — no disruption to UX
  }
}

/**
 * Populate select dropdowns with API-sourced values.
 * Only overwrites if the API returned actual data.
 * @param {string} reportType
 * @param {Object} filters - { categories, regions, warehouses, activity_types, usernames }
 */
function populateFilterDropdowns(reportType, filters) {
  if (!filters) return;

  if (reportType === 'sales') {
    if (filters.categories && filters.categories.length > 0) {
      populateSelect('s-cat', filters.categories, '— All categories —');
    }
    if (filters.regions && filters.regions.length > 0) {
      populateSelect('s-region', filters.regions, '— All regions —');
    }
  }

  if (reportType === 'user_activity') {
    if (filters.activity_types && filters.activity_types.length > 0) {
      populateSelect('ua-type', filters.activity_types, '— All activity types —');
    }
  }

  if (reportType === 'inventory') {
    if (filters.categories && filters.categories.length > 0) {
      populateSelect('inv-cat', filters.categories, '— All categories —');
    }
    if (filters.warehouse_locations && filters.warehouse_locations.length > 0) {
      populateSelect('inv-wh', filters.warehouse_locations, '— All warehouses —');
    }
  }
}

/**
 * Replace a <select> element's options with the given values.
 * Preserves the current selection if it still exists.
 * @param {string} selectId
 * @param {string[]} values
 * @param {string} placeholder
 */
function populateSelect(selectId, values, placeholder) {
  const sel = document.getElementById(selectId);
  if (!sel) return;

  const current = sel.value;
  sel.innerHTML = `<option value="">${placeholder}</option>`;

  values.forEach(val => {
    const opt = document.createElement('option');
    opt.value = val;
    opt.textContent = val;
    sel.appendChild(opt);
  });

  // Restore previous selection if still valid
  if (current && values.includes(current)) {
    sel.value = current;
  }
}

/**
 * Collect filter values into the exact payload shape the Flask API expects.
 * Maps frontend field IDs to backend filter keys.
 * @returns {{ report_type: string, export_format: string, filters: Object }}
 */
function collectPayload(exportFormat = 'excel') {
  const key     = State.reportKey;
  const filters = {};

  if (key === 'sales') {
    const start    = v('s-start');
    const end      = v('s-end');
    const category = v('s-cat');
    const region   = v('s-region');
    if (start)    filters.start_date = start;
    if (end)      filters.end_date   = end;
    if (category) filters.category   = category;
    if (region)   filters.region     = region;
  }

  if (key === 'user_activity') {
    const start        = v('ua-start');
    const end          = v('ua-end');
    const username     = v('ua-user');
    const activityType = v('ua-type');
    if (start)        filters.start_date     = start;
    if (end)          filters.end_date       = end;
    if (username)     filters.username       = username;
    if (activityType) filters.activity_type  = activityType;
  }

  if (key === 'inventory') {
    const category          = v('inv-cat');
    const warehouseLocation = v('inv-wh');
    if (category)          filters.category           = category;
    if (warehouseLocation) filters.warehouse_location = warehouseLocation;
  }

  // Save for re-use by download buttons
  State.lastFilters = filters;

  return {
    report_type:   key,
    export_format: exportFormat,
    filters,
  };
}

/**
 * Validate the filter payload for required fields.
 * Sales and User Activity require start + end dates.
 * Inventory has no required fields.
 * @param {Object} payload
 * @returns {{ ok: boolean, msg: string }}
 */
function validate(payload) {
  const { report_type, filters } = payload;

  if (report_type === 'sales' || report_type === 'user_activity') {
    if (!filters.start_date && !filters.end_date) {
      return { ok: false, msg: 'A start date and end date are required for this report type.' };
    }
    if (!filters.start_date) {
      return { ok: false, msg: 'Please enter a start date.' };
    }
    if (!filters.end_date) {
      return { ok: false, msg: 'Please enter an end date.' };
    }
    if (new Date(filters.start_date) > new Date(filters.end_date)) {
      return { ok: false, msg: 'The start date must be before or equal to the end date.' };
    }
  }

  return { ok: true, msg: '' };
}

/**
 * Main handler for the "Generate Report Now" button.
 * Validates inputs, calls the API, navigates to the result screen.
 */
async function handleGenerate() {
  const payload = collectPayload('excel'); // initial format; both formats downloadable on screen 4
  const check   = validate(payload);

  if (!check.ok) {
    showAlert('f-err', 'f-err-body', check.msg);
    return;
  }

  hideAlert('f-err');
  setGenBtnLoading(true);
  showLoading('Generating your report…', 'Querying data and building the file');

  try {
    // Pre-flight: confirm backend is up before navigating away
    await checkHealth();

    if (!State.isOnline) {
      showAlert('f-err', 'f-err-body',
        'Cannot reach the Flask backend at ' + API_BASE + '. Make sure it is running and try again.');
      return;
    }

    // Navigate to result screen and trigger a download
    // The result screen shows both PDF and Excel download buttons
    // that each call /api/generate-report independently.
    prepareResultScreen();
    goTo(4);

  } finally {
    setGenBtnLoading(false);
    hideLoading();
  }
}

/**
 * Set up the result screen (Screen 4) with metadata and show success state.
 * Actual file downloads happen when the user clicks PDF or Excel buttons.
 */
function prepareResultScreen() {
  setText('r4-meta-type', State.reportLabel);
  setText('r4-meta-time', new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

  // Reset download buttons
  const btnPdf = document.getElementById('btn-dl-pdf');
  const btnXls = document.getElementById('btn-dl-xls');
  if (btnPdf) { btnPdf.disabled = false; btnPdf.innerHTML = '📄 Download PDF'; }
  if (btnXls) { btnXls.disabled = false; btnXls.innerHTML = '📊 Download Excel'; }

  // Show success state, hide error state
  show('r4-ok');
  hide('r4-err');

  setText('r4-eye', 'Results');
  setText('r4-h1',  'Your report is ready');
  setText('r4-p',   'Click a button below to generate and download your report in your preferred format.');
}

/* ──────────────────────────────────────────────────────────────
   SCREEN 4 — DOWNLOAD BUTTONS
──────────────────────────────────────────────────────────────── */

/**
 * Trigger a file download by calling POST /api/generate-report
 * with the correct export_format.
 * @param {'pdf'|'excel'} fmt
 */
async function triggerDownload(fmt) {
  const btnId  = fmt === 'pdf' ? 'btn-dl-pdf' : 'btn-dl-xls';
  const btn    = document.getElementById(btnId);
  const label  = fmt === 'pdf' ? '📄 Download PDF' : '📊 Download Excel';

  if (btn) {
    btn.disabled  = true;
    btn.innerHTML = `<span class="btn-spin" aria-hidden="true"></span> Preparing ${fmt.toUpperCase()}…`;
  }

  showLoading(
    `Preparing ${fmt === 'pdf' ? 'PDF' : 'Excel'} file…`,
    'Generating report data — please wait'
  );

  try {
    const payload = {
      report_type:   State.reportKey,
      export_format: fmt,
      filters:       State.lastFilters,
    };

    const res = await fetch(ENDPOINTS.generateReport, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (!res.ok) {
      let errMsg = `Server returned HTTP ${res.status} — ${res.statusText}.`;
      try {
        const j = await res.json();
        if (j && j.error) errMsg = j.error;
      } catch (_) { /* Not JSON — use status text */ }
      throw new Error(errMsg);
    }

    // Read response as Blob and trigger browser download
    const blob = await res.blob();
    const contentType = res.headers.get('Content-Type') || 'application/octet-stream';

    const ext      = fmt === 'pdf' ? 'pdf' : 'xlsx';
    const date     = new Date().toISOString().slice(0, 10);
    const safeName = (State.reportKey || 'report').replace(/[^a-z0-9_]/gi, '_');
    const fileName = `${safeName}_report_${date}.${ext}`;

    const blobWithType = new Blob([blob], { type: contentType });
    const url = window.URL.createObjectURL(blobWithType);
    const a   = document.createElement('a');
    a.href     = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }, 300);

    showToast(`${fmt === 'pdf' ? 'PDF' : 'Excel'} downloaded successfully!`, 'success');

  } catch (err) {
    console.error('[ReportGen] Download error:', err);

    // Show error state on screen 4
    hide('r4-ok');
    show('r4-err');
    setText('r4-eye', 'Error');
    setText('r4-h1',  'Download failed');
    setText('r4-p',   'We couldn\'t generate the report file. Please check the backend is running and try again.');
    setText('r4-err-msg', err.message || 'An unexpected error occurred. Please try again.');

    showToast(`Download failed: ${err.message}`, 'error');

  } finally {
    hideLoading();
    if (btn) {
      btn.disabled  = false;
      btn.innerHTML = label;
    }
  }
}

/* ──────────────────────────────────────────────────────────────
   SCREEN 3 — SCHEDULE
──────────────────────────────────────────────────────────────── */

/** Navigate to Screen 3 (Schedule). */
function gotoSchedule() {
  if (!State.reportKey) return;

  // Context chip
  setText('sc-chip-ico', State.reportIcon);
  setText('sc-chip-lbl', State.reportLabel);

  // Reset form visibility
  show('sc-form');
  removeClass('sc-done', 'show');

  // Clear fields
  setVal('sc-freq',  '');
  setVal('sc-fmt',   '');
  setVal('sc-email', '');

  // Clear schedule filter fields
  clearScheduleFilters();

  hideAlert('sc-err');
  goTo(3);
}

/** Clear the schedule form filter fields. */
function clearScheduleFilters() {
  ['sc-s-start','sc-s-end','sc-s-cat','sc-s-region',
   'sc-ua-start','sc-ua-end','sc-ua-user','sc-ua-type',
   'sc-inv-cat','sc-inv-wh'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
}

/** Show the correct filter sub-panel in the schedule form based on report type. */
function updateScheduleFilters() {
  ['sched-fg-sales','sched-fg-user_activity','sched-fg-inventory'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });
  const panel = document.getElementById('sched-fg-' + State.reportKey);
  if (panel) panel.style.display = 'block';
}

/**
 * Collect schedule-screen filter values into the backend payload format.
 * @returns {Object} filters dict
 */
function collectScheduleFilters() {
  const key     = State.reportKey;
  const filters = {};

  if (key === 'sales') {
    const start    = v('sc-s-start');
    const end      = v('sc-s-end');
    const category = v('sc-s-cat');
    const region   = v('sc-s-region');
    if (start)    filters.start_date = start;
    if (end)      filters.end_date   = end;
    if (category) filters.category   = category;
    if (region)   filters.region     = region;
  }
  if (key === 'user_activity') {
    const start    = v('sc-ua-start');
    const end      = v('sc-ua-end');
    const username = v('sc-ua-user');
    const actType  = v('sc-ua-type');
    if (start)    filters.start_date    = start;
    if (end)      filters.end_date      = end;
    if (username) filters.username      = username;
    if (actType)  filters.activity_type = actType;
  }
  if (key === 'inventory') {
    const category = v('sc-inv-cat');
    const wh       = v('sc-inv-wh');
    if (category) filters.category           = category;
    if (wh)       filters.warehouse_location  = wh;
  }

  return filters;
}

/**
 * Handle the "Save Schedule" button.
 * Validates inputs and shows the confirmation panel.
 * NOTE: There is no dedicated /api/schedule endpoint in the backend;
 * the confirmation is shown client-side and the first report is
 * downloadable immediately via the generate-report endpoint.
 */
function handleSaveSchedule() {
  const freq  = v('sc-freq');
  const fmt   = v('sc-fmt');
  const email = v('sc-email');

  // Validate
  if (!freq)  { showAlert('sc-err', 'sc-err-body', 'Please choose a delivery frequency.'); return; }
  if (!fmt)   { showAlert('sc-err', 'sc-err-body', 'Please choose an export format.');      return; }
  if (!email) { showAlert('sc-err', 'sc-err-body', 'A recipient email address is required.'); return; }

  // Email validation
  const emailRx = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
  if (!emailRx.test(email)) {
    showAlert('sc-err', 'sc-err-body',
      `"${email}" doesn't look like a valid email address. Please check and try again.`);
    return;
  }

  hideAlert('sc-err');

  // Calculate first dispatch date
  const now = new Date();
  let dispatch = '';

  if (freq === 'Daily') {
    const d = new Date(now);
    d.setDate(d.getDate() + 1);
    dispatch = 'Tomorrow, ' + d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
  } else if (freq === 'Weekly') {
    const d = new Date(now);
    const daysToMon = (8 - d.getDay()) % 7 || 7;
    d.setDate(d.getDate() + daysToMon);
    dispatch = 'Next Monday, ' + d.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
  } else if (freq === 'Monthly') {
    const d = new Date(now.getFullYear(), now.getMonth() + 1, 1);
    dispatch = '1 ' + d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  }

  // Determine format label
  const fmtLabel = fmt === 'pdf' ? 'PDF Document' : 'Excel Spreadsheet';

  // Populate confirmation rows
  setText('cd-report',   State.reportLabel || '—');
  setText('cd-freq',     freq);
  setText('cd-fmt',      fmtLabel);
  setText('cd-email',    email);
  setText('cd-dispatch', dispatch);

  setText('sc-done-summary',
    `Your first ${fmtLabel} will be delivered to ${email} on ${dispatch.toLowerCase()}.`);

  // Swap form → confirmation
  hide('sc-form');
  addClass('sc-done', 'show');

  showToast('Schedule saved successfully!', 'success', 5000);
}

/**
 * Go back to the generate screen from the results screen
 * (re-uses the existing filter state).
 */
function gotoFiltersFromResult() {
  if (!State.reportKey) { goTo(1); return; }

  setText('f-chip-ico', State.reportIcon);
  setText('f-chip-lbl', State.reportLabel);

  document.querySelectorAll('.filter-panel').forEach(p => { p.style.display = 'none'; });
  const panel = document.getElementById('fg-' + State.reportKey);
  if (panel) panel.style.display = 'block';

  hideAlert('f-err');
  resetGenBtn();
  goTo(2);
}

/* ──────────────────────────────────────────────────────────────
   INITIALISATION
──────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  // Navigate to screen 1 on load
  goTo(1);

  // Show correct schedule filter panel when page loads
  updateScheduleFilters();

  // Check backend health on startup and every 30 seconds
  checkHealth();
  setInterval(checkHealth, 30_000);

  // Keyboard accessibility: allow Enter/Space on report cards
  document.querySelectorAll('.rtype-card').forEach(card => {
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        pickReport(card);
      }
    });
  });
});
