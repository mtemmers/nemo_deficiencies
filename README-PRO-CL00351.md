# NEMO Deficiencies

NEMO Deficiencies ist eine lokale Python-Webanwendung zur grafischen Bearbeitung von `(DEFICIENCIES)`-Berichten auf Basis der `nemo_library`. Das vorhandene CLI-Skript `nemo_import_export.py` bleibt fuer Index-, SQL- und Datenexporte enthalten.

Aktuelle Version: **1.6.1**

Für den schnellsten Einstieg siehe [QUICKSTART.md](QUICKSTART.md).

## Empfohlener Start für Anwender

Für Version 1.6.1 ist die Portable-Version der einfachste Weg. Eine Python-Installation ist nicht erforderlich:

1. Unter GitHub **Releases** `NEMO-Deficiencies-1.6.1-portable.zip` herunterladen.
2. Das ZIP vollständig in einen eigenen Ordner entpacken.
3. `NEMO Deficiencies.exe` starten.
4. Die Konfiguration über das Plus-Symbol in der Weboberfläche anlegen.

Die Anwendung startet unsichtbar im Hintergrund und öffnet automatisch:

```text
http://127.0.0.1:8000
```

Persönliche Daten, verschlüsselte Zugangsdaten und Logs bleiben unabhängig von Updates unter:

```text
%LOCALAPPDATA%\NEMO Deficiencies\
```

Der aktuelle lokale Release enthält das portable ZIP, ein Python-Wheel und `SHA256SUMS.txt`. Ein Installer kann mit dem dokumentierten Release-Skript zusätzlich erzeugt werden.

### Einfacher Start der Portable-Version

1. `NEMO-Deficiencies-<Version>-portable.zip` vollständig in einen eigenen Ordner entpacken.
2. `NEMO Deficiencies.exe` starten.
3. In der Hauptseite eine Konfiguration anlegen oder auswählen.
4. In der Kopfzeile **CLI-Wizard** öffnen.
5. Aktion und Berichte auswählen und **Export starten** anklicken.

Python und PowerShell werden dafür nicht benötigt. Ohne abweichende Angabe landen Exporte unter `Dokumente\NEMO Deficiencies Exports`.

Der CLI-Wizard ergänzt immer automatisch den Tenant als Unterordner. Bei mehreren Konfigurationen entsteht damit beispielsweise:

```text
Dokumente\NEMO Deficiencies Exports\gmt\
Dokumente\NEMO Deficiencies Exports\nextgendemo\
```

### Portable-Exporte automatisieren

Der CLI-Wizard kann ein wiederverwendbares PowerShell-Skript erzeugen:

1. Portable-Anwendung starten und im Browser den **CLI-Wizard** öffnen.
2. Konfiguration, Projekt, Aktion, Berichte und Zielordner festlegen.
3. **PowerShell-Automatisierung** aufklappen.
4. **PS1 herunterladen** anklicken.
5. Die erzeugte Datei bei Bedarf erneut ausführen:

```powershell
powershell.exe -ExecutionPolicy Bypass -File ".\nemo-export-config_gmt.ps1"
```

Das Skript enthält keine User-ID und kein Passwort. Es sucht die Konfiguration anhand ihres Namens in der verschlüsselten lokalen Datenbank und ruft die API der laufenden Portable-Anwendung auf. Deshalb muss NEMO Deficiencies vor dem Skript gestartet sein.

Für regelmäßige Exporte kann die Portable-Anwendung per Autostart gestartet und die `.ps1` über die Windows-Aufgabenplanung ausgeführt werden. Als Programm wird `powershell.exe` verwendet, als Argument beispielsweise:

```text
-NoProfile -ExecutionPolicy Bypass -File "C:\Pfad\nemo-export-config_gmt.ps1"
```

## Voraussetzungen

Die folgenden Voraussetzungen gelten nur für Entwicklung oder Installation über Python:

- Windows 10 oder 11
- Python 3.11 oder 3.12
- Zugriff auf die Python-Paketquelle, über die `nemo_library==1.6.63` bereitgestellt wird
- Git, wenn direkt aus GitHub installiert wird

## Installation direkt aus GitHub

