const LAST_CONFIG_STORAGE_KEY = "nemo-last-config-id";
const LAST_AI_CONFIG_STORAGE_KEY = "nemo-last-ai-config-id";
const UI_MODE_STORAGE_KEY = "nemo-ui-mode";
const UI_LANGUAGE_STORAGE_KEY = "nemo-ui-language";
const REPORT_LANGUAGE_STORAGE_KEY = "nemo-report-language";
const AI_PROVIDER_PRESETS = {
  groq: { name: "Groq", baseUrl: "https://api.groq.com/openai/v1", model: "openai/gpt-oss-120b", keyRequired: true },
  openai: { name: "OpenAI", baseUrl: "https://api.openai.com/v1", model: "gpt-5-mini", keyRequired: true },
  gemini: { name: "Gemini", baseUrl: "https://generativelanguage.googleapis.com/v1beta/openai", model: "gemini-3.5-flash", keyRequired: true },
  perplexity: { name: "Perplexity", baseUrl: "https://api.perplexity.ai", model: "sonar", keyRequired: true },
  ollama: { name: "Ollama lokal", baseUrl: "http://localhost:11434/v1", model: "qwen3:8b", keyRequired: false },
  lmstudio: { name: "LM Studio lokal", baseUrl: "http://localhost:1234/v1", model: "local-model", keyRequired: false },
  openai_compatible: { name: "Eigene KI", baseUrl: "http://localhost:8001/v1", model: "local-model", keyRequired: false },
};

const state = {
  configs: [],
  aiConfigs: [],
  aiConfigId: null,
  projects: [],
  projectColumns: {},
  loadingColumns: false,
  configId: null,
  project: "Master Data",
  reports: [],
  filteredReports: [],
  selectedReport: null,
  loadingReportRef: null,
  loadingReports: false,
  runningReport: false,
  activeView: "editor",
  harmonization: null,
  loadingHarmonization: false,
  selectedHarmonization: null,
  harmonizationPreview: null,
  previewingHarmonization: false,
  applyingHarmonization: false,
  editorModel: null,
  loadingEditor: false,
  editorLoadToken: 0,
  ruleCatalog: { dimensions: [], ruleTypes: [] },
  ruleTemplates: [],
  selectedRuleTemplateId: null,
  savingRuleTemplate: false,
  ruleTemplateAnalysis: null,
  selectedRuleTemplateCandidateKey: null,
  analyzingExistingRules: false,
  importingRuleCandidates: false,
  decidingRuleCandidate: false,
  originalEditorModel: null,
  editorDirty: false,
  currentDraft: null,
  savingDraft: false,
  deletingDraft: false,
  generatingSql: false,
  exportingSql: false,
  writingToNemo: false,
  loggingChange: false,
  undoingChange: false,
  restoringOriginal: false,
  creatingConfig: false,
  editingConfigId: null,
  configNameAuto: true,
  configStatistics: null,
  loadingConfigStatistics: false,
  creatingAiConfig: false,
  generatingAiRule: false,
  testingAiExamples: false,
  explainingAiRule: false,
  revisingAiRule: false,
  profilingAiField: false,
  renderedSql: null,
  changeLog: [],
  baseline: null,
  reportSqlHash: "",
  expandedGroups: new Set(),
  selectedRuleRef: null,
  selectedBlockIndex: null,
  selectedContextItem: null,
  sidebarCollapsed: false,
  uiMode: "standard",
  uiLanguage: "de",
  reportLanguage: "de",
  renderedReportLanguage: null,
  translatingMessages: false,
  messageTranslationCache: new Map(),
  lastTranslationStats: { browserHits: 0, sqliteHits: 0, aiTranslations: 0 },
};

const elements = {
  appShell: document.querySelector(".app-shell"),
  appVersion: document.querySelector("#appVersion"),
  sidebarToggleBtn: document.querySelector("#sidebarToggleBtn"),
  themeSelect: document.querySelector("#themeSelect"),
  uiLanguageSelect: document.querySelector("#uiLanguageSelect"),
  reportLanguageSelect: document.querySelector("#reportLanguageSelect"),
  standardModeBtn: document.querySelector("#standardModeBtn"),
  expertModeBtn: document.querySelector("#expertModeBtn"),
  connectionState: document.querySelector("#connectionState"),
  aiConnectionState: document.querySelector("#aiConnectionState"),
  aiProfileSelect: document.querySelector("#aiProfileSelect"),
  aiConfigBtn: document.querySelector("#aiConfigBtn"),
  aiConfigDialog: document.querySelector("#aiConfigDialog"),
  aiConfigForm: document.querySelector("#aiConfigForm"),
  closeAiConfigDialogBtn: document.querySelector("#closeAiConfigDialogBtn"),
  cancelAiConfigBtn: document.querySelector("#cancelAiConfigBtn"),
  saveAiConfigBtn: document.querySelector("#saveAiConfigBtn"),
  aiConfigNameInput: document.querySelector("#aiConfigNameInput"),
  aiProviderInput: document.querySelector("#aiProviderInput"),
  aiModelInput: document.querySelector("#aiModelInput"),
  aiBaseUrlInput: document.querySelector("#aiBaseUrlInput"),
  aiApiKeyInput: document.querySelector("#aiApiKeyInput"),
  ruleTemplateCatalogBtn: document.querySelector("#ruleTemplateCatalogBtn"),
  ruleTemplateCatalogDialog: document.querySelector("#ruleTemplateCatalogDialog"),
  ruleTemplateForm: document.querySelector("#ruleTemplateForm"),
  closeRuleTemplateCatalogBtn: document.querySelector("#closeRuleTemplateCatalogBtn"),
  cancelRuleTemplateCatalogBtn: document.querySelector("#cancelRuleTemplateCatalogBtn"),
  newRuleTemplateBtn: document.querySelector("#newRuleTemplateBtn"),
  saveRuleTemplateBtn: document.querySelector("#saveRuleTemplateBtn"),
  ruleTemplateList: document.querySelector("#ruleTemplateList"),
  ruleTemplateKeyInput: document.querySelector("#ruleTemplateKeyInput"),
  ruleTemplateStatusSelect: document.querySelector("#ruleTemplateStatusSelect"),
  ruleTemplateNameInput: document.querySelector("#ruleTemplateNameInput"),
  ruleTemplateDescriptionInput: document.querySelector("#ruleTemplateDescriptionInput"),
  ruleTemplateConditionInput: document.querySelector("#ruleTemplateConditionInput"),
  ruleTemplateDimensionInput: document.querySelector("#ruleTemplateDimensionInput"),
  ruleTemplateTypeInput: document.querySelector("#ruleTemplateTypeInput"),
  ruleTemplateMessageDeInput: document.querySelector("#ruleTemplateMessageDeInput"),
  ruleTemplateMessageEnInput: document.querySelector("#ruleTemplateMessageEnInput"),
  ruleTemplateParametersInput: document.querySelector("#ruleTemplateParametersInput"),
  ruleTemplateDataTypesInput: document.querySelector("#ruleTemplateDataTypesInput"),
  ruleTemplateCategoriesInput: document.querySelector("#ruleTemplateCategoriesInput"),
  ruleTemplateChangeNoteInput: document.querySelector("#ruleTemplateChangeNoteInput"),
  ruleTemplateVersionInfo: document.querySelector("#ruleTemplateVersionInfo"),
  analyzeExistingRulesBtn: document.querySelector("#analyzeExistingRulesBtn"),
  ruleTemplateAnalysisPanel: document.querySelector("#ruleTemplateAnalysisPanel"),
  ruleTemplateAnalysisInfo: document.querySelector("#ruleTemplateAnalysisInfo"),
  ruleTemplateCandidateList: document.querySelector("#ruleTemplateCandidateList"),
  importRuleTemplateCandidatesBtn: document.querySelector("#importRuleTemplateCandidatesBtn"),
  ruleTemplateEditorPanel: document.querySelector("#ruleTemplateEditorPanel"),
  ruleTemplateCandidateDetail: document.querySelector("#ruleTemplateCandidateDetail"),
  ruleTemplateCandidateName: document.querySelector("#ruleTemplateCandidateName"),
  ruleTemplateCandidateStatus: document.querySelector("#ruleTemplateCandidateStatus"),
  ruleTemplateCandidateMeta: document.querySelector("#ruleTemplateCandidateMeta"),
  ruleTemplateCandidateCondition: document.querySelector("#ruleTemplateCandidateCondition"),
  ruleTemplateCandidateParameters: document.querySelector("#ruleTemplateCandidateParameters"),
  ruleTemplateCandidateMessages: document.querySelector("#ruleTemplateCandidateMessages"),
  ruleTemplateCandidateLocations: document.querySelector("#ruleTemplateCandidateLocations"),
  rejectRuleTemplateCandidateBtn: document.querySelector("#rejectRuleTemplateCandidateBtn"),
  openCandidateTemplateBtn: document.querySelector("#openCandidateTemplateBtn"),
  importSingleRuleTemplateCandidateBtn: document.querySelector("#importSingleRuleTemplateCandidateBtn"),
  configSelect: document.querySelector("#configSelect"),
  configStatisticsBtn: document.querySelector("#configStatisticsBtn"),
  editConfigBtn: document.querySelector("#editConfigBtn"),
  addConfigBtn: document.querySelector("#addConfigBtn"),
  configDialog: document.querySelector("#configDialog"),
  configForm: document.querySelector("#configForm"),
  closeConfigDialogBtn: document.querySelector("#closeConfigDialogBtn"),
  cancelConfigBtn: document.querySelector("#cancelConfigBtn"),
  saveConfigBtn: document.querySelector("#saveConfigBtn"),
  deleteConfigBtn: document.querySelector("#deleteConfigBtn"),
  configDialogTitle: document.querySelector("#configDialogTitle"),
  configNameInput: document.querySelector("#configNameInput"),
  configTenantInput: document.querySelector("#configTenantInput"),
  configUserIdInput: document.querySelector("#configUserIdInput"),
  configPasswordInput: document.querySelector("#configPasswordInput"),
  configPasswordHint: document.querySelector("#configPasswordHint"),
  configNemoUrlInput: document.querySelector("#configNemoUrlInput"),
  configEnvironmentInput: document.querySelector("#configEnvironmentInput"),
  configStatisticsDialog: document.querySelector("#configStatisticsDialog"),
  closeConfigStatisticsBtn: document.querySelector("#closeConfigStatisticsBtn"),
  closeConfigStatisticsActionBtn: document.querySelector("#closeConfigStatisticsActionBtn"),
  exportConfigStatisticsBtn: document.querySelector("#exportConfigStatisticsBtn"),
  configStatisticsInfo: document.querySelector("#configStatisticsInfo"),
  configStatisticsLoading: document.querySelector("#configStatisticsLoading"),
  configStatisticsContent: document.querySelector("#configStatisticsContent"),
  statisticsReportsMetric: document.querySelector("#statisticsReportsMetric"),
  statisticsGroupsMetric: document.querySelector("#statisticsGroupsMetric"),
  statisticsFieldsMetric: document.querySelector("#statisticsFieldsMetric"),
  statisticsRulesMetric: document.querySelector("#statisticsRulesMetric"),
  statisticsActiveMetric: document.querySelector("#statisticsActiveMetric"),
  statisticsInactiveMetric: document.querySelector("#statisticsInactiveMetric"),
  statisticsActiveRate: document.querySelector("#statisticsActiveRate"),
  statisticsActiveBar: document.querySelector("#statisticsActiveBar"),
  statisticsInactiveBar: document.querySelector("#statisticsInactiveBar"),
  configStatisticsTable: document.querySelector("#configStatisticsTable"),
  projectTabs: document.querySelector("#projectTabs"),
  searchInput: document.querySelector("#searchInput"),
  refreshBtn: document.querySelector("#refreshBtn"),
  reportCount: document.querySelector("#reportCount"),
  reportList: document.querySelector("#reportList"),
  projectLabel: document.querySelector("#projectLabel"),
  reportTitle: document.querySelector("#reportTitle"),
  reportMeta: document.querySelector("#reportMeta"),
  columnsMetric: document.querySelector("#columnsMetric"),
  sqlMetric: document.querySelector("#sqlMetric"),
  rowsMetric: document.querySelector("#rowsMetric"),
  statusMetric: document.querySelector("#statusMetric"),
  maxRowsInput: document.querySelector("#maxRowsInput"),
  runBtn: document.querySelector("#runBtn"),
  resultViewBtn: document.querySelector("#resultViewBtn"),
  editorViewBtn: document.querySelector("#editorViewBtn"),
  harmonizationViewBtn: document.querySelector("#harmonizationViewBtn"),
  resultView: document.querySelector("#resultView"),
  editorView: document.querySelector("#editorView"),
  harmonizationView: document.querySelector("#harmonizationView"),
  harmonizationInfo: document.querySelector("#harmonizationInfo"),
  harmonizationSearchInput: document.querySelector("#harmonizationSearchInput"),
  refreshHarmonizationBtn: document.querySelector("#refreshHarmonizationBtn"),
  harmonizationReportsMetric: document.querySelector("#harmonizationReportsMetric"),
  harmonizationFieldsMetric: document.querySelector("#harmonizationFieldsMetric"),
  harmonizationDivergentMetric: document.querySelector("#harmonizationDivergentMetric"),
  harmonizationMissingMetric: document.querySelector("#harmonizationMissingMetric"),
  harmonizationMatrix: document.querySelector("#harmonizationMatrix"),
  emptyHarmonization: document.querySelector("#emptyHarmonization"),
  harmonizationDetail: document.querySelector("#harmonizationDetail"),
  previewInfo: document.querySelector("#previewInfo"),
  previewTable: document.querySelector("#previewTable"),
  emptyPreview: document.querySelector("#emptyPreview"),
  loadEditorBtn: document.querySelector("#loadEditorBtn"),
  validateEditorBtn: document.querySelector("#validateEditorBtn"),
  renderSqlBtn: document.querySelector("#renderSqlBtn"),
  exportSqlBtn: document.querySelector("#exportSqlBtn"),
  writeNemoBtn: document.querySelector("#writeNemoBtn"),
  resetEditorBtn: document.querySelector("#resetEditorBtn"),
  saveDraftBtn: document.querySelector("#saveDraftBtn"),
  deleteDraftBtn: document.querySelector("#deleteDraftBtn"),
  editorInfo: document.querySelector("#editorInfo"),
  blocksMetric: document.querySelector("#blocksMetric"),
  groupsMetric: document.querySelector("#groupsMetric"),
  rulesMetric: document.querySelector("#rulesMetric"),
  findingsMetric: document.querySelector("#findingsMetric"),
  blockList: document.querySelector("#blockList"),
  groupList: document.querySelector("#groupList"),
  contextPanelTitle: document.querySelector("#contextPanelTitle"),
  contextPanelActions: document.querySelector("#contextPanelActions"),
  addGroupBtn: document.querySelector("#addGroupBtn"),
  addRuleBtn: document.querySelector("#addRuleBtn"),
  groupToggleBtn: document.querySelector("#groupToggleBtn"),
  editorGrid: document.querySelector("#editorGrid"),
  parameterDetail: document.querySelector("#parameterDetail"),
  sqlPreviewPanel: document.querySelector("#sqlPreviewPanel"),
  ruleDetail: document.querySelector("#ruleDetail"),
  detailPanelTitle: document.querySelector("#detailPanelTitle"),
  undoChangeBtn: document.querySelector("#undoChangeBtn"),
  restoreOriginalBtn: document.querySelector("#restoreOriginalBtn"),
  changeLogInfo: document.querySelector("#changeLogInfo"),
  changeLogList: document.querySelector("#changeLogList"),
  validationList: document.querySelector("#validationList"),
  sqlPreviewInfo: document.querySelector("#sqlPreviewInfo"),
  sqlPreview: document.querySelector("#sqlPreview"),
  toast: document.querySelector("#toast"),
};

const UI_TEXT_EN = {
  "Sprache": "Language",
  "Berichtssprache": "Report language",
  "KI nicht eingerichtet": "AI not configured",
  "KI-Zugang": "AI access",
  "Regelkatalog": "Rule catalog",
  "Globale, projektübergreifende Regelvorlagen": "Global cross-project rule templates",
  "+ Vorlage": "+ Template",
  "Vorlage speichern": "Save template",
  "Schlüssel": "Key",
  "Entwurf": "Draft",
  "Freigegeben": "Approved",
  "Veraltet": "Deprecated",
  "Bedingung mit {field}": "Condition with {field}",
  "Fehlermeldung Deutsch": "German error message",
  "Fehlermeldung Englisch": "English error message",
  "Parameterdefinition (JSON)": "Parameter definition (JSON)",
  "Datentypen": "Data types",
  "Feldkategorien": "Field categories",
  "Änderungshinweis": "Change note",
  "Schließen": "Close",
  "Aus Katalog": "From catalog",
  "Master Data analysieren": "Analyze Master Data",
  "Analysekandidaten": "Analysis candidates",
  "Auswahl als Entwürfe übernehmen": "Import selection as drafts",
  "Aktive KI auswählen": "Select active AI",
  "Experte": "Expert",
  "Schema": "Theme",
  "Hell": "Light",
  "Dunkel": "Dark",
  "Konfiguration": "Configuration",
  "Konfiguration anlegen": "Create configuration",
  "Konfiguration bearbeiten": "Edit configuration",
  "Ausgewählte Konfiguration bearbeiten": "Edit selected configuration",
  "Name": "Name",
  "Tenant": "Tenant",
  "User-ID": "User ID",
  "Passwort": "Password",
  "NEMO-URL": "NEMO URL",
  "Environment": "Environment",
  "Wird verschlüsselt gespeichert": "Stored encrypted",
  "Leer lassen, um das gespeicherte Passwort beizubehalten": "Leave blank to keep the stored password",
  "Noch kein Passwort gespeichert": "No password stored yet",
  "Neu anlegen": "Create new",
  "Änderungen speichern": "Save changes",
  "Löschen": "Delete",
  "Statistik": "Statistics",
  "Statistik erstellen": "Create statistics",
  "Konfigurationsstatistik": "Configuration statistics",
  "Noch nicht erstellt": "Not created yet",
  "Berichte werden analysiert": "Reports are being analyzed",
  "Konfigurationsmetriken": "Configuration metrics",
  "Regelgruppen": "Rule groups",
  "Regelstatus": "Rule status",
  "Inaktiv": "Inactive",
  "Verteilung": "Distribution",
  "Tabelle exportieren": "Export table",
  "Projekt": "Project",
  "Suche": "Search",
  "Reportname": "Report name",
  "Aktualisieren": "Refresh",
  "Ergebnis laden": "Load result",
  "Spalten": "Columns",
  "Zeilen": "Rows",
  "Status": "Status",
  "bereit": "ready",
  "Ergebnis": "Result",
  "Harmonisierung": "Harmonization",
  "Feld suchen": "Search field",
  "Displayname oder Beschreibung": "Display name or description",
  "Harmonisierungsmetriken": "Harmonization metrics",
  "Berichte": "Reports",
  "Felder": "Fields",
  "Abweichungen": "Differences",
  "Fehlende Zuordnungen": "Missing assignments",
  "Harmonisierungs-Matrix": "Harmonization matrix",
  "Felddetails": "Field details",
  "Feld oder Berichtszelle auswählen": "Select a field or report cell",
  "Referenzbericht": "Reference report",
  "Zielberichte": "Target reports",
  "Änderungen prüfen": "Review changes",
  "Als Drafts übernehmen": "Apply as drafts",
  "Wird ersetzt": "Will be replaced",
  "Wird angelegt": "Will be created",
  "Kein Ergebnis geladen": "No result loaded",
  "Editor-Modell": "Editor model",
  "Modell laden": "Load model",
  "Validieren": "Validate",
  "SQL-Vorschau": "SQL preview",
  "SQL-Vorschau vollständig": "Full SQL preview",
  "SQL exportieren": "Export SQL",
  "In NEMO speichern": "Save to NEMO",
  "Zurücksetzen": "Reset",
  "Draft speichern": "Save draft",
  "Draft verwerfen": "Discard draft",
  "Blöcke": "Blocks",
  "Gruppen": "Groups",
  "Regeln": "Rules",
  "Hinweise": "Notices",
  "Datenqualitätsregeln": "Data quality rules",
  "Regelparameter": "Rule parameters",
  "Änderungsverlauf": "Change history",
  "Rückgängig": "Undo",
  "Ursprungsbericht wiederherstellen": "Restore original report",
  "Noch keine Änderungen": "No changes yet",
  "Noch keine Änderungen protokolliert": "No changes logged yet",
  "Noch nicht generiert": "Not generated yet",
  "Keine SQL-Vorschau": "No SQL preview",
  "Alle aufklappen": "Expand all",
  "+ Regelgruppe": "+ Rule group",
  "+ Regel": "+ Rule",
  "Neue Regelgruppe": "New rule group",
  "Regelgruppe bearbeiten": "Edit rule group",
  "Regelgruppe": "Rule group",
  "Regelgruppe entfernen": "Remove rule group",
  "Neue Regel": "New rule",
  "Feld suchen": "Search field",
  "Beschreibung": "Description",
  "Bedingung": "Condition",
  "Fehlermeldung": "Error message",
  "DQ-Typ": "DQ type",
  "Regeltyp": "Rule type",
  "Vollständigkeit": "Completeness",
  "Validität": "Validity",
  "Korrektheit": "Correctness",
  "Eindeutigkeit": "Uniqueness",
  "Konsistenz": "Consistency",
  "Aktualität": "Timeliness",
  "Genauigkeit": "Accuracy",
  "Redundanz": "Redundancy",
  "Einheitlichkeit": "Uniformity",
  "Relevanz": "Relevance",
  "Zuverlässigkeit": "Reliability",
  "Verständlichkeit": "Understandability",
  "Ohne Typ": "No type",
  "Ohne DQ-Typ": "No DQ type",
  "Aktiv": "Active",
  "Alle an/aus": "All on/off",
  "Formel erklären": "Explain formula",
  "Mit KI überarbeiten": "Revise with AI",
  "Regel prüfen": "Check rule",
  "Beispiele prüfen": "Test examples",
  "Vorschlag übernehmen": "Apply suggestion",
  "Übernehmen": "Apply",
  "Löschen": "Delete",
  "Abbrechen": "Cancel",
  "Anlegen": "Create",
  "Speichern und prüfen": "Save and test",
  "KI-Regelvorschläge erzeugen": "Generate AI rule suggestions",
  "Fachliche Regelbeschreibung": "Business rule description",
  "Entwurf erstellen": "Create draft",
  "Regelgruppe anlegen": "Create rule group",
  "Bezeichnung": "Name",
  "Anbieter": "Provider",
  "Modell": "Model",
  "API-Adresse": "API address",
  "API-Key": "API key",
  "Passwort": "Password",
  "Dialog schließen": "Close dialog",
  "Linke Spalte einklappen": "Collapse left column",
  "Linke Spalte ausklappen": "Expand left column",
};
const uiOriginalText = new WeakMap();
const uiOriginalAttributes = new WeakMap();

function translateUiTree(root = document.body) {
  if (!root) return;
  const nodes = root.nodeType === Node.TEXT_NODE ? [root] : [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    if (["SCRIPT", "STYLE", "PRE", "CODE"].includes(node.parentElement?.tagName)) continue;
    if (!uiOriginalText.has(node)) uiOriginalText.set(node, node.nodeValue);
    const original = uiOriginalText.get(node) || "";
    const trimmed = original.trim();
    const translated = state.uiLanguage === "en" ? (UI_TEXT_EN[trimmed] || trimmed) : trimmed;
    node.nodeValue = trimmed ? original.replace(trimmed, translated) : original;
  }
  const container = root.nodeType === Node.ELEMENT_NODE ? root : document.body;
  const attributedElements = [...(container.querySelectorAll?.("[placeholder], [title], [aria-label]") || [])];
  if (container.matches?.("[placeholder], [title], [aria-label]")) attributedElements.unshift(container);
  for (const element of attributedElements) {
    if (!uiOriginalAttributes.has(element)) {
      uiOriginalAttributes.set(element, Object.fromEntries(
        ["placeholder", "title", "aria-label"].filter((name) => element.hasAttribute(name)).map((name) => [name, element.getAttribute(name)]),
      ));
    }
    for (const [name, original] of Object.entries(uiOriginalAttributes.get(element))) {
      element.setAttribute(name, state.uiLanguage === "en" ? (UI_TEXT_EN[original] || original) : original);
    }
  }
}

function applyUiLanguage(language) {
  state.uiLanguage = language === "en" ? "en" : "de";
  document.documentElement.lang = state.uiLanguage;
  elements.uiLanguageSelect.value = state.uiLanguage;
  localStorage.setItem(UI_LANGUAGE_STORAGE_KEY, state.uiLanguage);
  translateUiTree(document.body);
  if (state.configStatistics) {
    renderConfigStatistics();
  }
}

function observeUiTranslations() {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE || node.nodeType === Node.TEXT_NODE) translateUiTree(node);
      }
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
}

function applySidebarState(collapsed) {
  state.sidebarCollapsed = Boolean(collapsed);
  elements.appShell.classList.toggle("sidebar-collapsed", state.sidebarCollapsed);
  elements.sidebarToggleBtn.setAttribute("aria-expanded", String(!state.sidebarCollapsed));
  const label = state.sidebarCollapsed ? "Linke Spalte ausklappen" : "Linke Spalte einklappen";
  elements.sidebarToggleBtn.setAttribute("aria-label", label);
  elements.sidebarToggleBtn.title = label;
  localStorage.setItem("nemo-sidebar-collapsed", state.sidebarCollapsed ? "1" : "0");
}

function toggleSidebar() {
  applySidebarState(!state.sidebarCollapsed);
}

function showParameterDetail() {
  elements.editorGrid?.classList.remove("detail-sql-active");
  if (elements.parameterDetail) {
    elements.parameterDetail.hidden = false;
  }
  if (elements.sqlPreviewPanel) {
    elements.sqlPreviewPanel.hidden = true;
  }
}

function showSqlDetail() {
  elements.editorGrid?.classList.add("detail-sql-active");
  if (elements.parameterDetail) {
    elements.parameterDetail.hidden = true;
  }
  if (elements.sqlPreviewPanel) {
    elements.sqlPreviewPanel.hidden = false;
  }
  elements.detailPanelTitle.textContent = "SQL-Vorschau vollständig";
}

async function applyUiMode(mode) {
  state.uiMode = mode === "expert" ? "expert" : "standard";
  const isStandard = state.uiMode === "standard";
  elements.appShell.classList.toggle("mode-standard", isStandard);
  elements.standardModeBtn.classList.toggle("active", isStandard);
  elements.expertModeBtn.classList.toggle("active", !isStandard);
  elements.standardModeBtn.setAttribute("aria-pressed", String(isStandard));
  elements.expertModeBtn.setAttribute("aria-pressed", String(!isStandard));
  localStorage.setItem(UI_MODE_STORAGE_KEY, state.uiMode);

  if (isStandard) {
    await switchView("editor");
    selectChecksBlockForStandard();
  }
}

function checksBlockIndex() {
  return (state.editorModel?.blocks || []).findIndex((block) => block.id === "checks");
}

function selectChecksBlockForStandard() {
  const blockIndex = checksBlockIndex();
  if (blockIndex >= 0 && state.selectedBlockIndex !== blockIndex) {
    selectBlock(blockIndex);
  }
}

