# Plan: Von CLI zu lokaler Python/Web-Anwendung

## Aktuelle Projektsteuerung

Stand: 10.08.2026

Diese Datei ist ab jetzt gleichzeitig:

- Gesamtplan der Anwendung
- priorisierte Aufgabenliste
- Dokumentation der erledigten Arbeitsschritte
- Grundlage für die Entscheidung über den jeweils nächsten Schritt

### Verbindlicher Arbeitsbereich

Es wird ausschließlich in diesem Projekt gearbeitet:

`C:\Users\temmers_m\OneDrive - proALPHA Group\projekte\Dev\nemo_deficiencies`

Die aktuellen Report-SQL-Dateien liegen im Ordner `Master Data`.

Für die fachliche Analyse gelten diese Regeln:

- `(DEFICIENCIES) ... TOP 25` wird nicht als eigenständiger Quellbericht analysiert.
- Der zugehörige TOP-25-Bericht wird beim Speichern beziehungsweise bei der Ausgabe weiterhin berücksichtigt.
- Bestehende Änderungen im Arbeitsverzeichnis werden nicht verworfen.
- Ein Git-Commit oder Push erfolgt nur nach ausdrücklicher Freigabe.

### Arbeitsweise für jeden weiteren Schritt

Jede Aufgabe wird in derselben Reihenfolge bearbeitet:

1. Aufgabe und betroffene Reports festlegen.
2. Ist-Zustand und bestehende Änderungen prüfen.
3. Fachliche und technische Auffälligkeiten dokumentieren.
4. Änderung möglichst klein und nachvollziehbar umsetzen.
5. Parser, Generator und passende Tests ausführen.
6. Ergebnis und noch offene Punkte in dieser Datei ergänzen.
7. Erst nach fachlicher Freigabe mit dem nächsten Themenblock fortfahren.
8. Git-Sicherung und Veröffentlichung nur auf Anweisung durchführen.

## Aktueller Gesamtstand

### Anwendungsbasis

- [x] Lokale Python-/FastAPI-Webanwendung
- [x] Start auf Port 8000 und PowerShell-Startskripte
- [x] Hell-/Dunkel-Darstellung entsprechend Browser beziehungsweise System
- [x] Standard- und Expertenmodus
- [x] Config-Auswahl und Speicherung der zuletzt verwendeten Config
- [x] Verschlüsselte Config-Daten in SQLite
- [x] Config-Anlage über die Oberfläche
- [x] NEMO-Projekt- und Reportauswahl
- [x] Ladeanzeige beim Öffnen eines Reports
- [x] Filter auf `(DEFICIENCIES)`-Berichte
- [x] Version 1.6.1 in Weboberfläche, CLI-Wizard und Health-API sichtbar
- [x] CLI-Exporte verwenden automatisch einen Tenant-Unterordner
- [x] Laufzeitdaten unabhängig von Startart unter `%LOCALAPPDATA%\NEMO Deficiencies`
- [x] Klartext-Konfigurationen und lokale Entwicklungsdatenbank aus dem Projekt entfernt
- [x] Alte lokale Release-Artefakte entfernt; nur Version 1.6.1 bleibt erhalten
- [ ] Git-Historie auf frühere Klartext-Konfigurationen prüfen und betroffene Zugangsdaten rotieren; lokal fehlen derzeit die `.git`-Metadaten

### Grafischer Report-Editor

- [x] Grafische Darstellung der SQL-Blöcke
- [x] Bearbeitung der Datenqualitätschecks
- [x] Regelgruppen anlegen, bearbeiten, verschieben, aktivieren und entfernen
- [x] Regeln anlegen, bearbeiten, verschieben, aktivieren und löschen
- [x] Dynamische Feldsuche über Displayname, Internalname, Importname und Description
- [x] Bearbeitbarer Displayname, Internalname und Beschreibung einer Regelgruppe
- [x] Kontextabhängige und beim Scrollen sichtbare rechte Detailspalte
- [x] Vollständige SQL-Vorschau
- [x] SQL-Generator mit Kopf, Datum, DQ-Kommentaren und Standardausgabe
- [x] Lokale Drafts pro Config, Projekt und Report
- [x] Persistentes Änderungsprotokoll und schrittweises Undo
- [x] Wiederherstellung des Ursprungsberichts

### NEMO-Speicherung

- [x] Bestätigtes Zurückschreiben eines Reports nach NEMO
- [x] Schutz vor Änderungen in der falschen Config
- [x] Behandlung geschützter Standardberichte über kundenspezifische Varianten
- [x] Aktualisierung beziehungsweise Erzeugung des zugehörigen TOP-25-Berichts
- [x] TOP-25-Ausgabe mit `SELECT TOP 25`
- [x] Sortierung nach `ERROREVALUATION DESC`
- [x] Fehlerlogging mit Vorgangs-ID

### KI-Unterstützung

- [x] Providerneutrale KI-Schnittstelle
- [x] Unterstützung OpenAI-kompatibler Anbieter und lokaler Endpunkte
- [x] Groq als erster Anbieter
- [x] Globale statt Config-spezifische KI-Einstellungen
- [x] Natürlichsprachliche Regelerstellung
- [x] KI-Vorschläge für neue Regelgruppen
- [x] Formeln erklären und prüfen
- [x] Bestehende Bedingungen mit KI überarbeiten
- [x] Übersetzung von Fehlermeldungen
- [x] SQLite-Cache für Übersetzungen
- [ ] Kosten-, Token- und Laufzeitübersicht
- [ ] Anbieterabhängige Modellprofile und Fallback-Reihenfolge

### Harmonisierung und Regelkatalog

- [x] Harmonisierungsübersicht gemeinsamer Felder
- [x] Vergleich von Regelanzahl und Aktivstatus je Report
- [x] Anzeige von Abweichungen in den Felddetails
- [x] TOP-25-Berichte aus der Harmonisierung ausgeschlossen
- [x] Grundstruktur für generische Regeln mit `{field}`
- [x] Regelkatalog und Kataloganalyse
- [ ] Bestehende Regeln vollständig in generische Katalogregeln überführen
- [ ] Fachlich freigegebenen Standard je gemeinsames Feld definieren
- [ ] Harmonisierung über mehrere NEMO-Projekte und Tenants

## Systematischer Plan für die aktuellen Master-Data-Berichte

Ziel ist ein nachvollziehbarer, fachlich geprüfter Ausgangsbestand. Die Berichte im Ordner `Master Data` gelten dafür als Arbeitsbasis.

### Stufe 1: Bestand und technische Grundprüfung

- [x] Aktuelle SQL-Dateien im Ordner `Master Data` identifiziert
- [x] TOP-25-Berichte von der eigenständigen Analyse ausgeschlossen
- [ ] Berichtsinventar mit Dateiname, Reportname, Sub-Type und Regelanzahl erstellen
- [ ] Alle Berichte mit dem Editor-Parser prüfen
- [ ] Doppelte, fehlende oder unbekannte Internalnames finden
- [ ] SQL-Generator-Roundtrip je Bericht prüfen
- [ ] Abweichungen zwischen Headerstatistik und tatsächlich erkannten Regeln finden

### Stufe 2: Berichtweise fachliche Prüfung

Die Berichte werden in dieser Reihenfolge bearbeitet:

1. `(DEFICIENCIES) Adressen`
2. `(DEFICIENCIES) Contacts`
3. `(DEFICIENCIES) Customers`
4. `(DEFICIENCIES) Suppliers`
5. `(DEFICIENCIES) Parts`
6. weitere vorhandene `(DEFICIENCIES)`-Berichte

Prüfpunkte je Bericht:

- Attribute und Master-Data-Quelle
- `MASTER_DATA_SUB_TYPE` und Ausnahmen
- Prozessrelevanz
- Join und prozessrelevante Daten
- Regelgruppen und verwendete Internalnames
- Bedingungen und HANA-Kompatibilität
- DQ-Typen
- Fehlermeldungen
- Standardausgabe
- TOP-25-Partner

### Stufe 3: Feldübergreifende Harmonisierung

- [ ] Gemeinsame Internalnames über alle Berichte gruppieren
- [ ] Displayname und Beschreibung je Feld vergleichen
- [ ] Regeln und Aktivstatus vergleichen
- [ ] Gewünschten Standard je Feld festlegen
- [ ] Standard in den Regelkatalog übernehmen
- [ ] Abweichende Reports kontrolliert an den Standard angleichen

### Stufe 4: Sprache und Benennung

- [ ] Deutsche Fehlermeldungen vollständig prüfen
- [ ] Englische Fehlermeldungen vollständig prüfen
- [ ] Einheitliches Muster `Feld: Fehlermeldung` durchsetzen
- [ ] Umlaute und `ß` in deutschen Ausgaben einheitlich verwenden
- [ ] Veraltete Ersatzschreibweisen wie `ae`, `oe` und `ue` entfernen
- [ ] Begriffe wie `Obsolet`, `Testwert`, `Ungültig` und `Leer` vereinheitlichen
- [ ] Übersetzungscache nach Änderungen gezielt aktualisieren

### Stufe 5: Abnahme und Verteilung

- [ ] Vollständigen automatisierten Testlauf ausführen
- [ ] SQL-Diff gegen den Ausgangsbestand prüfen
- [ ] Fachliche Stichproben mit gültigen und ungültigen Beispieldaten durchführen
- [ ] SQL zunächst in einer Test-Konfiguration nach NEMO schreiben
- [ ] Hauptbericht und TOP-25-Partner ausführen
- [ ] Ergebnisse fachlich freigeben
- [ ] Git-Commit und neue Version erstellen
- [ ] Freigegebene Berichte von der Testumgebung auf weitere Tenants spiegeln