Eine eigene virtuelle Umgebung verhindert Konflikte mit anderen Python-Projekten:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "nemo-deficiencies @ git+https://github.com/mtemmers/nemo_deficiencies.git"
```

Anwendung starten:

```powershell
nemo-deficiencies
```

Danach im Browser öffnen:

```text
http://127.0.0.1:8000
```

Beenden: Im PowerShell-Fenster `Strg+C` drücken.

## Installation aus einem lokalen Checkout

Repository klonen und Entwicklungsinstallation anlegen:

```powershell
git clone https://github.com/mtemmers/nemo_deficiencies.git
cd nemo_deficiencies
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
nemo-deficiencies
```

Alternativ bleibt die Installation über `requirements.txt` möglich:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

`pyproject.toml` und `requirements.txt` binden die getestete Version `nemo_library==1.6.63` fest ein. Eine Installation zieht daher nicht automatisch eine neuere, ungetestete Version.

## Neue Version veröffentlichen

### Einfachster Weg über GitHub

Im Projektordner genügt:

```powershell
.\scripts\publish-release.ps1 -Version 1.6.1
```

Der Ablauf:

1. `backend/__init__.py` wird auf die angegebene Version gesetzt.
2. Alle Tests werden ausgeführt.
3. Git zeigt alle Dateien, die in den Release aufgenommen werden.
4. Nach Bestätigung werden Commit und Tag `v1.6.1` erstellt und übertragen.
5. GitHub Actions baut automatisch Installer, portables ZIP, Wheel und Prüfsummen.
6. GitHub veröffentlicht die Dateien unter **Releases**.

Das Skript nimmt alle in der Git-Übersicht angezeigten Änderungen in den Release auf. Vor der Bestätigung sollten deshalb keine unerwünschten lokalen Änderungen vorhanden sein.

Optional kann vor dem Push zusätzlich lokal gebaut werden:

```powershell
.\scripts\publish-release.ps1 -Version 1.6.1 -BuildLocal
```

### Installer nur lokal bauen

Einmalig Inno Setup installieren:

```powershell
winget install JRSoftware.InnoSetup
```

Danach:

```powershell
.\scripts\build-installer.ps1
```

Das Skript installiert fehlende Build-Werkzeuge, führt die Tests aus und schreibt alle fertigen Dateien nach:

```text
release\
├─ NEMO-Deficiencies-Setup-<Version>.exe
├─ NEMO-Deficiencies-<Version>-portable.zip
├─ nemo_deficiencies-<Version>-py3-none-any.whl
└─ SHA256SUMS.txt
```

Der Windows-Build verwendet PyInstaller im One-Folder-Modus. Dadurch startet die Anwendung schneller als ein bei jedem Start temporär entpacktes One-File-Paket. Der Inno-Installer fasst diesen Ordner für Anwender wieder in einer einzelnen Setup-Datei zusammen.

## Lokale Laufzeitdaten

Unabhängig davon, ob die Anwendung portabel, über `pip` oder aus einem Git-Checkout gestartet wird, liegen Datenbank, Schlüssel und Logs standardmäßig außerhalb des Projekts:

```text
%LOCALAPPDATA%\NEMO Deficiencies\
├─ data\
└─ logs\
```

Der Speicherort kann beim Start geändert werden:

```powershell
nemo-deficiencies --home "C:\NEMO-Deficiencies-Daten"
```

Zugangsdaten und API-Keys werden verschlüsselt in SQLite gespeichert und nicht über die API ausgegeben. Im Projektordner werden keine Zugangsdaten, Schlüssel oder Laufzeitdatenbanken benötigt. Der Parameter `--home` sollte nur auf einen privaten, nicht versionierten Ordner zeigen.

### Sicherheitscheck vor einer Veröffentlichung

1. Im Projekt dürfen keine `.ini`, `.env`, `.db`, `.sqlite` oder `.key` mit Laufzeitdaten liegen.
2. Unter `release` nur die aktuelle Version und die dazugehörige `SHA256SUMS.txt` behalten.
3. Portable ZIP und Wheel vor dem Upload auf sensible Dateitypen prüfen.
4. Git-Historie zusätzlich prüfen; das Löschen einer Datei im aktuellen Stand entfernt sie nicht aus älteren Commits.
5. Passwörter und API-Keys sofort erneuern, wenn sie jemals committed, hochgeladen oder anderweitig weitergegeben wurden. Eine nachträgliche Historienbereinigung ersetzt keine Rotation.

Die aktive Laufzeitdatenbank und `nemo_config.key` unter `%LOCALAPPDATA%` werden für die gespeicherten Konfigurationen benötigt und dürfen nur gemeinsam in eine geschützte Sicherung aufgenommen werden.

## Erste Einrichtung

1. Anwendung starten und `http://127.0.0.1:8000` öffnen.
2. Neben der Config-Auswahl auf das Plus-Symbol klicken.
3. Tenant, User-ID und Passwort eintragen.
4. Config auswählen und einen `(DEFICIENCIES)`-Bericht öffnen.
5. Optional einen globalen Cloud- oder lokalen KI-Zugang über `KI-Zugang` einrichten.

### Konfiguration bearbeiten

Neben der Konfigurationsauswahl stehen drei Aktionen zur Verfügung:

- **Statistik** wertet die Berichte und Regeln der ausgewählten Konfiguration aus.
- **Stiftsymbol** bearbeitet Name, Tenant, User-ID, Passwort, NEMO-URL und Environment.
- **+** legt eine neue Konfiguration an.

Bei einer Neuanlage gelten `https://enter.nemo-ai.com` und `prod` als Standard. Im Bearbeitungsdialog bleibt das Passwortfeld leer; dadurch wird das gespeicherte Passwort beibehalten. Nur ein neu eingetragener Wert ersetzt es. Alle Werte werden verschlüsselt in SQLite gespeichert. Über **Löschen** kann die ausgewählte Konfiguration nach einer Bestätigung entfernt werden.