function applyTheme(theme) {
  if (theme === "system") {
    document.documentElement.removeAttribute("data-theme");
  } else {
    document.documentElement.dataset.theme = theme;
  }
  localStorage.setItem("nemo-theme", theme);
  elements.themeSelect.value = theme;
}

function setStatus(text, variant = "neutral") {
  elements.statusMetric.textContent = text;
  elements.statusMetric.style.color = variant === "ok" ? "var(--ok)" : variant === "warn" ? "var(--warn)" : "var(--text)";
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => elements.toast.classList.remove("visible"), 12000);
}

function activeConfig() {
  return state.configs.find((config) => config.id === state.configId) || null;
}

function setConnectionState(status) {
  const tenant = activeConfig()?.tenant || "";
  elements.connectionState.textContent = tenant ? `${status} · ${tenant}` : status;
}
async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      message = apiDetailText(payload.detail) || message;
    } catch (_) {
      // Keep HTTP status text.
    }
    const requestId = response.headers.get("X-Request-ID");
    if (requestId && !message.includes(requestId)) {
      message = `${message} (Vorgang: ${requestId})`;
    }
    throw new Error(message);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function loadBaseData() {
  setStatus("lade");
  const [health, configs, projects, ruleCatalog, ruleTemplates] = await Promise.all([
    requestJson("/api/health"),
    requestJson("/api/configs"),
    requestJson("/api/projects"),
    requestJson("/api/rule-catalog"),
    requestJson("/api/rule-templates"),
  ]);

  const version = health.version || "-";
  elements.appVersion.textContent = `v${version}`;
  document.title = `NEMO Deficiencies v${version}`;

  state.configs = configs.configs || [];
  const savedConfigId = localStorage.getItem(LAST_CONFIG_STORAGE_KEY);
  const defaultConfigId = configs.defaultConfigId || state.configs[0]?.id || null;
  state.configId = state.configs.some((config) => config.id === savedConfigId) ? savedConfigId : defaultConfigId;
  if (state.configId) {
    localStorage.setItem(LAST_CONFIG_STORAGE_KEY, state.configId);
  }
  state.projects = projects.projects || [];
  state.project = projects.defaultProject || state.projects[0]?.id || "Master Data";
  state.ruleCatalog = ruleCatalog || { dimensions: [], ruleTypes: [] };
  state.ruleTemplates = ruleTemplates.templates || [];

  renderConfigSelect();
  renderProjectTabs();
  await loadAiConfigs();
  await loadReports();
}

function renderConfigSelect() {
  elements.configSelect.replaceChildren();
  for (const config of state.configs) {
    const option = document.createElement("option");
    option.value = config.id;
    option.textContent = `${config.name} (${config.sourceFile || config.source})`;
    elements.configSelect.append(option);
  }
  elements.configSelect.value = state.configId || "";
  elements.editConfigBtn.disabled = !state.configId;
  elements.configStatisticsBtn.disabled = !state.configId;
}

function configNameFromTenant(tenant) {
  const normalized = String(tenant || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "_")
    .replace(/^[._-]+|[._-]+$/g, "");
  return normalized ? `config_${normalized}`.slice(0, 120) : "";
}

function openCreateConfigDialog() {
  elements.configForm.reset();
  state.editingConfigId = null;
  state.configNameAuto = true;
  elements.configDialogTitle.textContent = "Konfiguration anlegen";
  elements.configPasswordInput.required = true;
  elements.configPasswordInput.placeholder = "";
  elements.configPasswordHint.textContent = "Wird verschlüsselt gespeichert";
  elements.configNemoUrlInput.value = "https://enter.nemo-ai.com";
  elements.configEnvironmentInput.value = "prod";
  elements.deleteConfigBtn.hidden = true;
  elements.saveConfigBtn.textContent = "Neu anlegen";
  elements.configDialog.showModal();
  elements.configTenantInput.focus();
}

async function openEditConfigDialog() {
  if (!state.configId || state.creatingConfig) {
    return;
  }
  state.creatingConfig = true;
  elements.editConfigBtn.disabled = true;
  try {
    const payload = await requestJson(`/api/configs/${encodeURIComponent(state.configId)}/connection`);
    const config = payload.config;
    elements.configForm.reset();
    state.editingConfigId = config.id;
    state.configNameAuto = false;
    elements.configDialogTitle.textContent = "Konfiguration bearbeiten";
    elements.configNameInput.value = config.name || "";
    elements.configTenantInput.value = config.tenant || "";
    elements.configUserIdInput.value = config.userid || "";
    elements.configPasswordInput.value = "";
    elements.configPasswordInput.required = false;
    elements.configPasswordInput.placeholder = "Unverändert lassen";
    elements.configPasswordHint.textContent = config.hasPassword
      ? "Leer lassen, um das gespeicherte Passwort beizubehalten"
      : "Noch kein Passwort gespeichert";
    elements.configNemoUrlInput.value = config.nemoUrl || "https://enter.nemo-ai.com";
    elements.configEnvironmentInput.value = config.environment || "prod";
    elements.deleteConfigBtn.hidden = false;
    elements.saveConfigBtn.textContent = "Änderungen speichern";
    elements.configDialog.showModal();
    elements.configNameInput.focus();
  } catch (error) {
    showToast(error.message);
  } finally {
    state.creatingConfig = false;
    elements.editConfigBtn.disabled = !state.configId;
  }
}

function closeConfigDialog() {
  elements.configForm.reset();
  state.editingConfigId = null;
  elements.configDialog.close();
}

async function openConfigStatistics() {
  if (!state.configId || state.loadingConfigStatistics) {
    return;
  }
  const requestedConfigId = state.configId;
  const requestedProject = state.project;
  state.configStatistics = null;
  state.loadingConfigStatistics = true;
  elements.configStatisticsDialog.showModal();
  elements.configStatisticsLoading.hidden = false;
  elements.configStatisticsContent.hidden = true;
  elements.exportConfigStatisticsBtn.disabled = true;
  elements.configStatisticsBtn.disabled = true;
  elements.configStatisticsInfo.textContent = state.uiLanguage === "en"
    ? "The current NEMO reports are being loaded"
    : "Aktuelle NEMO-Berichte werden geladen";
  try {
    const params = new URLSearchParams({
      configId: requestedConfigId,
      project: requestedProject,
    });
    const payload = await requestJson(`/api/config-statistics?${params.toString()}`);
    if (requestedConfigId !== state.configId || requestedProject !== state.project) {
      return;
    }
    state.configStatistics = payload;
    renderConfigStatistics();
    elements.configStatisticsContent.hidden = false;
    elements.exportConfigStatisticsBtn.disabled = false;
  } catch (error) {
    elements.configStatisticsInfo.textContent = error.message;
    showToast(error.message);
  } finally {
    state.loadingConfigStatistics = false;
    elements.configStatisticsLoading.hidden = true;
    elements.configStatisticsBtn.disabled = false;
  }
}

function closeConfigStatistics() {
  elements.configStatisticsDialog.close();
}

function renderConfigStatistics() {
  const payload = state.configStatistics;
  if (!payload) {
    return;
  }
  const summary = payload.summary || {};
  const totalRules = Number(summary.ruleCount || 0);
  const activeRules = Number(summary.activeRuleCount || 0);
  const inactiveRules = Number(summary.inactiveRuleCount || 0);
  const activeRate = totalRules ? Math.round((activeRules / totalRules) * 100) : 0;
  const generatedAt = payload.generatedAt ? new Date(payload.generatedAt).toLocaleString(state.uiLanguage) : "";
  const configLabel = payload.configTenant || payload.configName || payload.configId;
  const skippedText = summary.skippedReportCount
    ? (state.uiLanguage === "en"
      ? ` · ${summary.skippedReportCount} skipped`
      : ` · ${summary.skippedReportCount} übersprungen`)
    : "";

  elements.configStatisticsInfo.textContent = `${configLabel} · ${payload.project} · ${generatedAt}${skippedText}`;
  elements.statisticsReportsMetric.textContent = String(summary.reportCount || 0);
  elements.statisticsGroupsMetric.textContent = String(summary.groupCount || 0);
  elements.statisticsFieldsMetric.textContent = state.uiLanguage === "en"
    ? `${summary.distinctFieldCount || 0} distinct fields`
    : `${summary.distinctFieldCount || 0} unterschiedliche Felder`;
  elements.statisticsRulesMetric.textContent = String(totalRules);
  elements.statisticsActiveMetric.textContent = String(activeRules);
  elements.statisticsInactiveMetric.textContent = String(inactiveRules);
  elements.statisticsActiveRate.textContent = state.uiLanguage === "en"
    ? `${activeRate}% active`
    : `${activeRate} % aktiv`;
  elements.statisticsActiveBar.style.width = `${activeRate}%`;
  elements.statisticsInactiveBar.style.width = `${totalRules ? 100 - activeRate : 0}%`;
  elements.statisticsActiveBar.parentElement.setAttribute(
    "aria-label",
    state.uiLanguage === "en"
      ? `${activeRules} active and ${inactiveRules} inactive rules`
      : `${activeRules} aktive und ${inactiveRules} inaktive Regeln`,
  );

  const body = elements.configStatisticsTable.querySelector("tbody");
  const foot = elements.configStatisticsTable.querySelector("tfoot");
  body.replaceChildren();
  foot.replaceChildren();
  for (const report of payload.reports || []) {
    const row = document.createElement("tr");
    const nameCell = document.createElement("td");
    const name = document.createElement("span");
    name.className = "statistics-report-name";
    name.append(
      textBlock("strong", report.displayName || report.internalName),
      textBlock(
        "small",
        `${report.internalName || ""}${report.source === "draft" ? (state.uiLanguage === "en" ? " · Draft" : " · Entwurf") : ""}`,
      ),
    );
    nameCell.append(name);
    const distributionCell = document.createElement("td");
    distributionCell.append(statisticsMiniBar(report.activeRuleCount, report.inactiveRuleCount));
    row.append(
      nameCell,
      textBlock("td", String(report.groupCount || 0)),
      textBlock("td", String(report.ruleCount || 0)),
      textBlock("td", String(report.activeRuleCount || 0)),
      textBlock("td", String(report.inactiveRuleCount || 0)),
      distributionCell,
    );
    body.append(row);
  }

  const totalRow = document.createElement("tr");
  totalRow.append(
    textBlock("td", state.uiLanguage === "en" ? "Total" : "Gesamt"),
    textBlock("td", String(summary.groupCount || 0)),
    textBlock("td", String(totalRules)),
    textBlock("td", String(activeRules)),
    textBlock("td", String(inactiveRules)),
    document.createElement("td"),
  );
  foot.append(totalRow);
}

function statisticsMiniBar(active, inactive) {
  const total = Number(active || 0) + Number(inactive || 0);
  const activeRate = total ? (Number(active || 0) / total) * 100 : 0;
  const bar = document.createElement("span");
  bar.className = "statistics-mini-bar";
  const activePart = document.createElement("span");
  activePart.className = "active";
  activePart.style.width = `${activeRate}%`;
  const inactivePart = document.createElement("span");
  inactivePart.className = "inactive";
  inactivePart.style.width = `${total ? 100 - activeRate : 0}%`;
  bar.append(activePart, inactivePart);
  return bar;
}

function exportConfigStatistics() {
  const payload = state.configStatistics;
  if (!payload) {
    return;
  }
  const summary = payload.summary || {};
  const headers = state.uiLanguage === "en"
    ? ["Report", "Internal name", "Rule groups", "Rules", "Active", "Inactive", "Source"]
    : ["Bericht", "Internalname", "Regelgruppen", "Regeln", "Aktiv", "Inaktiv", "Quelle"];
  const rows = [
    [state.uiLanguage === "en" ? "Configuration" : "Konfiguration", payload.configName || payload.configId],
    ["Tenant", payload.configTenant || ""],
    [state.uiLanguage === "en" ? "Project" : "Projekt", payload.project || ""],
    [state.uiLanguage === "en" ? "Created" : "Erstellt", payload.generatedAt || ""],
    [],
    headers,
    ...(payload.reports || []).map((report) => [
      report.displayName || "",
      report.internalName || "",
      report.groupCount || 0,
      report.ruleCount || 0,
      report.activeRuleCount || 0,
      report.inactiveRuleCount || 0,
      report.source === "draft" ? (state.uiLanguage === "en" ? "Draft" : "Entwurf") : "NEMO",
    ]),
    [
      state.uiLanguage === "en" ? "Total" : "Gesamt",
      "",
      summary.groupCount || 0,
      summary.ruleCount || 0,
      summary.activeRuleCount || 0,
      summary.inactiveRuleCount || 0,
      "",
    ],
  ];
  const csv = `\uFEFF${rows.map((row) => row.map(csvCell).join(";")).join("\r\n")}`;
  const configName = payload.configName || payload.configTenant || payload.configId || "config";
  const safeName = String(configName).replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^[._]+|[._]+$/g, "") || "config";
  const date = new Date().toISOString().slice(0, 10);
  downloadBlob(new Blob([csv], { type: "text/csv;charset=utf-8" }), `${safeName}_statistics_${date}.csv`);
  showToast(state.uiLanguage === "en" ? "Statistics table exported" : "Statistiktabelle exportiert");
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

async function saveConfigFromDialog(event) {
  event.preventDefault();
  if (state.creatingConfig || !elements.configForm.reportValidity()) {
    return;
  }

  const editingConfigId = state.editingConfigId;
  const name = elements.configNameInput.value.trim();
  const tenant = elements.configTenantInput.value.trim();
  const userid = elements.configUserIdInput.value.trim();
  const password = elements.configPasswordInput.value;
  const nemoUrl = elements.configNemoUrlInput.value.trim().replace(/\/+$/, "");
  const environment = elements.configEnvironmentInput.value.trim();
  state.creatingConfig = true;
  elements.saveConfigBtn.disabled = true;
  elements.deleteConfigBtn.disabled = true;
  elements.saveConfigBtn.textContent = editingConfigId ? "Wird gespeichert" : "Wird angelegt";
  try {
    const payload = await requestJson(
      editingConfigId
        ? `/api/configs/${encodeURIComponent(editingConfigId)}/connection`
        : "/api/configs/from-credentials",
      {
        method: editingConfigId ? "PUT" : "POST",
        body: JSON.stringify({ name, tenant, userid, password, nemoUrl, environment }),
      },
    );
    const config = payload.config;
    state.configs = [...state.configs.filter((item) => item.id !== config.id), config].sort(
      (left, right) => left.name.localeCompare(right.name),
    );
    state.configId = config.id;
    state.projectColumns = {};
    state.selectedReport = null;
    state.reports = [];
    state.filteredReports = [];
    localStorage.setItem(LAST_CONFIG_STORAGE_KEY, state.configId);
    renderConfigSelect();
    closeConfigDialog();
    clearPreview();
    clearEditor(editingConfigId ? "Konfiguration geändert - Berichte werden neu geladen" : "Neue Konfiguration - Berichte werden geladen");
    renderReports();
    renderSelection();
    await loadReports();
    showToast(
      editingConfigId
        ? `Änderungen an ${config.name} wurden verschlüsselt gespeichert`
        : `Konfiguration ${config.name} wurde verschlüsselt gespeichert`,
    );
  } catch (error) {
    showToast(error.message);
  } finally {
    elements.configPasswordInput.value = "";
    state.creatingConfig = false;
    elements.saveConfigBtn.disabled = false;
    elements.deleteConfigBtn.disabled = false;
    if (elements.configDialog.open) {
      elements.saveConfigBtn.textContent = editingConfigId ? "Änderungen speichern" : "Neu anlegen";
    }
  }
}

async function deleteConfigFromDialog() {
  const configId = state.editingConfigId;
  const config = state.configs.find((item) => item.id === configId);
  if (!configId || !config || state.creatingConfig) {
    return;
  }
  if (!window.confirm(`Konfiguration "${config.name}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`)) {
    return;
  }

  state.creatingConfig = true;
  elements.deleteConfigBtn.disabled = true;
  elements.saveConfigBtn.disabled = true;
  try {
    await requestJson(`/api/configs/${encodeURIComponent(configId)}`, {
      method: "DELETE",
    });
    state.configs = state.configs.filter((item) => item.id !== configId);
    state.configId = state.configs[0]?.id || null;
    state.projectColumns = {};
    state.selectedReport = null;
    state.reports = [];
    state.filteredReports = [];
    if (state.configId) {
      localStorage.setItem(LAST_CONFIG_STORAGE_KEY, state.configId);
    } else {
      localStorage.removeItem(LAST_CONFIG_STORAGE_KEY);
    }
    renderConfigSelect();
    closeConfigDialog();
    clearPreview();
    clearEditor(state.configId ? "Konfiguration gelöscht - Berichte werden neu geladen" : "Keine Konfiguration vorhanden");
    renderReports();
    renderSelection();
    if (state.configId) {
      await loadReports();
    }
    showToast(`Konfiguration ${config.name} wurde gelöscht`);
  } catch (error) {
    showToast(error.message);
  } finally {
    state.creatingConfig = false;
    elements.deleteConfigBtn.disabled = false;
    elements.saveConfigBtn.disabled = false;
  }
}

async function loadAiConfigs() {
  state.aiConfigs = [];
  state.aiConfigId = null;
  try {
    const payload = await requestJson("/api/ai/configs");
    state.aiConfigs = payload.configs || [];
    const savedId = localStorage.getItem(LAST_AI_CONFIG_STORAGE_KEY);
    state.aiConfigId = state.aiConfigs.some((item) => item.id === savedId)
      ? savedId
      : payload.defaultAiConfigId || state.aiConfigs[0]?.id || null;
    elements.aiProfileSelect.replaceChildren();
    for (const profile of state.aiConfigs) {
      const option = document.createElement("option");
      option.value = profile.id;
      option.textContent = `${profile.name} · ${profile.model}`;
      elements.aiProfileSelect.append(option);
    }
    elements.aiProfileSelect.hidden = state.aiConfigs.length === 0;
    elements.aiProfileSelect.value = state.aiConfigId || "";
    const active = state.aiConfigs.find((item) => item.id === state.aiConfigId);
    elements.aiConnectionState.textContent = active ? `KI · ${active.name}` : "KI nicht eingerichtet";
  } catch (error) {
    elements.aiConnectionState.textContent = "KI-Fehler";
    showToast(error.message);
  }
}

function openAiConfigDialog() {
  elements.aiConfigForm.reset();
  elements.aiProviderInput.value = "groq";
  applyAiProviderPreset();
  elements.aiConfigDialog.showModal();
  elements.aiConfigNameInput.focus();
}

function applyAiProviderPreset() {
  const preset = AI_PROVIDER_PRESETS[elements.aiProviderInput.value] || AI_PROVIDER_PRESETS.openai_compatible;
  elements.aiConfigNameInput.value = preset.name;
  elements.aiModelInput.value = preset.model;
  elements.aiBaseUrlInput.value = preset.baseUrl;
  elements.aiApiKeyInput.required = preset.keyRequired;
  elements.aiApiKeyInput.placeholder = preset.keyRequired ? "Erforderlich" : "Optional";
}

function closeAiConfigDialog() {
  elements.aiApiKeyInput.value = "";
  elements.aiConfigDialog.close();
}

async function loadRuleTemplates() {
  const payload = await requestJson("/api/rule-templates");
  state.ruleTemplates = payload.templates || [];
  renderRuleTemplateList();
}

async function analyzeExistingRules() {
  if (!state.configId || state.analyzingExistingRules) return;
  state.analyzingExistingRules = true;
  elements.analyzeExistingRulesBtn.disabled = true;
  elements.analyzeExistingRulesBtn.textContent = "Analyse läuft";
  try {
    state.ruleTemplateAnalysis = await requestJson("/api/rule-templates/analyze-existing", {
      method: "POST",
      body: JSON.stringify({configId: state.configId, project: "Master Data"}),
    });
    renderRuleTemplateAnalysis();
    const summary = state.ruleTemplateAnalysis.summary;
    showToast(`${summary.ruleCount} Regeln zu ${summary.candidateCount} Kandidaten gruppiert`);
  } catch (error) {
    showToast(error.message);
  } finally {
    state.analyzingExistingRules = false;
    elements.analyzeExistingRulesBtn.disabled = false;
    elements.analyzeExistingRulesBtn.textContent = "Master Data analysieren";
  }
}

function renderRuleTemplateAnalysis() {
  const analysis = state.ruleTemplateAnalysis;
  elements.ruleTemplateCandidateList.replaceChildren();
  elements.ruleTemplateAnalysisPanel.hidden = !analysis;
  if (!analysis) return;
  if (
    state.selectedRuleTemplateCandidateKey
    && !(analysis.candidates || []).some((candidate) => candidate.key === state.selectedRuleTemplateCandidateKey)
  ) {
    state.selectedRuleTemplateCandidateKey = null;
    elements.ruleTemplateCandidateDetail.hidden = true;
    elements.ruleTemplateEditorPanel.hidden = false;
    elements.saveRuleTemplateBtn.hidden = false;
  }
  const summary = analysis.summary || {};
  elements.ruleTemplateAnalysisInfo.textContent =
    `${summary.ruleCount || 0} Regeln · ${summary.newCandidateCount || 0} neu · ${summary.cataloguedCount || 0} katalogisiert`;
  for (const candidate of analysis.candidates || []) {
    const row = document.createElement("div");
    row.className = [
      "rule-template-candidate",
      candidate.existingTemplateId ? "catalogued" : "",
      candidate.decision === "rejected" ? "rejected" : "",
      candidate.decision === "imported" ? "imported" : "",
      candidate.key === state.selectedRuleTemplateCandidateKey ? "active" : "",
    ].filter(Boolean).join(" ");
    row.title = `${candidate.conditionTemplate}\n${candidate.messageDeTemplate || candidate.messageEnTemplate || ""}`;
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = candidate.key;
    checkbox.checked =
      candidate.decision === "pending" && !candidate.existingTemplateId && candidate.occurrenceCount >= 2;
    checkbox.disabled = candidate.decision === "rejected" || candidate.decision === "imported";
    const contentButton = document.createElement("button");
    contentButton.type = "button";
    contentButton.className = "rule-template-candidate-summary";
    const content = document.createElement("span");
    content.append(
      textBlock("strong", candidate.existingTemplateName || candidate.name),
      textBlock(
        "span",
        `${candidate.occurrenceCount} Vorkommen · ${candidate.reportCount} Berichte · ${Math.round(candidate.confidence * 100)} %`,
      ),
    );
    const parameterText = Object.entries(candidate.parameterVariants || {})
      .map(([name, variants]) => `${name}: ${(variants || []).map((variant) => variant.value).join(", ")}`)
      .join(" · ");
    if (parameterText) {
      content.append(textBlock("span", parameterText));
    }
    if (candidate.decision === "rejected") {
      content.append(textBlock("span", "Abgelehnt"));
    } else if (candidate.decision === "imported") {
      content.append(textBlock("span", "Übernommen"));
    }
    contentButton.append(content);
    contentButton.addEventListener("click", () => selectRuleTemplateCandidate(candidate.key));
    row.append(checkbox, contentButton);
    elements.ruleTemplateCandidateList.append(row);
  }
  const selectedCount = elements.ruleTemplateCandidateList.querySelectorAll('input[type="checkbox"]:checked').length;
  elements.importRuleTemplateCandidatesBtn.disabled = selectedCount === 0;
  elements.ruleTemplateCandidateList.onchange = () => {
    elements.importRuleTemplateCandidatesBtn.disabled =
      elements.ruleTemplateCandidateList.querySelectorAll('input[type="checkbox"]:checked').length === 0;
  };
  renderRuleTemplateCandidateDetail();
}

async function importRuleTemplateCandidates() {
  const candidateKeys = [...elements.ruleTemplateCandidateList.querySelectorAll('input[type="checkbox"]:checked')]
    .map((input) => input.value);
  if (!candidateKeys.length) {
    showToast("Keine Analysekandidaten ausgewählt");
    return;
  }
  await importRuleTemplateCandidateKeys(candidateKeys);
}

async function importRuleTemplateCandidateKeys(candidateKeys) {
  if (state.importingRuleCandidates || !candidateKeys.length) return;
  state.importingRuleCandidates = true;
  elements.importRuleTemplateCandidatesBtn.disabled = true;
  elements.importRuleTemplateCandidatesBtn.textContent = "Übernimmt";
  elements.importSingleRuleTemplateCandidateBtn.disabled = true;
  try {
    const payload = await requestJson("/api/rule-templates/import-existing", {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: "Master Data",
        candidateKeys,
      }),
    });
    await loadRuleTemplates();
    await analyzeExistingRules();
    showToast(`${payload.createdCount} Entwürfe und ${payload.bindingCount} Regelbindungen gespeichert`);
  } catch (error) {
    showToast(error.message);
  } finally {
    state.importingRuleCandidates = false;
    elements.importRuleTemplateCandidatesBtn.textContent = "Auswahl als Entwürfe übernehmen";
    elements.importSingleRuleTemplateCandidateBtn.disabled = false;
    renderRuleTemplateAnalysis();
  }
}

function selectedRuleTemplateCandidate() {
  return (state.ruleTemplateAnalysis?.candidates || [])
    .find((candidate) => candidate.key === state.selectedRuleTemplateCandidateKey) || null;
}

function selectRuleTemplateCandidate(candidateKey) {
  const candidate = (state.ruleTemplateAnalysis?.candidates || []).find((item) => item.key === candidateKey);
  if (!candidate) return;
  state.selectedRuleTemplateCandidateKey = candidate.key;
  state.selectedRuleTemplateId = null;
  elements.ruleTemplateEditorPanel.hidden = true;
  elements.ruleTemplateCandidateDetail.hidden = false;
  elements.saveRuleTemplateBtn.hidden = true;
  renderRuleTemplateList();
  renderRuleTemplateAnalysis();
}

function renderRuleTemplateCandidateDetail() {
  const candidate = selectedRuleTemplateCandidate();
  if (!candidate) return;
  elements.ruleTemplateCandidateName.textContent = candidate.existingTemplateName || candidate.name;
  const status =
    candidate.decision === "rejected"
      ? "Abgelehnt"
      : candidate.decision === "imported"
        ? "Übernommen"
        : candidate.existingTemplateId
          ? "Katalogisiert"
          : "Offen";
  elements.ruleTemplateCandidateStatus.textContent = status;
  elements.ruleTemplateCandidateStatus.className =
    `badge candidate-status-${candidate.decision || (candidate.existingTemplateId ? "catalogued" : "pending")}`;
  elements.ruleTemplateCandidateMeta.textContent =
    `${candidate.dimension} · ${candidate.ruleType} · ${candidate.occurrenceCount} Vorkommen in ${candidate.reportCount} Berichten`;
  elements.ruleTemplateCandidateCondition.textContent = candidate.conditionTemplate;

  elements.ruleTemplateCandidateParameters.replaceChildren();
  const parameterEntries = Object.entries(candidate.parameterVariants || {});
  if (!parameterEntries.length) {
    elements.ruleTemplateCandidateParameters.append(candidateEmptyNote("Keine variablen Parameter"));
  } else {
    for (const [name, variants] of parameterEntries) {
      elements.ruleTemplateCandidateParameters.append(
        detailRow(name, (variants || []).map((variant) => `${variant.value} (${variant.count}×)`).join(", ")),
      );
    }
  }

  elements.ruleTemplateCandidateMessages.replaceChildren();
  const messages = candidate.messageVariants || [];
  if (!messages.length) {
    elements.ruleTemplateCandidateMessages.append(candidateEmptyNote("Keine Fehlermeldung erkannt"));
  } else {
    for (const message of messages) {
      elements.ruleTemplateCandidateMessages.append(detailRow(`${message.count}×`, message.message));
    }
  }

  elements.ruleTemplateCandidateLocations.replaceChildren();
  for (const location of candidate.locations || []) {
    const item = document.createElement("div");
    item.className = "candidate-location";
    const parameterText = Object.entries(location.parameters || {})
      .map(([name, value]) => `${name}=${value}`)
      .join(" · ");
    item.append(
      textBlock("strong", location.reportName || location.reportRef),
      textBlock("span", `${location.groupName || location.groupRef} · ${location.field}`),
      textBlock("span", `${location.active ? "Aktiv" : "Inaktiv"}${parameterText ? ` · ${parameterText}` : ""}`),
    );
    elements.ruleTemplateCandidateLocations.append(item);
  }

  elements.rejectRuleTemplateCandidateBtn.textContent =
    candidate.decision === "rejected" ? "Zur Prüfung zurückstellen" : "Ablehnen";
  elements.rejectRuleTemplateCandidateBtn.disabled = state.decidingRuleCandidate || candidate.decision === "imported";
  elements.openCandidateTemplateBtn.hidden = !candidate.existingTemplateId;
  elements.importSingleRuleTemplateCandidateBtn.hidden = candidate.decision === "rejected";
  elements.importSingleRuleTemplateCandidateBtn.disabled =
    state.importingRuleCandidates || candidate.decision === "imported";
  elements.importSingleRuleTemplateCandidateBtn.textContent = candidate.existingTemplateId
    ? "Mit Katalog verknüpfen"
    : "Als Entwurf übernehmen";
}

