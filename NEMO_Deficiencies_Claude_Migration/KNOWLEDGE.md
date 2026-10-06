# Wissensbasis: NEMO Deficiencies

## Architektur

Das Projekt besteht aus einer lokalen Python-Webanwendung mit FastAPI-Backend und statischer Browseroberflaeche unter `backend/frontend`. Der Einstieg erfolgt ueber das Konsolenskript `nemo-deficiencies` aus `backend.cli:main` oder direkt ueber Uvicorn mit `backend.main:app`.

Wichtige Backend-Bereiche:

- `backend/main.py`: API-Endpunkte, Webauslieferung und zentrale App-Verdrahtung.
- `backend/cli.py`: Kommandozeilenstart.
- `backend/desktop.py`: Desktop-/Browserstartverhalten.
- `backend/services/config_store.py`: verschluesselte Config-Verwaltung.
- `backend/services/nemo_client.py`: NEMO-Kommunikation.
- `backend/services/sql_model.py`: internes Report-/Regelmodell.
- `backend/services/sql_generator.py`: SQL-Ausgabe aus dem Modell.
- `backend/services/report_service.py`, `report_utils.py`, `report_export.py`: Report laden/exportieren.
- `backend/services/config_statistics.py`: Statistik-/Harmonisierungsdaten.
- `backend/services/rule_catalog*.py`: Regelkatalog und Analyse.
- `backend/services/harmonization.py`: Vergleich gemeinsamer Felder.
- `backend/services/ai_*.py`: KI-Zugang, Connector, Config und Uebersetzungscache.
- `backend/services/rulebook_export.py`: im neueren Stand Regelwerksbericht als PDF/Excel.

Frontend:

- `backend/frontend/index.html`, `app.js`, `styles.css`
- zusaetzlich CLI-Wizard-Dateien `cli-wizard.html`, `cli-wizard.js`, `cli-wizard.css`

## Sicherheit und Laufzeitdaten

Die wichtigste Sicherheitsentscheidung: keine Klartext-Konfigurationen im Projekt. Konfigurationen, Zugangsdaten und API-Keys liegen verschluesselt in einer SQLite-Datenbank ausserhalb des Projekts:

```text
%LOCALAPPDATA%\NEMO Deficiencies\
```

Der Speicherort kann mit `--home` geaendert werden, soll aber privat und nicht versioniert bleiben.

Fruehere lokale Klartext-INIs und eine Entwicklungsdatenbank wurden nach sichtbarer Historie entfernt. Trotzdem besteht ein Restrisiko frueherer Git-Historie oder frueherer Online-Repositories. Deshalb gilt: alle damals verwendeten Zugangsdaten/API-Keys vorsorglich rotieren.

## Release und Distribution

Version `1.6.1` ist der aktuell dokumentierte Release. Vorhandene lokale Release-Dateien:

- `release\NEMO-Deficiencies-1.6.1-portable.zip`
- `release\nemo_deficiencies-1.6.1-py3-none-any.whl`
- `release\SHA256SUMS.txt`

Anwender sollen bevorzugt die Portable-Version nutzen. Python ist fuer Anwender nicht notwendig.

Release-Skript:

```powershell
.\scripts\publish-release.ps1 -Version 1.6.1
```

Optional lokal bauen:

```powershell
.\scripts\publish-release.ps1 -Version 1.6.1 -BuildLocal
```

Installer-Build:

```powershell
.\scripts\build-installer.ps1
```

## Tests und Verifikation

Dokumentierte Teststaende aus der Historie:

- Nach Adressen-/Namensregelarbeiten: 145 Tests bestanden.
- Nach Sicherheitsbereinigung: 164 Tests bestanden.
- Nach Regelwerksbericht: 167 Tests bestanden.

Diese Zahlen stammen aus frueheren Codex-Zusammenfassungen und muessen nach aktuellem Merge-/Arbeitsstand erneut verifiziert werden.

## Regelwerksbericht

Der Benutzer benoetigte einen kompakten Bericht ueber alle Berichte mit Prefix `(DEFICIENCIES)`, inklusive Bericht, Feld/Regelgruppe, Regeln, aktiv/inaktiv und Regeltyp, idealerweise als PDF.

Getroffene Umsetzung/Empfehlung:

- PDF als offizieller, gut lesbarer Bericht.
- Excel zusaetzlich fuer Filterung, Sortierung und Analyse.
- Standardmaessig TOP-25-Spiegelberichte ausschliessen, optional einschaltbar.
- Quelle waehlen: aktueller NEMO-Stand oder lokale Drafts.
- PDF enthaelt Kennzahlen, Bericht, Regelgruppe, Regel, Status, DQ-Typ, Regeltyp und Bedingung.
- Excel enthaelt Uebersichtsblatt, Statusgrafik und filterbare Regeldetailtabelle.

Technische Abhaengigkeiten im PRO-Stand:

- `openpyxl>=3.1,<4`
- `reportlab>=4.2,<5`

## Report-Editor-Funktionen

Der Editor kann:

- SQL-Bloecke grafisch darstellen.
- Datenqualitaetschecks bearbeiten.
- Regelgruppen und Regeln anlegen, bearbeiten, verschieben, aktivieren/deaktivieren und entfernen.
- Felder nach Displayname, Internalname, Importname und Description suchen.
- Displayname, Internalname und Beschreibung von Regelgruppen bearbeiten.
- SQL-Vorschau erzeugen.
- SQL mit Kopf, Datum, DQ-Kommentaren und Standardausgabe generieren.
- Drafts pro Config/Projekt/Report speichern.
- Aenderungsprotokoll und schrittweises Undo bereitstellen.
- Ursprungsbericht wiederherstellen.

## NEMO-Speicherung

Das Zurueckschreiben nach NEMO ist bestaetigungspflichtig. Schutzmechanismen:

- Schutz vor Speichern in falscher Config.
- Geschuetzte Standardberichte werden ueber kundenspezifische Varianten behandelt.
- TOP-25-Partner wird aktualisiert oder erzeugt.
- TOP-25-Ausgabe nutzt `SELECT TOP 25`.
- Sortierung erfolgt nach `ERROREVALUATION DESC`.
- Fehlerlogging nutzt eine Vorgangs-ID.

## KI-Unterstuetzung

Implementierte/angedachte Funktionen:

- Providerneutrale Schnittstelle.
- OpenAI-kompatible Anbieter und lokale Endpunkte.
- Groq als erster Anbieter.
- Globale statt Config-spezifische KI-Einstellungen.
- natuerlichsprachliche Regelerstellung.
- KI-Vorschlaege fuer neue Regelgruppen.
- Formeln erklaeren und pruefen.
- bestehende Bedingungen ueberarbeiten.
- Fehlermeldungen uebersetzen.
- SQLite-Cache fuer Uebersetzungen.

Offen:

- Kosten-, Token- und Laufzeituebersicht.
- Anbieterabhaengige Modellprofile und Fallback-Reihenfolge.

## Harmonisierung und Regelkatalog

Vorhanden:

- Harmonisierungsuebersicht gemeinsamer Felder.
- Vergleich von Regelanzahl und Aktivstatus je Report.
- Anzeige von Abweichungen in Felddetails.
- TOP-25-Berichte sind aus Harmonisierung ausgeschlossen.
- Grundstruktur fuer generische Regeln mit `{field}`.
- Regelkatalog und Kataloganalyse.

Offen:

- Bestehende Regeln vollstaendig in generische Katalogregeln ueberfuehren.
- Fachlich freigegebenen Standard je gemeinsames Feld definieren.
- Harmonisierung ueber mehrere NEMO-Projekte und Tenants.

## Master-Data-Berichte und fachlicher Stand

Aktuelle SQL-Dateien im Ordner `Master Data`:

- `(DEFICIENCIES) Adressen.sql`
- `(DEFICIENCIES) Kontakte.sql`
- `(DEFICIENCIES) Kunden.sql`
- `(DEFICIENCIES) Lieferanten.sql`
- `(DEFICIENCIES) Teile.sql`

Bearbeitungsreihenfolge laut Plan:

1. `(DEFICIENCIES) Adressen`
2. `(DEFICIENCIES) Contacts`
3. `(DEFICIENCIES) Customers`
4. `(DEFICIENCIES) Suppliers`
5. `(DEFICIENCIES) Parts`
6. weitere vorhandene `(DEFICIENCIES)`-Berichte

Hinweis: Plan verwendet teils deutsche Dateinamen und englische Berichtsnamen. Claude soll hier immer Originaldatei und Reportname pruefen, nicht aus dem Namen raten.