Beispiel für NextGen Demo:

```text
NEMO-URL:   https://nextgendemo.enter.nemo-ai.com
Environment: nextgendemo
```

Wenn Berichte nicht geladen werden und NEMO falsche Zugangsdaten meldet, die Konfiguration bearbeiten und insbesondere User-ID und Passwort erneut eintragen. Das Anwendungslog liegt unter `%LOCALAPPDATA%\NEMO Deficiencies\logs\nemo_deficiencies.log`.

## CLI-Wizard und Automatisierung

Der sichere Weg für interaktive und automatisierte Exporte ist der integrierte CLI-Wizard:

```text
http://127.0.0.1:8000/cli-wizard
```

Er liest die ausgewählte Konfiguration aus der verschlüsselten Laufzeitdatenbank, zeigt alle verfügbaren Berichte ohne Einschränkung an und kann Exporte direkt starten. Für wiederkehrende Abläufe erzeugt er ein PowerShell-Skript ohne User-ID, Passwort oder API-Key. Die Anwendung muss während der Ausführung des Skripts laufen.

Das ältere Skript `nemo_import_export.py` bleibt aus Kompatibilitätsgründen im Quellcode enthalten, erwartet jedoch eine Klartext-INI und wird deshalb für produktive Nutzung nicht empfohlen. Im Projekt und in Release-Artefakten werden keine solchen INI-Dateien mitgeliefert.


## Lokale Anwendung starten

Nach einer Paketinstallation:

```powershell
nemo-deficiencies
```

Beim Start aus dem Repository kann alternativ das portable PowerShell-Skript verwendet werden:

```powershell
.\start.ps1
```

Beenden:

```powershell
.\stop.ps1
```

### Automatisch bei der Windows-Anmeldung starten

Autostart fuer den aktuellen Windows-Benutzer einrichten und direkt testen:

```powershell
.\install-autostart.ps1 -StartNow
```

Die Anwendung startet danach bei jeder Windows-Anmeldung unsichtbar im Hintergrund.
Das Projektverzeichnis darf anschliessend nicht verschoben werden. Nach einem Umzug
muss der Autostart erneut eingerichtet werden.

Autostart wieder entfernen:

```powershell
.\uninstall-autostart.ps1
```

Autostart entfernen und die laufende Anwendung beenden:

```powershell
.\uninstall-autostart.ps1 -StopApplication
```

Alternativer manueller Start:

```powershell
python -m backend.cli --reload
```

Wichtige URLs:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/configs
http://127.0.0.1:8000/api/projects
http://127.0.0.1:8000/api/reports
```

Oben rechts kann zwischen zwei Bedienmodi gewechselt werden:

- **Standard** zeigt Konfiguration und Berichtsauswahl sowie Datenqualitaetsregeln, Regelparameter, SQL-Vorschau und das Speichern nach NEMO.
- **Experte** zeigt zusaetzlich Projekte, Ergebnisansicht, alle SQL-Bloecke, Validierung, Export, Drafts und Aenderungsverlauf.

Der zuletzt verwendete Modus wird im Browser gespeichert.

Zugehörige `TOP 25`-Berichte werden nicht als eigene Einträge in der Berichtsauswahl geladen. Beim Speichern nach NEMO werden sie weiterhin automatisch zusammen mit dem Hauptbericht aktualisiert oder erstellt.

Beim Speichern nach NEMO werden eigene Custom-Berichte aktualisiert. Standardberichte werden als eigene anpassbare Variante angelegt. Gehört ein Custom-Bericht zu einem anderen Tenant als die ausgewählte Konfiguration, wird das gesamte Update vor dem ersten Schreibzugriff abgebrochen.

Die Anwendung verwendet fuer Lesen und Schreiben immer die oben links ausgewählte Konfiguration. Vor jedem NEMO-Schreibvorgang wird die Report-ID erneut gegen diese Konfiguration geprüft. Hat sich die Konfiguration zwischenzeitlich geändert, wird derselbe Bericht anhand seines Internalname automatisch neu geladen; anschließend muss die SQL-Vorschau erneut erzeugt werden.

Neue Config-Profile werden über den Plus-Button neben der Config-Auswahl angelegt. Abgefragt werden Tenant, User-ID und Passwort; Profilname und Produktionsumgebung werden automatisch gesetzt. Die Zugangsdaten werden unmittelbar verschlüsselt in SQLite gespeichert. Das Passwort wird weder in API-Antworten noch in der Oberfläche erneut ausgegeben.

## Verschluesselte Config-Datenbank

NEMO- und KI-Zugänge werden verschlüsselt in der lokalen SQLite-Datenbank gespeichert. Die API gibt nur nicht geheime Profilinformationen zurück.

Wichtige Dateien:

```text
%LOCALAPPDATA%\NEMO Deficiencies\data\nemo_deficiencies.sqlite
%LOCALAPPDATA%\NEMO Deficiencies\data\nemo_config.key
```

Beide Dateien sind zusammen schützenswerte lokale Laufzeitdaten. Sie dürfen nicht veröffentlicht, in Supportpakete aufgenommen oder in Git eingecheckt werden. Ohne den Schlüssel sind die verschlüsselten Zugangsdaten nicht nutzbar; für eine Sicherung werden Datenbank und Schlüssel gemeinsam benötigt.

Config-Profile anzeigen:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/configs"
```

