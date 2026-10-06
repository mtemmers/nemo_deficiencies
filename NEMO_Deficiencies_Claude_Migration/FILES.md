# Relevante Dateien und Artefakte

## Uebergabepaket

- `CLAUDE.md` - Einstieg fuer Claude mit Rolle, Regeln und Projektueberblick. Original fuer Migration erforderlich.
- `PROJECT_STATUS.md` - aktueller Projektstand, Entscheidungen und naechste Schritte. Original fuer Migration erforderlich.
- `KNOWLEDGE.md` - konsolidierte Wissensbasis. Original fuer Migration erforderlich.
- `HISTORY.md` - chronologische Projekthistorie. Original fuer Migration erforderlich.
- `OPEN_TASKS.md` - offene Aufgaben mit Kontext. Original fuer Migration erforderlich.
- `FILES.md` - Dateiverzeichnis und Uebertragungshinweise. Original fuer Migration erforderlich.
- `files/` - kopierter Projekt-Snapshot wichtiger Originaldateien.

## Projektwurzel

- `README.md` - Hauptdokumentation fuer Anwender, Installation, Release, Sicherheit. Fuer Claude wichtig.
- `README-PRO-CL00351.md` - paralleler/neuerer Dokumentationsstand. Fuer Claude wichtig, um PRO-Stand zu beurteilen.
- `QUICKSTART.md` - kompakter Anwenderstart und Sicherheitsregeln. Fuer Claude wichtig.
- `Plan.md` - zentrale Projektsteuerung und Aufgabenliste mit Stand 10.08.2026. Fuer Claude sehr wichtig.
- `Plan-PRO-CL00351.md` - neuerer/alternativer Planstand mit Regelwerksbericht und Stand 07.09.2026. Fuer Claude sehr wichtig.
- `RELEASE_NOTES_v1.6.1.md` - Release Notes fuer Version 1.6.1. Fuer Claude wichtig.
- `pyproject.toml` - Paket- und Abhaengigkeitsdefinition des Hauptstands. Fuer Claude wichtig.
- `pyproject-PRO-CL00351.toml` - PRO-Stand mit zusaetzlichen Exportabhaengigkeiten. Fuer Claude wichtig.
- `requirements.txt` - Runtime-Abhaengigkeiten Hauptstand. Fuer Claude wichtig.
- `requirements-PRO-CL00351.txt` - PRO-Stand mit `openpyxl`/`reportlab`. Fuer Claude wichtig.
- `requirements-build.txt` - Build-Abhaengigkeiten. Fuer Release/Build relevant.
- `nemo_deficiencies.spec` - PyInstaller-Spec. Fuer Build relevant.
- `nemo_deficiencies.code-workspace` - VS-Code-Workspace. Optional.
- `nemo_import_export.py` - urspruengliches/weiterhin enthaltenes CLI-Skript fuer Index-, SQL- und Datenexporte. Fuer Claude wichtig.
- `start.ps1`, `stop.ps1` - lokale Start-/Stoppskripte. Fuer Claude wichtig.
- `install-autostart.ps1`, `uninstall-autostart.ps1` - Autostart-Skripte. Fuer Betrieb relevant.
- `STRUCTURE.sql`, `structure_customer.sql` - Struktur-SQL-Dateien. Fachlich/technisch relevant.

## Backend

- `backend/__init__.py` - Paketversion, aktuell `1.6.1`.
- `backend/main.py` - zentrale FastAPI-App im Hauptstand.
- `backend/main-PRO-CL00351.py` - PRO-Variante; wichtig fuer Merge-Pruefung.
- `backend/cli.py` - Kommandozeilenstart.
- `backend/desktop.py` - Desktop-/Browserstart.
- `backend/logging_config.py` - Logging.
- `backend/services/*.py` - zentrale Services fuer Config, NEMO, SQL-Modell, Generator, Reports, KI, Harmonisierung und Regelkatalog.
- `backend/services/config_statistics-PRO-CL00351.py` - PRO-Variante der Statistiklogik.
- `backend/services/rulebook_export.py` - PDF-/Excel-Regelwerksbericht. Sehr wichtig fuer neuesten Stand.