function detailRow(label, value) {
  const row = document.createElement("div");
  row.className = "candidate-detail-row";
  row.append(textBlock("strong", label), textBlock("span", value));
  return row;
}

function candidateEmptyNote(value) {
  const note = textBlock("span", value);
  note.className = "meta-line";
  return note;
}

async function setSelectedRuleTemplateCandidateDecision() {
  const candidate = selectedRuleTemplateCandidate();
  if (!candidate || state.decidingRuleCandidate || candidate.decision === "imported") return;
  const decision = candidate.decision === "rejected" ? "pending" : "rejected";
  state.decidingRuleCandidate = true;
  elements.rejectRuleTemplateCandidateBtn.disabled = true;
  try {
    await requestJson("/api/rule-templates/candidate-decisions", {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: "Master Data",
        candidateKey: candidate.key,
        decision,
      }),
    });
    candidate.decision = decision;
    renderRuleTemplateAnalysis();
    showToast(decision === "rejected" ? "Kandidat wurde abgelehnt" : "Kandidat ist wieder zur Prüfung vorgemerkt");
  } catch (error) {
    showToast(error.message);
  } finally {
    state.decidingRuleCandidate = false;
    renderRuleTemplateCandidateDetail();
  }
}

async function importSelectedRuleTemplateCandidate() {
  const candidate = selectedRuleTemplateCandidate();
  if (!candidate || candidate.decision === "rejected" || candidate.decision === "imported") return;
  await importRuleTemplateCandidateKeys([candidate.key]);
}

function openSelectedCandidateTemplate() {
  const candidate = selectedRuleTemplateCandidate();
  if (candidate?.existingTemplateId) {
    selectRuleTemplate(candidate.existingTemplateId);
  }
}

function openRuleTemplateCatalog() {
  const first = state.ruleTemplates.find((template) => template.id === state.selectedRuleTemplateId) || state.ruleTemplates[0];
  if (first) {
    selectRuleTemplate(first.id);
  } else {
    newRuleTemplate();
  }
  elements.ruleTemplateCatalogDialog.showModal();
}

function closeRuleTemplateCatalog() {
  elements.ruleTemplateCatalogDialog.close();
}

function newRuleTemplate() {
  state.selectedRuleTemplateCandidateKey = null;
  state.selectedRuleTemplateId = null;
  elements.ruleTemplateEditorPanel.hidden = false;
  elements.ruleTemplateCandidateDetail.hidden = true;
  elements.saveRuleTemplateBtn.hidden = false;
  elements.ruleTemplateForm.reset();
  elements.ruleTemplateKeyInput.disabled = false;
  elements.ruleTemplateStatusSelect.value = "draft";
  elements.ruleTemplateDimensionInput.value = "Korrektheit";
  elements.ruleTemplateTypeInput.value = "custom";
  elements.ruleTemplateParametersInput.value = "{}";
  elements.ruleTemplateChangeNoteInput.value = "Initiale Version";
  elements.ruleTemplateVersionInfo.textContent = "Neue Vorlage";
  renderRuleTemplateList();
  elements.ruleTemplateNameInput.focus();
}

function selectRuleTemplate(templateId) {
  const template = state.ruleTemplates.find((item) => item.id === templateId);
  if (!template) return;
  state.selectedRuleTemplateCandidateKey = null;
  state.selectedRuleTemplateId = template.id;
  elements.ruleTemplateEditorPanel.hidden = false;
  elements.ruleTemplateCandidateDetail.hidden = true;
  elements.saveRuleTemplateBtn.hidden = false;
  const version = template.version || {};
  elements.ruleTemplateKeyInput.value = template.key || "";
  elements.ruleTemplateKeyInput.disabled = true;
  elements.ruleTemplateStatusSelect.value = template.status || "draft";
  elements.ruleTemplateNameInput.value = template.name || "";
  elements.ruleTemplateDescriptionInput.value = template.description || "";
  elements.ruleTemplateConditionInput.value = version.conditionTemplate || "";
  elements.ruleTemplateDimensionInput.value = version.dimension || "Korrektheit";
  elements.ruleTemplateTypeInput.value = version.ruleType || "custom";
  elements.ruleTemplateMessageDeInput.value = version.messageDeTemplate || "";
  elements.ruleTemplateMessageEnInput.value = version.messageEnTemplate || "";
  elements.ruleTemplateParametersInput.value = JSON.stringify(version.parameterSchema || {}, null, 2);
  elements.ruleTemplateDataTypesInput.value = (version.compatibleDataTypes || []).join(", ");
  elements.ruleTemplateCategoriesInput.value = (version.fieldCategories || []).join(", ");
  elements.ruleTemplateChangeNoteInput.value = "";
  elements.ruleTemplateVersionInfo.textContent = `Aktuelle Version ${template.currentVersion}`;
  renderRuleTemplateList();
}

function renderRuleTemplateList() {
  elements.ruleTemplateList.replaceChildren();
  if (!state.ruleTemplates.length) {
    elements.ruleTemplateList.append(emptyNode("Noch keine Regelvorlagen"));
    return;
  }
  for (const template of state.ruleTemplates) {
    const button = document.createElement("button");
    button.type = "button";
    button.classList.toggle("active", template.id === state.selectedRuleTemplateId);
    button.append(
      textBlock("strong", template.name || template.key),
      textBlock("span", `${template.version?.dimension || "-"} · v${template.currentVersion} · ${template.status}`),
    );
    button.addEventListener("click", () => selectRuleTemplate(template.id));
    elements.ruleTemplateList.append(button);
  }
}

function commaSeparatedValues(value) {
  return [...new Set(String(value || "").split(",").map((item) => item.trim()).filter(Boolean))];
}

async function saveRuleTemplate(event) {
  event.preventDefault();
  if (state.savingRuleTemplate || !elements.ruleTemplateForm.reportValidity()) return;
  let parameterSchema;
  try {
    parameterSchema = JSON.parse(elements.ruleTemplateParametersInput.value || "{}");
    if (!parameterSchema || Array.isArray(parameterSchema) || typeof parameterSchema !== "object") {
      throw new Error("Parameterdefinition muss ein JSON-Objekt sein");
    }
  } catch (error) {
    showToast(`Parameterdefinition ungültig: ${error.message}`);
    elements.ruleTemplateParametersInput.focus();
    return;
  }

  const selected = state.ruleTemplates.find((template) => template.id === state.selectedRuleTemplateId);
  const versionPayload = {
    conditionTemplate: elements.ruleTemplateConditionInput.value.trim(),
    messageDeTemplate: elements.ruleTemplateMessageDeInput.value.trim(),
    messageEnTemplate: elements.ruleTemplateMessageEnInput.value.trim(),
    dimension: elements.ruleTemplateDimensionInput.value,
    ruleType: elements.ruleTemplateTypeInput.value.trim(),
    parameterSchema,
    compatibleDataTypes: commaSeparatedValues(elements.ruleTemplateDataTypesInput.value),
    fieldCategories: commaSeparatedValues(elements.ruleTemplateCategoriesInput.value),
    examples: selected?.version?.examples || [],
    changeNote: elements.ruleTemplateChangeNoteInput.value.trim(),
  };
  state.savingRuleTemplate = true;
  elements.saveRuleTemplateBtn.disabled = true;
  elements.saveRuleTemplateBtn.textContent = "Speichert";
  try {
    let saved;
    if (selected) {
      const payload = await requestJson(`/api/rule-templates/${encodeURIComponent(selected.id)}/versions`, {
        method: "POST",
        body: JSON.stringify(versionPayload),
      });
      saved = payload.template;
      const metadataPayload = await requestJson(`/api/rule-templates/${encodeURIComponent(selected.id)}`, {
        method: "PATCH",
        body: JSON.stringify({
          name: elements.ruleTemplateNameInput.value.trim(),
          description: elements.ruleTemplateDescriptionInput.value.trim(),
          status: elements.ruleTemplateStatusSelect.value,
        }),
      });
      saved = metadataPayload.template;
    } else {
      const payload = await requestJson("/api/rule-templates", {
        method: "POST",
        body: JSON.stringify({
          key: elements.ruleTemplateKeyInput.value.trim(),
          name: elements.ruleTemplateNameInput.value.trim(),
          description: elements.ruleTemplateDescriptionInput.value.trim(),
          status: elements.ruleTemplateStatusSelect.value,
          ...versionPayload,
        }),
      });
      saved = payload.template;
    }
    await loadRuleTemplates();
    selectRuleTemplate(saved.id);
    showToast(selected ? `Neue Vorlagenversion ${saved.currentVersion} gespeichert` : "Regelvorlage angelegt");
  } catch (error) {
    showToast(error.message);
  } finally {
    state.savingRuleTemplate = false;
    elements.saveRuleTemplateBtn.disabled = false;
    elements.saveRuleTemplateBtn.textContent = "Vorlage speichern";
  }
}

async function createAiConfigFromDialog(event) {
  event.preventDefault();
  if (state.creatingAiConfig || !elements.aiConfigForm.reportValidity()) {
    return;
  }
  state.creatingAiConfig = true;
  elements.saveAiConfigBtn.disabled = true;
  elements.saveAiConfigBtn.textContent = "Wird geprüft";
  try {
    const payload = await requestJson("/api/ai/configs", {
      method: "POST",
      body: JSON.stringify({
        name: elements.aiConfigNameInput.value.trim(),
        provider: elements.aiProviderInput.value,
        model: elements.aiModelInput.value,
        baseUrl: elements.aiBaseUrlInput.value.trim(),
        apiKey: elements.aiApiKeyInput.value,
      }),
    });
    state.aiConfigId = payload.config?.id || null;
    if (state.aiConfigId) {
      localStorage.setItem(LAST_AI_CONFIG_STORAGE_KEY, state.aiConfigId);
    }
    await loadAiConfigs();
    closeAiConfigDialog();
    showToast("KI-Zugang wurde gespeichert und geprüft");
  } catch (error) {
    showToast(error.message);
  } finally {
    elements.aiApiKeyInput.value = "";
    state.creatingAiConfig = false;
    elements.saveAiConfigBtn.disabled = false;
    elements.saveAiConfigBtn.textContent = "Speichern und prüfen";
  }
}

function renderProjectTabs() {
  elements.projectTabs.replaceChildren();
  for (const project of state.projects) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = project.name;
    button.className = project.id === state.project ? "active" : "";
    button.addEventListener("click", async () => {
      state.project = project.id;
      clearHarmonization();
      renderProjectTabs();
      await loadReports();
    });
    elements.projectTabs.append(button);
  }
}

async function loadReports() {
  state.editorLoadToken += 1;
  state.loadingEditor = false;
  if (!state.configId) {
    state.reports = [];
    state.selectedReport = null;
    state.editorModel = null;
    renderReports();
    renderSelection();
    clearEditor();
    setStatus("keine Config", "warn");
    setConnectionState("keine Config");
    return;
  }

  state.loadingReports = true;
  state.editorModel = null;
  elements.refreshBtn.disabled = true;
  setConnectionState("lade");
  setStatus("lade");
  renderReports();
  clearEditor("Kein Modell geladen");

  try {
    const params = new URLSearchParams({
      configId: state.configId,
      project: state.project,
      deficienciesOnly: "true",
    });
    const payload = await requestJson(`/api/reports?${params.toString()}`);
    updateActiveConfigTenant(payload.configTenant);
    state.reports = payload.reports || [];
    state.selectedReport = state.reports[0] || null;
    setConnectionState("verbunden");
    setStatus("bereit", "ok");
  } catch (error) {
    state.reports = [];
    state.selectedReport = null;
    setConnectionState("Fehler");
    setStatus("Fehler", "warn");
    showToast(error.message);
  } finally {
    state.loadingReports = false;
    elements.refreshBtn.disabled = false;
    applyReportFilter();
    renderSelection();
    clearPreview();
    if (state.activeView === "editor" && state.selectedReport) {
      await loadEditorModel();
    }
  }
}

function applyReportFilter() {
  const needle = elements.searchInput.value.trim().toLocaleLowerCase();
  if (!needle) {
    state.filteredReports = [...state.reports];
  } else {
    state.filteredReports = state.reports.filter((report) => {
      const name = `${report.displayName || ""} ${report.internalName || ""}`.toLocaleLowerCase();
      return name.includes(needle);
    });
  }
  if (state.selectedReport && !state.filteredReports.some((report) => reportRef(report) === reportRef(state.selectedReport))) {
    state.selectedReport = state.filteredReports[0] || null;
  }
  renderReports();
  renderSelection();
}

function renderReports() {
  elements.reportList.replaceChildren();
  if (state.loadingReports) {
    elements.reportCount.textContent = "lade";
    elements.reportList.append(emptyNode("Reports laden"));
    return;
  }

  elements.reportCount.textContent = `${state.filteredReports.length} Reports`;
  if (!state.filteredReports.length) {
    elements.reportList.append(emptyNode("Keine Reports"));
    return;
  }

  for (const report of state.filteredReports) {
    const currentReportRef = reportRef(report);
    const isSelected = state.selectedReport && currentReportRef === reportRef(state.selectedReport);
    const isLoading = state.loadingReportRef === currentReportRef;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `report-item ${isSelected ? "active" : ""} ${isLoading ? "loading" : ""}`;
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", String(Boolean(isSelected)));
    button.setAttribute("aria-busy", String(isLoading));
    button.disabled = Boolean(state.loadingReportRef);

    const name = document.createElement("span");
    name.className = "report-name";
    name.textContent = report.displayName || report.internalName || report.id || "Report";

    const nameRow = document.createElement("span");
    nameRow.className = "report-name-row";
    nameRow.append(name);
    if (isLoading) {
      const spinner = document.createElement("span");
      spinner.className = "report-spinner";
      spinner.setAttribute("aria-hidden", "true");
      nameRow.append(spinner);
    }

    const internal = document.createElement("span");
    internal.className = "report-internal";
    internal.textContent = report.internalName || report.id || "-";

    button.append(nameRow, internal);
    button.addEventListener("click", async () => {
      state.editorLoadToken += 1;
      state.loadingEditor = false;
      state.loadingReportRef = currentReportRef;
      state.selectedReport = report;
      state.editorModel = null;
      renderReports();
      renderSelection();
      clearPreview();
      clearEditor("Kein Modell geladen");
      try {
        await switchView("editor");
      } finally {
        if (state.loadingReportRef === currentReportRef) {
          state.loadingReportRef = null;
        }
        renderReports();
      }
    });
    elements.reportList.append(button);
  }
}

function renderSelection() {
  const report = state.selectedReport;
  elements.projectLabel.textContent = state.project;
  elements.runBtn.disabled = !report || state.runningReport;
  elements.loadEditorBtn.disabled = !report || state.loadingEditor;
  updateEditorButtons();

  if (!report) {
    elements.reportTitle.textContent = "Report";
    elements.reportMeta.textContent = "-";
    elements.columnsMetric.textContent = "-";
    elements.sqlMetric.textContent = "-";
    return;
  }

  elements.reportTitle.textContent = report.displayName || report.internalName || report.id || "Report";
  elements.reportMeta.textContent = report.internalName || report.id || "-";
  elements.columnsMetric.textContent = String(report.columnsCount ?? "-");
  elements.sqlMetric.textContent = report.hasQuerySyntax ? "ja" : "nein";
}

function updateActiveConfigTenant(tenant) {
  const config = activeConfig();
  if (config && tenant) {
    config.tenant = tenant;
  }
}

async function switchView(view) {
  state.activeView = view;
  const isEditor = view === "editor";
  const isResult = view === "result";
  const isHarmonization = view === "harmonization";
  elements.resultView.hidden = !isResult;
  elements.editorView.hidden = !isEditor;
  elements.harmonizationView.hidden = !isHarmonization;
  elements.resultViewBtn.classList.toggle("active", isResult);
  elements.editorViewBtn.classList.toggle("active", isEditor);
  elements.harmonizationViewBtn.classList.toggle("active", isHarmonization);
  elements.resultViewBtn.setAttribute("aria-selected", String(isResult));
  elements.editorViewBtn.setAttribute("aria-selected", String(isEditor));
  elements.harmonizationViewBtn.setAttribute("aria-selected", String(isHarmonization));
  if (isEditor && state.selectedReport && !state.editorModel && !state.loadingEditor) {
    await loadEditorModel();
  }
  if (isHarmonization && !state.harmonization && !state.loadingHarmonization) {
    await loadHarmonization();
  }
}

function clearHarmonization(message = "Noch keine Harmonisierungsdaten geladen") {
  state.harmonization = null;
  state.selectedHarmonization = null;
  state.harmonizationPreview = null;
  elements.harmonizationInfo.textContent = message;
  elements.harmonizationReportsMetric.textContent = "-";
  elements.harmonizationFieldsMetric.textContent = "-";
  elements.harmonizationDivergentMetric.textContent = "-";
  elements.harmonizationMissingMetric.textContent = "-";
  elements.harmonizationMatrix.querySelector("thead").replaceChildren();
  elements.harmonizationMatrix.querySelector("tbody").replaceChildren();
  elements.harmonizationMatrix.hidden = true;
  elements.emptyHarmonization.hidden = false;
  elements.emptyHarmonization.textContent = message;
  renderHarmonizationDetail();
}

async function loadHarmonization() {
  if (!state.configId || state.loadingHarmonization) {
    return;
  }
  state.loadingHarmonization = true;
  state.harmonizationPreview = null;
  elements.refreshHarmonizationBtn.disabled = true;
  elements.refreshHarmonizationBtn.textContent = "Lade";
  elements.harmonizationInfo.textContent = `${state.project} wird analysiert`;
  elements.emptyHarmonization.hidden = false;
  elements.emptyHarmonization.textContent = "Berichte werden verglichen";
  elements.harmonizationMatrix.hidden = true;
  try {
    const params = new URLSearchParams({ configId: state.configId, project: state.project });
    state.harmonization = await requestJson(`/api/harmonization?${params.toString()}`);
    renderHarmonization();
  } catch (error) {
    clearHarmonization("Harmonisierung konnte nicht geladen werden");
    showToast(error.message);
  } finally {
    state.loadingHarmonization = false;
    elements.refreshHarmonizationBtn.disabled = false;
    elements.refreshHarmonizationBtn.textContent = "Aktualisieren";
  }
}

function renderHarmonization() {
  const payload = state.harmonization;
  if (!payload) {
    clearHarmonization();
    return;
  }
  const summary = payload.summary || {};
  elements.harmonizationReportsMetric.textContent = String(summary.reportCount ?? 0);
  elements.harmonizationFieldsMetric.textContent = String(summary.fieldCount ?? 0);
  elements.harmonizationDivergentMetric.textContent = String(summary.divergentCount ?? 0);
  elements.harmonizationMissingMetric.textContent = String(summary.missingCount ?? 0);
  const skipped = payload.skippedReports?.length || 0;
  elements.harmonizationInfo.textContent = `${payload.project || state.project} · ${summary.reportCount || 0} Berichte${skipped ? ` · ${skipped} übersprungen` : ""}`;

  const needle = elements.harmonizationSearchInput.value.trim().toLocaleLowerCase();
  const fields = (payload.fields || []).filter((field) => {
    if (!needle) return true;
    const occurrences = Object.values(field.reports || {}).map((item) => item.internalName).join(" ");
    return `${field.displayName || ""} ${field.designation || ""} ${field.description || ""} ${occurrences}`.toLocaleLowerCase().includes(needle);
  });
  const reports = payload.reports || [];
  const head = elements.harmonizationMatrix.querySelector("thead");
  const body = elements.harmonizationMatrix.querySelector("tbody");
  head.replaceChildren();
  body.replaceChildren();

  const headerRow = document.createElement("tr");
  const fieldHeader = document.createElement("th");
  fieldHeader.scope = "col";
  fieldHeader.textContent = "Feld";
  headerRow.append(fieldHeader);
  for (const report of reports) {
    const th = document.createElement("th");
    th.scope = "col";
    th.title = report.displayName || report.internalName;
    th.textContent = report.displayName || report.internalName;
    headerRow.append(th);
  }
  head.append(headerRow);

  for (const field of fields) {
    const row = document.createElement("tr");
    const nameCell = document.createElement("th");
    nameCell.scope = "row";
    const nameButton = document.createElement("button");
    nameButton.type = "button";
    nameButton.className = "harmonization-field-button";
    nameButton.textContent = field.designation ? `${field.displayName} (${field.designation})` : field.displayName;
    nameButton.title = field.description || field.displayName;
    nameButton.addEventListener("click", () => selectHarmonization(field.key));
    nameCell.append(nameButton);
    row.append(nameCell);
    for (const report of reports) {
      const occurrence = field.reports?.[report.id];
      const cell = document.createElement("td");
      const button = document.createElement("button");
      button.type = "button";
      button.className = `harmonization-status ${occurrence?.status || "missing"}`;
      const statusLabel = textBlock(
        "span",
        occurrence?.status === "aligned" ? "Aktuell" : occurrence?.status === "divergent" ? "Abweichend" : "Fehlt",
        "harmonization-status-label",
      );
      button.append(statusLabel);
      if (occurrence) {
        const totalRules = Number(occurrence.ruleCount || 0);
        const activeRules = Number(occurrence.activeRuleCount || 0);
        const inactiveRules = Math.max(0, totalRules - activeRules);
        const counts = document.createElement("span");
        counts.className = "harmonization-rule-counts";
        counts.append(
          textBlock("span", `${totalRules} Regeln`, "harmonization-rule-total"),
          textBlock("span", `✓ ${activeRules}`, "harmonization-rule-active"),
        );
        if (inactiveRules) {
          counts.append(textBlock("span", `× ${inactiveRules}`, "harmonization-rule-inactive"));
        }
        button.append(counts);
      }
      button.title = occurrence ? `${occurrence.ruleCount} Regeln · ${occurrence.internalName}` : "Keine Regelgruppe in diesem Bericht";
      button.addEventListener("click", () => selectHarmonization(field.key, report.id));
      cell.append(button);
      row.append(cell);
    }
    body.append(row);
  }
  elements.harmonizationMatrix.hidden = !fields.length;
  elements.emptyHarmonization.hidden = Boolean(fields.length);
  if (!fields.length) elements.emptyHarmonization.textContent = needle ? "Keine passenden Felder" : "Keine gemeinsamen Felder gefunden";
  renderHarmonizationDetail();
}

function selectHarmonization(fieldKey, reportId = null) {
  const field = state.harmonization?.fields?.find((item) => item.key === fieldKey);
  if (!field) return;
  const sourceCandidates = (state.harmonization.reports || []).filter((report) => field.reports?.[report.id]);
  const sourceReportId = field.reports?.[reportId]
    ? reportId
    : sourceCandidates.find((report) => field.reports[report.id]?.status === "aligned")?.id || sourceCandidates[0]?.id || null;
  const targetReportIds = (state.harmonization.reports || [])
    .filter((report) => report.id !== sourceReportId)
    .filter((report) => !field.reports?.[report.id] || field.reports[report.id].status === "divergent")
    .map((report) => report.id);
  state.selectedHarmonization = { fieldKey, reportId, sourceReportId, targetReportIds };
  state.harmonizationPreview = null;
  renderHarmonizationDetail();
}

function renderHarmonizationDetail() {
  elements.harmonizationDetail.replaceChildren();
  const selected = state.selectedHarmonization;
  const field = state.harmonization?.fields?.find((item) => item.key === selected?.fieldKey);
  if (!field) {
    elements.harmonizationDetail.append(emptyNode("Feld oder Berichtszelle auswählen"));
    return;
  }
  if (selected.reportId) {
    elements.harmonizationDetail.append(harmonizationDifferencePanel(field, selected.reportId));
  }
  const title = document.createElement("h4");
  title.textContent = field.designation ? `${field.displayName} (${field.designation})` : field.displayName;
  const description = document.createElement("p");
  description.className = "meta-line";
  description.textContent = field.description || "Keine Beschreibung";
  const overview = document.createElement("dl");
  overview.className = "harmonization-facts";
  const present = field.reportCount || 0;
  const divergent = Object.values(field.reports || {}).filter((item) => item.status === "divergent").length;
  for (const [label, value] of [["In Berichten", present], ["Abweichend", divergent], ["Fehlend", field.missingReportCount || 0]]) {
    const dt = document.createElement("dt"); dt.textContent = label;
    const dd = document.createElement("dd"); dd.textContent = String(value);
    overview.append(dt, dd);
  }
  elements.harmonizationDetail.append(title, description, overview);
  if (selected.reportId) {
    const report = state.harmonization.reports.find((item) => item.id === selected.reportId);
    const occurrence = field.reports?.[selected.reportId];
    const reportTitle = document.createElement("h4");
    reportTitle.textContent = report?.displayName || selected.reportId;
    const reportInfo = document.createElement("p");
    reportInfo.className = "harmonization-report-info";
    reportInfo.textContent = occurrence
      ? `${occurrence.internalName} · ${occurrence.ruleCount} Regeln · ${occurrence.activeRuleCount} aktiv · ${occurrence.dimensions.join(", ")}`
      : "In diesem Bericht fehlt die Regelgruppe.";
    elements.harmonizationDetail.append(reportTitle, reportInfo);
  }
  renderHarmonizationTransferControls(field);
}

