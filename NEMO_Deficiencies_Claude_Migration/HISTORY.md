# Projekthistorie

## Kompakte Chronologie

2026-07-08 bis 2026-07-10 - Ausgangspunkt CLI/NEMO-Reports - Projekt enthielt `nemo_import_export.py`, Struktur-SQL-Dateien und Master-Data-Reportdateien. Ziel war, `(DEFICIENCIES)`-Berichte aus `Master Data` lesen und auswerten zu koennen.

2026-07 bis 2026-08 - Ausbau zur lokalen Webanwendung - FastAPI-Backend, lokale Browseroberflaeche, Startskripte, Config-Auswahl, Reportauswahl, Editor-Grundlagen und SQL-Modell/Generator entstanden.

2026-08-10 - Release-Stand 1.6.1 - README, QUICKSTART, Release Notes und lokale Release-Artefakte dokumentieren Version `1.6.1`. Anwenderstart bevorzugt per Portable-ZIP ohne Python-Installation.

2026-08-10 - Sicherheitsbereinigung - Klartext-INIs, Entwicklungsdatenbanken, lokale Schluessel und alte Release-Artefakte wurden aus dem Projekt entfernt. Laufzeitdaten wurden verbindlich nach `%LOCALAPPDATA%\NEMO Deficiencies\` verlagert. Restrisiko frueherer Git-Historie wurde dokumentiert; Passwortrotation empfohlen.

2026-08 - GitHub-/Repository-Neustart - Der Benutzer wollte das fruehere Online-Repository loeschen und ein neues, oeffentliches Repository `mtemmers/nemo_deficiencies` anlegen. Ein bereinigter Initialstand wurde als Ziel genannt. Wichtig: alte veroeffentlichte Geheimnisse waeren trotz neuem Repo zu rotieren.

2026-08 - Regelwerksbericht geplant - Der Benutzer fragte nach einem kompakten Bericht fuer alle `(DEFICIENCIES)`-Berichte mit Bericht, Feld/Regelgruppe, Regeln, Status und Regeltyp. Empfehlung: PDF als offizieller Bericht plus Excel fuer Analyse.

2026-08 - Regelwerksbericht umgesetzt - Laut Codex-Zusammenfassung wurden PDF-/Excel-Downloads in Statistik/Regelwerksbericht umgesetzt, inklusive optionaler TOP-25-Spiegelberichte, Quelle NEMO oder Drafts, Tests und visueller PDF-Pruefung. Dokumentierter Teststand: 167 Tests bestanden. Aenderungen waren damals noch nicht committed.

2026-09-07 - PRO-CL00351-Arbeitsstand - Dateien mit Suffix `PRO-CL00351` und `rulebook_export.py` liegen im aktuellen Arbeitsbaum. Der Plan-Stand vom 07.09.2026 enthaelt den Regelwerksbericht als erledigt und listet neue offene fachliche Aufgaben fuer `(DEFICIENCIES) Adressen`.

2026-09 - Prefect-Cloud-Hinweis im selben Projektkontext - Ein separater kurzer Task behandelte Prefect Cloud API-Key/Workspace-Konfiguration (`migframework`). Das scheint kein Kernbestandteil von NEMO Deficiencies zu sein, ist aber im sichtbaren Projektkontext aufgetaucht. Nur relevant, falls spaeter Prefect-Automatisierung auftaucht.

2026-10-05 - Claude-Migration - Dieses Uebergabepaket wurde aus dem aktuellen Arbeitsordner, Projektdateien und sichtbaren Codex-Aufgabenzusammenfassungen erstellt. Vollstaendige ChatGPT-Projektchats waren nicht vollstaendig verfuegbar.

## Entwicklungslinie nach Themen

CLI zu Web-App:

- Start mit `nemo_import_export.py`.
- Erweiterung zu FastAPI-Webanwendung.
- Portable-/Installer-Fokus fuer Anwender ohne Python.

Sicherheit:

- Weg von lokalen INI-Dateien.
- Verschluesselte SQLite-Konfigurationen.
- Laufzeitdaten ausserhalb des Repositories.
- Sensible Daten nie in Git oder Releases.

Editor:

- SQL-Bloecke und Datenqualitaetsregeln grafisch bearbeiten.
- Drafts, Undo und Ursprungsbericht.
- Speichern nach NEMO inklusive TOP-25-Partner.

Fachliche Reportarbeit:

- Fokus auf Master-Data-Berichte.
- Aktueller Schwerpunkt `(DEFICIENCIES) Adressen`.
- Ziel: systematische Pruefung, Harmonisierung und generischer Regelkatalog.

Auswertung:

- Statistik/Harmonisierung vorhanden.
- Neu: vollstaendiger Regelwerksbericht als PDF/Excel.
