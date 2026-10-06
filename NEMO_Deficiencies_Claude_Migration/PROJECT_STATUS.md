# Projektstatus: NEMO Deficiencies

Stand der Migration: 2026-10-05.

## Projektziel

Ziel ist eine lokale, sichere und anwenderfreundliche Python-/FastAPI-Webanwendung zur Bearbeitung von NEMO-`(DEFICIENCIES)`-Berichten. Anwender sollen Berichte grafisch analysieren, Regeln bearbeiten, Entwuerfe speichern, SQL erzeugen, Berichte nach NEMO zurueckschreiben, Regelwerke auswerten und Export-/Automatisierungsablaeufe ohne manuelle Klartext-Konfigurationsdateien nutzen koennen.

## Aktueller Stand

Die Anwendung ist als Version `1.6.1` dokumentiert und paketiert. Sie laeuft lokal auf Port `8000`, nutzt verschluesselte Konfigurationen unter `%LOCALAPPDATA%\NEMO Deficiencies\` und enthaelt eine Weboberflaeche fuer Config-Auswahl, Reportauswahl, Editor, CLI-Wizard, KI-Zugang, Statistik/Harmonisierung und Regelwerksausgaben.

Im aktuellen Arbeitsverzeichnis gibt es nicht committete beziehungsweise ungetrackte Dateien mit Suffix `PRO-CL00351` sowie neue Dateien fuer den Regelwerksbericht. Der Git-Status vor Erstellung dieses Uebergabepakets zeigte u. a.:

- `Plan-PRO-CL00351.md`
- `README-PRO-CL00351.md`
- `backend/frontend/app-PRO-CL00351.js`
- `backend/frontend/index-PRO-CL00351.html`
- `backend/frontend/styles-PRO-CL00351.css`
- `backend/main-PRO-CL00351.py`
- `backend/services/config_statistics-PRO-CL00351.py`
- `backend/services/rulebook_export.py`
- `pyproject-PRO-CL00351.toml`
- `requirements-PRO-CL00351.txt`
- `tests/test_frontend-PRO-CL00351.py`
- `tests/test_rulebook_export.py`

Die `PRO-CL00351`-Dateien scheinen einen neueren oder parallel gesicherten Arbeitsstand zu enthalten, insbesondere mit `openpyxl` und `reportlab` fuer PDF-/Excel-Regelwerksberichte. Die Hauptdateien `pyproject.toml` und `requirements.txt` enthalten diese Zusatzabhaengigkeiten im sichtbaren Stand noch nicht, waehrend `pyproject-PRO-CL00351.toml` und `requirements-PRO-CL00351.txt` sie enthalten.

## Bereits erledigte Arbeiten

- Lokale Python-/FastAPI-Webanwendung erstellt.
- Startskripte fuer PowerShell und Port `8000` vorhanden.
- Weboberflaeche mit Hell-/Dunkel-Darstellung, Standard-/Expertenmodus, Config-Auswahl und Reportauswahl.
- Konfigurationsdaten werden verschluesselt in SQLite gespeichert.
- Config-Anlage/-Bearbeitung/-Loeschung ueber die Weboberflaeche.
- Filter auf `(DEFICIENCIES)`-Berichte.
- Grafischer Report-Editor mit Regelgruppen, Regeln, Detailspalte, SQL-Vorschau, Drafts, Aenderungsprotokoll und Undo.
- Zurueckschreiben nach NEMO inklusive Schutz gegen falsche Config und Behandlung geschuetzter Standardberichte ueber kundenspezifische Varianten.
- TOP-25-Partnerberichte werden erzeugt/aktualisiert, mit `SELECT TOP 25` und Sortierung nach `ERROREVALUATION DESC`.
- Providerneutrale KI-Schnittstelle mit OpenAI-kompatiblen Cloud-/lokalen Anbietern, u. a. Groq, sowie Cache fuer Uebersetzungen.
- Harmonisierung gemeinsamer Felder und Grundstruktur fuer generische `{field}`-Regeln.
- Regelkatalog und Kataloganalyse.
- Sicherheitsbereinigung: Klartext-INIs, lokale Entwicklungsdatenbank, Entwicklungsschluessel und alte lokale Release-Artefakte wurden nach frueherem Codex-Stand entfernt.
- Release-Artefakte `1.6.1` liegen unter `release\`: portable ZIP, Wheel und `SHA256SUMS.txt`.
- Dokumentation `README.md`, `QUICKSTART.md`, `Plan.md` und `RELEASE_NOTES_v1.6.1.md` vorhanden.
- Regelwerksbericht wurde laut frueherem Codex-Task implementiert: PDF und Excel mit Bericht, Regelgruppe, Regel, Status, DQ-Typ, Regeltyp und Bedingung; optional TOP-25; Quelle NEMO-Stand oder Drafts.

## Getroffene Entscheidungen

- Portable-Version ist fuer Anwender der bevorzugte Einstieg.
- Laufzeitdaten liegen immer ausserhalb des Projekts unter `%LOCALAPPDATA%\NEMO Deficiencies\`.
- Zugangsdaten und API-Keys duerfen nicht in Projektdateien, Logs, Releases oder Git landen.
- `nemo_library==1.6.63` ist fest gepinnt.
- TOP-25-Berichte sind Spiegelberichte und werden fachlich nicht als eigene Quellberichte analysiert.
- Der CLI-Wizard ergaenzt automatisch den Tenant als Unterordner.
- Fuer offizielle Regelwerksausgaben ist PDF geeignet; Excel wird zusaetzlich fuer Analyse, Filterung und Weiterarbeit angeboten.
- Bei fachlicher Reportarbeit wird schrittweise gearbeitet: Ist-Zustand pruefen, Auffaelligkeiten dokumentieren, kleine Aenderung, Parser/Generator/Tests, Ergebnis dokumentieren, erst nach Freigabe weiter.

## Aktuell gueltige Konfigurationen und Einstellungen

- Paketversion: `1.6.1`
- Python: `>=3.11`, empfohlen 3.11/3.12
- Anwendung: `nemo-deficiencies` beziehungsweise `backend.main:app`
- Standardadresse: `http://127.0.0.1:8000`
- Laufzeitdaten: `%LOCALAPPDATA%\NEMO Deficiencies\`
- Master-Data-Arbeitsordner: `Master Data`
- Hauptabhaengigkeiten: FastAPI, Uvicorn, cryptography, requests, pandas, `nemo_library==1.6.63`
- Regelwerksbericht-Abhaengigkeiten im PRO-CL00351-Stand: `openpyxl>=3.1,<4`, `reportlab>=4.2,<5`

## Bekannte Probleme und Risiken

- Vollstaendige ChatGPT-Projekthistorie war nicht vollstaendig einsehbar. Dieses Paket enthaelt daher den rekonstruierbaren Wissensstand aus Projektdateien und sichtbaren Codex-Zusammenfassungen.
- Der aktuelle Arbeitsbaum enthaelt ungetrackte `PRO-CL00351`-Dateien und neue Exportdateien; Claude muss zuerst entscheiden, ob diese in die Hauptdateien integriert, als Vergleichsstand behalten oder verworfen werden sollen. Nicht ungefragt loeschen.
- In einem frueheren Task gab es Hinweise, dass alte Git-Historie frueher Config-Dateien enthalten haben koennte. Auch nach Bereinigung gilt: frueher verwendete Passwoerter/API-Keys vorsorglich rotieren.
- Ein Codex-Startversuch auf Port `8000` scheiterte in der Agentenumgebung wegen geschuetzter `%LOCALAPPDATA%`-Schreibrechte; Start im normalen Benutzerterminal per `.\start.ps1` war empfohlen.
- OneDrive kann Dateien sperren oder als Platzhalter bereitstellen; bei Build-/Release-Pruefungen auf Hydration und Locks achten.

## Offene Punkte

Siehe `OPEN_TASKS.md` fuer die ausfuehrliche Liste. Wichtigste naechste Punkte:

- `PRO-CL00351`-Stand konsolidieren: Regelwerksbericht-Abhaengigkeiten und Quell-/Testdateien sauber in Hauptstand uebernehmen oder bewusst separieren.
- Vollstaendigen Testlauf ausfuehren und aktuelle Testanzahl dokumentieren.
- Master-Data-Berichte systematisch inventarisieren und parser-/generatorseitig pruefen.
- Aktueller fachlicher Fokus: `(DEFICIENCIES) Adressen`, u. a. `ADDRESS_STATE` in `DESCRIPTION2`, Entscheidung zu `ADDRESS_I_D`, Mehrfeld-Regelgruppen.
- Bestehende Regeln in generische Katalogregeln ueberfuehren und Standards je gemeinsames Feld fachlich freigeben.
- Zugangsdatenrotation bestaetigen, falls alte Geheimnisse jemals in Git/Online-Repositories waren.

## Naechste sinnvolle Schritte

1. Git-Status und Datei-Diff zwischen Hauptdateien und `PRO-CL00351`-Dateien pruefen.
2. Entscheiden, welcher Stand als aktiv gilt.
3. Falls Regelwerksbericht aktiv werden soll: `openpyxl` und `reportlab` in `pyproject.toml`/`requirements.txt` uebernehmen und Hauptdateien aus PRO-Stand mergen.
4. Tests ausfuehren, mindestens die betroffenen Frontend-, API-, Statistik- und Exporttests; wenn moeglich komplette Suite.
5. `Plan.md` aktualisieren und danach erst ueber Commit/Release sprechen.

## Wichtige Abhaengigkeiten

- Zugriff auf `nemo_library==1.6.63`
- NEMO-Zugangsdaten lokal verschluesselt, nicht im Projekt
- Windows-Dateisystem und `%LOCALAPPDATA%`
- Optional GitHub fuer Releases
- Optional Inno Setup fuer Installer
- Optional KI-Anbieter/API-Key oder lokaler OpenAI-kompatibler Endpoint