function harmonizationDifferencePanel(field, reportId) {
  const panel = document.createElement("section");
  panel.className = "harmonization-differences";
  panel.append(textBlock("h4", "Abweichungen"));

  const occurrence = field.reports?.[reportId];
  const referenceReport = state.harmonization?.reports?.find((report) => report.id === field.referenceReportId);
  const referenceName = referenceReport?.displayName || field.referenceReportId || "Referenz";
  const referenceInfo = textBlock("p", `Referenz: ${referenceName}`, "harmonization-difference-reference");
  panel.append(referenceInfo);

  if (!occurrence) {
    panel.append(textBlock("p", "Die Regelgruppe fehlt in diesem Bericht.", "harmonization-difference-empty missing"));
    return panel;
  }
  const differences = occurrence.differences || [];
  if (!differences.length) {
    panel.append(textBlock("p", "Keine Abweichungen zur Referenz.", "harmonization-difference-empty aligned"));
    return panel;
  }

  const propertyLabels = {
    rule: "Regel",
    condition: "Bedingung",
    message: "Fehlermeldung",
    dimension: "DQ-Typ",
    ruleType: "Regeltyp",
    active: "Aktivstatus",
  };
  const list = document.createElement("div");
  list.className = "harmonization-difference-list";
  for (const difference of differences) {
    const item = document.createElement("div");
    item.className = "harmonization-difference-item";
    item.append(textBlock(
      "strong",
      `Regel ${difference.ruleNumber} · ${propertyLabels[difference.property] || difference.property}`,
    ));
    const values = document.createElement("dl");
    for (const [label, value, valueClass] of [
      ["Referenz", difference.referenceValue, "reference"],
      ["Bericht", difference.currentValue, "current"],
    ]) {
      const dt = document.createElement("dt");
      dt.textContent = label;
      const dd = document.createElement("dd");
      dd.className = valueClass;
      dd.textContent = typeof value === "boolean" ? (value ? "Aktiv" : "Inaktiv") : String(value ?? "");
      values.append(dt, dd);
    }
    item.append(values);
    list.append(item);
  }
  panel.append(list);
  return panel;
}

function renderHarmonizationTransferControls(field) {
  const selected = state.selectedHarmonization;
  const reports = state.harmonization?.reports || [];
  const sourceReports = reports.filter((report) => field.reports?.[report.id]);
  const form = document.createElement("div");
  form.className = "harmonization-transfer";

  const sourceLabel = document.createElement("label");
  sourceLabel.className = "field";
  const sourceCaption = document.createElement("span");
  sourceCaption.textContent = "Referenzbericht";
  const sourceSelect = document.createElement("select");
  sourceSelect.id = "harmonizationSourceSelect";
  for (const report of sourceReports) {
    const option = document.createElement("option");
    option.value = report.id;
    option.textContent = report.displayName || report.internalName;
    sourceSelect.append(option);
  }
  sourceSelect.value = selected.sourceReportId || "";
  sourceSelect.addEventListener("change", () => {
    selected.sourceReportId = sourceSelect.value;
    selected.targetReportIds = selected.targetReportIds.filter((reportId) => reportId !== selected.sourceReportId);
    state.harmonizationPreview = null;
    renderHarmonizationDetail();
  });
  sourceLabel.append(sourceCaption, sourceSelect);

  const targets = document.createElement("fieldset");
  targets.className = "harmonization-targets";
  const legend = document.createElement("legend");
  legend.textContent = "Zielberichte";
  targets.append(legend);
  for (const report of reports.filter((item) => item.id !== selected.sourceReportId)) {
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = report.id;
    checkbox.checked = selected.targetReportIds.includes(report.id);
    checkbox.addEventListener("change", () => {
      selected.targetReportIds = checkbox.checked
        ? [...new Set([...selected.targetReportIds, report.id])]
        : selected.targetReportIds.filter((reportId) => reportId !== report.id);
      state.harmonizationPreview = null;
      renderHarmonizationDetail();
    });
    const status = field.reports?.[report.id]?.status;
    const statusText = status === "divergent" ? "Abweichend" : status === "aligned" ? "Aktuell" : "Fehlt";
    const text = document.createElement("span");
    text.textContent = `${report.displayName || report.internalName} · ${statusText}`;
    label.append(checkbox, text);
    targets.append(label);
  }

  const previewButton = document.createElement("button");
  previewButton.id = "previewHarmonizationBtn";
  previewButton.className = "button secondary";
  previewButton.type = "button";
  previewButton.disabled = !selected.sourceReportId || !selected.targetReportIds.length || state.previewingHarmonization;
  previewButton.textContent = state.previewingHarmonization ? "Prüfung läuft" : "Änderungen prüfen";
  previewButton.addEventListener("click", previewHarmonizationTransfer);
  form.append(sourceLabel, targets, previewButton);

  if (state.harmonizationPreview) {
    const preview = document.createElement("div");
    preview.className = "harmonization-transfer-preview";
    const previewTitle = document.createElement("h4");
    previewTitle.textContent = "Änderungsvorschau";
    preview.append(previewTitle);
    for (const change of state.harmonizationPreview.changes || []) {
      const row = document.createElement("div");
      row.className = "harmonization-preview-row";
      const action = change.action === "create" ? "Wird angelegt" : "Wird ersetzt";
      row.textContent = `${change.reportName} · ${action} · ${change.oldRuleCount} → ${change.newRuleCount} Regeln`;
      preview.append(row);
    }
    const applyButton = document.createElement("button");
    applyButton.id = "applyHarmonizationBtn";
    applyButton.className = "button primary";
    applyButton.type = "button";
    applyButton.disabled = state.applyingHarmonization;
    applyButton.textContent = state.applyingHarmonization ? "Übernahme läuft" : "Als Drafts übernehmen";
    applyButton.addEventListener("click", applyHarmonizationTransfer);
    preview.append(applyButton);
    form.append(preview);
  }
  elements.harmonizationDetail.append(form);
}

function harmonizationTransferPayload() {
  const selected = state.selectedHarmonization;
  return {
    configId: state.configId,
    project: state.project,
    fieldKey: selected.fieldKey,
    sourceReportId: selected.sourceReportId,
    targetReportIds: selected.targetReportIds,
  };
}

async function previewHarmonizationTransfer() {
  if (!state.selectedHarmonization || state.previewingHarmonization) return;
  state.previewingHarmonization = true;
  renderHarmonizationDetail();
  try {
    state.harmonizationPreview = await requestJson("/api/harmonization/preview", {
      method: "POST",
      body: JSON.stringify(harmonizationTransferPayload()),
    });
  } catch (error) {
    showToast(error.message);
  } finally {
    state.previewingHarmonization = false;
    renderHarmonizationDetail();
  }
}

async function applyHarmonizationTransfer() {
  if (!state.harmonizationPreview || state.applyingHarmonization) return;
  const count = state.harmonizationPreview.summary?.targetCount || 0;
  const confirmed = window.confirm(`${count} Zielberichte als lokale Drafts harmonisieren? NEMO wird noch nicht verändert.`);
  if (!confirmed) return;
  state.applyingHarmonization = true;
  renderHarmonizationDetail();
  const selected = { ...state.selectedHarmonization, targetReportIds: [...state.selectedHarmonization.targetReportIds] };
  try {
    const payload = await requestJson("/api/harmonization/apply", {
      method: "POST",
      body: JSON.stringify(harmonizationTransferPayload()),
    });
    showToast(`${payload.applied?.length || 0} Drafts harmonisiert und protokolliert`);
    state.selectedHarmonization = selected;
    await loadHarmonization();
  } catch (error) {
    showToast(error.message);
  } finally {
    state.applyingHarmonization = false;
    renderHarmonizationDetail();
  }
}

async function runSelectedReport() {
  const report = state.selectedReport;
  if (!report || state.runningReport) {
    return;
  }

  state.runningReport = true;
  elements.runBtn.disabled = true;
  elements.runBtn.textContent = "Laden";
  setStatus("laeuft");
  clearPreview("Ergebnis laden");

  try {
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/run`, {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        maxRows: Number(elements.maxRowsInput.value) || 100,
      }),
    });
    renderPreview(payload.preview);
    setStatus("bereit", "ok");
  } catch (error) {
    setStatus("Fehler", "warn");
    showToast(error.message);
    clearPreview("Kein Ergebnis geladen");
  } finally {
    state.runningReport = false;
    elements.runBtn.disabled = !state.selectedReport;
    elements.runBtn.textContent = "Ergebnis laden";
  }
}

async function loadEditorModel(options = {}) {
  const report = state.selectedReport;
  const preferDraft = options.preferDraft ?? true;
  if (!report || state.loadingEditor) {
    return;
  }

  const loadToken = ++state.editorLoadToken;
  const requestedReportRef = reportRef(report);
  const requestedConfigId = state.configId;
  const requestedProject = state.project;
  state.loadingEditor = true;
  elements.loadEditorBtn.disabled = true;
  elements.loadEditorBtn.textContent = "Laden";
  elements.editorInfo.textContent = "Modell wird geladen";
  setStatus("lade");
  updateEditorButtons();

  try {
    const params = new URLSearchParams({
      configId: state.configId,
      project: state.project,
      preferDraft: String(preferDraft),
    });
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/editor-model?${params.toString()}`);
    if (
      loadToken !== state.editorLoadToken
      || requestedReportRef !== reportRef(state.selectedReport || {})
      || requestedConfigId !== state.configId
      || requestedProject !== state.project
    ) {
      return;
    }
    state.editorModel = payload.editorModel;
    await enrichGroupColumnMetadata(state.editorModel);
    ensureRuleMessageLanguages(state.editorModel);
    state.originalEditorModel = deepClone(payload.editorModel);
    state.currentDraft = payload.draft || null;
    state.baseline = payload.baseline || null;
    state.reportSqlHash = payload.reportSqlHash || "";
    state.changeLog = payload.changeLog || [];
    state.expandedGroups = new Set();
    state.selectedRuleRef = null;
    const defaultBlockIndex = checksBlockIndex();
    state.selectedBlockIndex = state.uiMode === "standard" && defaultBlockIndex >= 0 ? defaultBlockIndex : null;
    state.selectedContextItem = null;
    state.editorDirty = false;
    renderEditorModel();
    clearSqlPreview("Noch keine SQL-Vorschau");
    setStatus("bereit", "ok");
    if (payload.staleDraftDiscarded) {
      showToast(
        state.uiLanguage === "en"
          ? "The NEMO report was updated. The previous draft was archived and the current rules were loaded."
          : "Der NEMO-Bericht wurde aktualisiert. Der alte Draft wurde archiviert und die aktuellen Regeln wurden geladen."
      );
    }
  } catch (error) {
    if (loadToken !== state.editorLoadToken) {
      return;
    }
    state.editorModel = null;
    state.currentDraft = null;
    state.baseline = null;
    state.reportSqlHash = "";
    state.changeLog = [];
    clearEditor("Modell konnte nicht geladen werden");
    setStatus("Fehler", "warn");
    showToast(error.message);
  } finally {
    if (loadToken === state.editorLoadToken) {
      state.loadingEditor = false;
      elements.loadEditorBtn.disabled = !state.selectedReport;
      elements.loadEditorBtn.textContent = "Modell laden";
      updateEditorButtons();
    }
  }
}

function renderPreview(preview) {
  const columns = preview?.columns || [];
  const rows = preview?.rows || [];
  const thead = elements.previewTable.querySelector("thead");
  const tbody = elements.previewTable.querySelector("tbody");
  thead.replaceChildren();
  tbody.replaceChildren();

  elements.rowsMetric.textContent = String(preview?.rowCount ?? "-");
  elements.previewInfo.textContent = `${preview?.returnedRows ?? 0} von ${preview?.rowCount ?? 0} Zeilen`;

  if (!columns.length) {
    elements.emptyPreview.style.display = "grid";
    return;
  }

  const headerRow = document.createElement("tr");
  for (const column of columns) {
    const th = document.createElement("th");
    th.textContent = column;
    headerRow.append(th);
  }
  thead.append(headerRow);

  for (const row of rows) {
    const tr = document.createElement("tr");
    for (const column of columns) {
      const td = document.createElement("td");
      const value = row[column];
      td.textContent = value === null || value === undefined ? "" : String(value);
      tr.append(td);
    }
    tbody.append(tr);
  }

  elements.emptyPreview.style.display = rows.length ? "none" : "grid";
}

function renderEditorModel() {
  const model = state.editorModel;
  if (!model) {
    clearEditor();
    return;
  }

  const summary = model.summary || {};
  const findings = model.validation?.findings || [];
  const draftText = state.currentDraft ? ` · Draft ${formatTimestamp(state.currentDraft.updatedAt)}` : "";
  const dirtyText = state.editorDirty ? " · ungespeicherte Änderungen" : "";
  elements.editorInfo.textContent = `${summary.activeRuleCount || 0} aktive Regeln, ${summary.inactiveRuleCount || 0} inaktiv${draftText}${dirtyText}`;
  elements.editorInfo.classList.toggle("dirty-note", state.editorDirty);
  elements.blocksMetric.textContent = String(summary.blockCount ?? "-");
  elements.groupsMetric.textContent = String(summary.checkGroupCount ?? "-");
  elements.rulesMetric.textContent = String(summary.ruleCount ?? "-");
  elements.findingsMetric.textContent = String(findings.length);

  renderBlocks(model.blocks || []);
  renderContextPanel();
  renderRuleDetail();
  renderChangeLog();
  renderValidation(findings);
}

function renderBlocks(blocks) {
  elements.blockList.replaceChildren();
  if (!blocks.length) {
    elements.blockList.append(emptyNode("Keine Blöcke erkannt"));
    return;
  }

  for (const [index, block] of blocks.entries()) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = `block-item ${state.selectedBlockIndex === index ? "selected" : ""}`;
    item.setAttribute("aria-pressed", String(state.selectedBlockIndex === index));
    item.append(textBlock("strong", block.title || block.id));
    item.append(textBlock("div", block.cteName || "Finale Ausgabe", "meta-line"));
    const badges = document.createElement("div");
    badges.className = "badge-row";
    badges.append(badge(`${block.lineStart}-${block.lineEnd}`));
    badges.append(badge(block.id));
    item.append(badges);
    item.addEventListener("click", () => selectBlock(index));
    elements.blockList.append(item);
  }
}

function selectBlock(blockIndex) {
  showParameterDetail();
  state.selectedBlockIndex = blockIndex;
  state.selectedRuleRef = null;
  state.selectedContextItem = null;
  renderBlocks(state.editorModel?.blocks || []);
  renderContextPanel();
  renderRuleDetail();
  updateEditorButtons();
}

function renderContextPanel() {
  const blocks = state.editorModel?.blocks || [];
  const block = state.selectedBlockIndex === null ? null : blocks[state.selectedBlockIndex];
  if (!block || block.id === "checks") {
    elements.contextPanelTitle.textContent = "Datenqualitätsregeln";
    elements.contextPanelActions.hidden = false;
    renderGroups(state.editorModel?.checks?.groups || []);
    return;
  }

  elements.contextPanelTitle.textContent = contextPanelTitle(block.id);
  elements.contextPanelActions.hidden = true;
  updateGroupToggleButton([]);
  renderBlockContextItems(block);
}

function contextPanelTitle(blockType) {
  const titles = {
    source: "Attribute und Ausnahmen",
    process: "Prozessfilter und Felder",
    join: "Verknüpfungen",
    output: "Ausgabefelder",
  };
  return titles[blockType] || "Blockinhalt";
}

function renderBlockContextItems(block) {
  elements.groupList.replaceChildren();
  const entries = blockContextEntries(block);
  if (!entries.length) {
    elements.groupList.append(emptyNode("Keine Einträge erkannt"));
    return;
  }
  for (const [index, entry] of entries.entries()) {
    const selected = state.selectedContextItem?.blockIndex === state.selectedBlockIndex
      && state.selectedContextItem?.index === index;
    const item = document.createElement("button");
    item.type = "button";
    item.className = `context-item ${selected ? "selected" : ""}`;
    item.setAttribute("aria-pressed", String(selected));
    item.append(textBlock("strong", entry.label));
    if (entry.meta) {
      item.append(textBlock("span", entry.meta, "meta-line"));
    }
    item.addEventListener("click", () => selectContextItem(index));
    elements.groupList.append(item);
  }
}

function blockContextEntries(block) {
  if (block.id === "source") {
    return (state.editorModel?.source?.attributes || []).map((attribute) => ({
      kind: "attribute",
      label: attribute.name || attribute.expression || "Attribut",
      meta: attribute.comment || attribute.expression || "",
      data: attribute,
    }));
  }
  if (block.id === "process") {
    return [
      { kind: "process", label: "Business Processes", meta: "Projekt", data: { value: "Business Processes" } },
      { kind: "process", label: '$schema."pa_export"', meta: "Prozessquelle", data: { value: '$schema."pa_export"' } },
    ];
  }
  if (block.id === "join") {
    return [{ kind: "join", label: block.cteName || "joined", meta: "Verknüpfung der prozessrelevanten Daten", data: block }];
  }
  if (block.id === "output") {
    return (state.editorModel?.output?.fields || []).map((field) => ({
      kind: "output",
      label: field.name || field.expression || "Ausgabefeld",
      meta: field.expression || "",
      data: field,
    }));
  }
  return [];
}

function selectContextItem(index) {
  const block = (state.editorModel?.blocks || [])[state.selectedBlockIndex];
  if (!block) {
    return;
  }
  const entry = blockContextEntries(block)[index];
  if (!entry) {
    return;
  }
  showParameterDetail();
  state.selectedContextItem = { blockIndex: state.selectedBlockIndex, index };
  state.selectedRuleRef = null;
  renderBlockContextItems(block);
  renderRuleDetail();
}

function renderGroups(groups) {
  elements.groupList.replaceChildren();
  if (!groups.length) {
    elements.groupList.append(emptyNode("Keine Regeln erkannt"));
    updateGroupToggleButton(groups);
    return;
  }

  for (const [index, group] of groups.entries()) {
    const key = groupKey(group, index);
    const rules = group.rules || [];
    const activeCount = rules.filter((rule) => Boolean(rule.active)).length;
    const inactiveCount = rules.length - activeCount;
    const expanded = state.expandedGroups.has(key);

    const item = document.createElement("article");
    item.className = `group-item ${expanded ? "expanded" : "collapsed"}`;

    const header = document.createElement("button");
    header.className = "group-header";
    header.type = "button";
    header.setAttribute("aria-expanded", String(expanded));
    header.setAttribute("aria-controls", `rule-list-${index}`);

    const chevron = document.createElement("span");
    chevron.className = "group-chevron";
    chevron.textContent = "›";
    chevron.setAttribute("aria-hidden", "true");

    const indexBadge = document.createElement("span");
    indexBadge.className = "group-index";
    indexBadge.textContent = String(index + 1);

    const title = document.createElement("span");
    title.className = "group-title";
    const identity = document.createElement("span");
    identity.className = "group-identity";
    const displayName = groupDisplayName(group);
    const previewDisplayName = groupPreviewDisplayName(group);
    const displayNameNode = textBlock("strong", previewDisplayName);
    displayNameNode.title = previewDisplayName;
    identity.append(displayNameNode);
    const internalName = groupInternalName(group);
    if (internalName && internalName !== displayName) {
      const internalNameNode = textBlock("span", internalName, "group-subtitle");
      internalNameNode.title = internalName;
      identity.append(internalNameNode);
    }
    title.append(identity);
    const description = String(group.description || "").trim();
    if (description) {
      const descriptionNode = textBlock("span", description, "group-description");
      descriptionNode.title = description;
      title.append(descriptionNode);
      title.classList.add("has-description");
    }

    const counts = document.createElement("span");
    counts.className = "group-counts";
    counts.append(textBlock("span", `${rules.length} Regeln`));
    counts.append(textBlock("span", `✓ ${activeCount}`, "count-ok"));
    if (inactiveCount) {
      counts.append(textBlock("span", `× ${inactiveCount}`, "count-warn"));
    }

    header.append(chevron, indexBadge, title, counts);
    header.addEventListener("click", () => {
      if (expanded) {
        state.expandedGroups.delete(key);
      } else {
        state.expandedGroups.add(key);
      }
      renderGroups(groups);
    });

    const ruleList = document.createElement("div");
    ruleList.id = `rule-list-${index}`;
    ruleList.className = "rule-list";
    ruleList.hidden = !expanded;
    if (expanded) {
      ruleList.append(groupActionBar(group, index, activeCount, inactiveCount));
      if (rules.length) {
        for (const [ruleIndex, rule] of rules.entries()) {
          ruleList.append(ruleRowNode(rule, group, index, ruleIndex));
        }
      } else {
        ruleList.append(emptyNode("Noch keine Regeln in der Regelgruppe"));
      }
    }

    item.append(header, ruleList);
    elements.groupList.append(item);
  }

  updateGroupToggleButton(groups);
}
function ruleRowNode(rule, group, groupIndex, ruleIndex) {
  const selected = state.selectedRuleRef === ruleSelectionKey(group, groupIndex, ruleIndex);
  const item = document.createElement("div");
  item.className = `rule-item rule-row ${rule.active ? "" : "inactive"} ${selected ? "selected" : ""} ${dimensionClass(rule.dimension)}`;

  const statusDot = document.createElement("span");
  statusDot.className = `rule-status-dot ${rule.active ? "active" : "inactive"}`;
  statusDot.setAttribute("aria-hidden", "true");

  const titleButton = document.createElement("button");
  titleButton.className = "rule-title-button";
  titleButton.type = "button";
  titleButton.textContent = rule.message || rule.ruleType || "Regel ohne Namen";
  titleButton.addEventListener("click", (event) => {
    event.stopPropagation();
    selectRule(group, groupIndex, ruleIndex);
  });

  const dimensionBadge = badge(rule.dimension || "Ohne Typ", dimensionClass(rule.dimension));

  const activeToggle = document.createElement("label");
  activeToggle.className = "rule-switch";
  activeToggle.setAttribute("aria-label", "Regel aktiv");
  const activeInput = document.createElement("input");
  activeInput.type = "checkbox";
  activeInput.checked = Boolean(rule.active);
  const switchTrack = document.createElement("span");
  activeToggle.append(activeInput, switchTrack);

  activeInput.addEventListener("click", (event) => event.stopPropagation());
  activeInput.addEventListener("change", async () => {
    const oldValue = Boolean(rule.active);
    rule.active = activeInput.checked;
    markEditorDirty();
    recalculateEditorModel();
    await persistRuleChange(group, groupIndex, rule, ruleIndex, "active", "Aktiv", oldValue, Boolean(rule.active));
  });

  const actions = document.createElement("div");
  actions.className = "row-actions";
  const upButton = smallActionButton("↑", "Regel nach oben");
  upButton.disabled = ruleIndex === 0;
  upButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await moveRule(groupIndex, ruleIndex, -1);
  });
  const downButton = smallActionButton("↓", "Regel nach unten");
  downButton.disabled = ruleIndex >= (group.rules || []).length - 1;
  downButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await moveRule(groupIndex, ruleIndex, 1);
  });
  const deleteButton = smallActionButton("×", "Regel löschen", "danger");
  deleteButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await deleteRule(groupIndex, ruleIndex);
  });
  actions.append(upButton, downButton, deleteButton);

  item.addEventListener("click", () => selectRule(group, groupIndex, ruleIndex));
  item.append(statusDot, titleButton, dimensionBadge, activeToggle, actions);
  return item;
}

function selectRule(group, groupIndex, ruleIndex) {
  showParameterDetail();
  state.selectedBlockIndex = null;
  state.selectedContextItem = null;
  state.selectedRuleRef = ruleSelectionKey(group, groupIndex, ruleIndex);
  renderBlocks(state.editorModel?.blocks || []);
  renderContextPanel();
  renderRuleDetail();
}