## Frontend

- `backend/frontend/index.html`, `app.js`, `styles.css` - Hauptoberflaeche.
- `backend/frontend/index-PRO-CL00351.html`, `app-PRO-CL00351.js`, `styles-PRO-CL00351.css` - PRO-Varianten fuer Merge-Pruefung.
- `backend/frontend/cli-wizard.html`, `cli-wizard.js`, `cli-wizard.css` - CLI-Wizard fuer Exporte und Automatisierung.

## Tests

- `tests/*.py` - vorhandene Tests fuer API, Config, Editor-Stores, SQL-Modell/-Generator, Harmonisierung, KI, NEMO-Client, Frontend, Reportexport usw.
- `tests/test_frontend-PRO-CL00351.py` - PRO-Variante des Frontendtests.
- `tests/test_rulebook_export.py` - Tests fuer Regelwerksbericht. Sehr wichtig fuer neuesten Stand.

## Master-Data-SQL

Diese Dateien sind fachliche Arbeitsbasis und muessen Claude fuer weitere Reportarbeit vorliegen:

- `Master Data\(DEFICIENCIES) Adressen.sql`
- `Master Data\(DEFICIENCIES) Kontakte.sql`
- `Master Data\(DEFICIENCIES) Kunden.sql`
- `Master Data\(DEFICIENCIES) Lieferanten.sql`
- `Master Data\(DEFICIENCIES) Teile.sql`

## Konfiguration und Packaging

- `config\README.md` - Hinweis zur Konfigurationsablage; keine echten Secrets.
- `scripts\publish-release.ps1` - Release-Skript.
- `scripts\build-installer.ps1` - lokales Build-/Installer-Skript.
- `installer\nemo_deficiencies.iss` - Inno-Setup-Konfiguration.
- `.github\` - GitHub-Workflow-/Konfigurationsdateien, fuer Release-Automation relevant.

## Nicht in `files/` kopiert beziehungsweise separat behandeln

- `.git\` - Git-Historie wurde nicht ins Uebergabepaket kopiert. Muss separat ueber Repositoryzugriff/GitHub bereitgestellt werden, falls Claude Historie untersuchen soll.
- `.venv\`, `.pytest_cache\`, `__pycache__\`, `nemo_deficiencies.egg-info\` - lokale Entwicklungs-/Cache-Artefakte, nicht erforderlich.
- `build\`, `dist\` - Build-Artefakte, nicht erforderlich.
- `release\` - enthaelt grosse Release-Artefakte; nicht kopiert. Bei Bedarf separat uebergeben oder aus GitHub Release laden.
- `logs\` - lokale Logs, nicht kopiert; koennen sensible oder lokale Details enthalten.
- `%LOCALAPPDATA%\NEMO Deficiencies\` - aktive verschluesselte Laufzeitdatenbank, Schluessel und Logs. Nicht kopieren, ausser als bewusst geschuetztes Backup; enthaelt Zugangsdatenmaterial.
- Vollstaendige ChatGPT-Projektchats - waren in dieser Umgebung nicht vollstaendig exportiert/verfuegbar. Falls der Benutzer einen ChatGPT-Datenexport hat, sollte er ihn Claude separat geben.

## In diesem Paket kopierte Originaldateien

Der Unterordner `files/` soll einen Projekt-Snapshot enthalten mit:

- Projektdokumentation
- Python-Quellcode
- Frontend-Dateien
- Tests
- Master-Data-SQL-Dateien
- Scripts, Installer- und GitHub-Konfiguration
- PRO-CL00351-Arbeitsstand

Ausgeschlossen wurden bewusst lokale, schwere oder sensible Artefakte: Git-Historie, virtuelle Umgebung, Build-/Dist-/Release-Artefakte, Logs, Cache-Dateien und lokale Laufzeitdaten.