Konfigurationen werden ausschließlich über die Weboberfläche angelegt, geändert und gelöscht.

## Lokale Weboberflaeche

Nach dem Start der API ist die Weboberflaeche hier erreichbar:

```text
http://127.0.0.1:8000/
```

Die Oberflaeche bietet aktuell:

- Config-Auswahl aus der verschluesselten lokalen Datenbank
- vollständiger Regelwerksbericht als PDF und Excel je Konfiguration und Projekt
- zuletzt gewaehlte Config wird lokal im Browser gemerkt
- Standardmodus fuer den fokussierten DQ-Workflow und Expertenmodus fuer alle Funktionen
- Projekt-Auswahl fuer `Master Data` und `Business Processes`
- `(DEFICIENCIES)`-Reportliste
- Klick auf einen Report zeigt einen Ladeindikator und laedt zuerst das `Editor-Modell`
- Ergebnisvorschau fuer den ausgewaehlten Report ueber den Tab `Ergebnis`
- Ansicht `Editor-Modell` fuer grafische Report-/Regelbearbeitung
- Expertenansicht `Harmonisierung` zum berichtsübergreifenden Vergleich gleicher Felder und Regelwerke
- klickbare SQL-Blöcke mit kontextabhängigen Blockparametern in der rechten Spalte
- kontextabhängige mittlere Spalte für Attribute, Prozessfilter, Verknüpfungen, DQ-Regeln oder Ausgabefelder
- Quellkonfiguration für `MASTER_DATA_SUB_TYPE` und einfache `NOT IN`-Ausnahmen mit SQL-Generierung
- lokale Draft-Persistenz fuer bearbeitete Editor-Modelle
- persistenter Änderungsverlauf mit schrittweisem Rückgängig in SQLite
- unveränderlicher Ursprungssnapshot je Config, Projekt und Bericht mit Wiederherstellungsbutton
- automatische Hell/Dunkel-Anpassung plus manueller Umschalter
- harte Tenant-Sperre vor Haupt-/TOP-25-Updates bei unpassender Konfiguration
- automatische Aktualisierung veralteter Report-IDs vor dem NEMO-Schreiben

## Regelwerksbericht als PDF und Excel

Der Button **Statistik** neben der Konfigurationsauswahl lädt alle Berichte mit dem Präfix `(DEFICIENCIES)` aus dem ausgewählten Projekt. TOP-25-Spiegelberichte bleiben standardmäßig außen vor und können im Dialog zugeschaltet werden.

Als Datenquelle kann gewählt werden:

- **Aktueller NEMO-Stand** für einen offiziellen Ist-Bericht
- **Lokale Entwürfe bevorzugen** für den aktuellen Bearbeitungsstand

Die Auswertung zeigt Berichte, Regelgruppen, unterschiedliche Felder sowie aktive und inaktive Regeln. Über **PDF herunterladen** entsteht ein kompakter Regelwerksbericht mit Konfiguration, Tenant, Projekt, Erstellungszeit, Anwendungsversion und allen Regeln. Jede Regel enthält Bericht, Regelgruppe, Fehlermeldung, Aktivstatus, DQ-Typ, Regeltyp und HANA-Bedingung.

**Excel herunterladen** erzeugt eine Arbeitsmappe mit:

- `Übersicht`: Kennzahlen, Berichtssummen und Statusgrafik
- `Regeln`: vollständige filterbare Detailtabelle einschließlich Internalnames, Beschreibungen und Bedingungen

Die Sprache der Überschriften richtet sich nach der ausgewählten Oberflächensprache. Zugangsdaten werden nicht in die Dokumente geschrieben.

API-Endpunkte:

```text
GET /api/config-statistics
GET /api/config-statistics/report.pdf
GET /api/config-statistics/report.xlsx
```

## Berichtsübergreifende Harmonisierung

Im Expertenmodus vergleicht die Ansicht `Harmonisierung` die Regelgruppen aller `(DEFICIENCIES)`-Berichte im ausgewählten Projekt. `TOP 25`-Spiegelberichte werden nicht doppelt ausgewertet. Die Zuordnung gleicher Felder nutzt die NEMO-Metadaten für Displayname, Internalname und Importname; Regeln werden mit einem feldneutralen Platzhalter verglichen.

Die Matrix kennzeichnet übereinstimmende Regelwerke, Abweichungen und fehlende Regelgruppen. Ein Klick auf ein Feld oder eine Berichtszelle zeigt rechts Beschreibung, verwendeten Internalname, Regelanzahl, aktive Regeln und DQ-Typen. Vorhandene lokale Drafts werden bevorzugt berücksichtigt.