function renderRuleDetail() {
  if (!elements.ruleDetail) {
    return;
  }
  elements.ruleDetail.replaceChildren();
  if (state.selectedContextItem) {
    renderContextItemDetail();
    return;
  }
  if (state.selectedBlockIndex !== null) {
    renderBlockDetail(state.selectedBlockIndex);
    return;
  }
  elements.detailPanelTitle.textContent = "Regelparameter";
  const entry = selectedRuleEntry();
  if (!entry) {
    elements.ruleDetail.append(emptyNode("Keine Regel ausgewählt"));
    return;
  }

  const { group, groupIndex, rule, ruleIndex } = entry;
  const panel = document.createElement("div");
  panel.className = "rule-detail-panel";
  panel.append(textBlock("div", groupTitle(group), "detail-context"));
  const explanationResult = document.createElement("div");
  explanationResult.className = "ai-explanation";
  explanationResult.hidden = true;
  const revisionPanel = document.createElement("div");
  revisionPanel.className = "ai-revision";
  revisionPanel.hidden = true;
  const revisionInstruction = document.createElement("textarea");
  revisionInstruction.rows = 3;
  revisionInstruction.placeholder = "Optionaler Änderungswunsch, z. B. Leerzeichen ebenfalls als leer behandeln";
  const revisionStatus = textBlock("div", "Bestehende Regel fachlich und technisch prüfen", "ai-rule-status");
  const revisionResult = document.createElement("div");
  revisionResult.className = "ai-revision-result";
  const runRevisionButton = document.createElement("button");
  runRevisionButton.type = "button";
  runRevisionButton.className = "button primary compact-button";
  runRevisionButton.textContent = "Regel prüfen";
  const revisionActions = document.createElement("div");
  revisionActions.className = "rule-detail-actions ai-rule-actions";
  revisionActions.append(runRevisionButton);
  revisionPanel.append(
    parameterField("Änderungswunsch (optional)", revisionInstruction),
    revisionActions,
    revisionStatus,
    revisionResult,
  );
  let proposedRevision = null;

  function clearExplanation() {
    explanationResult.hidden = true;
    explanationResult.replaceChildren();
  }

  function clearRevisionProposal() {
    proposedRevision = null;
    revisionResult.replaceChildren();
    revisionStatus.textContent = "Bestehende Regel fachlich und technisch prüfen";
  }

  function clearAiResults() {
    clearExplanation();
    clearRevisionProposal();
  }

  const conditionInput = document.createElement("textarea");
  conditionInput.className = "parameter-textarea";
  conditionInput.value = rule.condition || "";
  conditionInput.rows = 5;
  let committedCondition = rule.condition || "";
  conditionInput.addEventListener("input", () => {
    rule.condition = conditionInput.value;
    clearAiResults();
    markEditorDirty();
  });
  async function commitConditionChange() {
    const oldValue = committedCondition;
    const newValue = conditionInput.value;
    committedCondition = newValue;
    await persistRuleChange(group, groupIndex, rule, ruleIndex, "condition", "Bedingung", oldValue, newValue);
  }
  conditionInput.addEventListener("change", commitConditionChange);

  const messageInput = document.createElement("input");
  messageInput.type = "text";
  messageInput.value = rule.message || "";
  let committedMessage = rule.message || "";
  messageInput.addEventListener("input", () => {
    rule.message = stripMessagePipe(messageInput.value);
    rule.messageLanguage = state.uiLanguage;
    clearAiResults();
    if (messageInput.value !== rule.message) {
      messageInput.value = rule.message;
    }
    markEditorDirty();
  });
  async function commitMessageChange() {
    const oldValue = committedMessage;
    const newValue = normalizeMessage(messageInput.value);
    messageInput.value = newValue;
    rule.message = newValue;
    committedMessage = newValue;
    await persistRuleChange(group, groupIndex, rule, ruleIndex, "message", "Fehlermeldung", oldValue, newValue);
  }
  messageInput.addEventListener("change", commitMessageChange);

  const dimensionSelect = document.createElement("select");
  const dimensions = catalogDimensions();
  dimensionSelect.append(optionNode("", "Ohne Typ"));
  for (const dimension of dimensions) {
    dimensionSelect.append(optionNode(dimension, dimension));
  }
  dimensionSelect.value = rule.dimension || "";
  dimensionSelect.addEventListener("change", async () => {
    const oldValue = rule.dimension || "";
    rule.dimension = dimensionSelect.value;
    clearAiResults();
    markEditorDirty();
    recalculateEditorModel();
    await persistRuleChange(group, groupIndex, rule, ruleIndex, "dimension", "DQ-Typ", oldValue, rule.dimension || "");
  });

  const typeSelect = document.createElement("select");
  const ruleTypes = catalogRuleTypes();
  for (const ruleType of ruleTypes) {
    typeSelect.append(optionNode(ruleType.id, ruleType.label || ruleType.id));
  }
  const currentType = rule.ruleType || "custom";
  if (![...typeSelect.options].some((option) => option.value === currentType)) {
    typeSelect.append(optionNode(currentType, currentType));
  }
  typeSelect.value = currentType;
  typeSelect.addEventListener("change", async () => {
    const oldValue = rule.ruleType || "custom";
    rule.ruleType = typeSelect.value || "custom";
    clearAiResults();
    const selectedType = findRuleType(rule.ruleType);
    if (selectedType?.defaultDimension && !rule.dimension) {
      rule.dimension = selectedType.defaultDimension;
      dimensionSelect.value = rule.dimension;
    }
    markEditorDirty();
    recalculateEditorModel();
    await persistRuleChange(group, groupIndex, rule, ruleIndex, "ruleType", "Regeltyp", oldValue, rule.ruleType || "custom");
  });

  const actions = document.createElement("div");
  actions.className = "rule-detail-actions";
  const explainButton = document.createElement("button");
  explainButton.type = "button";
  explainButton.className = "button secondary compact-button";
  explainButton.textContent = "Formel erklären";
  explainButton.addEventListener("click", async () => {
    if (state.explainingAiRule) return;
    if (!state.aiConfigId) {
      openAiConfigDialog();
      return;
    }
    const condition = conditionInput.value.trim();
    if (!condition) {
      showToast("Die Regel enthält keine Bedingung");
      return;
    }
    const column = projectColumnForGroup(group);
    state.explainingAiRule = true;
    explainButton.disabled = true;
    explainButton.textContent = "Erklärung läuft";
    explanationResult.hidden = false;
    explanationResult.replaceChildren(textBlock("div", "Formel wird erklärt", "ai-rule-status"));
    try {
      const payload = await requestJson("/api/ai/rules/explain", {
        method: "POST",
        body: JSON.stringify({
          configId: state.configId,
          aiConfigId: state.aiConfigId,
          language: state.uiLanguage,
          internalName: groupInternalName(group),
          displayName: group.displayName || column.displayName || "",
          description: group.description || column.description || "",
          dataType: column.dataType || "",
          condition,
          message: normalizeMessage(messageInput.value),
          dimension: dimensionSelect.value || "",
          ruleType: typeSelect.value || "custom",
        }),
      });
      renderRuleExplanation(explanationResult, payload.explanation || {});
    } catch (error) {
      explanationResult.hidden = true;
      showToast(error.message);
    } finally {
      state.explainingAiRule = false;
      explainButton.disabled = false;
      explainButton.textContent = "Formel erklären";
    }
  });
  const reviseButton = document.createElement("button");
  reviseButton.type = "button";
  reviseButton.className = "button secondary compact-button";
  reviseButton.textContent = "Mit KI überarbeiten";
  reviseButton.addEventListener("click", () => {
    if (!state.aiConfigId) {
      openAiConfigDialog();
      return;
    }
    revisionPanel.hidden = !revisionPanel.hidden;
    if (!revisionPanel.hidden) {
      revisionInstruction.focus();
    }
  });

  function renderRevisionProposal(revision) {
    revisionResult.replaceChildren();
    const currentCondition = conditionInput.value.trim();
    const currentMessage = normalizeMessage(messageInput.value);
    const proposedCondition = String(revision.condition || "").trim();
    const proposedMessage = normalizeMessage(revision.message || "");
    const proposedDimension = revision.dimension || dimensionSelect.value || "";
    const proposedRuleType = revision.ruleType || typeSelect.value || "custom";
    const hasDifference = currentCondition !== proposedCondition
      || currentMessage !== proposedMessage
      || dimensionSelect.value !== proposedDimension
      || typeSelect.value !== proposedRuleType;

    revisionResult.append(textBlock("h4", hasDifference ? "KI-Vorschlag" : "Prüfergebnis"));
    revisionResult.append(textBlock("p", revision.assessment || "Keine Bewertung verfügbar."));
    if (revision.clarificationQuestion) {
      revisionResult.append(textBlock("p", revision.clarificationQuestion, "ai-revision-question"));
    }

    const comparison = document.createElement("div");
    comparison.className = "ai-revision-comparison";
    comparison.append(
      textBlock("span", "Bisherige Bedingung", "meta-line"),
      textBlock("code", currentCondition || "-"),
      textBlock("span", "Vorgeschlagene Bedingung", "meta-line"),
      textBlock("code", proposedCondition || "-"),
      textBlock("span", "Vorgeschlagene Fehlermeldung", "meta-line"),
      textBlock("div", proposedMessage || "-"),
    );
    const badges = document.createElement("div");
    badges.className = "ai-revision-badges";
    badges.append(badge(proposedDimension || "Ohne DQ-Typ"), badge(proposedRuleType || "custom"));
    comparison.append(badges);
    revisionResult.append(comparison);

    for (const [title, values] of [["Änderungen", revision.changes], ["Hinweise", revision.warnings]]) {
      if (!Array.isArray(values) || !values.length) continue;
      revisionResult.append(textBlock("h4", title));
      const list = document.createElement("ul");
      values.forEach((value) => list.append(textBlock("li", value)));
      revisionResult.append(list);
    }

    const examples = Array.isArray(revision.examples) ? revision.examples : [];
    const resultActions = document.createElement("div");
    resultActions.className = "rule-detail-actions ai-rule-actions";
    const testButton = document.createElement("button");
    testButton.type = "button";
    testButton.className = "button secondary compact-button";
    testButton.textContent = "Beispiele prüfen";
    testButton.disabled = !examples.length;
    const applyRevisionButton = document.createElement("button");
    applyRevisionButton.type = "button";
    applyRevisionButton.className = "button primary compact-button";
    applyRevisionButton.textContent = "Vorschlag übernehmen";
    applyRevisionButton.disabled = !hasDifference;
    resultActions.append(testButton, applyRevisionButton);
    revisionResult.append(resultActions);

    const exampleResult = document.createElement("div");
    exampleResult.className = "ai-example-list";
    revisionResult.append(exampleResult);

    testButton.addEventListener("click", async () => {
      if (state.testingAiExamples || !examples.length) return;
      state.testingAiExamples = true;
      testButton.disabled = true;
      testButton.textContent = "Prüfung läuft";
      try {
        const payload = await requestJson("/api/ai/rules/test-examples", {
          method: "POST",
          body: JSON.stringify({
            configId: state.configId,
            aiConfigId: state.aiConfigId,
            language: state.uiLanguage,
            internalName: groupInternalName(group),
            condition: proposedCondition,
            message: proposedMessage,
            examples,
          }),
        });
        const results = payload.test?.results || [];
        exampleResult.replaceChildren();
        examples.forEach((example, index) => {
          const result = results[index];
          const row = document.createElement("div");
          row.className = `ai-example-item ${result ? (result.matchesExpectation ? "passed" : "failed") : ""}`.trim();
          row.append(
            textBlock("code", example.value === null ? "NULL" : String(example.value)),
            badge(example.expectedViolation ? "Fehler erwartet" : "Gültig erwartet"),
            textBlock("span", result?.explanation || example.explanation || "", "meta-line"),
          );
          exampleResult.append(row);
        });
        revisionStatus.textContent = payload.test?.summary || "Beispielprüfung abgeschlossen";
      } catch (error) {
        showToast(error.message);
      } finally {
        state.testingAiExamples = false;
        testButton.disabled = false;
        testButton.textContent = "Beispiele prüfen";
      }
    });

    applyRevisionButton.addEventListener("click", async () => {
      const oldRule = deepClone(rule);
      rule.condition = proposedCondition;
      rule.message = proposedMessage;
      rule.messageLanguage = state.uiLanguage;
      rule.dimension = proposedDimension;
      rule.ruleType = proposedRuleType;
      conditionInput.value = rule.condition;
      messageInput.value = rule.message;
      dimensionSelect.value = rule.dimension;
      if (![...typeSelect.options].some((option) => option.value === rule.ruleType)) {
        typeSelect.append(optionNode(rule.ruleType, rule.ruleType));
      }
      typeSelect.value = rule.ruleType;
      committedCondition = rule.condition;
      committedMessage = rule.message;
      markEditorDirty();
      recalculateEditorModel();
      await saveChangeLogEntry({
        changeType: "rule_ai_revision",
        targetPath: `checks.groups.${groupIndex}.rules.${ruleIndex}`,
        targetLabel: `${groupTitle(group)} · ${rule.message || "Regel"} · KI-Überarbeitung`,
        oldValue: oldRule,
        newValue: deepClone(rule),
      });
      showToast("KI-Vorschlag übernommen und protokolliert");
    });
  }

  runRevisionButton.addEventListener("click", async () => {
    if (state.revisingAiRule) return;
    const condition = conditionInput.value.trim();
    if (!condition) {
      showToast("Die Regel enthält keine Bedingung");
      return;
    }
    const column = projectColumnForGroup(group);
    state.revisingAiRule = true;
    runRevisionButton.disabled = true;
    runRevisionButton.textContent = "KI-Prüfung läuft";
    revisionStatus.textContent = "Die bestehende Regel wird geprüft";
    revisionResult.replaceChildren();
    try {
      const payload = await requestJson("/api/ai/rules/revise", {
        method: "POST",
        body: JSON.stringify({
          configId: state.configId,
          aiConfigId: state.aiConfigId,
          language: state.uiLanguage,
          internalName: groupInternalName(group),
          displayName: group.displayName || column.displayName || "",
          description: group.description || column.description || "",
          dataType: column.dataType || "",
          condition,
          message: normalizeMessage(messageInput.value),
          dimension: dimensionSelect.value || "",
          ruleType: typeSelect.value || "custom",
          instruction: revisionInstruction.value.trim(),
        }),
      });
      proposedRevision = payload.revision || {};
      renderRevisionProposal(proposedRevision);
      revisionStatus.textContent = proposedRevision.hasChanges ? "Verbesserungsvorschlag erstellt" : "Prüfung abgeschlossen";
    } catch (error) {
      revisionStatus.textContent = "KI-Prüfung fehlgeschlagen";
      showToast(error.message);
    } finally {
      state.revisingAiRule = false;
      runRevisionButton.disabled = false;
      runRevisionButton.textContent = "Regel prüfen";
    }
  });
  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "button secondary danger compact-button";
  deleteButton.textContent = "Löschen";
  deleteButton.addEventListener("click", async () => deleteRule(groupIndex, ruleIndex));
  const applyButton = document.createElement("button");
  applyButton.type = "button";
  applyButton.className = "button primary compact-button";
  applyButton.textContent = "Übernehmen";
  applyButton.addEventListener("click", async () => {
    await commitConditionChange();
    await commitMessageChange();
    recalculateEditorModel();
    renderEditorModel();
    showToast("Regel aktualisiert");
  });
  actions.append(explainButton, reviseButton, deleteButton, applyButton);

  panel.append(
    parameterField("Bedingung", conditionInput),
    parameterField("Fehlermeldung", messageInput),
    parameterField("DQ-Typ", dimensionSelect),
    parameterField("Regeltyp", typeSelect),
    actions,
    revisionPanel,
    explanationResult,
  );
  elements.ruleDetail.append(panel);
}

function renderContextItemDetail() {
  const selection = state.selectedContextItem;
  const block = (state.editorModel?.blocks || [])[selection?.blockIndex];
  const entry = block ? blockContextEntries(block)[selection.index] : null;
  if (!block || !entry) {
    state.selectedContextItem = null;
    renderBlockDetail(state.selectedBlockIndex);
    return;
  }

  const titles = {
    attribute: "Attributparameter",
    process: "Prozessparameter",
    join: "Join-Parameter",
    output: "Ausgabeparameter",
  };
  elements.detailPanelTitle.textContent = titles[entry.kind] || "Elementparameter";
  const panel = document.createElement("div");
  panel.className = "rule-detail-panel context-detail-panel";
  panel.append(textBlock("div", block.title || block.id, "detail-context"));
  panel.append(parameterField("Name", readonlyInput(entry.label)));
  if (entry.kind === "attribute") {
    panel.append(
      parameterField("Ausdruck", readonlyTextarea(entry.data.expression || "-", 4)),
      parameterField("Kommentar", readonlyInput(entry.data.comment || "-")),
    );
  } else if (entry.kind === "output") {
    panel.append(parameterField("Ausdruck", readonlyTextarea(entry.data.expression || "-", 4)));
  } else if (entry.kind === "process") {
    panel.append(parameterField("Wert", readonlyInput(entry.data.value || entry.label)));
  } else if (entry.kind === "join") {
    panel.append(
      parameterField("CTE", readonlyInput(block.cteName || "joined")),
      parameterField("Zeilen", readonlyInput(`${block.lineStart || "-"}-${block.lineEnd || "-"}`)),
    );
  }
  elements.ruleDetail.append(panel);
}

function renderBlockDetail(blockIndex) {
  const block = (state.editorModel?.blocks || [])[blockIndex];
  if (!block || !elements.ruleDetail) {
    state.selectedBlockIndex = null;
    elements.detailPanelTitle.textContent = "Regelparameter";
    elements.ruleDetail.append(emptyNode("Kein Block ausgewählt"));
    return;
  }

  elements.detailPanelTitle.textContent = "Blockparameter";
  const panel = document.createElement("form");
  panel.className = "rule-detail-panel block-detail-panel";
  panel.append(textBlock("div", block.title || block.id || "Block", "detail-context"));

  const titleInput = document.createElement("input");
  titleInput.type = "text";
  titleInput.value = block.title || "";

  const descriptionInput = document.createElement("textarea");
  descriptionInput.className = "parameter-textarea";
  descriptionInput.rows = 4;
  descriptionInput.value = block.description || "";

  const source = state.editorModel?.source || {};
  const subtypeInput = document.createElement("input");
  subtypeInput.type = "text";
  subtypeInput.value = source.masterDataSubType || "";
  subtypeInput.placeholder = "CUSTOMER";

  const exceptionsInput = document.createElement("textarea");
  exceptionsInput.className = "parameter-textarea";
  exceptionsInput.rows = 4;
  exceptionsInput.value = formatSourceExceptions(source.exceptions || []);
  exceptionsInput.placeholder = "CUSTOMER_I_D: 10000000, 10000001";

  panel.append(
    parameterField("Anzeigename", titleInput),
    parameterField("Beschreibung", descriptionInput),
    parameterField("CTE / Bereich", readonlyInput(block.cteName || "Finale Ausgabe")),
    parameterField("Blocktyp", readonlyInput(block.id || "")),
    parameterField("Zeilen", readonlyInput(`${block.lineStart || "-"}-${block.lineEnd || "-"}`)),
  );
  if (block.id === "source") {
    panel.append(
      parameterField("MASTER_DATA_SUB_TYPE", subtypeInput),
      parameterField("Ausnahmen", exceptionsInput),
    );
  }

  const context = blockContextField(block);
  if (context) {
    panel.append(context);
  }

  const actions = document.createElement("div");
  actions.className = "rule-detail-actions";
  const applyButton = document.createElement("button");
  applyButton.type = "submit";
  applyButton.className = "button primary compact-button";
  applyButton.textContent = "Übernehmen";
  actions.append(applyButton);
  panel.append(actions);

  panel.addEventListener("submit", async (event) => {
    event.preventDefault();
    const oldModel = deepClone(state.editorModel);
    const oldBlock = deepClone(block);
    block.title = titleInput.value.trim() || oldBlock.title || block.id;
    block.description = descriptionInput.value.trim();
    if (block.id === "source") {
      let exceptions;
      try {
        exceptions = parseSourceExceptionLines(exceptionsInput.value);
      } catch (error) {
        showToast(error.message);
        return;
      }
      state.editorModel.source = state.editorModel.source || {};
      state.editorModel.source.masterDataSubType = subtypeInput.value.trim().toUpperCase();
      state.editorModel.source.exceptions = exceptions;
    }
    const oldValue = block.id === "source" ? oldModel : oldBlock;
    const newValue = block.id === "source" ? deepClone(state.editorModel) : deepClone(block);
    if (valuesEqual(oldValue, newValue)) {
      return;
    }
    markEditorDirty();
    recalculateEditorModel();
    renderEditorModel();
    await saveChangeLogEntry({
      changeType: block.id === "source" ? "source_configuration" : "block_metadata",
      targetPath: block.id === "source" ? "$" : `blocks.${blockIndex}`,
      targetLabel: `${block.title || block.id} · ${block.id === "source" ? "Quellkonfiguration" : "Blockparameter"}`,
      oldValue,
      newValue,
    });
    showToast("Blockparameter aktualisiert");
  });

  elements.ruleDetail.append(panel);
}

function formatSourceExceptions(exceptions) {
  return (exceptions || [])
    .map((exception) => `${exception.field || ""}: ${(exception.values || []).join(", ")}`)
    .join("\n");
}

function parseSourceExceptionLines(value) {
  const exceptions = [];
  for (const rawLine of String(value || "").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) {
      continue;
    }
    const match = /^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$/.exec(line);
    if (!match) {
      throw new Error(`Ungültige Ausnahme: ${line}`);
    }
    const values = match[2].split(",").map((item) => item.trim()).filter(Boolean);
    if (!values.length) {
      throw new Error(`Ausnahme für ${match[1]} benötigt einen Wert`);
    }
    exceptions.push({ field: match[1], operator: "NOT IN", values });
  }
  return exceptions;
}

function readonlyInput(value) {
  const input = document.createElement("input");
  input.type = "text";
  input.value = String(value || "");
  input.readOnly = true;
  return input;
}

function readonlyTextarea(value, rows = 5) {
  const textarea = document.createElement("textarea");
  textarea.className = "parameter-textarea block-context-value";
  textarea.value = String(value || "");
  textarea.rows = rows;
  textarea.readOnly = true;
  return textarea;
}

function blockContextField(block) {
  if (block.id === "source") {
    const attributes = (state.editorModel?.source?.attributes || [])
      .map((attribute) => attribute.name || attribute.expression)
      .filter(Boolean);
    return parameterField(`Attribute (${attributes.length})`, readonlyTextarea(attributes.join("\n") || "-"));
  }
  if (block.id === "process") {
    return parameterField("Prozessquelle", readonlyInput('Business Processes / $schema."pa_export"'));
  }
  if (block.id === "join") {
    return parameterField("Datenbasis", readonlyInput(block.cteName || "joined"));
  }
  if (block.id === "checks") {
    const groups = state.editorModel?.checks?.groups || [];
    const rules = groups.flatMap((group) => group.rules || []);
    return parameterField("DQ-Checks", readonlyInput(`${groups.length} Regelgruppen · ${rules.length} Regeln`));
  }
  if (block.id === "output") {
    const fields = (state.editorModel?.output?.fields || [])
      .map((field) => field.name || field.expression)
      .filter(Boolean);
    return parameterField(`Ausgabefelder (${fields.length})`, readonlyTextarea(fields.join("\n") || "-"));
  }
  return null;
}

function parameterField(labelText, control) {
  const label = document.createElement("label");
  label.className = "parameter-field";
  label.append(textBlock("span", labelText));
  label.append(control);
  return label;
}

function selectedRuleEntry() {
  if (!state.selectedRuleRef) {
    return null;
  }
  const groups = state.editorModel?.checks?.groups || [];
  for (const [groupIndex, group] of groups.entries()) {
    const rules = group.rules || [];
    for (const [ruleIndex, rule] of rules.entries()) {
      if (state.selectedRuleRef === ruleSelectionKey(group, groupIndex, ruleIndex)) {
        return { group, groupIndex, rule, ruleIndex };
      }
    }
  }
  return null;
}

function ruleSelectionKey(group, groupIndex, ruleIndex) {
  return `${groupKey(group, groupIndex)}:${ruleIndex}`;
}
function renderValidation(findings) {
  void findings;
  elements.validationList.replaceChildren();
  elements.validationList.hidden = true;
  renderChangeLog();
}

function clearPreview(message = "Kein Ergebnis geladen") {
  elements.previewTable.querySelector("thead").replaceChildren();
  elements.previewTable.querySelector("tbody").replaceChildren();
  elements.emptyPreview.textContent = message;
  elements.emptyPreview.style.display = "grid";
  elements.previewInfo.textContent = "-";
  elements.rowsMetric.textContent = "-";
}

function clearEditor(message = "Kein Modell geladen") {
  showParameterDetail();
  state.editorModel = null;
  state.originalEditorModel = null;
  state.currentDraft = null;
  state.baseline = null;
  state.reportSqlHash = "";
  state.changeLog = [];
  state.editorDirty = false;
  state.selectedRuleRef = null;
  state.selectedBlockIndex = null;
  state.selectedContextItem = null;
  clearSqlPreview(message);
  elements.editorInfo.textContent = message;
  elements.blocksMetric.textContent = "-";
  elements.groupsMetric.textContent = "-";
  elements.rulesMetric.textContent = "-";
  elements.findingsMetric.textContent = "-";
  elements.blockList.replaceChildren(emptyNode(message));
  elements.groupList.replaceChildren(emptyNode(message));
  elements.contextPanelTitle.textContent = "Datenqualitätsregeln";
  elements.contextPanelActions.hidden = false;
  elements.validationList.replaceChildren();
  elements.validationList.hidden = true;
  renderChangeLog();
  if (elements.ruleDetail) {
    elements.detailPanelTitle.textContent = "Regelparameter";
    elements.ruleDetail.replaceChildren(emptyNode(message));
  }
  updateGroupToggleButton([]);
}

function emptyNode(text) {
  const div = document.createElement("div");
  div.className = "empty-state";
  div.textContent = text;
  return div;
}

function textBlock(tag, text, className = "") {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) {
    node.className = className;
  }
  return node;
}

function badge(text, className = "") {
  const span = document.createElement("span");
  span.className = `badge ${className}`.trim();
  span.textContent = text || "-";
  return span;
}

function renderRuleExplanation(container, explanation) {
  container.replaceChildren();
  container.hidden = false;
  container.append(textBlock("h4", "Fachliche Erklärung"));
  container.append(textBlock("div", "KI-generierte Erklärung · fachlich prüfen", "ai-explanation-note"));
  container.append(textBlock("p", explanation.summary || "Keine Zusammenfassung verfügbar."));
  container.append(textBlock("h4", "Wann entsteht ein Fehler?"));
  container.append(textBlock("p", explanation.triggerBehavior || "-"));

  const sections = [
    ["Gültige Beispiele", explanation.validExamples],
    ["Fehlerhafte Beispiele", explanation.invalidExamples],
    ["Sonderfälle", explanation.edgeCases],
    ["Hinweise", explanation.warnings],
  ];
  for (const [title, values] of sections) {
    if (!Array.isArray(values) || !values.length) continue;
    container.append(textBlock("h4", title));
    const list = document.createElement("ul");
    for (const value of values) {
      list.append(textBlock("li", value));
    }
    container.append(list);
  }
}

function dimensionClass(value = "") {
  const normalized = value.toLocaleLowerCase();
  if (normalized.includes("voll")) return "dimension-vollstaendigkeit";
  if (normalized.includes("valid")) return "dimension-validitaet";
  if (normalized.includes("korrekt")) return "dimension-korrektheit";
  if (normalized.includes("eindeut")) return "dimension-eindeutigkeit";
  if (normalized.includes("konsist")) return "dimension-konsistenz";
  if (normalized.includes("aktual")) return "dimension-aktualitaet";
  if (normalized.includes("genau")) return "dimension-genauigkeit";
  if (normalized.includes("redund")) return "dimension-redundanz";
  if (normalized.includes("einheit")) return "dimension-einheitlichkeit";
  if (normalized.includes("relev")) return "dimension-relevanz";
  if (normalized.includes("zuverl")) return "dimension-zuverlaessigkeit";
  if (normalized.includes("verständ") || normalized.includes("verstaend")) return "dimension-verstaendlichkeit";
  return "";
}


function groupTitle(group) {
  const displayName = groupDisplayName(group);
  const internalName = groupInternalName(group);
  if (displayName && internalName && displayName !== internalName) {
    return `${displayName} (${internalName})`;
  }
  return displayName || internalName || `Prüfung ${group.number || ""}`.trim();
}

function groupDisplayName(group) {
  if (group.displayName) {
    return group.displayName;
  }
  const title = String(group.title || "").trim();
  const match = title.match(/^.+?\s*\((.+)\)$/);
  return match?.[1]?.trim() || title || group.field || `Prüfung ${group.number || ""}`.trim();
}

function groupPreviewDisplayName(group) {
  const displayName = groupDisplayName(group);
  if (!displayName || /\([^()]+\)\s*$/.test(displayName)) {
    return displayName;
  }
  const title = String(group.title || "").trim();
  const designation = title.match(/\(([^()]+)\)\s*$/)?.[1]?.trim() || "";
  if (!designation || normalizeColumnKey(designation) === normalizeColumnKey(displayName)) {
    return displayName;
  }
  return `${displayName} (${designation})`;
}

function groupInternalName(group) {
  return group.internalName || group.field || "";
}

function groupKey(group, index) {
  return String(group.id || group.number || group.field || group.title || index);
}

function allGroupsExpanded(groups) {
  return Boolean(groups.length) && groups.every((group, index) => state.expandedGroups.has(groupKey(group, index)));
}

function updateGroupToggleButton(groups = state.editorModel?.checks?.groups || []) {
  if (!elements.groupToggleBtn) {
    return;
  }
  elements.groupToggleBtn.disabled = !groups.length;
  elements.groupToggleBtn.textContent = allGroupsExpanded(groups) ? "Alle zuklappen" : "Alle aufklappen";
}

function toggleAllGroups() {
  const groups = state.editorModel?.checks?.groups || [];
  if (!groups.length) {
    return;
  }
  if (allGroupsExpanded(groups)) {
    state.expandedGroups = new Set();
  } else {
    state.expandedGroups = new Set(groups.map((group, index) => groupKey(group, index)));
  }
  renderGroups(groups);
}

