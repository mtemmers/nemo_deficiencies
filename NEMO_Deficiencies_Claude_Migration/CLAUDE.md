# Claude-Uebergabe: NEMO Deficiencies

## Projektname und Zweck

**NEMO Deficiencies** ist eine lokale Windows-/Python-Webanwendung zur grafischen Bearbeitung, Analyse und Ausgabe von NEMO-`(DEFICIENCIES)`-Berichten. Die Anwendung baut auf `nemo_library` auf und soll fachliche Datenqualitaetsregeln fuer Master-Data-Berichte sichtbar, editierbar, testbar und sicher nach NEMO zurueckschreibbar machen.

Das Projekt hat sich aus einem CLI-Import-/Export-Skript zu einer lokalen FastAPI-Webanwendung mit Browseroberflaeche, verschluesselter Konfigurationsverwaltung, Report-Editor, KI-Unterstuetzung, Harmonisierung, Regelkatalog und Exportfunktionen entwickelt.

## Rolle von Claude

Claude soll in diesem Projekt als technischer und fachlicher Entwicklungsassistent weiterarbeiten:

- vorhandenen Code und Dokumentation zuerst lesen, bevor Aenderungen umgesetzt werden
- kleine, nachvollziehbare Aenderungen bevorzugen
- bestehende Nutzerentscheidungen und Sicherheitsregeln respektieren
- keine bestehenden lokalen Aenderungen verwerfen
- bei fachlichen Report-Regeln vorsichtig vorgehen und Aenderungen vor groesserem Umbau begruenden
- Tests passend zur Aenderung ausfuehren oder klar dokumentieren, wenn Tests nicht moeglich waren

## Benutzer und Arbeitsweise

Der Benutzer arbeitet unter Windows mit Projekten in OneDrive-/proALPHA-Pfaden. Er bevorzugt praktische, direkt nutzbare Ergebnisse statt abstrakter Plaene. Bei Entwicklungsaufgaben soll Claude aktiv umsetzen, aber bei Releases, Git-Commits, Pushes, Loeschungen sensibler Daten oder fachlich weitreichenden Regelentscheidungen explizite Freigabe abwarten.

Wichtige Arbeitskonventionen:

- Verbindlicher Arbeitsbereich: `C:\Users\temmers_m\OneDrive - proALPHA Group\projekte\Dev\nemo_deficiencies`
- Aktuelle Master-Data-SQL-Dateien liegen im Ordner `Master Data`.
- Bestehende Aenderungen im Arbeitsverzeichnis nie ungefragt verwerfen.
- Git-Commit oder Push nur nach ausdruecklicher Freigabe.
- `(DEFICIENCIES) ... TOP 25` nicht als eigenstaendigen Quellbericht fachlich analysieren.
- TOP-25-Partnerberichte beim Speichern oder bei Ausgaben weiterhin beruecksichtigen.
- Zugangsdaten, API-Keys, SQLite-Datenbanken, Schluesseldateien und lokale Laufzeitdaten gehoeren nicht ins Projekt oder in Git.

## Technologien und Systeme

- Windows 10/11
- Python 3.11 oder 3.12
- FastAPI und Uvicorn
- lokale Browseroberflaeche auf `http://127.0.0.1:8000`
- `nemo_library==1.6.63`
- SQLite fuer lokale, verschluesselte Konfigurationsdaten
- `cryptography` fuer verschluesselte Secrets
- `requests`, `pandas`
- fuer den neueren Regelwerksbericht: `openpyxl>=3.1,<4` und `reportlab>=4.2,<5`
- PyInstaller/Inno Setup fuer Windows-Builds
- GitHub-Releases als Ziel fuer verteilbare Artefakte

Aktuelle App-Version laut Paket: `1.6.1`.

## Wichtige Begriffe

- **NEMO**: Zielsystem/Plattform fuer Berichte und Datenqualitaetsauswertungen.
- **`(DEFICIENCIES)`-Bericht**: Datenqualitaetsbericht, der im Editor analysiert und bearbeitet wird.
- **TOP-25-Bericht**: Spiegel-/Partnerbericht mit `SELECT TOP 25`, nicht als eigenstaendige fachliche Quelle behandeln.
- **Report-Editor**: Weboberflaeche zur grafischen Bearbeitung von Regelgruppen und Regeln.
- **Regelgruppe**: fachliche Gruppe zu einem Feld/Internalname.
- **Regel**: einzelne Datenqualitaetsbedingung mit Status, DQ-Typ, Regeltyp und Meldung.
- **Internalname**: technischer Feldname, z. B. `ADDRESS_Z_I_P_CODE`.
- **Displayname**: fachlich lesbarer Name einer Regelgruppe/eines Feldes.
- **Draft**: lokaler Entwurf pro Config, Projekt und Report.
- **Regelkatalog**: Ansatz fuer generische Regeln, u. a. mit `{field}`-Vorlagen.
- **Harmonisierung**: Vergleich gemeinsamer Felder und Regeln ueber mehrere Berichte.

## Weitere Dateien im Uebergabepaket

- `PROJECT_STATUS.md`: aktueller Stand, Entscheidungen, Probleme und naechste Schritte.
- `KNOWLEDGE.md`: konsolidierte Wissensbasis mit technischen und fachlichen Erkenntnissen.
- `HISTORY.md`: kompakte chronologische Projekthistorie.
- `OPEN_TASKS.md`: offene Aufgaben mit Kontext.
- `FILES.md`: relevante Dateien und Originalartefakte.
- `files/`: kopierter Projekt-Snapshot ohne Git-Historie, virtuelle Umgebung, Build-/Release-Artefakte oder lokale Laufzeitdaten.

## Wichtige Zugriffseinschraenkung

Dieses Paket wurde aus den lokal erreichbaren Projektdateien, sichtbaren Codex-Aufgabenzusammenfassungen und dem aktuellen Arbeitsordner erstellt. Vollstaendige ChatGPT-Projektchats ausserhalb der sichtbaren Codex-Zusammenfassungen waren nicht vollstaendig einsehbar. Wo Wissen nur aus Zusammenfassungen stammt oder nicht pruefbar war, ist es in den weiteren Dateien als unsicher oder eingeschraenkt gekennzeichnet.
