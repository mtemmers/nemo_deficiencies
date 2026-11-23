# NEMO Deficiencies v1.7.1

## Deutsch

### Änderungen

- Die Export-Funktionen **SQL (MSSQL / T-SQL)**, **JSON** und **InfoZoom** sind aus der Anwendung entfernt.
- Entfernt sind außerdem der Endpunkt `/api/reports/{report_ref}/export-sql`, der Export-Endpunkt `/api/editor/{report_ref}/export` und `/api/export-connectors`.
- Vollständig entfernt wurde alles rund um das **InfoZoom SDK**: Connector, SDK-Wrapper (COM/pywin32), Feldzuordnung für InfoZoom, Regelübersetzungscache und Fehlerprotokoll (`backend/.cache`), die SDK-Installationsdateien und die zugehörige Dokumentation.
- Die Abhängigkeit `pywin32` wurde aus `requirements.txt` entfernt.
- Im Editor entfallen das Export-Menü und der MSSQL-Dialog.

### Unverändert

- SQL-Vorschau und **In NEMO speichern** (inklusive TOP-25-Bericht) bleiben erhalten.
- CSV-Export der Regeldetails, Regelwerksbericht (PDF/Excel), CLI-Wizard und KI-Übersetzungscache bleiben erhalten.

### Hinweis

Version 1.7.0 enthielt die entfernten Export-Funktionen. Wer 1.7.0 verwendet, sollte auf 1.7.1 aktualisieren.

## English

### Changes

- The export functions **SQL (MSSQL / T-SQL)**, **JSON**, and **InfoZoom** have been removed from the application.
- Also removed: the endpoints `/api/reports/{report_ref}/export-sql`, `/api/editor/{report_ref}/export`, and `/api/export-connectors`.
- Everything related to the **InfoZoom SDK** has been removed completely: connector, SDK wrapper (COM/pywin32), InfoZoom field cascader, rule translation cache and error log (`backend/.cache`), the SDK installation files, and the related documentation.
- The `pywin32` dependency has been removed from `requirements.txt`.
- The editor no longer shows the export menu or the MSSQL dialog.

### Unchanged

- SQL preview and **Save to NEMO** (including the TOP 25 report) remain available.
- CSV export of rule details, rulebook report (PDF/Excel), CLI wizard, and the AI translation cache remain available.

### Note

Version 1.7.0 contained the removed export functions. Users of 1.7.0 should update to 1.7.1.

## Verification

- 166 automated tests passed.
- Application imports and starts with 60 routes.