function groupActionBar(group, groupIndex, activeCount, inactiveCount) {
  const bar = document.createElement("div");
  bar.className = "group-actions";
  bar.append(textBlock("span", `${activeCount} aktiv · ${inactiveCount} inaktiv`, "meta-line"));

  const controls = document.createElement("div");
  controls.className = "row-actions group-row-actions";

  const addRuleButton = document.createElement("button");
  addRuleButton.type = "button";
  addRuleButton.className = "button secondary compact-button";
  addRuleButton.textContent = "+ Regel";
  addRuleButton.addEventListener("click", (event) => {
    event.stopPropagation();
    openRuleWizard(groupIndex);
  });

  const catalogRuleButton = document.createElement("button");
  catalogRuleButton.type = "button";
  catalogRuleButton.className = "button secondary compact-button";
  catalogRuleButton.textContent = "Aus Katalog";
  catalogRuleButton.addEventListener("click", (event) => {
    event.stopPropagation();
    openCatalogRuleWizard(groupIndex);
  });

  const editGroupButton = document.createElement("button");
  editGroupButton.type = "button";
  editGroupButton.className = "button secondary compact-button";
  editGroupButton.textContent = "Bearbeiten";
  editGroupButton.title = "Displayname, Internalname und Beschreibung bearbeiten";
  editGroupButton.setAttribute("aria-label", "Displayname, Internalname und Beschreibung bearbeiten");
  editGroupButton.addEventListener("click", (event) => {
    event.stopPropagation();
    openGroupEditor(groupIndex);
  });

  const groupActive = activeCount > 0;
  const toggleButton = document.createElement("button");
  toggleButton.type = "button";
  toggleButton.className = "button secondary compact-button";
  toggleButton.textContent = groupActive ? "Regelgruppe aus" : "Regelgruppe an";
  toggleButton.disabled = !(group.rules || []).length;
  toggleButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await toggleGroupActive(groupIndex, !groupActive);
  });

  const upButton = smallActionButton("↑", "Regelgruppe nach oben");
  upButton.disabled = groupIndex === 0;
  upButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await moveGroup(groupIndex, -1);
  });

  const downButton = smallActionButton("↓", "Regelgruppe nach unten");
  downButton.disabled = groupIndex >= (state.editorModel?.checks?.groups || []).length - 1;
  downButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await moveGroup(groupIndex, 1);
  });

  const deleteGroupButton = smallActionButton("×", "Regelgruppe entfernen", "danger");
  deleteGroupButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await deleteGroup(groupIndex);
  });

  controls.append(
    addRuleButton,
    catalogRuleButton,
    editGroupButton,
    toggleButton,
    upButton,
    downButton,
    deleteGroupButton,
  );
  bar.append(controls);
  return bar;
}

function smallActionButton(text, title, variant = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button secondary compact-button icon-button ${variant}`.trim();
  button.textContent = text;
  button.title = title;
  button.setAttribute("aria-label", title);
  return button;
}

function ensureChecks() {
  if (!state.editorModel) {
    return { groups: [] };
  }
  state.editorModel.checks = state.editorModel.checks || {};
  state.editorModel.checks.groups = state.editorModel.checks.groups || [];
  return state.editorModel.checks;
}

function groupsPath() {
  return "checks.groups";
}

function groupPath(groupIndex) {
  return `checks.groups.${groupIndex}`;
}

function groupRulesPath(groupIndex) {
  return `checks.groups.${groupIndex}.rules`;
}

async function persistGroupsChange(changeType, targetLabel, oldGroups, newGroups) {
  if (valuesEqual(oldGroups, newGroups)) {
    return;
  }
  await saveChangeLogEntry({
    changeType,
    targetPath: groupsPath(),
    targetLabel,
    oldValue: oldGroups,
    newValue: newGroups,
  });
}

async function persistModelChange(changeType, targetLabel, oldModel, newModel) {
  if (valuesEqual(oldModel, newModel)) {
    return;
  }
  await saveChangeLogEntry({
    changeType,
    targetPath: "$",
    targetLabel,
    oldValue: oldModel,
    newValue: newModel,
  });
}

function ensureSourceAttribute(column) {
  const source = state.editorModel.source = state.editorModel.source || {};
  source.attributes = source.attributes || [];
  const internalName = String(column?.internalName || "").trim();
  if (!internalName) {
    throw new Error("Das ausgewählte Feld besitzt keinen internalName");
  }
  const wanted = normalizeColumnKey(internalName);
  const exists = source.attributes.some((attribute) => normalizeColumnKey(attribute.name) === wanted);
  if (!exists) {
    source.attributes.push({
      name: internalName,
      expression: internalName,
      displayName: String(column?.displayName || internalName).trim(),
      comment: String(column?.description || "").trim(),
    });
  }
}

async function persistGroupChange(groupIndex, changeType, targetLabel, oldGroup, newGroup) {
  if (valuesEqual(oldGroup, newGroup)) {
    return;
  }
  await saveChangeLogEntry({
    changeType,
    targetPath: groupPath(groupIndex),
    targetLabel,
    oldValue: oldGroup,
    newValue: newGroup,
  });
}

async function persistGroupRulesChange(group, groupIndex, changeType, targetLabel, oldRules, newRules) {
  if (valuesEqual(oldRules, newRules)) {
    return;
  }
  await saveChangeLogEntry({
    changeType,
    targetPath: groupRulesPath(groupIndex),
    targetLabel: targetLabel || groupTitle(group),
    oldValue: oldRules,
    newValue: newRules,
  });
}

function replaceInternalName(value, previousInternalName, nextInternalName) {
  if (!previousInternalName || previousInternalName === nextInternalName) {
    return String(value || "");
  }
  const escaped = previousInternalName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return String(value || "").replace(
    new RegExp(`(?<![A-Za-z0-9_])${escaped}(?![A-Za-z0-9_])`, "gi"),
    nextInternalName,
  );
}

function applyGroupInternalName(group, previousInternalName, nextInternalName) {
  group.internalName = nextInternalName;
  group.field = nextInternalName;
  group.title = replaceInternalName(group.title, previousInternalName, nextInternalName);
  for (const rule of group.rules || []) {
    rule.condition = replaceInternalName(rule.condition, previousInternalName, nextInternalName);
  }
  const source = state.editorModel.source = state.editorModel.source || {};
  const attributes = source.attributes = source.attributes || [];
  for (const attribute of attributes) {
    const matchesName = normalizeColumnKey(attribute.name) === normalizeColumnKey(previousInternalName);
    if (matchesName) attribute.name = nextInternalName;
    attribute.expression = replaceInternalName(attribute.expression, previousInternalName, nextInternalName);
  }
  const sourceContainsNextName = attributes.some(
    (attribute) => normalizeColumnKey(attribute.name) === normalizeColumnKey(nextInternalName),
  );
  if (!sourceContainsNextName) {
    attributes.push({
      name: nextInternalName,
      expression: nextInternalName,
      displayName: String(group.displayName || nextInternalName).trim(),
      comment: String(group.description || "").trim(),
    });
  }
}

function openGroupEditor(groupIndex) {
  const group = (state.editorModel?.checks?.groups || [])[groupIndex];
  if (!group || !elements.ruleDetail) {
    return;
  }
  showParameterDetail();
  elements.detailPanelTitle.textContent = "Regelgruppe";
  state.selectedRuleRef = null;
  state.selectedBlockIndex = null;
  state.selectedContextItem = null;
  elements.ruleDetail.replaceChildren();

  const panel = document.createElement("form");
  panel.className = "rule-detail-panel";
  panel.append(textBlock("div", "Regelgruppe bearbeiten", "detail-context"));

  const displayName = document.createElement("input");
  displayName.type = "text";
  displayName.value = groupPreviewDisplayName(group);
  displayName.required = true;
  displayName.maxLength = 240;

  const internalName = document.createElement("input");
  internalName.type = "text";
  internalName.value = groupInternalName(group);
  internalName.required = true;
  internalName.maxLength = 240;
  internalName.autocomplete = "off";

  const descriptionInput = document.createElement("textarea");
  descriptionInput.className = "parameter-textarea";
  descriptionInput.value = group.description || "";
  descriptionInput.rows = 5;

  const actions = document.createElement("div");
  actions.className = "rule-detail-actions";
  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "button secondary compact-button";
  cancelButton.textContent = "Abbrechen";
  cancelButton.addEventListener("click", renderRuleDetail);
  const applyButton = document.createElement("button");
  applyButton.type = "submit";
  applyButton.className = "button primary compact-button";
  applyButton.textContent = "Übernehmen";
  actions.append(cancelButton, applyButton);

  panel.append(
    parameterField("Displayname", displayName),
    parameterField("Internalname", internalName),
    parameterField("Beschreibung", descriptionInput),
    actions,
  );

  panel.addEventListener("submit", async (event) => {
    event.preventDefault();
    const nextDisplayName = displayName.value.trim();
    const previousInternalName = groupInternalName(group).trim();
    const nextInternalName = internalName.value.trim();
    if (!nextDisplayName) {
      displayName.focus();
      showToast("Displayname darf nicht leer sein", true);
      return;
    }
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(nextInternalName)) {
      internalName.focus();
      showToast("Internalname muss ein gültiger Feldname ohne Leer- oder Sonderzeichen sein");
      return;
    }
    const duplicate = (state.editorModel?.checks?.groups || []).some(
      (item, index) => index !== groupIndex && normalizeColumnKey(groupInternalName(item)) === normalizeColumnKey(nextInternalName),
    );
    if (duplicate) {
      internalName.focus();
      showToast("Dieser Internalname wird bereits von einer anderen Regelgruppe verwendet");
      return;
    }
    const oldGroup = deepClone(group);
    const oldModel = deepClone(state.editorModel);
    const internalNameChanged = normalizeColumnKey(previousInternalName) !== normalizeColumnKey(nextInternalName);
    group.displayName = nextDisplayName;
    group.description = descriptionInput.value.trim();
    applyGroupInternalName(group, previousInternalName, nextInternalName);
    markEditorDirty();
    recalculateEditorModel();
    renderEditorModel();
    if (internalNameChanged) {
      await persistModelChange(
        "group_internal_name",
        `${groupTitle(group)} · Internalname geändert`,
        oldModel,
        deepClone(state.editorModel),
      );
    } else {
      await persistGroupChange(
        groupIndex,
        "group_metadata",
        `${groupTitle(group)} · Bezeichnung oder Beschreibung geändert`,
        oldGroup,
        deepClone(group),
      );
    }
    showToast("Regelgruppe aktualisiert");
  });

  elements.ruleDetail.append(panel);
  displayName.focus();
}

async function openGroupWizard() {
  if (!state.editorModel || !elements.ruleDetail) {
    return;
  }
  showParameterDetail();
  elements.detailPanelTitle.textContent = "Neue Regelgruppe";
  state.selectedRuleRef = null;
  state.selectedBlockIndex = null;
  state.selectedContextItem = null;
  elements.ruleDetail.replaceChildren();

  const panel = document.createElement("form");
  panel.className = "rule-detail-panel wizard-panel";
  panel.append(textBlock("div", "Neue Regelgruppe", "detail-context"));

  const fieldInput = document.createElement("input");
  fieldInput.type = "text";
  fieldInput.placeholder = "Displayname, internalName oder importName suchen";
  fieldInput.autocomplete = "off";

  const columnSearch = document.createElement("div");
  columnSearch.className = "column-search";
  const columnStatus = textBlock("div", "Felder werden geladen", "meta-line column-search-status");
  const columnResults = document.createElement("div");
  columnResults.className = "column-search-results";
  columnResults.hidden = true;
  columnSearch.append(fieldInput, columnStatus, columnResults);

  const descriptionInput = document.createElement("input");
  descriptionInput.type = "text";
  descriptionInput.placeholder = "Ort";
  descriptionInput.autocomplete = "off";

  const aiProfilePanel = document.createElement("div");
  aiProfilePanel.className = "ai-field-profile";
  aiProfilePanel.hidden = true;
  const aiProfileStatus = textBlock(
    "div",
    "Übertragung: anonymisiertes Einspaltenprofil ohne Rohwerte",
    "ai-rule-status",
  );
  const analyzeFieldButton = document.createElement("button");
  analyzeFieldButton.type = "button";
  analyzeFieldButton.className = "button secondary compact-button";
  analyzeFieldButton.textContent = "KI-Regelvorschläge erzeugen";
  const aiProfileActions = document.createElement("div");
  aiProfileActions.className = "rule-detail-actions ai-rule-actions";
  aiProfileActions.append(analyzeFieldButton);
  const aiSuggestionList = document.createElement("div");
  aiSuggestionList.className = "ai-field-suggestions";
  aiProfilePanel.append(aiProfileActions, aiProfileStatus, aiSuggestionList);

  const actions = document.createElement("div");
  actions.className = "rule-detail-actions";
  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "button secondary compact-button";
  cancelButton.textContent = "Abbrechen";
  cancelButton.addEventListener("click", () => renderRuleDetail());
  const submitButton = document.createElement("button");
  submitButton.type = "submit";
  submitButton.className = "button primary compact-button";
  submitButton.textContent = "Regelgruppe anlegen";
  actions.append(cancelButton, submitButton);

  panel.append(
    parameterField("Feld suchen", columnSearch),
    parameterField("Beschreibung", descriptionInput),
    aiProfilePanel,
    actions,
  );

  panel.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedColumn) {
      showToast("Bitte ein freies Feld aus der Trefferliste auswählen");
      fieldInput.focus();
      return;
    }
    const field = selectedColumn.internalName || "";
    if (!field) {
      showToast("Das ausgewählte Feld besitzt keinen internalName");
      return;
    }
    const oldModel = deepClone(state.editorModel);
    const checks = ensureChecks();
    const description = descriptionInput.value.trim();
    const displayName = selectedColumn?.displayName || field;
    const newGroup = {
      id: generatedId("group"),
      number: (checks.groups || []).length + 1,
      title: displayName !== field ? `${field} (${displayName})` : field,
      displayName,
      internalName: field,
      field,
      description,
      typeHints: [],
      lineStart: null,
      rules: suggestionSelections
        .filter((entry) => entry.checkbox.checked)
        .map((entry, index) => ({
          id: generatedId("rule"),
          number: index + 1,
          condition: entry.suggestion.condition || "",
          message: normalizeMessage(entry.suggestion.message || ""),
          messageLanguage: state.uiLanguage,
          dimension: entry.suggestion.dimension || defaultDimensionForRuleType(entry.suggestion.ruleType || "custom"),
          ruleType: entry.suggestion.ruleType || "custom",
          active: true,
        })),
      activeRules: 0,
      inactiveRules: 0,
    };
    ensureSourceAttribute(selectedColumn);
    checks.groups.push(newGroup);
    renumberGroups(checks.groups);
    state.expandedGroups.add(groupKey(newGroup, checks.groups.length - 1));
    state.selectedRuleRef = null;
    markEditorDirty();
    recalculateEditorModel();
    renderEditorModel();
    await persistModelChange(
      "group_create",
      `Regelgruppe und Quellattribut angelegt · ${groupTitle(newGroup)}`,
      oldModel,
      deepClone(state.editorModel),
    );
  });

  elements.ruleDetail.append(panel);
  fieldInput.focus();

  let columns = [];
  let selectedColumn = null;
  let suggestionSelections = [];

  function clearFieldSuggestions() {
    suggestionSelections = [];
    aiSuggestionList.replaceChildren();
    aiProfileStatus.textContent = "Übertragung: anonymisiertes Einspaltenprofil ohne Rohwerte";
  }

  function selectColumnForBlock(column) {
    selectedColumn = column;
    fieldInput.value = column.internalName || column.importName || column.displayName || "";
    descriptionInput.value = column.description || "";
    columnResults.hidden = true;
    columnResults.replaceChildren();
    columnStatus.textContent = `${column.displayName || column.internalName || "Feld"} ausgewählt`;
    clearFieldSuggestions();
    aiProfilePanel.hidden = false;
  }

  function renderFieldSuggestions(payload) {
    const analysis = payload.analysis || {};
    const suggestions = analysis.suggestions || [];
    suggestionSelections = [];
    aiSuggestionList.replaceChildren();
    aiProfileStatus.textContent = analysis.profileSummary
      || `${payload.profile?.sampleSize || 0} Werte anonymisiert analysiert`;
    for (const suggestion of suggestions) {
      const label = document.createElement("label");
      label.className = "ai-field-suggestion";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = true;
      const content = document.createElement("span");
      content.className = "ai-field-suggestion-content";
      const heading = document.createElement("span");
      heading.className = "ai-field-suggestion-heading";
      heading.append(
        badge(suggestion.dimension || "Ohne DQ-Typ", dimensionClass(suggestion.dimension || "")),
        textBlock("strong", normalizeMessage(suggestion.message || "Regelvorschlag")),
      );
      content.append(
        heading,
        textBlock("code", suggestion.condition || "-"),
        textBlock("span", suggestion.evidence || suggestion.rationale || "", "meta-line"),
      );
      label.append(checkbox, content);
      aiSuggestionList.append(label);
      suggestionSelections.push({ suggestion, checkbox });
    }
    for (const warning of analysis.warnings || []) {
      aiSuggestionList.append(textBlock("div", warning, "ai-field-warning"));
    }
  }

  analyzeFieldButton.addEventListener("click", async () => {
    if (state.profilingAiField || !selectedColumn) return;
    if (!state.aiConfigId) {
      openAiConfigDialog();
      return;
    }
    state.profilingAiField = true;
    analyzeFieldButton.disabled = true;
    analyzeFieldButton.textContent = "Feldanalyse läuft";
    aiProfileStatus.textContent = "NEMO-Feldwerte werden lokal anonymisiert profiliert";
    aiSuggestionList.replaceChildren();
    try {
      const payload = await requestJson("/api/ai/fields/suggest-rules", {
        method: "POST",
        body: JSON.stringify({
          configId: state.configId,
          aiConfigId: state.aiConfigId,
          language: state.uiLanguage,
          project: state.project,
          internalName: selectedColumn.internalName,
          displayName: selectedColumn.displayName || "",
          description: selectedColumn.description || "",
          dataType: selectedColumn.dataType || "",
          maxRows: 500,
        }),
      });
      renderFieldSuggestions(payload);
      showToast(`${payload.analysis?.suggestions?.length || 0} KI-Regelvorschläge erstellt`);
    } catch (error) {
      aiProfileStatus.textContent = "Feldanalyse fehlgeschlagen";
      showToast(error.message);
    } finally {
      state.profilingAiField = false;
      analyzeFieldButton.disabled = false;
      analyzeFieldButton.textContent = "KI-Regelvorschläge erzeugen";
    }
  });

  function renderColumnMatches() {
    const query = fieldInput.value.trim();
    columnResults.replaceChildren();
    if (!query) {
      columnResults.hidden = true;
      columnStatus.textContent = columns.length ? `${columns.length} Felder geladen` : "Suchbegriff eingeben";
      return;
    }
    const matches = filterProjectColumns(columns, query);
    if (!matches.length) {
      columnResults.hidden = false;
      columnResults.append(emptyNode("Kein Feld gefunden"));
      columnStatus.textContent = "Kein Treffer";
      return;
    }
    columnResults.hidden = false;
    columnStatus.textContent = `${matches.length} Treffer`;
    for (const column of matches.slice(0, 20)) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "column-result";
      button.append(textBlock("strong", column.displayName || column.internalName || column.importName || "Feld"));
      button.append(textBlock("span", columnSubtitle(column), "meta-line"));
      if (column.description) {
        button.append(textBlock("span", column.description, "column-description"));
      }
      button.addEventListener("click", () => selectColumnForBlock(column));
      columnResults.append(button);
    }
  }

  fieldInput.addEventListener("input", () => {
    const selectedInternalName = selectedColumn?.internalName || selectedColumn?.importName || selectedColumn?.displayName || "";
    if (fieldInput.value.trim() !== selectedInternalName) {
      selectedColumn = null;
      aiProfilePanel.hidden = true;
      clearFieldSuggestions();
    }
    renderColumnMatches();
  });

  try {
    const projectColumns = await loadProjectColumns();
    const usedKeys = new Set(
      (ensureChecks().groups || [])
        .flatMap((group) => [group.internalName, group.field])
        .map(normalizeColumnKey)
        .filter(Boolean),
    );
    columns = projectColumns.filter((column) => {
      const keys = [column.internalName, column.importName].map(normalizeColumnKey).filter(Boolean);
      return !keys.some((key) => usedKeys.has(key));
    });
    if (!columns.length) {
      columnStatus.textContent = "Alle verfügbaren Felder besitzen bereits eine Regelgruppe";
    }
    renderColumnMatches();
  } catch (error) {
    columnStatus.textContent = "Felder konnten nicht geladen werden";
    showToast(error.message);
  }
}

function projectColumnCacheKey(project = state.project) {
  return `${state.configId || ""}::${project || ""}`;
}

async function loadProjectColumns(force = false) {
  if (!state.configId) {
    throw new Error("Keine Config ausgewählt");
  }
  const key = projectColumnCacheKey();
  if (!force && state.projectColumns[key]) {
    return state.projectColumns[key];
  }
  state.loadingColumns = true;
  try {
    const params = new URLSearchParams({ configId: state.configId });
    const payload = await requestJson(`/api/projects/${encodeURIComponent(state.project)}/columns?${params.toString()}`);
    const columns = payload.columns || [];
    state.projectColumns[key] = columns;
    return columns;
  } finally {
    state.loadingColumns = false;
  }
}

function filterProjectColumns(columns, query) {
  const normalizedQuery = normalizeSearchText(query);
  if (!normalizedQuery) {
    return [];
  }
  return columns.filter((column) => {
    const haystack = normalizeSearchText(
      `${column.displayName || ""} ${column.internalName || ""} ${column.importName || ""} ${column.description || ""}`,
    );
    return haystack.includes(normalizedQuery);
  });
}

function normalizeSearchText(value) {
  return String(value || "").trim().toLocaleLowerCase();
}

function columnSubtitle(column) {
  return [column.internalName, column.importName, column.dataType]
    .filter(Boolean)
    .join(" · ") || "-";
}

async function enrichGroupColumnMetadata(model) {
  const groups = model?.checks?.groups || [];
  if (!groups.length) {
    return;
  }
  try {
    const columns = await loadProjectColumns();
    const byName = new Map();
    for (const column of columns) {
      for (const value of [column.internalName, column.importName]) {
        const key = normalizeColumnKey(value);
        if (key && !byName.has(key)) {
          byName.set(key, column);
        }
      }
    }
    for (const group of groups) {
      let column = byName.get(normalizeColumnKey(group.internalName || group.field));
      if (!column) {
        const identifiers = (group.rules || [])
          .flatMap((rule) => String(rule.condition || "").match(/[A-Za-z_][A-Za-z0-9_]*/g) || []);
        column = identifiers.map((value) => byName.get(normalizeColumnKey(value))).find(Boolean);
      }
      if (!column) {
        continue;
      }
      group.displayName = column.displayName || group.displayName;
      group.internalName = column.internalName || group.internalName || group.field;
    }
  } catch (error) {
    console.warn("Regelgruppen-Metadaten konnten nicht ergänzt werden", error);
  }
}

function normalizeColumnKey(value) {
  return String(value || "").toLocaleLowerCase().replace(/[^a-z0-9]/g, "");
}

function projectColumnForGroup(group) {
  const columns = state.projectColumns[`${state.configId || ""}::${state.project || ""}`] || [];
  const wanted = normalizeColumnKey(groupInternalName(group));
  return columns.find((column) => normalizeColumnKey(column.internalName) === wanted) || {};
}

function openCatalogRuleWizard(groupIndex) {
  const group = (state.editorModel?.checks?.groups || [])[groupIndex];
  if (!group || !elements.ruleDetail) return;
  const templates = state.ruleTemplates.filter((template) => template.status !== "deprecated");
  if (!templates.length) {
    showToast("Keine verwendbare Regelvorlage vorhanden");
    if (state.uiMode === "expert") openRuleTemplateCatalog();
    return;
  }

  showParameterDetail();
  elements.detailPanelTitle.textContent = "Regel aus Katalog";
  state.selectedRuleRef = null;
  state.selectedBlockIndex = null;
  state.selectedContextItem = null;
  elements.ruleDetail.replaceChildren();

  const panel = document.createElement("form");
  panel.className = "rule-detail-panel wizard-panel catalog-rule-wizard";
  panel.append(textBlock("div", groupTitle(group), "detail-context"));

  const templateSelect = document.createElement("select");
  for (const template of templates) {
    templateSelect.append(optionNode(template.id, `${template.name} · v${template.currentVersion}`));
  }
  const templateInfo = textBlock("p", "", "meta-line");
  const parameterFields = document.createElement("div");
  parameterFields.className = "catalog-parameter-fields";
  const conditionPreview = textBlock("code", "Noch nicht aufgelöst", "catalog-condition-preview");
  const messagePreview = textBlock("div", "Noch nicht aufgelöst", "catalog-message-preview");
  const previewBox = document.createElement("div");
  previewBox.className = "catalog-rule-preview";
  previewBox.append(
    textBlock("strong", "Vorschau"),
    conditionPreview,
    messagePreview,
  );

  const actions = document.createElement("div");
  actions.className = "rule-detail-actions";
  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "button secondary compact-button";
  cancelButton.textContent = "Abbrechen";
  cancelButton.addEventListener("click", renderRuleDetail);
  const previewButton = document.createElement("button");
  previewButton.type = "button";
  previewButton.className = "button secondary compact-button";
  previewButton.textContent = "Vorlage prüfen";
  const applyButton = document.createElement("button");
  applyButton.type = "submit";
  applyButton.className = "button primary compact-button";
  applyButton.textContent = "Regel übernehmen";
  applyButton.disabled = true;
  actions.append(cancelButton, previewButton, applyButton);

  let parameterInputs = new Map();
  let resolvedPayload = null;

  function selectedTemplate() {
    return templates.find((template) => template.id === templateSelect.value) || templates[0];
  }

  function invalidatePreview() {
    resolvedPayload = null;
    applyButton.disabled = true;
    conditionPreview.textContent = "Noch nicht aufgelöst";
    messagePreview.textContent = "Noch nicht aufgelöst";
  }

  function renderTemplateParameters() {
    const template = selectedTemplate();
    const version = template?.version || {};
    templateInfo.textContent = `${template?.description || "Keine Beschreibung"} · ${version.dimension || "-"} · ${version.ruleType || "-"}`;
    parameterFields.replaceChildren();
    parameterInputs = new Map();
    for (const [name, definition] of Object.entries(version.parameterSchema || {})) {
      let input;
      if (definition.type === "boolean") {
        input = document.createElement("input");
        input.type = "checkbox";
        input.checked = Boolean(definition.default);
      } else if (definition.type === "enum") {
        input = document.createElement("select");
        for (const choice of definition.choices || []) {
          input.append(optionNode(String(choice), String(choice)));
        }
        input.value = String(definition.default ?? definition.choices?.[0] ?? "");
      } else {
        input = document.createElement("input");
        input.type = ["integer", "number"].includes(definition.type) ? "number" : "text";
        if (definition.type === "number") input.step = "any";
        if (definition.min !== undefined) input.min = String(definition.min);
        if (definition.max !== undefined) input.max = String(definition.max);
        input.value = String(definition.default ?? "");
        input.required = definition.required !== false;
      }
      input.dataset.parameterType = definition.type || "string";
      input.addEventListener("input", invalidatePreview);
      parameterInputs.set(name, input);
      parameterFields.append(parameterField(definition.label || name, input));
    }
    if (!parameterInputs.size) {
      parameterFields.append(textBlock("span", "Keine zusätzlichen Parameter", "meta-line"));
    }
    invalidatePreview();
  }

  function catalogParameters() {
    return Object.fromEntries([...parameterInputs.entries()].map(([name, input]) => {
      if (input.type === "checkbox") return [name, input.checked];
      if (input.dataset.parameterType === "integer") return [name, Number.parseInt(input.value, 10)];
      if (input.dataset.parameterType === "number") return [name, Number.parseFloat(input.value)];
      return [name, input.value];
    }));
  }

  async function resolveTemplate() {
    const template = selectedTemplate();
    const column = projectColumnForGroup(group);
    previewButton.disabled = true;
    previewButton.textContent = "Prüft";
    try {
      resolvedPayload = await requestJson(`/api/rule-templates/${encodeURIComponent(template.id)}/resolve`, {
        method: "POST",
        body: JSON.stringify({
          version: template.currentVersion,
          field: groupInternalName(group),
          displayName: groupDisplayName(group) || column.displayName || groupInternalName(group),
          description: group.description || column.description || "",
          parameters: catalogParameters(),
        }),
      });
      const resolved = resolvedPayload.resolvedRule;
      conditionPreview.textContent = resolved.condition;
      messagePreview.textContent = state.uiLanguage === "en" ? resolved.messageEn : resolved.messageDe;
      applyButton.disabled = false;
      showToast("Regelvorlage erfolgreich aufgelöst");
    } catch (error) {
      invalidatePreview();
      showToast(error.message);
    } finally {
      previewButton.disabled = false;
      previewButton.textContent = "Vorlage prüfen";
    }
  }

  templateSelect.addEventListener("change", renderTemplateParameters);
  previewButton.addEventListener("click", resolveTemplate);
  panel.append(
    parameterField("Regelvorlage", templateSelect),
    templateInfo,
    parameterFields,
    previewBox,
    actions,
  );
  panel.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!resolvedPayload) return;
    const template = resolvedPayload.template;
    const resolved = resolvedPayload.resolvedRule;
    group.rules = group.rules || [];
    const oldRules = deepClone(group.rules);
    const rule = {
      id: generatedId("rule"),
      number: group.rules.length + 1,
      condition: resolved.condition,
      message: state.uiLanguage === "en" ? resolved.messageEn : resolved.messageDe,
      messageLanguage: state.uiLanguage,
      dimension: resolved.dimension,
      ruleType: resolved.ruleType,
      active: true,
      catalogTemplateId: template.id,
      catalogTemplateVersion: template.currentVersion,
      catalogParameters: resolved.parameters,
    };
    group.rules.push(rule);
    renumberRules(group);
    state.expandedGroups.add(groupKey(group, groupIndex));
    state.selectedRuleRef = ruleSelectionKey(group, groupIndex, group.rules.length - 1);
    markEditorDirty();
    recalculateEditorModel();
    renderEditorModel();
    await persistGroupRulesChange(
      group,
      groupIndex,
      "catalog_rule_create",
      `${groupTitle(group)} · ${template.name} aus Regelkatalog`,
      oldRules,
      deepClone(group.rules),
    );
    try {
      await requestJson("/api/rule-template-bindings", {
        method: "POST",
        body: JSON.stringify({
          templateId: template.id,
          templateVersion: template.currentVersion,
          configId: state.configId,
          project: state.project,
          reportRef: reportRef(state.selectedReport),
          groupRef: group.id || groupInternalName(group),
          ruleRef: rule.id,
          parameters: resolved.parameters,
        }),
      });
      showToast("Katalogregel angelegt und Vorlagenbindung gespeichert");
    } catch (error) {
      showToast(`Regel angelegt, Vorlagenbindung fehlgeschlagen: ${error.message}`);
    }
  });

  elements.ruleDetail.append(panel);
  renderTemplateParameters();
}

function openRuleWizard(initialGroupIndex = null) {
  if (!state.editorModel || !elements.ruleDetail) {
    return;
  }
  showParameterDetail();
  elements.detailPanelTitle.textContent = "Neue Regel";
  const groups = ensureChecks().groups || [];
  if (!groups.length) {
    openGroupWizard();
    showToast("Zuerst Regelgruppe anlegen");
    return;
  }

  const selectedEntry = selectedRuleEntry();
  const requestedIndex = Number.isInteger(initialGroupIndex) ? initialGroupIndex : selectedEntry?.groupIndex ?? 0;
  const safeGroupIndex = Math.max(0, Math.min(requestedIndex, groups.length - 1));
  state.selectedRuleRef = null;
  state.selectedBlockIndex = null;
  state.selectedContextItem = null;
  elements.ruleDetail.replaceChildren();

  const panel = document.createElement("form");
  panel.className = "rule-detail-panel wizard-panel";
  panel.append(textBlock("div", "Neue Regel", "detail-context"));

  const groupSelect = document.createElement("select");
  for (const [index, group] of groups.entries()) {
    groupSelect.append(optionNode(String(index), groupTitle(group)));
  }
  groupSelect.value = String(safeGroupIndex);

  const typeSelect = document.createElement("select");
  for (const ruleType of catalogRuleTypes()) {
    typeSelect.append(optionNode(ruleType.id, ruleType.label || ruleType.id));
  }
  typeSelect.value = typeSelect.querySelector('option[value="completeness"]') ? "completeness" : "custom";

  const dimensionSelect = document.createElement("select");
  dimensionSelect.append(optionNode("", "Ohne Typ"));
  for (const dimension of catalogDimensions()) {
    dimensionSelect.append(optionNode(dimension, dimension));
  }

  const conditionInput = document.createElement("textarea");
  conditionInput.className = "parameter-textarea";
  conditionInput.rows = 5;

  const messageInput = document.createElement("input");
  messageInput.type = "text";

  const requirementInput = document.createElement("textarea");
  requirementInput.className = "parameter-textarea";
  requirementInput.rows = 4;
  requirementInput.placeholder = "Zum Beispiel: Der Wert muss genau zehn Ziffern enthalten.";

  const aiStatus = textBlock("div", state.aiConfigId ? "Bereit" : "Kein KI-Zugang eingerichtet", "ai-rule-status");
  const aiExamples = document.createElement("div");
  aiExamples.className = "ai-example-list";
  let generatedExamples = [];

  const aiActions = document.createElement("div");
  aiActions.className = "rule-detail-actions ai-rule-actions";
  const generateButton = document.createElement("button");
  generateButton.type = "button";
  generateButton.className = "button primary compact-button";
  generateButton.textContent = "Entwurf erstellen";
  const testExamplesButton = document.createElement("button");
  testExamplesButton.type = "button";
  testExamplesButton.className = "button secondary compact-button";
  testExamplesButton.textContent = "Beispiele prüfen";
  testExamplesButton.disabled = true;
  aiActions.append(generateButton, testExamplesButton);

  const activeWrap = document.createElement("label");
  activeWrap.className = "rule-toggle";
  const activeInput = document.createElement("input");
  activeInput.type = "checkbox";
  activeInput.checked = true;
  activeWrap.append(activeInput, textBlock("span", "Aktiv"));

  let conditionTouched = false;
  let messageTouched = false;
  conditionInput.addEventListener("input", () => {
    conditionTouched = true;
  });
  messageInput.addEventListener("input", () => {
    messageTouched = true;
    const clean = stripMessagePipe(messageInput.value);
    if (clean !== messageInput.value) {
      messageInput.value = clean;
    }
  });

  function selectedGroup() {
    return groups[Number(groupSelect.value)] || groups[0];
  }

  function selectedColumn(group) {
    const columns = state.projectColumns[`${state.configId || ""}::${state.project || ""}`] || [];
    const wanted = normalizeColumnKey(groupInternalName(group));
    return columns.find((column) => normalizeColumnKey(column.internalName) === wanted) || {};
  }

  function renderAiExamples(examples, testResults = null) {
    aiExamples.replaceChildren();
    const results = testResults?.results || [];
    examples.forEach((example, index) => {
      const result = results[index];
      const row = document.createElement("div");
      row.className = `ai-example-item ${result ? (result.matchesExpectation ? "passed" : "failed") : ""}`.trim();
      const value = example.value === null ? "NULL" : String(example.value);
      row.append(
        textBlock("code", value),
        badge(example.expectedViolation ? "Fehler erwartet" : "Gültig erwartet"),
        textBlock("span", result?.explanation || example.explanation || "", "meta-line"),
      );
      aiExamples.append(row);
    });
  }

  generateButton.addEventListener("click", async () => {
    if (state.generatingAiRule) return;
    if (!state.aiConfigId) {
      openAiConfigDialog();
      return;
    }
    const requirement = requirementInput.value.trim();
    if (requirement.length < 3) {
      showToast("Bitte die gewünschte Regel fachlich beschreiben");
      requirementInput.focus();
      return;
    }
    const group = selectedGroup();
    const column = selectedColumn(group);
    state.generatingAiRule = true;
    generateButton.disabled = true;
    generateButton.textContent = "Entwurf läuft";
    aiStatus.textContent = "KI erstellt den Regelentwurf";
    try {
      const payload = await requestJson("/api/ai/rules/draft", {
        method: "POST",
        body: JSON.stringify({
          configId: state.configId,
          aiConfigId: state.aiConfigId,
          language: state.uiLanguage,
          internalName: groupInternalName(group),
          displayName: group.displayName || column.displayName || "",
          description: group.description || column.description || "",
          dataType: column.dataType || "",
          requirement,
          existingRules: (group.rules || []).map((rule) => ({
            condition: rule.condition || "",
            message: rule.message || "",
            dimension: rule.dimension || "",
          })),
        }),
      });
      const draft = payload.draft || {};
      if (typeSelect.querySelector(`option[value="${CSS.escape(draft.ruleType || "")}"]`)) {
        typeSelect.value = draft.ruleType;
      } else {
        typeSelect.value = "custom";
      }
      dimensionSelect.value = draft.dimension || defaultDimensionForRuleType(typeSelect.value);
      conditionInput.value = draft.condition || "";
      messageInput.value = stripMessagePipe(draft.message || "");
      conditionTouched = true;
      messageTouched = true;
      generatedExamples = draft.examples || [];
      renderAiExamples(generatedExamples);
      testExamplesButton.disabled = !generatedExamples.length;
      aiStatus.textContent = draft.clarificationQuestion || draft.rationale || "Entwurf erstellt";
      showToast("KI-Regelentwurf erstellt");
    } catch (error) {
      aiStatus.textContent = "Entwurf fehlgeschlagen";
      showToast(error.message);
    } finally {
      state.generatingAiRule = false;
      generateButton.disabled = false;
      generateButton.textContent = "Entwurf erstellen";
    }
  });

  testExamplesButton.addEventListener("click", async () => {
    if (state.testingAiExamples || !generatedExamples.length) return;
    const group = selectedGroup();
    state.testingAiExamples = true;
    testExamplesButton.disabled = true;
    testExamplesButton.textContent = "Prüfung läuft";
    try {
      const payload = await requestJson("/api/ai/rules/test-examples", {
        method: "POST",
        body: JSON.stringify({
          configId: state.configId,
          aiConfigId: state.aiConfigId,
          language: state.uiLanguage,
          internalName: groupInternalName(group),
          condition: conditionInput.value.trim(),
          message: normalizeMessage(messageInput.value),
          examples: generatedExamples,
        }),
      });
      renderAiExamples(generatedExamples, payload.test);
      aiStatus.textContent = payload.test?.summary || "Fachliche Beispielprüfung abgeschlossen";
      showToast(payload.test?.allPassed ? "Alle Beispiele entsprechen der Erwartung" : "Mindestens ein Beispiel ist auffällig");
    } catch (error) {
      showToast(error.message);
    } finally {
      state.testingAiExamples = false;
      testExamplesButton.disabled = false;
      testExamplesButton.textContent = "Beispiele prüfen";
    }
  });

  function syncDefaults(force = false) {
    const group = selectedGroup();
    const ruleType = typeSelect.value || "custom";
    const defaultDimension = defaultDimensionForRuleType(ruleType);
    if ((force || !dimensionSelect.value) && defaultDimension) {
      dimensionSelect.value = defaultDimension;
    }
    if (force || !conditionTouched) {
      conditionInput.value = defaultConditionForRuleType(group, ruleType);
    }
    if (force || !messageTouched) {
      messageInput.value = defaultMessageForRuleType(group, ruleType);
    }
  }

  groupSelect.addEventListener("change", () => syncDefaults(false));
  typeSelect.addEventListener("change", () => syncDefaults(false));
  syncDefaults(true);

  const actions = document.createElement("div");
  actions.className = "rule-detail-actions";
  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "button secondary compact-button";
  cancelButton.textContent = "Abbrechen";
  cancelButton.addEventListener("click", () => renderRuleDetail());
  const submitButton = document.createElement("button");
  submitButton.type = "submit";
  submitButton.className = "button primary compact-button";
  submitButton.textContent = "Regel anlegen";
  actions.append(cancelButton, submitButton);

  panel.append(
    parameterField("Regelgruppe", groupSelect),
    parameterField("Fachliche Regelbeschreibung", requirementInput),
    aiActions,
    aiStatus,
    aiExamples,
    parameterField("Regeltyp", typeSelect),
    parameterField("DQ-Typ", dimensionSelect),
    parameterField("Bedingung", conditionInput),
    parameterField("Fehlermeldung", messageInput),
    parameterField("Status", activeWrap),
    actions,
  );

  panel.addEventListener("submit", async (event) => {
    event.preventDefault();
    const groupIndex = Number(groupSelect.value);
    const group = groups[groupIndex];
    if (!group) {
      showToast("Regelgruppe nicht gefunden");
      return;
    }
    const condition = conditionInput.value.trim();
    const message = normalizeMessage(messageInput.value);
    if (!condition || !message) {
      showToast("Bedingung und Fehlermeldung fehlen");
      return;
    }

    group.rules = group.rules || [];
    const oldRules = deepClone(group.rules);
    const rule = {
      id: generatedId("rule"),
      number: group.rules.length + 1,
      condition,
      message,
      messageLanguage: state.uiLanguage,
      dimension: dimensionSelect.value || defaultDimensionForRuleType(typeSelect.value || "custom"),
      ruleType: typeSelect.value || "custom",
      active: Boolean(activeInput.checked),
    };
    group.rules.push(rule);
    renumberRules(group);
    state.expandedGroups.add(groupKey(group, groupIndex));
    state.selectedRuleRef = ruleSelectionKey(group, groupIndex, group.rules.length - 1);
    markEditorDirty();
    recalculateEditorModel();
    renderEditorModel();
    await persistGroupRulesChange(group, groupIndex, "rule_create", `${groupTitle(group)} · Regel angelegt`, oldRules, deepClone(group.rules));
  });

  elements.ruleDetail.append(panel);
  conditionInput.focus();
}

function catalogDimensions() {
  return state.ruleCatalog.dimensions?.length
    ? state.ruleCatalog.dimensions
    : [
      "Vollständigkeit",
      "Validität",
      "Korrektheit",
      "Eindeutigkeit",
      "Konsistenz",
      "Aktualität",
      "Genauigkeit",
      "Redundanz",
      "Einheitlichkeit",
      "Relevanz",
      "Zuverlässigkeit",
      "Verständlichkeit",
    ];
}

function catalogRuleTypes() {
  const ruleTypes = state.ruleCatalog.ruleTypes || [];
  return ruleTypes.length ? ruleTypes : [{ id: "custom", label: "Sonderregel", defaultDimension: "Korrektheit" }];
}

function findRuleType(ruleTypeId) {
  return catalogRuleTypes().find((ruleType) => ruleType.id === ruleTypeId);
}

function defaultDimensionForRuleType(ruleTypeId) {
  return findRuleType(ruleTypeId)?.defaultDimension || "Korrektheit";
}

function fieldExpression(group) {
  return String(groupInternalName(group) || "FIELD_NAME").trim() || "FIELD_NAME";
}

function defaultConditionForRuleType(group, ruleTypeId) {
  const field = fieldExpression(group);
  switch (ruleTypeId) {
    case "completeness":
      return `${field} IS NULL OR TRIM(${field}) = ''`;
    case "trim_whitespace":
      return `${field} <> TRIM(${field})`;
    case "min_length":
      return `LENGTH(TRIM(${field})) < 2`;
    case "max_length":
      return `LENGTH(${field}) > 100`;
    case "regex":
      return `NOT (${field} LIKE_REGEXPR '^[[:alnum:] ._/-]+$' FLAG 'i')`;
    case "missing_letters":
      return `NOT (${field} LIKE_REGEXPR '[[:alpha:]]' FLAG 'i')`;
    case "obsolete_terms":
      return `${field} LIKE_REGEXPR '(test|dummy|obsolete)' FLAG 'i'`;
    case "mixed_umlaut_spelling":
      return `${field} LIKE_REGEXPR '(ä|ö|ü|ß|ae|oe|ue|ss)' FLAG 'i'`;
    case "legal_form_normalization":
      return `${field} LIKE_REGEXPR '(Gmbh|G.M.B.H.|AG\\.)' FLAG 'i'`;
    default:
      return `${field} IS NULL`;
  }
}

function defaultMessageForRuleType(group, ruleTypeId) {
  const label = group?.description || group?.field || (state.uiLanguage === "en" ? "Field" : "Feld");
  const messages = state.uiLanguage === "en" ? {
    completeness: `${label}: Empty`,
    trim_whitespace: `${label}: Invalid whitespace`,
    min_length: `${label}: Too short`,
    max_length: `${label}: Too long`,
    regex: `${label}: Invalid characters`,
    missing_letters: `${label}: No letters`,
    obsolete_terms: `${label}: Obsolete`,
    mixed_umlaut_spelling: `${label}: Inconsistent umlaut spelling`,
    legal_form_normalization: `${label}: Inconsistent legal form`,
  } : {
    completeness: `${label}: Leer`,
    trim_whitespace: `${label}: Ungültige Leerzeichen`,
    min_length: `${label}: Zu kurz`,
    max_length: `${label}: Zu lang`,
    regex: `${label}: Ungültige Zeichen`,
    missing_letters: `${label}: Keine Buchstaben`,
    obsolete_terms: `${label}: Obsolet`,
    mixed_umlaut_spelling: `${label}: Uneinheitliche Umlaut-/ß-Schreibweise`,
    legal_form_normalization: `${label}: Uneinheitliche Rechtsform`,
  };
  return messages[ruleTypeId] || `${label}: ${state.uiLanguage === "en" ? "Check" : "Prüfung"}`;
}

function generatedId(prefix) {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function stripMessagePipe(value) {
  return String(value || "").replace(/^\s*\|+\s*/, "");
}

function normalizeMessage(value) {
  return stripMessagePipe(value).trim();
}

function renumberGroups(groups = state.editorModel?.checks?.groups || []) {
  groups.forEach((group, index) => {
    group.number = index + 1;
    group.title = group.title || groupTitle(group);
    group.rules = group.rules || [];
    renumberRules(group);
  });
}

function renumberRules(group) {
  (group.rules || []).forEach((rule, index) => {
    rule.number = index + 1;
    rule.id = rule.id || generatedId("rule");
    rule.message = normalizeMessage(rule.message);
    rule.ruleType = rule.ruleType || "custom";
    rule.dimension = rule.dimension || defaultDimensionForRuleType(rule.ruleType);
    rule.active = Boolean(rule.active);
  });
}

async function moveRule(groupIndex, ruleIndex, direction) {
  const group = (state.editorModel?.checks?.groups || [])[groupIndex];
  const rules = group?.rules || [];
  const nextIndex = ruleIndex + direction;
  if (!group || nextIndex < 0 || nextIndex >= rules.length) {
    return;
  }
  const oldRules = deepClone(rules);
  const [rule] = rules.splice(ruleIndex, 1);
  rules.splice(nextIndex, 0, rule);
  renumberRules(group);
  state.selectedRuleRef = ruleSelectionKey(group, groupIndex, nextIndex);
  state.expandedGroups.add(groupKey(group, groupIndex));
  markEditorDirty();
  recalculateEditorModel();
  renderEditorModel();
  await persistGroupRulesChange(group, groupIndex, "rule_move", `${groupTitle(group)} · Regel verschoben`, oldRules, deepClone(group.rules));
}

async function deleteRule(groupIndex, ruleIndex) {
  const group = (state.editorModel?.checks?.groups || [])[groupIndex];
  const rules = group?.rules || [];
  const rule = rules[ruleIndex];
  if (!group || !rule) {
    return;
  }
  if (!window.confirm(`Regel "${rule.message || rule.ruleType || "ohne Namen"}" löschen?`)) {
    return;
  }
  const oldRules = deepClone(rules);
  rules.splice(ruleIndex, 1);
  renumberRules(group);
  state.selectedRuleRef = null;
  state.expandedGroups.add(groupKey(group, groupIndex));
  markEditorDirty();
  recalculateEditorModel();
  renderEditorModel();
  await persistGroupRulesChange(group, groupIndex, "rule_delete", `${groupTitle(group)} · Regel gelöscht`, oldRules, deepClone(group.rules));
}

async function toggleGroupActive(groupIndex, shouldActivate) {
  const group = (state.editorModel?.checks?.groups || [])[groupIndex];
  const rules = group?.rules || [];
  if (!group || !rules.length) {
    return;
  }
  const oldGroup = deepClone(group);
  if (shouldActivate) {
    const previousStates = Array.isArray(group.previousRuleActive) ? group.previousRuleActive : [];
    rules.forEach((rule, index) => {
      rule.active = previousStates.length ? Boolean(previousStates[index]) : true;
    });
    delete group.previousRuleActive;
  } else {
    group.previousRuleActive = rules.map((rule) => Boolean(rule.active));
    rules.forEach((rule) => {
      rule.active = false;
    });
  }
  state.expandedGroups.add(groupKey(group, groupIndex));
  markEditorDirty();
  recalculateEditorModel();
  renderEditorModel();
  await persistGroupChange(
    groupIndex,
    shouldActivate ? "group_activate" : "group_deactivate",
    `${groupTitle(group)} · ${shouldActivate ? "Regelgruppe aktiviert" : "Regelgruppe deaktiviert"}`,
    oldGroup,
    deepClone(group),
  );
}

async function moveGroup(groupIndex, direction) {
  const groups = state.editorModel?.checks?.groups || [];
  const nextIndex = groupIndex + direction;
  if (nextIndex < 0 || nextIndex >= groups.length) {
    return;
  }
  const oldGroups = deepClone(groups);
  const [group] = groups.splice(groupIndex, 1);
  groups.splice(nextIndex, 0, group);
  renumberGroups(groups);
  state.selectedRuleRef = null;
  state.expandedGroups = new Set([groupKey(group, nextIndex)]);
  markEditorDirty();
  recalculateEditorModel();
  renderEditorModel();
  await persistGroupsChange("group_move", `${groupTitle(group)} · Regelgruppe verschoben`, oldGroups, deepClone(groups));
}

async function deleteGroup(groupIndex) {
  const groups = state.editorModel?.checks?.groups || [];
  const group = groups[groupIndex];
  if (!group) {
    return;
  }
  const ruleCount = (group.rules || []).length;
  const prompt =
    `Regelgruppe "${groupTitle(group)}" mit ${ruleCount} ${ruleCount === 1 ? "Regel" : "Regeln"} entfernen?\n\n`
    + "Das Quellattribut bleibt erhalten.";
  if (!window.confirm(prompt)) {
    return;
  }
  const oldGroups = deepClone(groups);
  const removedKey = groupKey(group, groupIndex);
  groups.splice(groupIndex, 1);
  renumberGroups(groups);
  state.selectedRuleRef = null;
  state.expandedGroups.delete(removedKey);
  markEditorDirty();
  recalculateEditorModel();
  renderEditorModel();
  await persistGroupsChange(
    "group_delete",
    `${groupTitle(group)} · Regelgruppe entfernt`,
    oldGroups,
    deepClone(groups),
  );
}
function valuesEqual(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function ruleTargetPath(groupIndex, ruleIndex, field) {
  return `checks.groups.${groupIndex}.rules.${ruleIndex}.${field}`;
}

function ruleTargetLabel(group, rule, fieldLabel) {
  const ruleName = rule.message || rule.ruleType || "Regel";
  return `${groupTitle(group)} · ${ruleName} · ${fieldLabel}`;
}

async function persistRuleChange(group, groupIndex, rule, ruleIndex, field, fieldLabel, oldValue, newValue) {
  if (valuesEqual(oldValue, newValue) || !state.editorModel) {
    return;
  }
  recalculateEditorModel();
  await saveChangeLogEntry({
    changeType: `rule_${field}`,
    targetPath: ruleTargetPath(groupIndex, ruleIndex, field),
    targetLabel: ruleTargetLabel(group, rule, fieldLabel),
    oldValue,
    newValue,
  });
}

async function saveChangeLogEntry(change) {
  const report = state.selectedReport;
  if (!report || !state.editorModel || state.loggingChange) {
    return;
  }
  state.loggingChange = true;
  updateEditorButtons();
  try {
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/change-log`, {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        editorModel: state.editorModel,
        baseSqlHash: state.reportSqlHash,
        change,
      }),
    });
    applyEditorPersistencePayload(payload);
    showToast("Änderung protokolliert");
  } catch (error) {
    showToast(`Änderung nicht protokolliert: ${error.message}`);
  } finally {
    state.loggingChange = false;
    updateEditorButtons();
  }
}

