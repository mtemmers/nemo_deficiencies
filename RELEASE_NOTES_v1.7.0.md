# NEMO Deficiencies v1.7.0

## Deutsch

### Highlights

- Export nach **InfoZoom** (`.fox`-Datei über das InfoZoom-SDK, Windows-COM).
- Export nach **MSSQL** als T-SQL-Validierungsskript mit Tabellenerstellung und Inserts.
- Einheitliche Export-Connectoren (InfoZoom, JSON, MSSQL): Verfügbare Ziele werden automatisch erkannt und im Editor angeboten.
- **Regelwerksbericht** als PDF und Excel inklusive Regelgruppen, Regeln, Status und Regeltyp.
- **LiteLLM** als KI-Anbieter, inklusive Modellabruf, Projektauswahl und Fehlerprotokoll.
- Persistenter Übersetzungscache für Regelmeldungen: bereits übersetzte Meldungen stehen nach einem Neustart ohne erneuten KI-Aufruf zur Verfügung.

### Export

- Regel-Export als CSV mit Filteroptionen.
- InfoZoom-Export nutzt den SDK-Wrapper mit Fehlerbehandlung für fehlende SDK-Installation und Lizenzaktivierung.
- MSSQL-Export übersetzt NEMO-spezifische SQL-Funktionen und Bedingungen nach T-SQL und meldet nicht übersetzbare Ausdrücke als Warnung.
- Feldbezogene Regelausgaben werden über den Field-Cascader zusammengeführt.

### KI-Zugang

- LiteLLM-Profil mit Modellliste und Projekt-Dropdown.
- Fehler bei API-Aufrufen und Modellabrufen werden protokolliert.
- Setup-Anleitung `LITELLM_SETUP.md` und Hilfsskripte `litellm-restart.ps1` sowie `kill-port.ps1`.

### Portable

- Das portable ZIP benötigt weiterhin keine Python-Installation.
- Das ZIP enthält keine Konfigurationen, Datenbanken, Passwörter oder Schlüsseldateien.

## English

### Highlights

- Export to **InfoZoom** (`.fox` file via the InfoZoom SDK, Windows COM).
- Export to **MSSQL** as a T-SQL validation script with table creation and inserts.
- Unified export connectors: available targets (InfoZoom, JSON, MSSQL) are discovered automatically and offered in the editor.
- **Rulebook report** as PDF and Excel, including rule groups, rules, status, and rule type.
- **LiteLLM** as an AI provider, including model loading, project selection, and error logging.
- Persistent translation cache for rule messages: translated messages remain available after a restart without a new AI call.

### Export

- Rule export as CSV with filter options.
- InfoZoom export uses the SDK wrapper with error handling for a missing SDK and license activation.
- MSSQL export translates NEMO-specific SQL functions and conditions to T-SQL and reports untranslatable expressions as warnings.

### AI access

- LiteLLM profile with model list and project dropdown.
- Errors from API calls and model loading are logged.

### Portable package

- The portable ZIP still requires no separate Python installation.
- The ZIP contains no configurations, databases, passwords, or encryption keys.

## Verification

- 167 automated tests passed.
- Installer, portable ZIP and wheel built; portable package started and reports version `1.7.0`.
- No configurations, databases, passwords, or encryption keys in the portable ZIP.