## Aktueller Bericht: Adressen

- [x] Postleitzahlen-Regelgruppe geprüft
- [x] Falsche Ländergruppen korrigiert
- [x] Sonderformate für unter anderem USA, Lettland, Venezuela, Kasachstan und Myanmar ergänzt
- [x] Island nur noch dreistellig geprüft
- [x] Chile auf sieben, Iran auf zehn sowie Taiwan und Kambodscha auf sechs Stellen korrigiert
- [x] Postleitzahlenblock auf 29 aktive Regeln aktualisiert
- [x] Deutsche Fehlermeldungen auf Umlaute und `ß` geprüft
- [x] Tippfehler `Obosolet` korrigiert
- [x] Ausgabeformat `Feld: Meldung` vereinheitlicht
- [x] Auch Meldungen deaktivierter Regeln bereinigt
- [x] Parservalidierung erfolgreich
- [x] 19 Modell- und Generator-Tests erfolgreich
- [x] Regelgruppe `Name 1-3` von `FULLNAME_T` auf die Originalfelder umgestellt
- [x] `ADDRESS_NAME`, `ADDRESS_NAME2` und `ADDRESS_NAME3` werden direkt in den Bedingungen geprüft
- [x] Hilfsspalte `FULLNAME_T` aus Quelle und Standardausgabe entfernt
- [x] Parser- und Generator-Roundtrip der Namensregeln erfolgreich
- [x] `FULL_T` aus der Quellprojektion entfernt
- [x] Zusammengesetzte Detailinformationen werden direkt als `DESCRIPTION2` ausgegeben
- [x] Neue Quellattribute werden vom Generator automatisch an `DESCRIPTION2` angehängt
- [x] Displayname eines neuen Feldes wird als Label der Detailausgabe verwendet
- [x] Erneutes Generieren erzeugt weder doppelte Quellfelder noch doppelte Detailwerte
- [x] Vollständiger Testlauf mit 145 erfolgreichen Tests
- [x] Quellfelder gegen `DESCRIPTION2` abgeglichen
- [ ] `ADDRESS_STATE` in `DESCRIPTION2` ergänzen
- [ ] Entscheiden, ob `ADDRESS_I_D` trotz separater Ausgabe als `IDENTIFIER` zusätzlich in `DESCRIPTION2` erscheinen soll
- [ ] Mehrfeld-Regelgruppen im Modell unterstützen (`fields` statt nur `internalName`)
- [ ] Namensregeln im Editor einmalig als `{field}`-Vorlagen anzeigen
- [ ] Aggregation je Regel festlegen: `ANY` für Fehler in mindestens einem Feld, `ALL` für gemeinsame Vollständigkeitsprüfungen
- [ ] SQL-Generator erweitert Mehrfeld-Vorlagen erst bei der Ausgabe auf die drei Originalfelder
- [ ] Parser-Markierung ergänzen, damit Mehrfeld-Regeln nach erneutem Laden kompakt bleiben
- [ ] Die aktuell ausgeschriebenen Dreifachbedingungen anschließend durch Mehrfeld-Vorlagen ersetzen
- [ ] Attribute und Quellprojektion vollständig prüfen
- [ ] Alle übrigen Regelgruppen fachlich prüfen
- [ ] Gemeinsame Adressfelder mit Contacts, Customers und Suppliers vergleichen
- [ ] Bericht durch den SQL-Generator führen und Diff prüfen
- [ ] Gültige und ungültige Beispieldaten gegen kritische Regeln testen

### Feldweise fachliche Überarbeitung

Ziel je Feld:

1. Bestehende Regeln und Aktivstatus erfassen.
2. Regeln den DQ-Typen Vollständigkeit, Korrektheit, Einheitlichkeit und Aktualität zuordnen.
3. Doppelte, widersprüchliche oder zu unscharfe Prüfungen identifizieren.
4. Fehlende fachlich sinnvolle Prüfungen vorschlagen.
5. Positive und negative Beispiele festlegen.
6. Änderung erst nach fachlicher Freigabe umsetzen.
7. Regeln nach Möglichkeit in den generischen Regelkatalog übernehmen.
8. Parser, Generator und Tests ausführen.

Bearbeitungsreihenfolge:

- [x] `ADDRESS_NAME`, `ADDRESS_NAME2`, `ADDRESS_NAME3` - Name 1-3
- [ ] Mehrfeld-Vorlagen für Name 1-3 technisch umsetzen
- [x] `ADDRESS_Z_I_P_CODE` - Postleitzahl
- [x] `ADDRESS_STREET` - Straßenname
- [x] `ADDRESS_STREET_NO` - Hausnummer
- [x] `ADDRESS_SEARCH_TERM` - Suchbegriff
- [x] `ADDRESS_CITY` - Ort
- [x] `ADDRESS_COUNTRY` - Land
- [x] `ADDRESS_STATE` - Bundesland geprüft, Regeln bewusst inaktiv belassen
- [x] `ADDRESS_E_MAIL` - E-Mail
- [x] `ADDRESS_TELEPHONE` - Telefonnummer
- [x] `ADDRESS_U_R_L` - Website

#### Aktuelle Analyse: `ADDRESS_STREET`

Bestehender Stand: 13 Regeln, davon 12 aktiv und 1 inaktiv.

Vorläufige Bewertung:

- [x] Bestehende Regeln und Aktivstatus erfasst
- [x] Leerprüfung beibehalten
- [x] Prüfung auf fehlende Buchstaben beibehalten
- [x] Prüfung auf ungültige Zeichen beibehalten
- [x] Mindestlänge beibehalten
- [x] Führende und nachfolgende Leerzeichen dem DQ-Typ `Einheitlichkeit` zugeordnet
- [x] Mehrfache innere Leerzeichen als eigene Prüfung ergänzt
- [x] Doppelte Schrägstriche mit der allgemeinen Prüfung mehrfacher Sonderzeichen zusammengeführt
- [x] Fehlerhafte Regel `Drei aufeinanderfolgende Großbuchstaben` entfernt
- [x] Allgemeine Umlaut-/`ss`-Prüfung durch länderabhängige Regeln ersetzt
- [x] Für DE/AT `Straße` statt `Strasse` geprüft
- [x] Für CH `ss` statt `ß` geprüft
- [x] Abkürzungsprüfung `Str.` auf DE/AT begrenzt
- [x] Platzhalterwerte als Aktualitätsprüfung ergänzt
- [x] Keine pauschale Prüfung auf Hausnummern im Straßenfeld eingeführt
- [x] Straßenblock auf 14 aktive und 0 inaktive Regeln aktualisiert
- [x] Parser- und Generator-Roundtrip erfolgreich
- [x] Vollständiger Testlauf mit 145 erfolgreichen Tests

#### Aktuelle Analyse: `ADDRESS_STREET_NO`

Bestehender Stand: 10 Regeln, davon 9 aktiv und 1 inaktiv.

Vorläufige Bewertung:

- [x] Bestehende Regeln und Aktivstatus erfasst
- [x] Überschneidungen und Reihenfolge der Bedingungen geprüft
- [x] Internationale Hausnummernformate berücksichtigt
- [ ] Leerprüfung fachlich bestätigen; sie ist derzeit bewusst inaktiv
- [x] Leerzeichenprüfung von `Vollständigkeit` nach `Einheitlichkeit` verschieben
- [x] Spezifische Prüfungen vor die allgemeine Formatprüfung setzen
- [x] Allgemeines Format auf wiederholbare Zahlen-/Buchstaben-Segmente erweitern
- [ ] Kleinbuchstaben-Suffix und führende Nullen nur länderabhängig bewerten
- [ ] Feste Maximallänge `10` gegen die NEMO-Feldmetadaten prüfen
- [ ] Positive und negative Beispieldaten als Tests ergänzen

Festgestellte Probleme:

- `12//3` wird bereits als ungültiges Format erkannt; die genauere Meldung für mehrfache Separatoren ist nicht erreichbar.
- `12.3` wird bereits als ungültiges Format erkannt; die genauere Meldung für Punkte ist nicht erreichbar.
- `n.a.` wird bereits als Wert ohne Zahl erkannt; die genauere Aktualitätsmeldung ist nicht erreichbar.
- Führende und nachfolgende Leerzeichen sind ein Problem der Einheitlichkeit, nicht der Vollständigkeit.
- Das aktuelle Format ist für strukturierte internationale Werte wie `12A-14C` oder `12A/3` zu eng.
- Die feste Maximallänge kann gültige internationale Hausnummern ablehnen.

Empfohlener Zielstandard:

- Internationales Grundformat: `^\d+[A-Za-z]?([/\-]\d+[A-Za-z]?)*$`
- Gültige Beispiele: `12`, `12A`, `12-14`, `12A-14C`, `12/3`, `12A/3`
- Ungültige Beispiele: `12//3`, `12.3`, `ABC`, `n.a.`
- Länderspezifische Schreibweisen nur bei eindeutigem `ADDRESS_COUNTRY` prüfen.
- Eine optionale Querprüfung "Hausnummer steht im Straßenfeld" erst nach gesonderter fachlicher Entscheidung ergänzen.

#### Automatischer Durchlauf der verbleibenden Adressfelder

Umgesetzte eindeutige Korrekturen:

- `ADDRESS_SEARCH_TERM`: Die bisher wirkungslose Prüfung wurde zu einer echten Prüfung auf unzulässige Zeichen korrigiert.
- `ADDRESS_Z_I_P_CODE`: Rand-Leerzeichen korrekt dem DQ-Typ `Einheitlichkeit` zugeordnet.
- `ADDRESS_CITY`: Rand-Leerzeichen korrekt dem DQ-Typ `Einheitlichkeit` zugeordnet.
- `ADDRESS_COUNTRY`: Rand-Leerzeichen korrekt zugeordnet, Kleinbuchstaben vor der Strukturprüfung erkannt und ungültige ISO-2-Strukturen aktiviert.
- `ADDRESS_E_MAIL`: Rand-Leerzeichen korrekt zugeordnet, Prüfung auf doppelte Punkte repariert, numerische TLD vor die allgemeine Formatprüfung verschoben und einstellige lokale Namen sowie `+` zugelassen.
- `ADDRESS_TELEPHONE`: Rand-Leerzeichen korrekt zugeordnet, Längen nur anhand der Ziffern berechnet, Pluszeichen außerhalb des Anfangs erkannt und Testwert-Regulärausdruck repariert.
- `ADDRESS_U_R_L`: Rand-Leerzeichen korrekt zugeordnet, irreführenden RFC-Hinweis entfernt und innere Leerzeichen zuverlässig erkannt.

Bewusst übersprungen oder unverändert:

- `ADDRESS_STATE`: Alle Regeln bleiben inaktiv, weil die erwarteten Formate vom Land und vom Quellsystem abhängen; die pauschale Annahme von exakt drei Zeichen ist nicht sicher.
- `ADDRESS_CITY`: Groß-/Kleinschreibung und Umlauttransliteration bleiben unverändert, bis die gewünschte internationale Schreibweise festgelegt ist.
- `ADDRESS_COUNTRY`: Es wird die ISO-2-Struktur geprüft, aber noch keine vollständige Liste gültiger ISO-Ländercodes hinterlegt.
- `ADDRESS_STREET_NO`: Leerprüfung, maximale Länge, führende Nullen und Kleinbuchstaben-Suffix benötigen noch eine fachliche beziehungsweise länderspezifische Entscheidung.
- Pflichtstatus von E-Mail, Telefon und URL bleibt unverändert inaktiv.
- Feste Grenzwerte werden ohne Quellmetadaten nicht weiter verschärft.

Nicht als eigene DQ-Regelgruppen vorgesehen:

- `ADDRESS_I_D` bleibt technischer Identifier.
- `MASTER_DATA_SUB_TYPE` bleibt Quellfilter.
- `COMPANY` bleibt Kontextfeld, sofern keine eigene fachliche Anforderung entsteht.

## Arbeitsjournal

| Datum | Schritt | Ergebnis | Prüfung |
| --- | --- | --- | --- |
| 27.07.2026 | Aktuelle Master-Data-SQL als Arbeitsbasis festgelegt | TOP-25-Berichte werden nicht eigenständig analysiert | Ordner und Berichtsnamen geprüft |
| 27.07.2026 | Postleitzahlenblock in `(DEFICIENCIES) Adressen` analysiert | Mehrere falsche und veraltete Länderzuordnungen gefunden | Abgleich mit UPU und offiziellen Postquellen |
| 27.07.2026 | Postleitzahlenblock korrigiert | 29 aktive Regeln und länderspezifische Sonderformate | Parser erfolgreich, 19 Tests erfolgreich |
| 27.07.2026 | Deutsche Fehlerausgaben vereinheitlicht | Umlaute, `ß`, Doppelpunkte, Begriffe und Tippfehler korrigiert | Keine alten Ersatzschreibweisen gefunden, Parser erfolgreich |
| 27.07.2026 | Fortlaufende Projektsteuerung in `Plan.md` ergänzt | Arbeitsweise, Gesamtstand und nächste Stufen dokumentiert | Bestehende historische Planung beibehalten |
| 27.07.2026 | Regelgruppe `Name 1-3` auf Originalfelder umgestellt | `FULLNAME_T` entfernt; Regeln prüfen `ADDRESS_NAME`, `ADDRESS_NAME2` und `ADDRESS_NAME3` direkt | Parser und Generator-Roundtrip erfolgreich, 19 Tests erfolgreich |
| 27.07.2026 | Elegantere Modellierung der Namensregeln bewertet | Mehrfeld-Regelgruppe mit `{field}`-Vorlagen und `ANY`-/`ALL`-Aggregation als Ziel festgelegt | Umsetzung noch offen; ausgeschriebene Dreifachbedingungen sind ein Zwischenstand |
| 27.07.2026 | `FULL_T` in die Standardausgabe verschoben | Quelle enthält nur noch Originalattribute; `DESCRIPTION2` wird im finalen `SELECT` aufgebaut | Parser und SQL-Struktur erfolgreich |
| 27.07.2026 | Generator um dynamische Detailausgabe erweitert | Neue Felder werden mit Displayname und Wert automatisch in `DESCRIPTION2` ergänzt | Idempotenz-Roundtrip, JavaScript-Syntax und 145 Tests erfolgreich |
| 27.07.2026 | Quellprojektion mit `DESCRIPTION2` verglichen | 14 von 16 Feldern enthalten; `ADDRESS_STATE` und `ADDRESS_I_D` fehlen | `ADDRESS_I_D` wird separat als `IDENTIFIER` ausgegeben, `ADDRESS_STATE` derzeit nicht |
| 27.07.2026 | Feldweise Überarbeitung der Adressregeln begonnen | Feste Reihenfolge und einheitliches Prüfschema für alle Felder definiert | Name 1-3 und Postleitzahl als bearbeitet markiert |
| 27.07.2026 | `ADDRESS_STREET` erstbewertet | Überschneidungen, falscher Großbuchstaben-Regex und zu pauschale Sprachregeln gefunden | Noch keine SQL-Änderung; Länderstrategie ist offen |
| 27.07.2026 | `ADDRESS_STREET` bereinigt und länderabhängig erweitert | 14 aktive Regeln; DE/AT und CH getrennt, doppelte und fehlerhafte Prüfungen entfernt | Parser- und Generator-Roundtrip sowie 145 Tests erfolgreich |
| 27.07.2026 | `ADDRESS_STREET_NO` fachlich geprüft | Unerreichbare Detailregeln, falscher DQ-Typ und zu enges internationales Format gefunden | Noch keine SQL-Änderung; Leerprüfung und Länderstrategie sind offen |
| 27.07.2026 | Alle verbleibenden Adressfelder automatisch geprüft und eindeutig sichere Korrekturen gespeichert | Hausnummer, Suchbegriff, PLZ, Ort, Land, E-Mail, Telefon und URL verbessert; unsichere Bundesland- und Länderregeln übersprungen | Parser ohne Befund, Generator-Roundtrip erfolgreich und 145 Tests erfolgreich |
| 28.07.2026 | Falsch zugeordneten Editor-Draft behoben | Ein Adressenmodell war unter dem Kundenbericht gespeichert; fremde Drafts werden nun automatisch entfernt, fremde Modelle serverseitig abgelehnt und verspätete Browserantworten verworfen | JavaScript-Syntax, 147 Tests und realer API-Abruf erfolgreich; `deficiencies_customers` lädt wieder `customer_source` |
| 28.07.2026 | Windows-Installer und reproduzierbaren Releaseprozess fertiggestellt | PyInstaller-Desktop-Build, Inno-Setup, portables ZIP, Wheel, Prüfsummen, lokales Build-Skript und taggesteuerter GitHub-Release ergänzt; frühes Startprotokoll für installierte Versionen eingebaut | 148 Tests erfolgreich; portable EXE sowie echte Installation, Health-Check und Deinstallation erfolgreich; Entwicklungsserver auf Port 8000 wiederhergestellt |
| 29.07.2026 | DQ-Typ-Katalog auf zwölf Qualitätsdimensionen erweitert | Backend-Katalog, Parser, Validator, KI-Schema, Weboberfläche und englische SQL-Ausgabe um Validität, Eindeutigkeit, Konsistenz, Genauigkeit, Redundanz, Relevanz, Zuverlässigkeit und Verständlichkeit ergänzt | Katalogreihenfolge, neue Dimensionen und Übersetzungen durch Regressionstests abgesichert |
| 29.07.2026 | Native Dropdowns im Dark Mode korrigiert | Optionshintergrund, Textfarbe und Auswahlmarkierung an das Theme angepasst; CSS-Cachekennung erhöht | 28 Frontendtests erfolgreich; geladene CSS-Regeln und berechnete Dark-Mode-Farben im Browser verifiziert |
| 29.07.2026 | Aktuelle NEMO-Berichte gegen lokale Editor-Drafts abgesichert | Jeder Draft ist nun an den Fingerabdruck seines NEMO-Ausgangs-SQL gebunden. Nach einer externen Berichtsaktualisierung wird ein veralteter Draft archiviert, sein alter Undo-Verlauf deaktiviert und das aktuelle NEMO-SQL geladen; der unveränderliche Ursprungsbericht bleibt weiterhin wiederherstellbar | Realprüfung mit `deficiencies_suppliers`: statt 87 alten Regeln werden 139 aktuelle Regeln geladen; alle fünf Hauptberichte geprüft, 152 Tests erfolgreich |
| 29.07.2026 | Konfigurationsstatistik ergänzt | Statistikknopf neben der Konfigurationsauswahl lädt die aktuellen Hauptberichte ohne TOP 25 und zeigt Berichte, Regelgruppen, unterschiedliche Felder, Regeln sowie aktive und inaktive Regeln; Gesamt- und Berichtsverteilung werden grafisch dargestellt und die Detailtabelle kann als CSV exportiert werden | Reale Auswertung für zwei Konfigurationen, responsive Browserprüfung ohne Konsolenfehler und 154 Tests erfolgreich |
| 29.07.2026 | Portables Release `v1.4.0` erstellt | Versionsmetadaten aktualisiert; portables Windows-ZIP, Python-Wheel und SHA-256-Prüfsummen gebaut. Der Build wählt bei übersprungener Abhängigkeitsinstallation nun automatisch eine vollständig eingerichtete Python-Buildumgebung | 154 Tests erfolgreich; ZIP-Inhalt geprüft; portable EXE eigenständig gestartet und API-Version `1.4.0` bestätigt |
| 07.08.2026 | Separaten CLI-Wizard und portables Release `v1.5.0` erstellt | Neue Seite `/cli-wizard` erzeugt PowerShell-Aufrufe aus verschlüsselten Konfigurationen; alle Berichte eines Projekts können ohne Deficiency- oder TOP-25-Einschränkung gesucht und mehrfach ausgewählt werden; Hauptseite verlinkt den Wizard | 155 Tests erfolgreich; Portable-ZIP und Wheel gebaut; SHA-256 geprüft; Wizard-Assets im ZIP nachgewiesen; portable EXE mit API-Version `1.5.0`, Health-Check und Berichtsauswahl erfolgreich gestartet |
| 07.08.2026 | Portable-Bedienung für `v1.5.1` vereinfacht und Altprofil entfernt | SQL- und Datenexport können im CLI-Wizard direkt gestartet werden; Standardziel ist der Dokumente-Ordner, PowerShell bleibt nur als eingeklappte Experteninformation; `config_spitzer` wurde aus Entwicklungs- und Portable-Datenbank sowie als alte INI-Datei entfernt | 159 Tests erfolgreich; direkter API- und Browserexport eines echten GMT-Berichts ohne Browserfehler; ZIP ohne INI, SQLite oder Schlüssel; SHA-256 geprüft; Portable-EXE meldet Version `1.5.1` und stellt die direkte Export-Route bereit |
| 07.08.2026 | API-basierte PowerShell-Automatisierung und Portable `v1.5.2` fertiggestellt | Der Wizard erzeugt und lädt wiederverwendbare `.ps1`-Dateien herunter, die ohne Python und ohne Zugangsdaten die lokale Portable-API verwenden; README und Schnellstart beschreiben direkte und geplante Exporte | 159 Tests, JavaScript- und Python-Prüfung erfolgreich; ZIP ohne Config-, SQLite- oder Schlüsseldateien; SHA-256 geprüft; Portable-EXE mit API-Version `1.5.2`, Wizard und Automationsskript erfolgreich gestartet |
| 10.08.2026 | Vollständigen Konfigurationseditor und Portable `v1.6.0` fertiggestellt | Ausgewählte Profile können über die Oberfläche mit Name, Tenant, User-ID, Passwort, NEMO-URL und Environment bearbeitet oder gelöscht werden; Neuanlagen behalten die Produktivstandards; unbekannte INI-Zusatzfelder bleiben erhalten; Authentifizierungsfehler verweisen direkt auf den Editor | 162 Tests sowie Desktop- und Mobile-Browserprüfung erfolgreich; ZIP ohne sensible Laufzeitdateien; SHA-256 geprüft; Portable mit bestehender Datenbank gestartet und NextGen-Fehler als falsche URL, falsches Environment und abgelehnte Zugangsdaten bestätigt |
| 10.08.2026 | Sichtbare Versionskennung und tenantgetrennte CLI-Exporte als Portable `v1.6.1` fertiggestellt | Hauptseite und CLI-Wizard lesen die Version zentral aus der Health-API und zeigen sie in Kopfzeile und Fenstertitel; Browser- und PowerShell-Exporte schreiben automatisch unter `<Basisordner>\<Tenant>` | 164 Tests, JavaScript-/Python-Prüfung und Browserprüfung erfolgreich; ZIP ohne sensible Laufzeitdateien; SHA-256 geprüft; Portable `v1.6.1` auf Port 8000 gestartet |