Für eine kontrollierte Übernahme wird rechts ein Referenzbericht gewählt. Abweichende und fehlende Zielberichte sind vorausgewählt, weitere Ziele können ergänzt werden. `Änderungen prüfen` zeigt vorab, ob eine Regelgruppe ersetzt oder neu angelegt wird und wie sich die Regelanzahl ändert. `Als Drafts übernehmen` schreibt noch nicht nach NEMO: Die Regelgruppe wird je Zielbericht an dessen Internalname angepasst, bei Bedarf im Quellblock ergänzt, als lokaler Draft gespeichert und als einzelner rückgängig machbarer Schritt in SQLite protokolliert.

```text
GET /api/harmonization?configId=<config>&project=Master+Data
POST /api/harmonization/preview
POST /api/harmonization/apply
```

## Globaler Regelkatalog

Der technische Kern für einen projektübergreifend nutzbaren Regelkatalog liegt in SQLite vor. Regelvorlagen sind global und enthalten deshalb selbst keine Config-, Projekt- oder Berichtszuordnung. Eine spätere konkrete Verwendung wird separat als Bindung aus Vorlagen-ID, Version, Config, Projekt, Bericht, Regelgruppe und Regel gespeichert. Damit kann dieselbe fachliche Vorlage in `Master Data`, `Business Processes` und weiteren Projekten verglichen und harmonisiert werden.

Jede Vorlage besitzt unveränderliche Versionen mit:

- generischer HANA-SQL-Bedingung
- deutscher und englischer Fehlermeldung
- DQ-Typ und Regeltyp
- typisierten Parametern und Standardwerten
- passenden Datentypen und Feldkategorien
- Testbeispielen und Änderungshinweis
- Status `draft`, `approved` oder `deprecated`

Unterstützte Standardplatzhalter:

```text
{field}        -> Internalname der Regelgruppe
{displayName}  -> sichtbare Feldbezeichnung
{description}  -> fachliche Feldbeschreibung
```

Zusätzliche Parameter werden in der Vorlage definiert, beispielsweise:

```text
LENGTH(TRIM({field})) < {min_length}
```

Der Resolver validiert Feldnamen und Parameter, setzt Zahlen ohne SQL-Anführungszeichen ein und maskiert Text- sowie Regexwerte als SQL-Literale. Unbekannte oder fehlende Platzhalter werden abgelehnt.

Im Expertenmodus öffnet `Regelkatalog` die globale Vorlagenverwaltung. Dort können Vorlagen angelegt, bearbeitet, freigegeben oder als veraltet markiert werden. Änderungen an Bedingung, Meldungen oder Parametern erzeugen eine neue unveränderliche Version. Vier freigegebene Startvorlagen stehen automatisch bereit: Pflichtfeldprüfung, äußere Leerzeichen, Mindestlänge und Maximallänge.

`Master Data analysieren` untersucht die bestehenden Regeln der aktuell ausgewählten Konfiguration. `TOP 25`-Spiegelberichte werden dabei nicht als eigene Quelle ausgewertet. Internalnames werden durch `{field}` ersetzt und fachlich gleiche Bedingungen nach DQ-Typ und Regeltyp gruppiert. Sichere variable Bestandteile werden zusätzlich parametrisiert: Grenzwerte von Mindest- und Maximallängen sowie Muster von Regexregeln. Die konkrete Ausprägung bleibt pro Regelbindung erhalten. Komplexe Länderlisten und individuelle Spezialbedingungen werden nicht automatisch verallgemeinert.

Die Kandidatenansicht zeigt Vorkommen, betroffene Berichte, erkannte Parameterwerte und eine Konfidenz. Bereits katalogisierte Regeln werden gekennzeichnet; neue Kandidaten mit mindestens zwei Vorkommen sind vorausgewählt.

Ein Klick auf einen Kandidaten öffnet rechts die fachliche Prüfung mit generischer Bedingung, Parameterwerten, allen Fehlermeldungsvarianten und sämtlichen Fundstellen. Kandidaten können einzeln als Entwurf übernommen oder abgelehnt werden. Die Entscheidung wird je Konfiguration und Projekt in SQLite gespeichert und bleibt nach einem Neustart erhalten. Eine Ablehnung kann über `Zur Prüfung zurückstellen` aufgehoben werden. Nach einer Übernahme öffnet `Vorlage öffnen` den normalen Vorlageneditor; dort wird der Entwurf geprüft und über den Status `Freigegeben` veröffentlicht.

Erst `Auswahl als Entwürfe übernehmen` legt globale Katalogentwürfe und die zugehörigen Bindungen in SQLite an. Die Analyse und Übernahme verändern weder lokale Berichtsentwürfe noch SQL oder NEMO-Berichte.

In einer geöffneten Regelgruppe fügt `Aus Katalog` eine Vorlage ein. Die Oberfläche erzeugt für definierte Parameter passende Eingabefelder, löst `{field}` gegen den Internalname der Regelgruppe auf und zeigt Bedingung sowie Fehlermeldung vor der Übernahme. Die neue Regel wird als lokaler Draft protokolliert und kann rückgängig gemacht werden. Zusätzlich wird ihre Vorlagenbindung mit Config, Projekt, Bericht und Regelgruppe in SQLite gespeichert. NEMO wird erst über den bestehenden Button `In NEMO speichern` geändert.

