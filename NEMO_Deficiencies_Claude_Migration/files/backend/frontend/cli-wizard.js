const elements = {
  appVersion: document.querySelector("#appVersion"),
  form: document.querySelector("#cliForm"),
  configSelect: document.querySelector("#configSelect"),
  configTenant: document.querySelector("#configTenant"),
  projectSelect: document.querySelector("#projectSelect"),
  selectionSection: document.querySelector("#selectionSection"),
  exportOptions: document.querySelector("#exportOptions"),
  selectionMode: document.querySelector("#selectionMode"),
  reportValuesField: document.querySelector("#reportValuesField"),
  reportValues: document.querySelector("#reportValues"),
  reportBrowser: document.querySelector("#reportBrowser"),
  reportSearchInput: document.querySelector("#reportSearchInput"),
  reportLoadState: document.querySelector("#reportLoadState"),
  reportChoiceList: document.querySelector("#reportChoiceList"),
  selectAllReportsBtn: document.querySelector("#selectAllReportsBtn"),
  clearReportsBtn: document.querySelector("#clearReportsBtn"),
  outputInput: document.querySelector("#outputInput"),
  refreshIndex: document.querySelector("#refreshIndex"),
  refreshIndexField: document.querySelector("#refreshIndexField"),
  runHint: document.querySelector("#runHint"),
  runExportBtn: document.querySelector("#runExportBtn"),
  runExportLabel: document.querySelector("#runExportLabel"),
  exportResult: document.querySelector("#exportResult"),
  commandPreview: document.querySelector("#commandPreview"),
  downloadCommandBtn: document.querySelector("#downloadCommandBtn"),
  copyCommandBtn: document.querySelector("#copyCommandBtn"),
  copyState: document.querySelector("#copyState"),
};

const state = {
  configs: [],
  reports: [],
  selectedReports: new Set(),
  reportsLoading: false,
  reportError: "",
  reportLoadKey: "",
  reportLoadToken: 0,
  exportRunning: false,
};
const CONFIG_STORAGE_KEY = "nemo-deficiencies-config-id";

function psQuote(value) {
  return `'${String(value).replaceAll("'", "''")}'`;
}

function psArray(values) {
  return `@(${values.map(psQuote).join(", ")})`;
}

function selectedAction() {
  return elements.form.querySelector('input[name="action"]:checked')?.value || "show";
}

function selectedConfig() {
  return state.configs.find((config) => config.id === elements.configSelect.value) || null;
}

function reportValues() {
  return elements.reportValues.value
    .split(/\r?\n/)
    .map((value) => value.trim())
    .filter(Boolean);
}

function reportReference(report) {
  return report.internalName || report.id || report.displayName;
}

function selectedReportValues() {
  return state.reports
    .filter((report) => state.selectedReports.has(reportReference(report)))
    .map(reportReference);
}