## Nächster geplanter Schritt

Als Nächstes wird der überarbeitete Bericht mit echten Daten validiert:

1. Trefferzahlen je Regel vor und nach der Änderung vergleichen.
2. Stichproben für neue oder geänderte Treffer prüfen.
3. Übersprungene Entscheidungen zu Hausnummer, Ort, Land und Bundesland fachlich klären.
4. Freigegebene Regeln in den generischen Regelkatalog übernehmen.
5. Anschließend den nächsten Hauptbericht nach demselben Verfahren bearbeiten.

## Zielbild

Aus dem bestehenden CLI-Skript soll eine lokal laufende Web-Anwendung entstehen. Basis bleibt Python plus `nemo_library`.

Die Anwendung soll:

- mehrere NEMO-Konfigurationen verwalten
- Configdaten nicht mehr offen in `config.ini` speichern
- eine Konfiguration auswaehlbar machen
- NEMO-Projekte aus der Verbindung laden
- standardmaessig `Master Data` oder `Business Processes` anbieten
- nur Reports mit Praefix `(DEFICIENCIES)` anzeigen
- Reports ausfuehren und Ergebnisdaten anzeigen
- HANA-SQL-Reports grafisch bearbeiten koennen
- SQL aus einem Modell generieren, nicht als primaere Bearbeitungsoberflaeche zeigen
- Weboberflaeche automatisch an das Browser-Farbschema anpassen (Hell/Dunkel)

## Grundlage aus STRUCTURE.sql

`STRUCTURE.sql` beschreibt einen konkreten `(DEFICIENCIES)` Report fuer Lieferanten.

Wichtige Fakten aus der Datei:

- Report: `(DEFICIENCIES) Lieferanten`
- Master Data Typ: `SUPPLIER`
- Quelle: `$schema.$table`
- Prozessrelevanz: `$schema."pa_export"`
- CTE-Struktur:
  - `supp_src`: Master-Data-Quelle, Attribute, Hilfsfelder, Sub-Type-Filter, Ausnahmen
  - `proc_src`: prozessrelevante Lieferanten aus `pa_export`
  - `joined`: Inner Join zwischen Stammdaten und Prozessrelevanz
  - `checks`: Datenqualitaetsregeln, erzeugt `DEFICIENCY_DESCRIPTION`
  - finale Ausgabe: standardisierte DQM-Spalten
- Pruefgruppen: 16
- Regeln: 87 aktiv, 0 inaktiv
- Beispiele fuer Felder:
  - `ADDRESS_NAME`, `ADDRESS_NAME2`, `ADDRESS_NAME3`
  - `ADDRESS_STREET`, `ADDRESS_STREET_NO`
  - `ADDRESS_SEARCH_TERM`
  - `ADDRESS_Z_I_P_CODE`, `ADDRESS_CITY`, `ADDRESS_COUNTRY`
  - `ADDRESS_E_MAIL`, `ADDRESS_TELEPHONE`, `ADDRESS_U_R_L`
  - `SUPPLIER_SEARCH_TERM`, `SUPPLIER_INDUSTRY`
  - `SUPPLIER_CREDIT_TERMS_DESC`, `SUPPLIER_PAYMENT_METHOD`
  - `SUPPLIER_CREATION_DATE`, `SUPPLIER_CHANGE_DATE`
- Ausnahmen im Quellblock:
  - `SUPPLIER_I_D not in (...)`
- Finale Standardausgabe:
  - `RULENUMBER`
  - `RULENAME`
  - `RULEDESCRIPTION`
  - `ERROREVALUATION`
  - `AREA`
  - `RULEFIELD`
  - `IDENTIFIER`
  - `DESCRIPTION`
  - `DESCRIPTION2`
  - `CATEGORY`
  - `ANALYSISDATE`
  - `COMPANY`
  - `FIELDNAME`
  - `PERSON`
  - `STATUS`

Auffaelligkeit in `STRUCTURE.sql`:

- Im `checks` Block steht mehrfach `WHEN WHEN`.
- Viele `THEN` Ausgaben sind nur `'|'` statt sprechender Fehlermeldungen.

Daraus folgt: Die Web-App braucht nicht nur einen Editor, sondern auch eine Validierung und einen SQL-Generator, der syntaktisch sauberes HANA SQL erzeugt und fehlende Fehlermeldungen erkennt.

## Grundlage aus structure_customer.sql

`structure_customer.sql` beschreibt einen konkreten `(DEFICIENCIES)` Report fuer Kunden und erweitert die Supplier-Struktur um fachliche Qualitaetsdimensionen direkt in den Regelkommentaren.

Wichtige Fakten aus der Datei:

- Report: `(DEFICIENCIES) Kunden`
- Master Data Typ: `CUSTOMER`
- Source CTE: `customer_source`
- Prozess-CTE: `process_source`
- Join-CTE: `joined`
- Check-CTE: `checks`
- Pruefgruppen: 20
- Regeln: 156, davon 127 aktiv und 29 inaktiv
- Primaere Objekt-ID: `CUSTOMER_I_D`
- Standard-Prozessquelle: `$schema."pa_export"`

Zusaetzliche Kundengruppen gegenueber Supplier:

- `CUSTOMER_PRICE_GROUP`
- `CUSTOMER_CREATION_USER`
- `CUSTOMER_CHANGE_USER`
- `ADDRESS_STATE`

Wichtig fuer den grafischen Editor:

- Regeln tragen fachliche Dimensionen als Kommentar, z.B. `-- Vollständigkeit`, `-- Einheitlichkeit`, `-- Korrektheit`, `-- Aktualität`.
- Gruppenkommentare enthalten eine Typen-Zeile, z.B. `Typen: Vollständigkeit, Einheitlichkeit, Korrektheit, Aktualität`.
- Einige Regeln sind fachlich vorhanden, aber per leerem `THEN '' --'|...'` deaktiviert. Das sollte im Modell als `active = false` abgebildet werden, nicht als verlorene Regel.

## Fachliche Qualitaetsdimensionen