API-Endpunkte:

```text
GET   /api/rule-templates
GET   /api/rule-templates/{template_ref}
POST  /api/rule-templates
PATCH /api/rule-templates/{template_ref}
POST  /api/rule-templates/{template_ref}/versions
POST  /api/rule-templates/{template_ref}/resolve
POST  /api/rule-templates/analyze-existing
POST  /api/rule-templates/import-existing
POST  /api/rule-templates/candidate-decisions
POST  /api/rule-template-bindings
```

## Report-Editor-Modell

Die Weboberflaeche hat neben der Ergebnisansicht eine Ansicht `Editor-Modell`. Sie zeigt den SQL-Report als fachliches Modell und vermeidet einen rohen SQL-Editor als Hauptbedienung:

- SQL-Bloecke: Quelle, Prozessrelevanz, Join, Checks, Ausgabe
- Auswahl eines SQL-Blocks öffnet rechts dessen Basisdaten und blocktypabhängige Strukturinformationen
- Check-Gruppen aus den `CASE`-Bloecken
- auf-/zuklappbare Prüfblöcke
- Regelgruppen mit Sicherheitsabfrage entfernen; die Änderung wird protokolliert und kann rückgängig gemacht werden
- kompakte Regelzeilen je Prüfblock
- einzelne Regeln mit Dimension, Regeltyp, Bedingung, Meldung und Aktiv-Status
- rechte Detailspalte `Regelparameter` fuer die ausgewaehlte Regel
- Validierungshinweise aus dem Backend

API-Endpunkte:

```text
GET    /api/reports/{report_ref}/editor-model
GET    /api/reports/{report_ref}/draft
PUT    /api/reports/{report_ref}/draft
DELETE /api/reports/{report_ref}/draft
GET    /api/reports/{report_ref}/change-log
POST   /api/reports/{report_ref}/change-log
POST   /api/reports/{report_ref}/change-log/undo
POST   /api/reports/{report_ref}/restore-original
POST   /api/reports/{report_ref}/validate
POST   /api/reports/{report_ref}/render-sql
POST   /api/reports/{report_ref}/export-sql
POST   /api/reports/{report_ref}/write-to-nemo
```

Der aktuelle Stand merkt sich die zuletzt gewaehlte Config im Browser, oeffnet Reports zuerst im Editor-Modell und kann Editor-Modelle laden, lokal bearbeiten, validieren, als Draft in SQLite speichern, Änderungen persistent protokollieren, schrittweise rückgängig machen und eine vollständige SQL-Vorschau erzeugen. Beim ersten Laden wird der Ursprungsbericht dauerhaft in SQLite gesichert. `Ursprungsbericht wiederherstellen` ersetzt den aktuellen Draft durch diesen Stand und protokolliert den Vorgang; NEMO wird dabei noch nicht verändert. Beim erneuten Laden wird ein vorhandener Draft bevorzugt angezeigt; über `Draft verwerfen` wird wieder das aktuell aus NEMO geladene Modell angezeigt. Die SQL-Vorschau ersetzt gezielt den `checks AS (...)` Block im Original-SQL, zeigt aber unten das komplette SQL inklusive Kopfkommentar, Standardausgabe und DQ-Kommentaren an. Fehlermeldungen werden im Editor ohne Pipe gepflegt; der SQL-Generator schreibt die Pipe automatisch. Das SQL kann lokal exportiert oder nach einer expliziten Überschreib-Bestätigung in NEMO zurückgeschrieben werden. Dabei werden der ausgewählte Bericht und der zugehörige Bericht mit dem Suffix `TOP 25` gemeinsam aktualisiert. Die Zuordnung erkennt deutsche und englische Sachbegriffe, unter anderem `Customers/Kunden`, `Suppliers/Lieferanten`, `Parts/Teile`, `Addresses/Adressen` und `Contacts/Kontakte`. Fehlt der Partner, wird er aus den Metadaten des Hauptberichts neu angelegt. Der Partnerbericht erhält `SELECT TOP 25` und `ORDER BY ERROREVALUATION DESC`; mehrdeutige Treffer brechen den Schreibvorgang weiterhin ab. Ein vollständiger SQL-Diff ist noch offen.

API-Aufrufe und NEMO-Schreibvorgänge werden mit einer Vorgangs-ID in `logs/nemo_deficiencies.log` protokolliert. Die Datei rotiert bei 5 MB; bis zu fünf ältere Logdateien bleiben erhalten. Fehlermeldungen in der Weboberfläche zeigen die Vorgangs-ID zur gezielten Suche im Log an.