function buildCommand() {
  const config = selectedConfig();
  const action = selectedAction();
  const configName = config?.name || "";
  const lines = [
    "$ErrorActionPreference = 'Stop'",
    "$baseUrl = 'http://127.0.0.1:8000'",
    "",
    "try {",
    "  $configs = Invoke-RestMethod -Uri \"$baseUrl/api/configs\"",
    "} catch {",
    "  throw 'NEMO Deficiencies ist nicht erreichbar. Bitte zuerst die Portable-Anwendung starten.'",
    "}",
    `$config = $configs.configs | Where-Object { $_.name -eq ${psQuote(configName)} } | Select-Object -First 1`,
    `if (-not $config) { throw ${psQuote(`Konfiguration nicht gefunden: ${configName}`)} }`,
    `$project = ${psQuote(elements.projectSelect.value)}`,
    "",
  ];
  if (action === "show") {
    lines.push(
      "$configId = [uri]::EscapeDataString($config.id)",
      "$projectName = [uri]::EscapeDataString($project)",
      "$response = Invoke-RestMethod -Uri \"$baseUrl/api/reports?configId=$configId&project=$projectName&deficienciesOnly=false\"",
      "$response.reports | Select-Object displayName, internalName, description | Format-Table -AutoSize"
    );
    return lines.join("\r\n");
  }

  const mode = elements.selectionMode.value;
  const exactValues = mode === "exact" ? selectedReportValues() : [];
  const containsValues = mode === "contains" ? reportValues() : [];
  lines.push(
    "$body = @{",
    "  configId = $config.id",
    "  project = $project",
    `  action = ${psQuote(action)}`,
    `  selectionMode = ${psQuote(mode)}`,
    `  reportRefs = ${psArray(exactValues)}`,
    `  containsValues = ${psArray(containsValues)}`,
    `  outputDir = ${psQuote(elements.outputInput.value.trim())}`,
    `  refreshIndex = ${elements.refreshIndex.checked ? "$true" : "$false"}`,
    "} | ConvertTo-Json -Depth 5",
    "",
    "$result = Invoke-RestMethod -Method Post -Uri \"$baseUrl/api/cli-wizard/export\" -ContentType 'application/json' -Body $body",
    "$result | Format-List"
  );
  return lines.join("\r\n");
}

function filteredReports() {
  const search = elements.reportSearchInput.value.trim().toLocaleLowerCase("de");
  if (!search) return state.reports;
  return state.reports.filter((report) =>
    [report.displayName, report.internalName, report.description]
      .some((value) => String(value || "").toLocaleLowerCase("de").includes(search))
  );
}

function renderReportList() {
  const reports = filteredReports();
  const selectedCount = state.selectedReports.size;
  elements.reportLoadState.textContent = state.reportsLoading
    ? "Berichte werden ohne Einschränkung aus NEMO geladen ..."
    : state.reportError || `${state.reports.length} Berichte verfügbar · ${selectedCount} ausgewählt · ${reports.length} angezeigt`;
  elements.reportChoiceList.replaceChildren();
  if (state.reportsLoading) return;
  if (!reports.length) {
    const empty = document.createElement("p");
    empty.className = "cli-report-empty";
    empty.textContent = state.reports.length ? "Keine Berichte zur Suche gefunden." : "Keine Berichte gefunden.";
    elements.reportChoiceList.append(empty);
    return;
  }
  const fragment = document.createDocumentFragment();
  for (const report of reports) {
    const reference = reportReference(report);
    const label = document.createElement("label");
    label.className = "cli-report-item";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = reference;
    checkbox.checked = state.selectedReports.has(reference);
    const copy = document.createElement("span");
    copy.className = "cli-report-copy";
    const title = document.createElement("strong");
    title.textContent = report.displayName || report.internalName || report.id;
    const internalName = document.createElement("small");
    internalName.textContent = report.internalName || report.id || "";
    copy.append(title, internalName);
    if (report.description) {
      const description = document.createElement("small");
      description.className = "cli-report-description";
      description.textContent = report.description;
      description.title = report.description;
      copy.append(description);
    }
    label.append(checkbox, copy);
    fragment.append(label);
  }
  elements.reportChoiceList.append(fragment);
}