Aus `structure_customer.sql` ergeben sich mindestens diese DQ-Dimensionen:

| Dimension | Bedeutung in der UI | Beispiele |
| --- | --- | --- |
| `Vollständigkeit` | Pflichtfeld, leer, NULL, fehlender Benutzer | `TRIM(field) = ''`, `field IS NULL` |
| `Korrektheit` | Format, Regex, Laenge, Wertemenge, Datum | E-Mail-Format, PLZ-Muster, Datum in Zukunft |
| `Einheitlichkeit` | Schreibweise, Gross-/Kleinschreibung, Separatoren, Umlaute | `Str.` vs `Strasse`, doppelte Leerzeichen |
| `Aktualität` | obsolete/test/inaktive Werte, veraltete Datensaetze | `test`, `inactive`, `obsolete`, zu alte Daten |

Diese Dimensionen sollen im Rule Builder erstklassige Felder sein:

- Filter nach Dimension
- farbliche Kennzeichnung
- Auswertung pro Dimension
- Pflichtfeld bei jeder Regel
- Vorschlag aus Kommentar beim SQL-Import

## Empfohlene Zielarchitektur

```text
nemo-report-web/
├─ backend/
│  ├─ main.py                 # FastAPI App
│  ├─ services/
│  │  ├─ nemo_client.py        # Zugriff auf nemo_library
│  │  ├─ config_store.py       # Config-Profile + Verschluesselung
│  │  ├─ report_service.py     # Reports laden, ausfuehren, speichern
│  │  ├─ sql_model.py          # internes Report-/Blockmodell
│  │  ├─ sql_generator.py      # Modell -> HANA SQL
│  │  ├─ sql_validator.py      # Modell + SQL pruefen
│  │  └─ sql_importer.py       # optional: SQL -> Modell, soweit moeglich
│  ├─ db/
│  │  └─ app.db                # lokale SQLite DB
│  └─ requirements.txt
├─ frontend/
│  ├─ index.html
│  ├─ app.js
│  └─ styles.css
├─ data/
│  ├─ exports/
│  └─ logs/
├─ tests/
├─ README.md
└─ .gitignore
```

Fuer den Start reicht ein einfaches Frontend mit HTML/CSS/JavaScript. React/Vue kann spaeter kommen, wenn die fachlichen Masken stabil sind.

## Technische Basis

### Backend

Empfehlung: `FastAPI`

Gruende:

- sehr gut fuer lokale Webapps
- einfache API-Endpunkte
- gute OpenAPI-Dokumentation automatisch
- laesst sich spaeter auch als Service deployen

### Frontend

Startempfehlung: statische HTML-Seite mit JavaScript.

Gruende:

- weniger Setup-Aufwand
- schneller Prototyp
- gut genug fuer Tabellen, Formulare, Wizard und Preview

Spaeter moeglich:

- React fuer komplexeren Rule Builder
- Monaco Editor nur fuer optionale SQL-Vorschau, nicht als Haupteditor

### UI-Theme

Die Weboberflaeche soll sich an das Browser-/Betriebssystemschema anpassen:

- CSS ueber `prefers-color-scheme: light` und `prefers-color-scheme: dark`
- Farbwerte als CSS-Variablen, z.B. `--bg`, `--surface`, `--text`, `--border`, `--accent`
- optionaler manueller Umschalter `System`, `Hell`, `Dunkel`
- Tabellen, Formulare und SQL-Vorschau muessen in beiden Modi lesbar sein
- keine hart codierten Schwarz/Weiss-Flaechen in Komponenten

### Datenbank

Startempfehlung: SQLite lokal.

Zu speichern:

- Config-Profile
- verschluesselte Zugangsdaten
- gecachte Projektlisten
- gecachte Report-Metadaten
- Report-Drafts
- SQL-Editor-Modelle
- Regelvorlagen
- Wertelisten, z.B. erlaubte Branchen
- Regex-Bibliothek, z.B. PLZ, E-Mail, URL

## Config-Sicherheit

Ziel: keine sichtbaren Passwoerter mehr in `config.ini`.

Die `nemo_library` kann direkte Parameter nutzen:

```python
NemoLibrary(
    environment=...,
    tenant=...,
    userid=...,
    password=...
)
```

Dadurch muessen wir keine temporaere `.ini` Datei schreiben.

### Vorschlag A: SQLite + Feldverschluesselung

DB speichert:

```text
config_profiles
- id
- name
- environment
- tenant
- userid_encrypted
- password_encrypted
- created_at
- updated_at
```

Verschluesselung:

- Python `cryptography.Fernet`
- Master-Key nicht in der DB
- Master-Key z.B. in Windows Credential Manager ueber `keyring`

Vorteil:

- gut kontrollierbar
- wenige bewegliche Teile
- lokal stabil

Nachteil:

- App muss Key-Handling sauber machen

### Vorschlag B: SQLCipher

Die komplette SQLite-Datei wird verschluesselt.

Vorteil:

- DB-Datei ist komplett verschluesselt

Nachteil:

- zusaetzliche native Abhaengigkeit
- Installation auf Windows manchmal hakeliger

### Empfehlung

Fuer den lokalen Start: Vorschlag A.

SQLite bleibt einfach, sensible Felder werden gezielt verschluesselt, der Key liegt im Windows Credential Manager.

## Gewuenschter Ablauf in der Weboberflaeche

1. Anwendung starten
2. Konfiguration auswaehlen
3. Verbindung testen
4. Projekt aus NEMO laden und auswaehlen
5. Standard-Projekte oben anzeigen:
   - `Master Data`
   - `Business Processes`
6. Reports laden
7. Nur Reports mit Praefix `(DEFICIENCIES)` anzeigen
8. Report auswaehlen
9. Option waehlen:
   - Ergebnis ansehen
   - Bericht bearbeiten

## API-Entwurf

```text
GET    /api/configs
POST   /api/configs
PUT    /api/configs/{config_id}
DELETE /api/configs/{config_id}

POST   /api/configs/{config_id}/test
GET    /api/configs/{config_id}/projects

GET    /api/reports?config_id=...&project=Master%20Data
GET    /api/reports/{report_id}
POST   /api/reports/{report_id}/run

GET    /api/reports/{report_id}/editor-model
PUT    /api/reports/{report_id}/editor-model
POST   /api/reports/{report_id}/render-sql
POST   /api/reports/{report_id}/validate
POST   /api/reports/{report_id}/save-to-nemo
```

## Reportliste

Filterregel:

```text
displayName starts with "(DEFICIENCIES)"
```

Optional spaeter:

- Suche
- Kategorie
- Master-Data-Typ
- aktive/inaktive Regeln
- paDQM / Top 25 Kennzeichen

## Ergebnis des Berichts ansehen

Fuer die erste Version:

- Report per `nemo.LoadReport(...)` ausfuehren
- Ergebnis als Tabelle anzeigen
- Paging im Frontend
- CSV-Download anbieten
- Fehler sichtbar machen

Spaeter:

- Spaltenfilter
- Sortierung
- Export-Historie
- Laufzeit anzeigen
- Abbruch bei langen Reports

## HANA SQL grafisch bearbeitbar machen

Wichtig: Nicht das blanke SQL als primaere Quelle nehmen.

Empfehlung: Ein internes Report-Modell als JSON. Die UI bearbeitet dieses Modell, der SQL-Generator erzeugt daraus HANA SQL.

`STRUCTURE.sql` zeigt, dass wir mindestens diese CTE-Schablone modellieren muessen:

```text
WITH <source_cte> AS (...),
     proc_src AS (...),
     joined AS (...),
     checks AS (...)
SELECT ...
FROM checks
```

Das SQL soll aus Bausteinen erzeugt werden, nicht frei zusammengeklickt als Text.

## SQL-Blockmodell aus STRUCTURE.sql

### Block 1: Master Data Source

Entspricht in `STRUCTURE.sql`:

```text
supp_src AS (...)
```

Aufgaben dieses Blocks:

- Attribute aus `$schema.$table` laden
- `MASTER_DATA_SUB_TYPE = 'SUPPLIER'` filtern
- technische IDs und Fachattribute bereitstellen
- Hilfsfelder erzeugen, z.B. `FULLNAME_T` und `FULL_T`
- Ausnahmen definieren, z.B. `SUPPLIER_I_D not in (...)`

Konfigurierbar in der UI:

- Source CTE Name, z.B. `supp_src`
- `MASTER_DATA_SUB_TYPE`, z.B. `SUPPLIER`, `CUSTOMER`, `PART`, `ADDRESS`
- Primaer-ID, z.B. `SUPPLIER_I_D`
- Company-Feld, z.B. `COMPANY`
- Attribute mit ERP-Origin-Kommentar
- berechnete Felder:
  - `FULLNAME_T`
  - `FULL_T`
- Ausnahmen:
  - Feld
  - Operator, z.B. `not in`, `=`, `<>`, `is not null`
  - Werte

UI-Vorschlag:

- Tab `Quelle`
- Formular fuer Typ und ID-Felder
- Attributtabelle mit Checkbox `verwenden`
- Bereich `Berechnete Felder`
- Bereich `Ausnahmen`

### Block 2: Prozessrelevanz

Entspricht in `STRUCTURE.sql`:

```text
proc_src AS (
    SELECT DISTINCT
        TRIM(CAST(COMPANY AS NVARCHAR(256))) AS COMPANY,
        TRIM(CAST(SUPPLIER_I_D AS NVARCHAR(256))) AS SUPPLIER_I_D
    FROM $schema."pa_export"
    WHERE SUPPLIER_I_D IS NOT NULL
)
```

Aufgaben dieses Blocks:

- relevante IDs aus `Business Processes` / `pa_export` lesen
- Duplikate entfernen
- Felder normalisieren mit `TRIM(CAST(... AS NVARCHAR(256)))`

Konfigurierbar in der UI:

- Prozessrelevanz aktiv ja/nein
- Prozessquelle, Standard: `$schema."pa_export"`
- Join-Felder:
  - `COMPANY`
  - Objekt-ID, z.B. `SUPPLIER_I_D`
- Filterbedingung, z.B. `SUPPLIER_I_D IS NOT NULL`

UI-Vorschlag:

- Tab `Prozessrelevanz`
- Schalter `Nur prozessrelevante Daten`
- Mapping-Tabelle `Master Data Feld -> Process Feld`
- Vorschau der Join-Bedingung

### Block 3: Join auf prozessrelevante Daten

Entspricht in `STRUCTURE.sql`:

```text
joined AS (
    SELECT c.*
    FROM supp_src c
    INNER JOIN proc_src p
      ON c.COMPANY = p.COMPANY
     AND c.SUPPLIER_I_D = p.SUPPLIER_I_D
)
```

Konfigurierbar in der UI:

- Join-Modus:
  - `INNER JOIN`: nur prozessrelevante Daten
  - `LEFT JOIN`: alle Daten plus Relevanzflag
  - `kein Join`: alle Stammdaten
- Join-Bedingungen
- Alias-Namen `c` und `p`

UI-Vorschlag:

- Radio Button:
  - Alle Stammdaten
  - Nur prozessrelevante Daten
  - Alle Stammdaten mit Relevanzkennzeichen

### Block 4: Datenqualitaetschecks

Entspricht in `STRUCTURE.sql`:

```text
checks AS (
    SELECT
        j.*,
        (CASE ... END || CASE ... END || ...) AS DEFICIENCY_DESCRIPTION
    FROM joined j
)
```

Das ist der wichtigste Block.

In `STRUCTURE.sql` gibt es 16 Pruefgruppen:

1. `NAME1-3`
2. `ADDRESS_STREET`
3. `ADDRESS_STREET_NO`
4. `ADDRESS_SEARCH_TERM`
5. `ADDRESS_Z_I_P_CODE`
6. `ADDRESS_CITY`
7. `ADDRESS_COUNTRY`
8. `ADDRESS_E_MAIL`
9. `ADDRESS_TELEPHONE`
10. `ADDRESS_U_R_L`
11. `SUPPLIER_SEARCH_TERM`
12. `SUPPLIER_INDUSTRY`
13. `SUPPLIER_CREDIT_TERMS_DESC`
14. `SUPPLIER_PAYMENT_METHOD`
15. `SUPPLIER_CREATION_DATE`
16. `SUPPLIER_CHANGE_DATE`

Regeltypen aus `STRUCTURE.sql`:

- leer oder `NULL`
- fuehrende/abschliessende Leerzeichen
- keine Buchstaben
- keine Zahlen
- ungueltige Zeichen per Regex
- obsolete/Test-Begriffe per Regex
- laenderspezifisches PLZ-Muster
- fixer Wertemengencheck, z.B. Branche in `AMB`, `ASM`
- Ausschluss-Wertemenge, z.B. Branche in `AB`, `BC`, `CD`
- Gross-/Kleinschreibung
- Datum ist `NULL`
- Datum in Zukunft
- Datum vor Erstellungsdatum
- Datum zu alt, z.B. mehr als 100 Jahre
- Datum kleiner `1900-01-01`

Wichtig fuer die Web-App:

- Jede Regel braucht eine fachliche Fehlermeldung.
- Der Generator darf kein `WHEN WHEN` erzeugen.
- Der Generator darf keine leeren Meldungen wie nur `'|'` erzeugen, ausser dies wird bewusst erlaubt.

UI-Vorschlag:

- Tab `Checks`
- Links: Pruefgruppen/Felder
- Mitte: Regeln der ausgewaehlten Gruppe
- Rechts: Regel-Details und SQL-Vorschau

Pro Regel:

- aktiv/inaktiv
- Reihenfolge
- fachliche Dimension, z.B. `Vollständigkeit`, `Korrektheit`, `Einheitlichkeit`, `Aktualität`
- technischer Regeltyp
- Feld oder Ausdruck
- Bedingung
- Parameter, z.B. Regex, Werteliste, Datumsgrenze
- Fehlermeldung, z.B. `|Lieferantenname leer`
- optionaler Kommentar

### Block 5: Standardisierte Ausgabe

Entspricht in `STRUCTURE.sql` dem finalen `SELECT` aus `checks`.

Standardspalten:

```text
RULENUMBER
RULENAME
RULEDESCRIPTION
ERROREVALUATION
AREA
RULEFIELD
IDENTIFIER
DESCRIPTION
DESCRIPTION2
CATEGORY
ANALYSISDATE
COMPANY
FIELDNAME
PERSON
STATUS
```

Konfigurierbar in der UI:

- `RULENUMBER`, z.B. `02`
- `RULENAME`, z.B. `Lieferanten-Stammdaten Datenqualitaetssicherung`
- `AREA`, z.B. `S_Lieferant`
- `RULEFIELD`, z.B. `Lieferant`
- Identifier-Ausdruck, z.B. `REPLACE_REGEXPR('\.' IN SUPPLIER_I_D WITH '')`
- `DESCRIPTION`, z.B. `FULLNAME_T`
- `DESCRIPTION2`, z.B. `FULL_T`
- `CATEGORY`, z.B. `Supplier`
- `FIELDNAME`, z.B. `Lieferant`
- `PERSON`, z.B. `paSystem`
- Status-Logik
- Filter `DEFICIENCY_DESCRIPTION <> ''`
- Sortierung `ORDER BY ERROREVALUATION DESC`
- Top-N, z.B. `TOP 25`

UI-Vorschlag:

- Tab `Ausgabe`
- Formular fuer Metadaten
- Spaltenvorschau
- Schalter:
  - Nur Fehler anzeigen
  - Top-N aktiv
  - Nach Fehleranzahl sortieren

## Datenmodell fuer den grafischen Editor

Vorschlag fuer ein internes JSON-Modell:

```json
{
  "report": {
    "displayName": "(DEFICIENCIES) Lieferanten",
    "internalName": "deficiencies_lieferanten",
    "ruleNumber": "02",
    "ruleName": "Lieferanten-Stammdaten Datenqualitaetssicherung"
  },
  "source": {
    "cteName": "supp_src",
    "schemaPlaceholder": "$schema",
    "tablePlaceholder": "$table",
    "masterDataSubType": "SUPPLIER",
    "idField": "SUPPLIER_I_D",
    "companyField": "COMPANY",
    "attributes": [
      { "field": "ADDRESS_NAME", "label": "Name 1", "erpOrigin": "S_Adresse.Name1", "active": true },
      { "field": "SUPPLIER_I_D", "label": "Lieferant", "erpOrigin": "S_Lieferant.Lieferant", "active": true }
    ],
    "computedFields": [
      { "name": "FULLNAME_T", "type": "concat_trim", "fields": ["ADDRESS_NAME", "ADDRESS_NAME2", "ADDRESS_NAME3"] },
      { "name": "FULL_T", "type": "tagged_concat" }
    ],
    "exceptions": [
      { "field": "SUPPLIER_I_D", "operator": "not_in", "values": ["10000000", "10000001"] }
    ]
  },
  "processRelevance": {
    "enabled": true,
    "cteName": "proc_src",
    "table": "pa_export",
    "joins": [
      { "masterField": "COMPANY", "processField": "COMPANY" },
      { "masterField": "SUPPLIER_I_D", "processField": "SUPPLIER_I_D" }
    ],
    "filterNotNull": ["SUPPLIER_I_D"]
  },
  "join": {
    "cteName": "joined",
    "mode": "inner"
  },
  "checks": [
    {
      "group": "NAME1-3",
      "label": "Lieferantenname",
      "rules": [
        { "type": "required_expression", "dimension": "Vollständigkeit", "expression": "FULLNAME_T", "message": "|Lieferantenname leer", "active": true },
        { "type": "contains_letter", "dimension": "Korrektheit", "expression": "FULLNAME_T", "message": "|Lieferantenname keine Buchstaben", "active": true }
      ]
    }
  ],
  "output": {
    "area": "S_Lieferant",
    "ruleField": "Lieferant",
    "identifierExpression": "REPLACE_REGEXPR('\\.' IN SUPPLIER_I_D WITH '')",
    "descriptionField": "FULLNAME_T",
    "description2Field": "FULL_T",
    "category": "Supplier",
    "person": "paSystem",
    "onlyDeficiencies": false,
    "top": null,
    "orderByErrorEvaluation": false
  }
}
```

## Vorschlaege fuer den SQL-Editor

### Vorschlag 1: Template-basierter Block-Editor

Die App speichert ein JSON-Modell. Ein SQL-Template rendert daraus HANA SQL.

Vorteil:

- stabil
- testbar
- keine freie SQL-Manipulation
- UI kann einfach bleiben
- verhindert Fehler wie `WHEN WHEN`

Nachteil:

- bestehendes SQL muss einmal in Modellform gebracht werden

Empfehlung: Das ist der beste Start.

### Vorschlag 2: Rule-Catalog Builder

Wir bauen eine Bibliothek aus wiederverwendbaren DQ-Regeln.

Regelkatalog fuer den Start:

- `required`
- `trim_mismatch`
- `contains_letter`
- `contains_number`
- `allowed_regex`
- `forbidden_regex`
- `obsolete_keywords`
- `country_zip_pattern`
- `email_format`
- `phone_format`
- `url_format`
- `value_in_list`
- `value_not_in_list`
- `uppercase_required`
- `date_not_future`
- `date_after_or_equal_field`
- `date_min`
- `date_max_age_years`
- `duplicate_separator`
- `invalid_start_end`
- `mixed_umlaut_spelling`
- `legal_form_normalization`
- `inactive_commented_rule`