Beim Aktualisieren vorhandener kundenspezifischer NEMO-Berichte bleiben `tenant` und `projectId` im vollständigen PUT-Payload enthalten. Vor dem gemeinsamen Update werden die Tenants aller vorhandenen Custom-Berichte mit dem Tenant der ausgewählten Config verglichen. Eine Abweichung liefert einen verständlichen Konflikt und verhindert jeden Teilschreibvorgang. Beim Neuanlegen eines fehlenden TOP-25-Berichts bleiben alle Erstellungsinformationen erhalten. API-Fehlerdetails von NEMO werden gekürzt direkt in der Weboberfläche angezeigt.

Ist ein vorhandener Bericht ein geschütztes Standard-Metadatenobjekt (`isCustom=false`), wird er nicht per PUT verändert. Stattdessen legt die Anwendung über den NEMO-Persistence-Endpunkt eine kundenspezifische Variante mit identischem Internalname an. Bereits kundenspezifische Berichte werden weiterhin aktualisiert.

## DQ Rule Builder

Die Ansicht `Editor-Modell` erlaubt erste grafische Aenderungen am geladenen Modell:

- Prüfblöcke auf- und zuklappen
- Displayname, Internalname und Beschreibung einer Regelgruppe bearbeiten; Internalname-Änderungen werden in Bedingungen und Quellattributen mitgeführt und vollständig protokolliert
- Klammerbezeichnung aus dem SQL-Gruppentitel sowie Beschreibung direkt neben Displayname und Internalname in der Übersicht anzeigen
- rechte Parameterleiste bleibt beim Scrollen sichtbar und besitzt einen eigenen Scrollbereich
- SQL-Vorschau kontextbezogen in der rechten Leiste anzeigen; Regel- oder Regelgruppenauswahl wechselt zurück zu den Parametern
- Regel per Klick auf den Regelnamen auswaehlen
- Regelparameter rechts bearbeiten:
  - Bedingung
  - Fehlermeldung
  - DQ-Typ / fachliche Dimension
  - Regeltyp
- Regeln aktivieren/deaktivieren
- Aenderungen lokal zuruecksetzen
- Aenderungen in SQLite protokollieren und schrittweise rueckgaengig machen
- bearbeitetes Modell gegen den Backend-Validator pruefen
- Regelkatalog im Backend verwenden

Verfügbare DQ-Typen sind: `Vollständigkeit`, `Validität`, `Korrektheit`, `Eindeutigkeit`, `Konsistenz`, `Aktualität`, `Genauigkeit`, `Redundanz`, `Einheitlichkeit`, `Relevanz`, `Zuverlässigkeit` und `Verständlichkeit`. Sie stehen sowohl bei manuellen Regeln und Regelvorlagen als auch für KI-generierte Vorschläge zur Verfügung.

API-Endpunkte:

```text
GET  /api/rule-catalog
POST /api/editor-model/validate
```

Dieser Stand speichert bearbeitete Modelle lokal als Draft, protokolliert Regeländerungen in SQLite und kann daraus eine vollständige SQL-Vorschau neu generieren. DQ-Typ-Kommentare werden vor den `WHEN`-Regeln erzeugt; fehlende DQ-Typen werden heuristisch gesetzt. Export und bestätigtes Rückschreiben nach NEMO einschließlich des zugehörigen `TOP 25`-Berichts sind umgesetzt. Der SQL-Diff bleibt als nächster Schritt offen.

## Sprachen

Die Oberflächensprache kann in der Kopfzeile unabhängig von der Berichtssprache zwischen Deutsch und Englisch umgeschaltet werden. Neue manuelle oder KI-unterstützte Regeln werden in der gewählten Oberflächensprache erstellt. Beide Auswahlen bleiben im Browser gespeichert.

Die Berichtssprache steuert die Fehlermeldungen und die vom Generator erzeugten SQL-Kommentare. Weicht sie von der Sprache einer Fehlermeldung ab, übersetzt das aktive globale KI-Profil die Meldung beim Umschalten und vor Vorschau, Export oder NEMO-Speicherung. Die Originalmeldung im Regelwerk bleibt unverändert; Übersetzungen werden nur für die Ausgabe verwendet. Erfolgreiche Übersetzungen werden pro KI-Profil, Modell, Ausgangssprache und Zielsprache dauerhaft in SQLite zwischengespeichert und stehen dadurch auch nach einem Neustart ohne erneuten KI-Aufruf zur Verfügung. Doppelte Meldungen werden zusammengefasst und neue Übersetzungen in kleinen Paketen verarbeitet. Ein vorübergehend nicht erreichbarer KI-Dienst blockiert bereits gecachte Übersetzungen nicht. Ohne eingerichteten KI-Zugang kann ein Bericht nur erzeugt werden, wenn keine Meldung übersetzt werden muss.

## Generische KI-Anbindung

Die Anwendung unterstützt mehrere globale KI-Profile. In der Kopfzeile kann das aktive Profil ausgewählt werden; die Auswahl bleibt im Browser erhalten und ist unabhängig von NEMO-Konfiguration, Projekt und Bericht. Cloud-API-Keys werden mit demselben lokalen Schlüssel wie die NEMO-Zugangsdaten verschlüsselt in SQLite gespeichert und von der API nie ausgegeben. Lokale Dienste können ohne API-Key betrieben werden.