async function loadReports() {
  const config = selectedConfig();
  if (!config) return;
  const loadKey = `${config.id}\u0000${elements.projectSelect.value}`;
  if (state.reportLoadKey === loadKey && (state.reportsLoading || state.reports.length)) return;
  const token = ++state.reportLoadToken;
  state.reportLoadKey = loadKey;
  state.reports = [];
  state.selectedReports.clear();
  state.reportsLoading = true;
  state.reportError = "";
  render();
  const params = new URLSearchParams({
    configId: config.id,
    project: elements.projectSelect.value,
    deficienciesOnly: "false",
  });
  try {
    const response = await fetch(`/api/reports?${params}`, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Berichte konnten nicht geladen werden (${response.status}).`);
    const payload = await response.json();
    if (token !== state.reportLoadToken) return;
    state.reports = (payload.reports || []).sort((left, right) =>
      reportReference(left).localeCompare(reportReference(right), "de", { sensitivity: "base" })
    );
  } catch (error) {
    if (token !== state.reportLoadToken) return;
    state.reportError = error.message;
  } finally {
    if (token === state.reportLoadToken) {
      state.reportsLoading = false;
      render();
    }
  }
}

function maybeLoadReports() {
  if (selectedAction() === "show" || elements.selectionMode.value === "exact") loadReports();
}

function render() {
  const action = selectedAction();
  const mode = elements.selectionMode.value;
  const config = selectedConfig();
  elements.selectionSection.hidden = false;
  elements.exportOptions.hidden = action === "show";
  elements.reportValuesField.hidden = action === "show" || mode !== "contains";
  elements.reportBrowser.hidden = action !== "show" && mode !== "exact";
  elements.refreshIndexField.hidden = action === "show";
  elements.configTenant.textContent = config?.tenant ? `Tenant: ${config.tenant}` : "";
  const hasSelection = mode === "all"
    || (mode === "exact" && state.selectedReports.size > 0)
    || (mode === "contains" && reportValues().length > 0);
  elements.runExportBtn.disabled = action === "show" || !config || !hasSelection || state.exportRunning;
  elements.runExportBtn.classList.toggle("is-loading", state.exportRunning);
  elements.runExportLabel.textContent = state.exportRunning ? "Export läuft ..." : "Export starten";
  elements.runHint.textContent = action === "show"
    ? "Alle verfügbaren Berichte werden oben angezeigt. Für einen Export bitte SQL oder Daten auswählen."
    : action === "data"
      ? "SQL und Berichtsdaten werden direkt exportiert. Das kann je nach Auswahl einige Minuten dauern."
      : "Die SQL-Dateien werden direkt exportiert. PowerShell oder Python sind nicht erforderlich.";
  renderReportList();
  elements.commandPreview.textContent = buildCommand();
  elements.copyState.textContent = "";
}

async function loadConfigs() {
  const response = await fetch("/api/configs", { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`Konfigurationen konnten nicht geladen werden (${response.status}).`);
  const payload = await response.json();
  state.configs = payload.configs || [];
  elements.configSelect.replaceChildren();
  for (const config of state.configs) {
    const option = document.createElement("option");
    option.value = config.id;
    option.textContent = config.name;
    elements.configSelect.append(option);
  }
  const savedId = localStorage.getItem(CONFIG_STORAGE_KEY);
  const preferredId = state.configs.some((config) => config.id === savedId) ? savedId : payload.defaultConfigId;
  if (preferredId) elements.configSelect.value = preferredId;
  if (!state.configs.length) {
    elements.configSelect.append(new Option("Keine Konfiguration vorhanden", ""));
    elements.copyCommandBtn.disabled = true;
  }
  render();
  maybeLoadReports();
}

async function loadDefaults() {
  const response = await fetch("/api/cli-wizard/defaults", { headers: { Accept: "application/json" } });
  if (!response.ok) return;
  const payload = await response.json();
  if (!elements.outputInput.value) elements.outputInput.value = payload.outputDir || "";
  render();
}

async function loadAppInfo() {
  const response = await fetch("/api/health", { headers: { Accept: "application/json" } });
  if (!response.ok) return;
  const payload = await response.json();
  const version = payload.version || "-";
  elements.appVersion.textContent = `v${version}`;
  document.title = `CLI-Wizard - NEMO Deficiencies v${version}`;
}

function apiDetailText(detail) {
  if (typeof detail === "string") return detail;
  if (detail && typeof detail.message === "string") return detail.message;
  if (Array.isArray(detail)) return detail.map((item) => item?.msg || String(item)).join("; ");
  return "Der Export konnte nicht abgeschlossen werden.";
}

function showExportResult(title, lines, isError = false) {
  elements.exportResult.replaceChildren();
  const heading = document.createElement("strong");
  heading.textContent = title;
  elements.exportResult.append(heading);
  for (const line of lines) {
    const text = document.createElement("span");
    text.textContent = line;
    elements.exportResult.append(text);
  }
  elements.exportResult.classList.toggle("is-error", isError);
  elements.exportResult.hidden = false;
}

async function runExport() {
  const config = selectedConfig();
  const action = selectedAction();
  if (!config || action === "show" || state.exportRunning) return;
  state.exportRunning = true;
  elements.exportResult.hidden = true;
  render();
  const mode = elements.selectionMode.value;
  const payload = {
    configId: config.id,
    project: elements.projectSelect.value,
    action,
    selectionMode: mode,
    reportRefs: mode === "exact" ? selectedReportValues() : [],
    containsValues: mode === "contains" ? reportValues() : [],
    outputDir: elements.outputInput.value.trim(),
    refreshIndex: elements.refreshIndex.checked,
  };
  try {
    const response = await fetch("/api/cli-wizard/export", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(apiDetailText(result.detail));
    const lines = [
      `Zielordner: ${result.outputDir}`,
      `${result.sqlFileCount} SQL-Dateien · ${result.dataFileCount} Datendateien`,
    ];
    if (result.dataErrorCount) lines.push(`${result.dataErrorCount} Datenexporte sind fehlgeschlagen; Details stehen im Index.`);
    showExportResult("Export abgeschlossen", lines);
  } catch (error) {
    showExportResult("Export fehlgeschlagen", [error.message], true);
  } finally {
    state.exportRunning = false;
    render();
  }
}

async function copyCommand() {
  try {
    await navigator.clipboard.writeText(buildCommand());
    elements.copyState.textContent = "Befehl wurde in die Zwischenablage kopiert.";
  } catch (_error) {
    const range = document.createRange();
    range.selectNodeContents(elements.commandPreview);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    elements.copyState.textContent = "Befehl ist markiert. Mit Strg+C kopieren.";
  }
}

function downloadCommand() {
  const config = selectedConfig();
  const safeName = (config?.name || "config").replace(/[^A-Za-z0-9._-]+/g, "_");
  const blob = new Blob([`\uFEFF${buildCommand()}\r\n`], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `nemo-export-${safeName}.ps1`;
  link.click();
  URL.revokeObjectURL(url);
  elements.copyState.textContent = "PowerShell-Datei wurde erstellt.";
}

elements.form.addEventListener("input", render);
elements.form.addEventListener("change", () => {
  if (elements.configSelect.value) localStorage.setItem(CONFIG_STORAGE_KEY, elements.configSelect.value);
  render();
  maybeLoadReports();
});
elements.reportChoiceList.addEventListener("input", (event) => {
  if (!(event.target instanceof HTMLInputElement) || event.target.type !== "checkbox") return;
  if (event.target.checked) state.selectedReports.add(event.target.value);
  else state.selectedReports.delete(event.target.value);
  render();
});
elements.selectAllReportsBtn.addEventListener("click", () => {
  state.selectedReports = new Set(state.reports.map(reportReference));
  render();
});
elements.clearReportsBtn.addEventListener("click", () => {
  state.selectedReports.clear();
  render();
});
elements.runExportBtn.addEventListener("click", runExport);
elements.downloadCommandBtn.addEventListener("click", downloadCommand);
elements.copyCommandBtn.addEventListener("click", copyCommand);

loadConfigs().catch((error) => {
  elements.configSelect.replaceChildren(new Option("Fehler beim Laden", ""));
  elements.copyCommandBtn.disabled = true;
  elements.copyState.textContent = error.message;
});
loadDefaults().catch(() => {});
loadAppInfo().catch(() => {});
