# NEMO Deficiencies: Schnellstart

## Empfohlen: Portable-Version 1.6.1

1. Unter GitHub **Releases** `NEMO-Deficiencies-1.6.1-portable.zip` herunterladen.
2. Das ZIP vollständig in einen eigenen Ordner entpacken.
3. `NEMO Deficiencies.exe` starten.
4. Neben der Config-Auswahl auf **+** klicken und Tenant, User-ID sowie Passwort eintragen.

Abweichende NEMO-Instanzen können anschließend über das **Stiftsymbol** neben der Konfiguration bearbeitet werden. Dort lassen sich auch NEMO-URL, Environment und Passwort ändern. Ein leeres Passwortfeld behält das vorhandene Passwort bei.

Python und Git werden dafür nicht benötigt. Die Weboberfläche öffnet sich automatisch unter `http://127.0.0.1:8000`.

## Berichte exportieren

1. Konfiguration anlegen oder auswählen.
2. In der Kopfzeile **CLI-Wizard** öffnen.
3. Aktion und Berichte wählen und **Export starten** anklicken.

Python und PowerShell sind nicht erforderlich. Der Standardordner für Exporte ist `Dokumente\NEMO Deficiencies Exports`.

Beim Export wird der Tenant automatisch als Unterordner ergänzt, beispielsweise `NEMO Deficiencies Exports\gmt`.

Für wiederkehrende Exporte im CLI-Wizard **PowerShell-Automatisierung** öffnen und **PS1 herunterladen** anklicken. Das Skript benötigt kein Python und enthält keine Zugangsdaten; die Portable-Anwendung muss während der Ausführung laufen.

## Sicherheit

- Zugangsdaten ausschließlich über die Weboberfläche eingeben, niemals in eine `.ini`, `.env`, ein Skript oder Git schreiben.
- Datenbank und Schlüssel liegen unter `%LOCALAPPDATA%\NEMO Deficiencies\data` und dürfen nicht weitergegeben werden.
- Portable ZIP und PowerShell-Exportskripte enthalten keine Zugangsdaten.
- Vor einer Veröffentlichung nur die aktuelle Version aus `release` hochladen und `SHA256SUMS.txt` prüfen.

## Alternative: Python-Installation

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "nemo-deficiencies @ git+https://github.com/mtemmers/nemo_deficiencies.git"
nemo-deficiencies
```

## Neue Version veröffentlichen

Im Projektordner:

```powershell
.\scripts\publish-release.ps1 -Version 1.6.1
```

Nach der Bestätigung erzeugt GitHub automatisch den neuen Release samt Windows-Installer.

## NEMO-Verbindung anlegen

Neben der Config-Auswahl auf **+** klicken und Tenant, User-ID sowie Passwort eingeben. Danach Config und Bericht auswählen.

Optional unter **KI-Zugang** Groq, OpenAI, Gemini, Perplexity oder einen lokalen Ollama-/LM-Studio-Dienst auswählen. Bei lokalen Diensten sind API-Adresse und Modell erforderlich, ein API-Key jedoch nicht.

Bei der Python-Installation wird die Anwendung im PowerShell-Fenster mit `Strg+C` beendet.

## Optional: Autostart einrichten

Beim Start aus dem Repository:

```powershell
.\install-autostart.ps1 -StartNow
```

Entfernen:

```powershell
.\uninstall-autostart.ps1
```