Voreinstellungen:

| Anbieter | API-Adresse | Beispielmodell |
| --- | --- | --- |
| Groq | `https://api.groq.com/openai/v1` | `openai/gpt-oss-120b` |
| OpenAI / ChatGPT | `https://api.openai.com/v1` | `gpt-5-mini` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-3.5-flash` |
| Perplexity | `https://api.perplexity.ai` | `sonar` |
| Ollama | `http://localhost:11434/v1` | beispielsweise `qwen3:8b` |
| LM Studio | `http://localhost:1234/v1` | Name des geladenen Modells |

Über `Eigener OpenAI-kompatibler Dienst` können API-Adresse, Modellname und optionaler API-Key frei definiert werden. Die Adresse darf auch bereits auf `/chat/completions` enden. Unterstützt ein Dienst das strikte JSON-Schema nicht, versucht der Konnektor automatisch JSON-Objekt-Modus und anschließend reinen JSON-Prompt-Modus. Die fachlichen und SQL-bezogenen Sicherheitsprüfungen im Backend bleiben bei allen Anbietern aktiv.

Für Ollama muss das gewünschte Modell lokal vorhanden sein und der Ollama-Dienst laufen. Für LM Studio muss der lokale Server mit einem geladenen Modell gestartet sein. Danach wird das passende Profil über `KI-Zugang` angelegt und direkt durch einen strukturierten Verbindungstest geprüft.

Beim Anlegen einer Regel kann eine fachliche Anforderung in natürlicher Sprache eingegeben werden. Der Konnektor übergibt den Internalname, Displayname, die Beschreibung, den Datentyp und bereits vorhandene Regeln der ausgewählten Regelgruppe. Die aktive KI liefert einen strukturierten Entwurf mit Bedingung, Fehlermeldung, DQ-Typ, Regeltyp, Begründung und fiktiven Beispielen. Das Backend erzwingt den Internalname in der Bedingung und blockiert Semikolon sowie schreibende SQL-Anweisungen.

Die erzeugten Beispiele können über `Beispiele prüfen` semantisch durch das Modell gegengeprüft werden. Diese Prüfung ist eine fachliche KI-Einschätzung und noch keine Ausführung der HANA-Bedingung. Erst `Regel anlegen` übernimmt den bearbeitbaren Entwurf in das Editor-Modell und protokolliert ihn über den vorhandenen Änderungsverlauf.

Bei bestehenden Regeln erklärt `Formel erklären` die sichtbare HANA-Bedingung in fachlicher Sprache. Die rechte Spalte zeigt Zusammenfassung, Auslöseverhalten, gültige und fehlerhafte Beispiele, Sonderfälle und Warnungen. Die Erklärung ist rein lesend und verändert weder Regel noch Änderungsprotokoll.

`Mit KI überarbeiten` prüft eine bestehende Regel und kann zusätzlich einen frei formulierten Änderungswunsch berücksichtigen. Der Vorschlag wird mit bisheriger und neuer Bedingung, Fehlermeldung, DQ-Typ, Regeltyp, Begründung und Warnungen angezeigt. Fiktive Beispiele lassen sich vor der Übernahme mit `Beispiele prüfen` gegenlesen. Erst `Vorschlag übernehmen` ändert die Regel; die komplette KI-Überarbeitung wird als ein rückgängig machbarer Schritt in SQLite protokolliert. Das Backend verhindert vollständige SQL-Anweisungen und neue Feldbezeichner, die in der ursprünglichen Bedingung nicht vorkamen.

Beim Anlegen einer Regelgruppe zeigt die Feldsuche nur Attribute, die im aktuellen Bericht noch keiner Regelgruppe zugeordnet sind. Nach Auswahl eines Feldes kann `KI-Regelvorschläge erzeugen` eine Stichprobe von höchstens 500 Werten aus genau dieser Spalte analysieren. Dafür wird in der ausgewählten NEMO-Konfiguration kurzzeitig ein eindeutig benannter technischer Report angelegt und nach dem Download auch im Fehlerfall gelöscht. Die Werte werden lokal in Längen-, Leerwert-, Zeichensatz-, Häufigkeits- und Formmuster umgewandelt; die aktive KI erhält ausschließlich dieses anonymisierte Profil und keine Rohwerte. Die KI liefert mindestens drei auswählbare Vorschläge mit Bedingung, Fehlermeldung, DQ-Typ, Regeltyp und Musterbegründung. Ausgewählte Vorschläge werden gemeinsam mit der Regelgruppe angelegt und als eine Änderung protokolliert.

API-Endpunkte:

```text
GET  /api/ai/configs
POST /api/ai/configs
POST /api/ai/configs/{ai_config_id}/test
POST /api/ai/rules/draft
POST /api/ai/rules/test-examples
POST /api/ai/rules/explain
POST /api/ai/rules/revise
POST /api/ai/fields/suggest-rules
```

## Tests

```powershell
python -m unittest discover -s tests -v
```