function applyEditorPersistencePayload(payload) {
  state.editorModel = payload.editorModel || state.editorModel;
  if (state.editorModel) {
    state.originalEditorModel = deepClone(state.editorModel);
  }
  state.currentDraft = payload.draft || state.currentDraft;
  state.changeLog = payload.changes || payload.changeLog || state.changeLog || [];
  state.editorDirty = false;
  clearSqlPreview("Modell geändert - SQL-Vorschau neu erzeugen");
  renderEditorModel();
}

function renderChangeLog() {
  if (!elements.changeLogList || !elements.changeLogInfo) {
    return;
  }
  const changes = state.changeLog || [];
  const undoableCount = changes.filter((change) => !change.undoneAt).length;
  elements.changeLogList.replaceChildren();
  elements.changeLogInfo.textContent = changes.length
    ? `${changes.length} Änderungen · ${undoableCount} rückgängig möglich`
    : "Noch keine Änderungen";

  if (!changes.length) {
    elements.changeLogList.append(emptyNode("Noch keine Änderungen protokolliert"));
    return;
  }

  for (const change of changes.slice(0, 12)) {
    const item = document.createElement("div");
    item.className = `change-log-item ${change.undoneAt ? "undone" : ""}`;
    item.append(textBlock("strong", change.targetLabel || change.changeType || "Änderung"));
    item.append(textBlock("span", `${formatTimestamp(change.createdAt)} · ${change.undoneAt ? "rückgängig" : "aktiv"}`, "meta-line"));
    item.append(textBlock("span", `${formatChangeValue(change.oldValue)} → ${formatChangeValue(change.newValue)}`, "change-log-values"));
    elements.changeLogList.append(item);
  }
}

function formatChangeValue(value) {
  if (typeof value === "boolean") {
    return value ? "an" : "aus";
  }
  if (Array.isArray(value)) {
    return `${value.length} Einträge`;
  }
  if (value && typeof value === "object") {
    return "Objekt";
  }
  if (value === null || value === undefined || value === "") {
    return "leer";
  }
  const text = String(value).replace(/\s+/g, " ").trim();
  return text.length > 80 ? `${text.slice(0, 77)}...` : text;
}

async function undoLastChange() {
  const report = state.selectedReport;
  if (!report || !state.editorModel || state.undoingChange) {
    return;
  }
  state.undoingChange = true;
  updateEditorButtons();
  try {
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/change-log/undo`, {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        baseSqlHash: state.reportSqlHash,
      }),
    });
    applyEditorPersistencePayload(payload);
    showToast(`Rückgängig: ${payload.undoneChange?.targetLabel || "letzte Änderung"}`);
  } catch (error) {
    showToast(error.message);
  } finally {
    state.undoingChange = false;
    updateEditorButtons();
  }
}

async function restoreOriginalReport() {
  const report = state.selectedReport;
  if (!report || !state.editorModel || !state.baseline || state.restoringOriginal) {
    return;
  }
  const confirmed = window.confirm(
    "Ursprungsbericht wiederherstellen?\n\nDer aktuelle Draft wird ersetzt und die Wiederherstellung protokolliert. NEMO wird erst über 'In NEMO speichern' geändert."
  );
  if (!confirmed) {
    return;
  }

  state.restoringOriginal = true;
  updateEditorButtons();
  try {
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/restore-original`, {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        baseSqlHash: state.reportSqlHash,
      }),
    });
    state.baseline = payload.baseline || state.baseline;
    applyEditorPersistencePayload(payload);
    state.expandedGroups = new Set();
    state.selectedRuleRef = null;
    state.selectedBlockIndex = null;
    state.selectedContextItem = null;
    showToast("Ursprungsbericht wiederhergestellt");
  } catch (error) {
    showToast(error.message);
  } finally {
    state.restoringOriginal = false;
    updateEditorButtons();
  }
}
function markEditorDirty() {
  state.editorDirty = true;
  clearSqlPreview("Modell geändert - SQL-Vorschau neu erzeugen");
  updateEditorButtons();
}