Der Benutzer weist Regeln per Klick Feldern zu.

Vorteil:

- sehr einfach fuer Fachanwender
- Regeln werden standardisiert
- gute Wiederverwendung

Nachteil:

- Sonderfaelle brauchen Erweiterbarkeit

Empfehlung:

Mit Vorschlag 1 kombinieren. Der Rule-Catalog ist der wichtigste Teil des Block-Editors.

### Vorschlag 3: SQL-Import aus STRUCTURE.sql als Hilfsfunktion

Bestehendes SQL wird analysiert:

- CTEs erkennen
- `MASTER_DATA_SUB_TYPE` erkennen
- Attribute erkennen
- Ausnahmen erkennen
- `proc_src` Join-Felder erkennen
- CASE-Regeln im `checks` Block erkennen
- Regex/Wertelisten extrahieren
- finale Ausgabe-Metadaten erkennen

Vorteil:

- bestehende Reports koennen als Startpunkt dienen

Nachteil:

- SQL ist komplex
- Parser wird fragil
- viele Sonderfaelle
- `STRUCTURE.sql` zeigt bereits Generator-Artefakte wie `WHEN WHEN`

Empfehlung:

Nur als Importhilfe verwenden. Danach wird das JSON-Modell die Wahrheit.

### Vorschlag 4: Hybrid mit SQL-Vorschau

Der Benutzer arbeitet grafisch. Daneben gibt es:

- SQL-Vorschau
- Validierungsergebnisse
- Diff zur aktuellen NEMO-Version
- optionaler Expert-Modus

Empfehlung:

SQL-Vorschau ja. Direktes SQL-Editieren erst spaeter und nur fuer Admin/Experten.

## SQL-Generator und Validierung

Der Generator muss HANA SQL erzeugen und mindestens pruefen:

- keine doppelten Keywords wie `WHEN WHEN`
- jede aktive Regel hat eine nicht-leere Fehlermeldung
- jede aktive Regel hat eine fachliche Dimension
- im Editor werden Fehlermeldungen ohne fuehrende Pipe gepflegt
- der SQL-Generator setzt die fuehrende Pipe vor Fehlermeldungen automatisch im SQL
- jedes verwendete Feld existiert in Block 1 oder ist ein berechnetes Feld
- Join-Felder existieren in Quelle und Prozessquelle
- `MASTER_DATA_SUB_TYPE` ist gesetzt
- `DEFICIENCY_DESCRIPTION` wird erzeugt
- finale Standardspalten sind vorhanden
- deaktivierte Regeln aus Kommentaren bleiben im Modell erhalten, erzeugen aber kein aktives SQL
- optional: HANA Syntax-Check ueber Testausfuehrung mit `TOP 1`

## Empfohlene Kombination

Fuer eine stabile lokale Anwendung:

1. Template-basierter Block-Editor
2. Rule-Catalog fuer Datenqualitaetschecks
3. JSON-Modell als zentrale Wahrheit
4. SQL-Generator mit Validierung
5. SQL-Vorschau
6. Optionaler SQL-Import aus bestehenden Reports nur als Hilfsfunktion

## Grobe Umsetzungsphasen

### Phase 1: Bestehende CLI stabilisieren und auslagern

Ziel:

- CLI bleibt nutzbar
- Kernlogik wird Service-Code

Aufgaben:

- `nemo_import_export.py` in CLI und Services aufteilen
- Config-Suche auslagern
- NEMO-Zugriff kapseln
- Report-Filter `(DEFICIENCIES)` als Funktion
- Tests fuer Auswahl und Dateinamen

### Phase 2: Lokale Web-API

Status: umgesetzt am 08.07.2026. FastAPI laeuft lokal, Basisendpunkte und `(DEFICIENCIES)`-Reportliste sind getestet.


Ziel:

- FastAPI startet lokal
- Reports koennen ueber API geladen werden

Aufgaben:

- FastAPI Grundgeruest
- `/api/configs`
- `/api/projects`
- `/api/reports`
- `/api/reports/{id}/run`

### Phase 3: Config-Verwaltung mit Verschluesselung

Status: erster lokaler Stand umgesetzt am 08.07.2026. SQLite speichert Config-Inhalte verschluesselt, lokale `.ini` Dateien werden ausschliesslich aus `config/` importiert, API gibt keine Secrets aus. Offene Haertung: Schluesselverwaltung spaeter ueber Windows Credential Store, Master-Passwort oder Secret-Provider.


Ziel:

- mehrere Profile
- keine sichtbare `config.ini`

Aufgaben:

- SQLite DB
- Config-Profile
- Verschluesselung
- Verbindung testen
- aktive Config auswaehlen

### Phase 4: Erste Weboberflaeche

Status: erster UI-Stand umgesetzt am 08.07.2026. FastAPI liefert die Webapp unter /, mit Config-Auswahl, Projekt-Auswahl, (DEFICIENCIES)-Reportliste, Ergebnisvorschau und Hell/Dunkel-Anpassung.

Ziel:

- Bedienbare lokale Webapp

Seiten:

- Configs
- Projekte
- Reports
- Report Ergebnis

### Phase 5: Report-Editor Modell

Status: lesender Editor-MVP umgesetzt am 08.07.2026. SQL wird serverseitig in Blöcke, Source-Attribute, Check-Gruppen, Regeln, DQ-Dimensionen, Aktiv-Status, Output-Felder und Validierungshinweise zerlegt. Die UI zeigt dieses Modell ohne rohen SQL-Editor.

Ziel:

- grafische Bearbeitung ohne SQL-Verstaendnis

Aufgaben:

- JSON-Modell anhand `STRUCTURE.sql` definieren
- Block 1 bis 5 modellieren
- SQL-Generator bauen
- SQL-Validator bauen
- SQL-Vorschau

### Phase 6: DQ Rule Builder

Status: lokaler Rule-Builder-MVP umgesetzt und am 10.07.2026 UI-seitig verfeinert. Prüfblöcke sind auf- und zuklappbar. Nach dem Aufklappen werden nur kompakte Regelzeilen angezeigt; der Regelname ist klickbar. Die Bearbeitung der ausgewählten Regel erfolgt in der rechten Spalte `Regelparameter` mit Bedingung, Fehlermeldung, DQ-Typ und Regeltyp. Regeln können weiterhin aktiviert/deaktiviert, Dimensionen gesetzt, Fehlermeldungen bearbeitet, Änderungen lokal zurückgesetzt, als Draft gespeichert, über das Backend validiert und als `checks`-SQL-Vorschau generiert werden.

Ziel:

- Checks einfach konfigurieren
- Regelgruppen übersichtlich navigieren
- Regelparameter ohne rohen SQL-Editor bearbeiten

Umgesetzt:

- Regelkatalog
- auf-/zuklappbare Prüfblöcke
- kompakte Regelzeilen ohne Inline-Detailfelder
- Auswahl einer Regel per Klick auf den Regelnamen
- rechte Detailspalte für Bedingung, Fehlermeldung, DQ-Typ und Regeltyp
- Aktiv/inaktiv-Schalter je Regel
- lokale Validierung des bearbeiteten Editor-Modells
- Frontend-Regressionstests für Editor-Controls und klappbare Regelgruppen

Offen:

- grafischer Bedingungs-Builder statt Textfeld für SQL-Bedingung
- Regel hinzufügen, kopieren, löschen und sortieren
- Persistenz der bearbeiteten Modelle
- SQL-Neugenerierung aus dem Modell
### Phase 7: Speichern und Rueckschreiben

Status: Draft-Persistenz umgesetzt am 10.07.2026, SQL-Generator-MVP ergänzt am 13.07.2026. Bearbeitete Editor-Modelle werden lokal in SQLite pro Config, Projekt und Report gespeichert, beim Laden bevorzugt angezeigt und können in der UI wieder verworfen werden. Der SQL-Generator ersetzt den `checks AS (...)` Block im Originalreport und liefert seit Phase 8 die vollständige SQL-Vorschau mit Kopf, Fuß, Standardausgabe, automatischer Pipe vor Fehlermeldungen sowie DQ-Kommentaren vor den `WHEN`-Regeln. Noch offen: Vergleich Original vs. Draft, vollständiger SQL-Diff, Export und optionales Rückschreiben nach NEMO.

Ziel:

- Drafts lokal speichern
- bearbeitete Modelle wieder laden
- gültiges HANA SQL aus dem Modell erzeugen
- Änderungen kontrolliert prüfen, bevor sie exportiert oder nach NEMO geschrieben werden

Empfohlene Reihenfolge:

1. SQLite-Tabelle für Editor-Drafts anlegen - umgesetzt
2. Draft pro Config, Projekt und Report speichern - umgesetzt
3. Draft beim Laden eines Reports bevorzugt anzeigen - umgesetzt
4. Originalmodell und Draftmodell vergleichen - offen
5. SQL-Generator für den wichtigsten Block `Datenqualitätschecks` bauen - umgesetzt als `checks`-Block-Generator
6. SQL-Vorschau und Diff Original vs. generiert anzeigen - vollständige SQL-Vorschau umgesetzt, Diff offen
7. Validierung vor Speichern und vor Export erzwingen - offen
8. erst danach optional `Save to NEMO` via `createReports` - umgesetzt am 14.07.2026 mit SQL-Vorschau-Pflicht, eindeutiger Internalname-Prüfung und Überschreib-Bestätigung; ausgewählter Bericht und namensgleicher `TOP 25`-Partner werden gemeinsam geschrieben, wobei der Partner `SELECT TOP 25` und `ORDER BY ERROREVALUATION DESC` erhält