## Fachlicher Stand Adressen

Erledigt:

- Postleitzahlen-Regelgruppe geprueft.
- Falsche Laendergruppen korrigiert.
- Sonderformate fuer USA, Lettland, Venezuela, Kasachstan, Myanmar ergaenzt.
- Island nur noch dreistellig.
- Chile siebenstellig, Iran zehnstellig, Taiwan und Kambodscha sechsstellig.
- Postleitzahlenblock auf 29 aktive Regeln aktualisiert.
- Deutsche Fehlermeldungen auf Umlaute und `ss`/`ß` geprueft.
- Tippfehler `Obosolet` korrigiert.
- Ausgabeformat `Feld: Meldung` vereinheitlicht.
- Auch Meldungen deaktivierter Regeln bereinigt.
- Regelgruppe `Name 1-3` von `FULLNAME_T` auf Originalfelder umgestellt.
- `ADDRESS_NAME`, `ADDRESS_NAME2`, `ADDRESS_NAME3` werden direkt in Bedingungen geprueft.
- Hilfsspalte `FULLNAME_T` aus Quelle und Standardausgabe entfernt.
- `FULL_T` aus der Quellprojektion entfernt.
- Zusammengesetzte Detailinformationen werden direkt als `DESCRIPTION2` ausgegeben.
- Neue Quellattribute werden vom Generator automatisch an `DESCRIPTION2` angehaengt.
- Displayname eines neuen Feldes wird als Label der Detailausgabe verwendet.
- Erneutes Generieren erzeugt keine doppelten Quellfelder oder Detailwerte.
- `ADDRESS_STATE` wurde fachlich geprueft, Regeln bewusst inaktiv belassen.
- Gepruefte Felder im PRO-Plan: `ADDRESS_STREET`, `ADDRESS_STREET_NO`, `ADDRESS_SEARCH_TERM`, `ADDRESS_CITY`, `ADDRESS_COUNTRY`, `ADDRESS_STATE`, `ADDRESS_E_MAIL`, `ADDRESS_TELEPHONE`, `ADDRESS_U_R_L`.

Offen:

- `ADDRESS_STATE` in `DESCRIPTION2` ergaenzen.
- Entscheiden, ob `ADDRESS_I_D` trotz separater Ausgabe als `IDENTIFIER` zusaetzlich in `DESCRIPTION2` erscheinen soll.
- Mehrfeld-Regelgruppen im Modell unterstuetzen (`fields` statt nur `internalName`).
- Namensregeln im Editor einmalig als `{field}`-Vorlagen anzeigen.
- Aggregation je Regel festlegen: `ANY` fuer Fehler in mindestens einem Feld, `ALL` fuer gemeinsame Vollstaendigkeitspruefungen.
- SQL-Generator soll Mehrfeld-Vorlagen erst bei Ausgabe auf Originalfelder erweitern.
- Parser-Markierung ergaenzen, damit Mehrfeld-Regeln nach erneutem Laden kompakt bleiben.
- Aktuell ausgeschriebene Dreifachbedingungen spaeter durch Mehrfeld-Vorlagen ersetzen.
- Attribute und Quellprojektion vollstaendig pruefen.
- Uebrige Regelgruppen fachlich pruefen.
- Gemeinsame Adressfelder mit Contacts, Customers und Suppliers vergleichen.
- SQL-Generator-Diff pruefen.
- Gueltige und ungueltige Beispieldaten gegen kritische Regeln testen.

## Bekannte Fehlversuche oder Einschraenkungen

- Ein automatischer Hintergrundstart aus Codex heraus konnte Port `8000` nicht dauerhaft binden, weil die Agentenumgebung nicht in geschuetzte lokale Laufzeitdaten-/Logordner schreiben durfte. Empfehlung war Start im VS-Code-/Benutzerterminal mit `.\start.ps1`.
- Git-Historie konnte in einer frueheren Phase zeitweise nicht geprueft werden, weil `.git` fehlte beziehungsweise nicht erreichbar war. Aktuell ist `.git` wieder vorhanden, aber die alte Online-Historie bleibt als Risiko dokumentiert.
- OneDrive kann lokale Artefakte sperren oder nur als Platzhalter bereitstellen; bei Release-Dateien kann Hydration noetig sein.