function updateEditorButtons() {
  const hasReport = Boolean(state.selectedReport);
  const hasModel = Boolean(state.editorModel);
  const selectedBlock = state.selectedBlockIndex === null ? null : (state.editorModel?.blocks || [])[state.selectedBlockIndex];
  const checksContextActive = !selectedBlock || selectedBlock.id === "checks";
  const busy = state.loadingEditor || state.savingDraft || state.deletingDraft || state.generatingSql || state.exportingSql || state.writingToNemo || state.loggingChange || state.undoingChange || state.restoringOriginal || state.translatingMessages;
  elements.loadEditorBtn.disabled = !hasReport || busy;
  elements.validateEditorBtn.disabled = !hasReport || !hasModel || busy;
  elements.renderSqlBtn.disabled = !hasReport || !hasModel || busy;
  elements.exportSqlBtn.disabled = !hasReport || !hasModel || busy;
  elements.writeNemoBtn.disabled = !hasReport || !hasModel || !state.renderedSql || busy;
  elements.resetEditorBtn.disabled = !hasModel || !state.editorDirty || busy;
  elements.saveDraftBtn.disabled = !hasReport || !hasModel || !state.editorDirty || busy;
  elements.deleteDraftBtn.disabled = !hasReport || !state.currentDraft || busy;
  if (elements.addGroupBtn) {
    elements.addGroupBtn.disabled = !hasReport || !hasModel || !checksContextActive || busy;
  }
  if (elements.addRuleBtn) {
    elements.addRuleBtn.disabled = !hasReport || !hasModel || !checksContextActive || busy;
  }
  const hasUndoableChange = (state.changeLog || []).some((change) => !change.undoneAt);
  if (elements.undoChangeBtn) {
    elements.undoChangeBtn.disabled = !hasReport || !hasModel || !state.currentDraft || !hasUndoableChange || busy;
    elements.undoChangeBtn.textContent = state.undoingChange ? "Setzt zurück" : "Rückgängig";
  }
  if (elements.restoreOriginalBtn) {
    elements.restoreOriginalBtn.disabled = !hasReport || !hasModel || !state.baseline || busy;
    elements.restoreOriginalBtn.textContent = state.restoringOriginal ? "Wird wiederhergestellt" : "Ursprungsbericht wiederherstellen";
  }
  elements.saveDraftBtn.textContent = state.savingDraft ? "Speichert" : "Draft speichern";
  elements.deleteDraftBtn.textContent = state.deletingDraft ? "Verwirft" : "Draft verwerfen";
  elements.renderSqlBtn.textContent = state.generatingSql ? "Generiert" : "SQL-Vorschau";
  elements.exportSqlBtn.textContent = state.exportingSql ? "Exportiert" : "SQL exportieren";
  elements.writeNemoBtn.textContent = state.writingToNemo ? "Speichert" : "In NEMO speichern";
  if (state.loggingChange) {
    elements.saveDraftBtn.textContent = "Protokolliert";
  }
}

function recalculateEditorModel() {
  if (!state.editorModel) {
    return;
  }
  const groups = ensureChecks().groups || [];
  renumberGroups(groups);
  const rules = groups.flatMap((group) => group.rules || []);
  for (const group of groups) {
    const groupRules = group.rules || [];
    group.activeRules = groupRules.filter((rule) => Boolean(rule.active)).length;
    group.inactiveRules = groupRules.length - group.activeRules;
  }
  const dimensionCounts = {};
  for (const rule of rules) {
    const key = rule.dimension || "Ohne Dimension";
    dimensionCounts[key] = (dimensionCounts[key] || 0) + 1;
  }
  state.editorModel.summary = {
    ...(state.editorModel.summary || {}),
    checkGroupCount: groups.length,
    ruleCount: rules.length,
    activeRuleCount: rules.filter((rule) => Boolean(rule.active)).length,
    inactiveRuleCount: rules.filter((rule) => !Boolean(rule.active)).length,
    dimensionCounts,
  };
}

async function saveEditorDraft() {
  const report = state.selectedReport;
  if (!report || !state.editorModel || state.savingDraft) {
    return;
  }
  state.savingDraft = true;
  updateEditorButtons();
  try {
    recalculateEditorModel();
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/draft`, {
      method: "PUT",
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        editorModel: state.editorModel,
        baseSqlHash: state.reportSqlHash,
      }),
    });
    state.editorModel = payload.editorModel;
    state.originalEditorModel = deepClone(payload.editorModel);
    state.currentDraft = payload.draft || null;
    state.editorDirty = false;
    renderEditorModel();
    showToast("Draft gespeichert");
  } catch (error) {
    showToast(error.message);
  } finally {
    state.savingDraft = false;
    updateEditorButtons();
  }
}

async function deleteEditorDraft() {
  const report = state.selectedReport;
  if (!report || !state.currentDraft || state.deletingDraft) {
    return;
  }
  state.deletingDraft = true;
  updateEditorButtons();
  try {
    const params = new URLSearchParams({
      configId: state.configId,
      project: state.project,
    });
    await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/draft?${params.toString()}`, {
      method: "DELETE",
    });
    state.currentDraft = null;
    state.editorDirty = false;
    await loadEditorModel({ preferDraft: false });
    showToast("Draft verworfen");
  } catch (error) {
    showToast(error.message);
  } finally {
    state.deletingDraft = false;
    updateEditorButtons();
  }
}

function formatTimestamp(value) {
  if (!value) {
    return "gespeichert";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "gespeichert";
  }
  return date.toLocaleString(state.uiLanguage === "en" ? "en-GB" : "de-DE", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function ensureRuleMessageLanguages(model = state.editorModel) {
  for (const group of model?.checks?.groups || []) {
    for (const rule of group.rules || []) {
      rule.messageLanguage = rule.messageLanguage === "en" ? "en" : "de";
    }
  }
}

function reportMessageReferences(model) {
  const references = [];
  for (const group of model?.checks?.groups || []) {
    for (const rule of group.rules || []) {
      if (String(rule.message || "").trim()) references.push(rule);
    }
  }
  return references;
}

async function editorModelForReport() {
  const model = deepClone(state.editorModel);
  model.reportLanguage = state.reportLanguage;
  state.lastTranslationStats = { browserHits: 0, sqliteHits: 0, aiTranslations: 0 };
  const rules = reportMessageReferences(model).filter(
    (rule) => (rule.messageLanguage === "en" ? "en" : "de") !== state.reportLanguage,
  );
  if (!rules.length) return model;
  if (!state.aiConfigId) {
    throw new Error(state.uiLanguage === "en"
      ? "Configure an AI connection to translate report messages."
      : "Für die Übersetzung der Berichtsmeldungen muss ein KI-Zugang eingerichtet sein.");
  }

  const pendingByKey = new Map();
  rules.forEach((rule) => {
    const sourceLanguage = rule.messageLanguage === "en" ? "en" : "de";
    const key = `${state.aiConfigId}|${sourceLanguage}|${state.reportLanguage}|${rule.message}`;
    if (state.messageTranslationCache.has(key)) {
      rule.message = state.messageTranslationCache.get(key);
      state.lastTranslationStats.browserHits += 1;
      return;
    }
    if (pendingByKey.has(key)) {
      pendingByKey.get(key).rules.push(rule);
      return;
    }
    pendingByKey.set(key, {
      id: `message-${pendingByKey.size + 1}`,
      text: rule.message,
      sourceLanguage,
      key,
      rules: [rule],
    });
  });
  const pending = [...pendingByKey.values()];
  if (!pending.length) return model;

  const batchSize = 20;
  for (let offset = 0; offset < pending.length; offset += batchSize) {
    const batch = pending.slice(offset, offset + batchSize);
    const translatedBefore = Math.min(offset, pending.length);
    const progressText = `${state.uiLanguage === "en" ? "Translating messages" : "Übersetze Fehlermeldungen"} ${translatedBefore}/${pending.length}`;
    setStatus(progressText);
    showToast(progressText);
    const payload = await requestJson("/api/ai/messages/translate", {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        aiConfigId: state.aiConfigId,
        targetLanguage: state.reportLanguage,
        messages: batch.map(({ id, text, sourceLanguage }) => ({ id, text, sourceLanguage })),
      }),
    });
    state.lastTranslationStats.sqliteHits += Number(payload.cache?.hits || 0);
    state.lastTranslationStats.aiTranslations += Number(payload.cache?.misses || 0);
    const translations = new Map(
      (payload.translations || []).map((translation) => [String(translation.id), stripMessagePipe(translation.text || "")]),
    );
    for (const target of batch) {
      const translated = translations.get(target.id);
      if (!translated) continue;
      state.messageTranslationCache.set(target.key, translated);
      target.rules.forEach((rule) => { rule.message = translated; });
    }
  }
  return model;
}

async function prepareReportLanguage() {
  if (!state.editorModel || state.translatingMessages) return;
  state.translatingMessages = true;
  updateEditorButtons();
  try {
    await editorModelForReport();
    const stats = state.lastTranslationStats;
    const cached = stats.browserHits + stats.sqliteHits;
    showToast(state.uiLanguage === "en"
      ? `Report messages are ready (${cached} cached, ${stats.aiTranslations} translated by AI).`
      : `Berichtsfehlermeldungen sind vorbereitet (${cached} aus Cache, ${stats.aiTranslations} neu per KI).`);
  } catch (error) {
    setStatus("Fehler", "warn");
    showToast(error.message);
  } finally {
    state.translatingMessages = false;
    updateEditorButtons();
  }
}

async function renderGeneratedSql() {
  const report = state.selectedReport;
  if (!report || !state.editorModel || state.generatingSql) {
    return;
  }
  state.generatingSql = true;
  showSqlDetail();
  clearSqlPreview("SQL wird generiert");
  updateEditorButtons();
  setStatus("rendere");
  try {
    recalculateEditorModel();
    const reportModel = await editorModelForReport();
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/render-sql`, {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        editorModel: reportModel,
      }),
    });
    renderSqlPreview(payload);
    state.renderedReportLanguage = state.reportLanguage;
    setStatus("bereit", "ok");
    showToast(payload.changed ? "SQL-Vorschau generiert" : "SQL ist unverändert");
  } catch (error) {
    setStatus("Fehler", "warn");
    clearSqlPreview("SQL konnte nicht generiert werden");
    showToast(error.message);
  } finally {
    state.generatingSql = false;
    updateEditorButtons();
  }
}

async function exportGeneratedSql() {
  const report = state.selectedReport;
  if (!report || !state.editorModel || state.exportingSql) {
    return;
  }
  state.exportingSql = true;
  updateEditorButtons();
  setStatus("exportiere");
  try {
    recalculateEditorModel();
    const reportModel = await editorModelForReport();
    const response = await fetch(`/api/reports/${encodeURIComponent(reportRef(report))}/export-sql`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        editorModel: reportModel,
      }),
    });
    if (!response.ok) {
      throw new Error(await responseErrorMessage(response));
    }
    const blob = await response.blob();
    const filename = exportFileNameFromDisposition(response.headers.get("Content-Disposition")) || fallbackSqlFileName(report);
    downloadBlob(blob, filename);
    setStatus("bereit", "ok");
    showToast("SQL exportiert");
  } catch (error) {
    setStatus("Fehler", "warn");
    showToast(error.message);
  } finally {
    state.exportingSql = false;
    updateEditorButtons();
  }
}

async function writeGeneratedSqlToNemo() {
  let report = state.selectedReport;
  if (!report || !state.editorModel || !state.renderedSql || state.writingToNemo) {
    return;
  }
  if (state.renderedReportLanguage !== state.reportLanguage) {
    showToast(state.uiLanguage === "en" ? "Generate the SQL preview in the selected report language first." : "Bitte zuerst die SQL-Vorschau in der gewählten Berichtssprache erzeugen.");
    return;
  }
  try {
    report = await ensureFreshReportBeforeWrite(report);
  } catch (error) {
    setStatus("Fehler", "warn");
    showToast(error.message);
    return;
  }
  if (!report) {
    return;
  }

  const internalName = String(report.internalName || "").trim();
  if (!internalName) {
    showToast("Der Bericht hat keinen Internalname");
    return;
  }

  const config = activeConfig();
  const configLabel = config?.tenant || config?.name || state.configId || "-";
  const isTop25Report = /(?:\s+|_)top(?:\s+|_)25$/i.test(report.displayName || internalName);
  const top25Name = isTop25Report ? "" : `${report.displayName || internalName} TOP 25`;
  const affectedReports = isTop25Report
    ? `Bericht: ${report.displayName || internalName}`
    : `Berichte:\n- ${report.displayName || internalName}\n- ${top25Name}`;
  const confirmed = window.confirm(
    `Bericht in NEMO überschreiben?\n\nKonfiguration: ${configLabel}\nProjekt: ${state.project}\n${affectedReports}\nInternalname: ${internalName}\n\nDas bestehende SQL wird ersetzt. Der TOP-25-Bericht wird auf 25 Zeilen begrenzt und nach ErrorEvaluation absteigend sortiert.`,
  );
  if (!confirmed) {
    return;
  }

  state.writingToNemo = true;
  updateEditorButtons();
  setStatus("speichere");
  try {
    recalculateEditorModel();
    const reportModel = await editorModelForReport();
    const payload = await requestJson(`/api/reports/${encodeURIComponent(reportRef(report))}/write-to-nemo`, {
      method: "POST",
      body: JSON.stringify({
        configId: state.configId,
        project: state.project,
        editorModel: reportModel,
        overwriteConfirmation: internalName,
      }),
    });
    setStatus("bereit", "ok");
    const updatedCount = payload.updatedReports?.length || 1;
    showToast(`${updatedCount} ${updatedCount === 1 ? "Bericht" : "Berichte"} in NEMO aktualisiert`);
  } catch (error) {
    setStatus("Fehler", "warn");
    showToast(error.message);
  } finally {
    state.writingToNemo = false;
    updateEditorButtons();
  }
}

async function ensureFreshReportBeforeWrite(report) {
  const params = new URLSearchParams({
    configId: state.configId,
    project: state.project,
    deficienciesOnly: "true",
  });
  const payload = await requestJson(`/api/reports?${params.toString()}`);
  updateActiveConfigTenant(payload.configTenant);
  const reports = payload.reports || [];
  const currentRef = reportRef(report);
  const exactReport = reports.find((item) => reportRef(item) === currentRef);
  if (exactReport) {
    state.reports = reports;
    state.selectedReport = exactReport;
    applyReportFilter();
    setConnectionState("verbunden");
    return exactReport;
  }

  const internalName = String(report.internalName || "").trim().toLocaleLowerCase();
  const replacement = reports.find(
    (item) => String(item.internalName || "").trim().toLocaleLowerCase() === internalName,
  );
  if (!replacement) {
    throw new Error(`Bericht ist in der ausgewählten Konfiguration nicht vorhanden: ${report.internalName || currentRef}`);
  }

  const reloadConfirmed = !state.editorDirty || window.confirm(
    "Die ausgewählte Konfiguration hat sich geändert. Der Bericht muss vor dem Speichern neu geladen werden. Ungespeicherte Änderungen werden verworfen. Jetzt neu laden?",
  );
  if (!reloadConfirmed) {
    return null;
  }

  state.reports = reports;
  state.selectedReport = replacement;
  applyReportFilter();
  renderSelection();
  clearPreview();
  clearEditor("Bericht wird für die ausgewählte Konfiguration neu geladen");
  await loadEditorModel();
  showToast("Bericht wurde für die ausgewählte Konfiguration neu geladen. Bitte SQL-Vorschau erneut erzeugen.");
  return null;
}

async function responseErrorMessage(response) {
  const message = `${response.status} ${response.statusText}`;
  try {
    const payload = await response.json();
    const detail = apiDetailText(payload.detail) || message;
    const requestId = response.headers.get("X-Request-ID");
    return requestId && !detail.includes(requestId) ? `${detail} (Vorgang: ${requestId})` : detail;
  } catch (_) {
    return message;
  }
}

function apiDetailText(detail) {
  if (detail === null || detail === undefined) {
    return "";
  }
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map(apiDetailText).filter(Boolean).join("; ");
  }
  if (typeof detail === "object") {
    const location = Array.isArray(detail.loc) ? detail.loc.filter((item) => item !== "body").join(".") : "";
    const message = detail.message || detail.msg || detail.detail;
    if (message) {
      const text = apiDetailText(message);
      return location ? `${text} (${location})` : text;
    }
    try {
      return JSON.stringify(detail);
    } catch (_) {
      return "Unbekannter API-Fehler";
    }
  }
  return String(detail);
}

function exportFileNameFromDisposition(disposition) {
  const match = /filename="?([^";]+)"?/i.exec(disposition || "");
  return match ? match[1] : "";
}

function fallbackSqlFileName(report) {
  const baseName = report.internalName || report.displayName || report.id || "nemo_report";
  const safeName = String(baseName).replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^[._]+|[._]+$/g, "") || "nemo_report";
  return safeName.toLocaleLowerCase().endsWith(".sql") ? safeName : `${safeName}.sql`;
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
function renderSqlPreview(payload) {
  state.renderedSql = payload.sql || "";
  const previewSql = payload.sql || payload.generatedChecksSql || "";
  elements.sqlPreview.textContent = previewSql || "Kein SQL generiert";
  elements.sqlPreviewInfo.textContent = payload.changed ? "Vollständiges SQL generiert" : "Keine Änderung";
  showSqlDetail();
}

function clearSqlPreview(message = "Keine SQL-Vorschau") {
  state.renderedSql = null;
  state.renderedReportLanguage = null;
  if (elements.sqlPreview) {
    elements.sqlPreview.textContent = message;
  }
  if (elements.sqlPreviewInfo) {
    elements.sqlPreviewInfo.textContent = "Noch nicht generiert";
  }
}

async function validateEditedModel() {
  if (!state.editorModel) {
    return;
  }
  try {
    const payload = await requestJson("/api/editor-model/validate", {
      method: "POST",
      body: JSON.stringify({ editorModel: state.editorModel }),
    });
    state.editorModel = payload.editorModel;
    renderEditorModel();
    const findingCount = payload.validation?.findings?.length || 0;
    showToast(findingCount ? `${findingCount} Hinweise gefunden` : "Modell ist ohne Hinweise validiert");
  } catch (error) {
    showToast(error.message);
  }
}

function resetEditorModel() {
  if (!state.originalEditorModel) {
    return;
  }
  state.editorModel = deepClone(state.originalEditorModel);
  state.selectedRuleRef = null;
  state.selectedBlockIndex = null;
  state.selectedContextItem = null;
  state.editorDirty = false;
  clearSqlPreview("Noch keine SQL-Vorschau");
  renderEditorModel();
}

function deepClone(value) {
  if (typeof structuredClone === "function") {
    return structuredClone(value);
  }
  return JSON.parse(JSON.stringify(value));
}

function optionNode(value, text) {
  const option = document.createElement("option");
  option.value = value;
  option.textContent = text;
  return option;
}
function reportRef(report) {
  return report.internalName || report.id || report.displayName;
}

function bindEvents() {
  elements.sidebarToggleBtn.addEventListener("click", toggleSidebar);
  elements.uiLanguageSelect.addEventListener("change", () => {
    applyUiLanguage(elements.uiLanguageSelect.value);
    renderEditorModel();
  });
  elements.reportLanguageSelect.addEventListener("change", async () => {
    state.reportLanguage = elements.reportLanguageSelect.value === "en" ? "en" : "de";
    localStorage.setItem(REPORT_LANGUAGE_STORAGE_KEY, state.reportLanguage);
    clearSqlPreview(state.uiLanguage === "en" ? "Report language changed - generate SQL preview again" : "Berichtssprache geändert - SQL-Vorschau neu erzeugen");
    updateEditorButtons();
    await prepareReportLanguage();
  });
  elements.aiConfigBtn.addEventListener("click", openAiConfigDialog);
  elements.ruleTemplateCatalogBtn.addEventListener("click", openRuleTemplateCatalog);
  elements.closeRuleTemplateCatalogBtn.addEventListener("click", closeRuleTemplateCatalog);
  elements.cancelRuleTemplateCatalogBtn.addEventListener("click", closeRuleTemplateCatalog);
  elements.newRuleTemplateBtn.addEventListener("click", newRuleTemplate);
  elements.ruleTemplateCatalogDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeRuleTemplateCatalog();
  });
  elements.ruleTemplateForm.addEventListener("submit", saveRuleTemplate);
  elements.analyzeExistingRulesBtn.addEventListener("click", analyzeExistingRules);
  elements.importRuleTemplateCandidatesBtn.addEventListener("click", importRuleTemplateCandidates);
  elements.rejectRuleTemplateCandidateBtn.addEventListener("click", setSelectedRuleTemplateCandidateDecision);
  elements.importSingleRuleTemplateCandidateBtn.addEventListener("click", importSelectedRuleTemplateCandidate);
  elements.openCandidateTemplateBtn.addEventListener("click", openSelectedCandidateTemplate);
  elements.aiProviderInput.addEventListener("change", applyAiProviderPreset);
  elements.aiProfileSelect.addEventListener("change", () => {
    state.aiConfigId = elements.aiProfileSelect.value || null;
    if (state.aiConfigId) {
      localStorage.setItem(LAST_AI_CONFIG_STORAGE_KEY, state.aiConfigId);
    }
    const profile = state.aiConfigs.find((item) => item.id === state.aiConfigId);
    elements.aiConnectionState.textContent = profile ? `KI · ${profile.name}` : "KI nicht eingerichtet";
    showToast(profile ? `KI ${profile.name} ausgewählt` : "Keine KI ausgewählt");
  });
  elements.closeAiConfigDialogBtn.addEventListener("click", closeAiConfigDialog);
  elements.cancelAiConfigBtn.addEventListener("click", closeAiConfigDialog);
  elements.aiConfigDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeAiConfigDialog();
  });
  elements.aiConfigForm.addEventListener("submit", createAiConfigFromDialog);
  elements.standardModeBtn.addEventListener("click", async () => applyUiMode("standard"));
  elements.expertModeBtn.addEventListener("click", async () => applyUiMode("expert"));
  elements.themeSelect.addEventListener("change", () => applyTheme(elements.themeSelect.value));
  elements.addConfigBtn.addEventListener("click", openCreateConfigDialog);
  elements.editConfigBtn.addEventListener("click", openEditConfigDialog);
  elements.configStatisticsBtn.addEventListener("click", openConfigStatistics);
  elements.closeConfigDialogBtn.addEventListener("click", closeConfigDialog);
  elements.cancelConfigBtn.addEventListener("click", closeConfigDialog);
  elements.configDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeConfigDialog();
  });
  elements.configForm.addEventListener("submit", saveConfigFromDialog);
  elements.deleteConfigBtn.addEventListener("click", deleteConfigFromDialog);
  elements.configNameInput.addEventListener("input", () => {
    state.configNameAuto = false;
  });
  elements.configTenantInput.addEventListener("input", () => {
    if (!state.editingConfigId && state.configNameAuto) {
      elements.configNameInput.value = configNameFromTenant(elements.configTenantInput.value);
    }
  });
  elements.closeConfigStatisticsBtn.addEventListener("click", closeConfigStatistics);
  elements.closeConfigStatisticsActionBtn.addEventListener("click", closeConfigStatistics);
  elements.exportConfigStatisticsBtn.addEventListener("click", exportConfigStatistics);
  elements.configStatisticsDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeConfigStatistics();
  });
  elements.configSelect.addEventListener("change", async () => {
    state.configId = elements.configSelect.value;
    state.configStatistics = null;
    state.projectColumns = {};
    state.ruleTemplateAnalysis = null;
    state.selectedRuleTemplateCandidateKey = null;
    elements.ruleTemplateCandidateDetail.hidden = true;
    elements.ruleTemplateEditorPanel.hidden = false;
    elements.saveRuleTemplateBtn.hidden = false;
    renderRuleTemplateAnalysis();
    clearHarmonization("Konfiguration gewechselt - Harmonisierung neu laden");
    state.selectedReport = null;
    state.reports = [];
    state.filteredReports = [];
    clearPreview();
    clearEditor("Konfiguration gewechselt - Bericht wird neu geladen");
    renderReports();
    renderSelection();
    if (state.configId) {
      localStorage.setItem(LAST_CONFIG_STORAGE_KEY, state.configId);
    }
    await loadReports();
  });
  elements.searchInput.addEventListener("input", applyReportFilter);
  elements.refreshBtn.addEventListener("click", loadReports);
  elements.runBtn.addEventListener("click", runSelectedReport);
  elements.loadEditorBtn.addEventListener("click", loadEditorModel);
  elements.validateEditorBtn.addEventListener("click", validateEditedModel);
  elements.renderSqlBtn.addEventListener("click", renderGeneratedSql);
  elements.exportSqlBtn.addEventListener("click", exportGeneratedSql);
  elements.writeNemoBtn.addEventListener("click", writeGeneratedSqlToNemo);
  elements.resetEditorBtn.addEventListener("click", resetEditorModel);
  elements.saveDraftBtn.addEventListener("click", saveEditorDraft);
  elements.deleteDraftBtn.addEventListener("click", deleteEditorDraft);
  elements.undoChangeBtn?.addEventListener("click", undoLastChange);
  elements.restoreOriginalBtn?.addEventListener("click", restoreOriginalReport);
  elements.groupToggleBtn?.addEventListener("click", toggleAllGroups);
  elements.addGroupBtn?.addEventListener("click", openGroupWizard);
  elements.addRuleBtn?.addEventListener("click", () => openRuleWizard());
  elements.resultViewBtn.addEventListener("click", () => switchView("result"));
  elements.editorViewBtn.addEventListener("click", () => switchView("editor"));
  elements.harmonizationViewBtn.addEventListener("click", () => switchView("harmonization"));
  elements.refreshHarmonizationBtn.addEventListener("click", loadHarmonization);
  elements.harmonizationSearchInput.addEventListener("input", renderHarmonization);
}

async function boot() {
  bindEvents();
  state.reportLanguage = localStorage.getItem(REPORT_LANGUAGE_STORAGE_KEY) === "en" ? "en" : "de";
  elements.reportLanguageSelect.value = state.reportLanguage;
  applyUiLanguage(localStorage.getItem(UI_LANGUAGE_STORAGE_KEY) || "de");
  observeUiTranslations();
  applySidebarState(localStorage.getItem("nemo-sidebar-collapsed") === "1");
  await applyUiMode(localStorage.getItem(UI_MODE_STORAGE_KEY) || "standard");
  applyTheme(localStorage.getItem("nemo-theme") || "system");
  clearEditor();
  clearHarmonization();
  try {
    await loadBaseData();
  } catch (error) {
    setStatus("Fehler", "warn");
    setConnectionState("Fehler");
    showToast(error.message);
  }
}

boot();