Aufgaben:

- Draft-Versionen
- Draft-API: speichern, laden, verwerfen
- SQL-Diff
- SQL-Generator für HANA SQL
- Validierung
- Export als `.sql`
- optionales Rückschreiben nach NEMO
### Phase 8: Vollständige SQL-Vorschau und Generator-Härtung

Status: umgesetzt am 13.07.2026. Die SQL-Vorschau zeigt jetzt das komplette generierte Report-SQL inklusive Kopfbereich, unveränderten Quell-/Prozessblöcken, neu erzeugtem `checks`-Block und finaler Standardausgabe. Header-Kommentare listen Report, Quelle, Gruppen und aktive Checks auf. Vor den `WHEN`-Regeln erzeugt der Generator DQ-Kommentare und nutzt dabei vorhandene oder heuristisch erkannte Dimensionen.

Umgesetzt:

- vollständiges SQL statt nur `checks`-Block in der Vorschau
- Header-Kommentar mit Report-Metadaten, Quelltabellen, Gruppen und aktiven Checks
- automatische Pipe vor Fehlermeldungen im SQL
- Editor zeigt Fehlermeldungen ohne führende Pipe
- DQ-Typ-Heuristik für Regeln ohne vorhandenen Kommentar
- Tests für Generator, Modellnormalisierung und Frontend-Vorschau
- zuletzt gewählte Config wird im Browser gespeichert
- Berichtsklick lädt direkt das Editor-Modell
- Ansichtsschalter zeigt `Editor` vor `Ergebnis`

Offen:

- Original-vs.-Draft-Diff
- Export als `.sql`
- Rückschreiben nach NEMO mit Bestätigung

### Phase 9a: Änderungslog und persistentes Undo

Status: umgesetzt am 13.07.2026. Regeländerungen werden in SQLite protokolliert und der aktuelle Draft wird dabei automatisch gespeichert. Dadurch bleibt der Änderungsverlauf auch nach einem Neustart der App verfügbar. Der letzte nicht rückgängig gemachte Schritt kann über die UI zurückgesetzt werden; der Log-Eintrag bleibt erhalten und wird als rückgängig markiert.

Umgesetzt:

- SQLite-Tabelle `editor_change_log` für Regeländerungen
- API zum Lesen und Schreiben des Änderungsverlaufs
- API zum schrittweisen Rückgängigmachen des letzten aktiven Log-Eintrags
- UI-Bereich `Änderungsverlauf` mit Undo-Button in der rechten Editor-Spalte
- automatische Draft-Persistenz beim Protokollieren einer Änderung
- Tests für Store, API-Routen und Frontend-Controls
- unveränderlicher Ursprungssnapshot beim ersten Laden eines Berichts
- Wiederherstellung des Ursprungsberichts als protokollierter und rückgängig machbarer Schritt
- erster Blockeditor-Grundstand: klickbare SQL-Blöcke, kontextabhängige rechte Detailspalte sowie protokollierbare Anzeigenamen und Beschreibungen
- mittlere Editorspalte wechselt abhängig vom Block zwischen Attributen, Prozessfiltern, Verknüpfungen, DQ-Regeln und Ausgabefeldern
- Quellblock-MVP erweitert um editierbaren `MASTER_DATA_SUB_TYPE` und protokollierbare `NOT IN`-Ausnahmen; Attributauswahl und Reihenfolge folgen als nächster Teilschritt
- TOP-25-Partner werden sprachübergreifend erkannt oder bei Bedarf angelegt; persistentes API-/Fehlerlogging mit Vorgangs-ID ergänzt
- NEMO-Update-Payload differenziert: Custom-Berichte behalten `tenant` und `projectId` beim PUT; Standardberichte wechseln in den Custom-POST-Pfad
- geschützte Standardberichte (`isCustom=false`) werden beim Speichern als kundenspezifische Variante angelegt statt per PUT verändert

Offen:

- Redo/Wiederholen
- Änderungsdetails filtern oder exportieren
- SQL-Diff Original vs. generiertes SQL

### Phase 10: KI-unterstützte Regelentwürfe

Status: erster Groq-MVP umgesetzt am 17.07.2026.

Umgesetzt:

- providerneutrale KI-Schnittstelle mit erstem OpenAI-kompatiblen Groq-Adapter
- verschlüsselte Groq-Konfiguration je NEMO-Konfiguration in SQLite
- Verbindungstest beim Einrichten des Zugangs
- natürliche fachliche Regelbeschreibung im Regel-Wizard
- strukturierter Entwurf mit Regeltyp, DQ-Typ, Bedingung, Meldung und Begründung
- verbindliche Verwendung des Internalname und serverseitige SQL-Sicherheitsprüfung
- fiktive Positiv-/Negativbeispiele und fachliche KI-Beispielprüfung
- Übernahme ausschließlich nach Benutzerbestätigung über den bestehenden Änderungsverlauf

Als nächste Ausbaustufen vorgesehen:

- deterministische Beispielprüfung für die unterstützten Regeltypen
- frei erfassbare fachliche Testwerte und erwartete Ergebnisse
- Regelkatalog als Kontext für die KI
- weitere Anbieter über denselben Connector-Vertrag
- Nutzungs-, Kosten- und Fehlerstatistik ohne Speicherung fachlicher Eingaben

## Minimaler MVP

Der kleinste sinnvolle erste Stand:

1. lokale FastAPI App
2. Configprofil aus DB
3. Projektliste aus NEMO
4. `(DEFICIENCIES)` Reports anzeigen
5. Report ausfuehren
6. Ergebnis als Tabelle anzeigen
7. CSV exportieren

Danach erst der grafische SQL-Editor.

## MVP fuer den SQL-Editor

Der kleinste sinnvolle SQL-Editor:

1. Zwei Templates als Referenz: Lieferanten aus `STRUCTURE.sql` und Kunden aus `structure_customer.sql`
2. Quelle mit `SUPPLIER` und `CUSTOMER`
3. Ausnahmen fuer `SUPPLIER_I_D` und optional `CUSTOMER_I_D`
4. Prozessrelevanz ueber `pa_export`
5. 5 bis 8 erste Regeltypen:
   - Pflichtfeld
   - Trim
   - Regex erlaubt
   - Regex verboten
   - Wert in Liste
   - Datum nicht Zukunft
   - Datum nach anderem Datum
   - PLZ nach Land
6. SQL-Vorschau
7. Validierung gegen `WHEN WHEN`, leere Meldungen, fehlende Dimensionen und fehlende Felder

## Risiken

- HANA SQL ist flexibel und nicht immer sauber parsebar
- bestehende Reports koennen voneinander abweichen
- direkter SQL-Editor waere zwar schnell, aber fachlich schwer wartbar
- verschluesselte Configs brauchen klares Key-Handling
- lange Reports brauchen Status, Timeout und gute Fehleranzeige
- vorhandene SQL-Dateien koennen Generator-Artefakte enthalten, z.B. `WHEN WHEN`
- fehlende oder leere Fehlermeldungen machen `DEFICIENCY_DESCRIPTION` fachlich wertlos

## Wichtige Entscheidungen

Bitte entscheiden:

1. Soll die App nur lokal fuer einen Benutzer laufen oder spaeter mehrbenutzerfaehig werden?
2. Reicht SQLite + Feldverschluesselung oder soll die komplette DB per SQLCipher verschluesselt werden?
3. Soll das Rueckschreiben nach NEMO im ersten Schritt erlaubt sein oder erst nur lokal als Draft/SQL exportiert werden?
4. Soll der grafische Editor bestehende SQL-Reports importieren koennen oder starten wir mit neu generierten Reports aus einem Modell?
5. Soll es einen Admin/Expert-Modus mit SQL-Vorschau oder editierbarem SQL geben?
6. Welche DQ-Regeltypen sind fuer den ersten Prototyp Pflicht?
7. Soll Prozessrelevanz immer ueber `Business Processes` / `$schema."pa_export"` laufen oder pro Config/Projekt einstellbar sein?
8. Sollen leere Fehlermeldungen wie `THEN '|'` verboten werden?
9. Soll der erste Editor nur fuer `SUPPLIER` gebaut werden oder direkt auch `CUSTOMER`, `PART`, `ADDRESS`?
10. Sollen DQ-Dimensionen auf die vier Werte `Vollständigkeit`, `Korrektheit`, `Einheitlichkeit`, `Aktualität` begrenzt werden?
11. Soll die UI einen manuellen Theme-Schalter haben oder nur dem Browser folgen?

## Meine Empfehlung fuer den naechsten Schritt

Der technische Unterbau, der lokale Rule-Builder-MVP, die Draft-Persistenz, das persistente Änderungslog mit Undo und die vollständige SQL-Vorschau stehen. Der Generator ersetzt weiterhin gezielt den Block `Datenqualitätschecks`, hält aber Kopf, Quelle, Prozessrelevanz und Standardausgabe im vollständigen SQL sichtbar.

Warum diese Reihenfolge:

- Bearbeitete Regeln bleiben als Draft erhalten und können erneut geladen werden.
- Der kritischste Teil, `DEFICIENCY_DESCRIPTION`, kann nun aus dem Modell neu erzeugt werden.
- Vor Export oder Rückschreiben nach NEMO fehlt noch Transparenz über die konkrete Änderung.

Der nächste konkrete Arbeitsschritt ist daher:

- Diff Original-SQL vs. generiertes SQL ergänzen
- Validierung vor Export erzwingen
- Export als `.sql` vorbereiten
