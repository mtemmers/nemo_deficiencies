# NEMO Deficiencies v1.6.1

## Deutsch

### Highlights

- Die Versionsnummer wird auf der Hauptseite, im CLI-Wizard und im Fenstertitel angezeigt.
- CLI-Exporte werden automatisch nach Tenant getrennt: `<Zielordner>\<Tenant>`.
- Konfigurationen können vollständig über die Weboberfläche angelegt, bearbeitet und gelöscht werden.

### Konfigurationen

- Änderbar sind Name, Tenant, User-ID, Passwort, NEMO-URL und Environment.
- Ein leeres Passwortfeld behält beim Bearbeiten das vorhandene Passwort bei.
- Neue oder geänderte Zugangsdaten werden verschlüsselt in der lokalen SQLite-Datenbank gespeichert.
- Zusätzliche vorhandene INI-Parameter bleiben beim Bearbeiten erhalten.
- Fehlerhafte Zugangsdaten werden verständlich gemeldet und verweisen direkt auf den Konfigurationseditor.

### CLI-Wizard und Portable

- Browserexport und erzeugte PowerShell-Skripte verwenden dieselbe tenantgetrennte Ordnerstruktur.
- Ungültige Zeichen im Tenantnamen werden automatisch für Windows-Verzeichnisse bereinigt.
- Die Portable-Version benötigt weiterhin keine separate Python-Installation.
- Das portable ZIP enthält keine Konfigurationen, Datenbanken, Passwörter oder Schlüsseldateien.

## English

### Highlights

- The version number is now visible on the main page, in the CLI Wizard, and in the window title.
- CLI exports are automatically separated by tenant: `<output folder>\<tenant>`.
- Configurations can now be created, edited, and deleted completely through the web interface.

### Configuration management

- Name, tenant, user ID, password, NEMO URL, and environment can be changed.
- Leaving the password field empty while editing keeps the existing password.
- New or changed credentials are stored encrypted in the local SQLite database.
- Additional existing INI parameters are preserved when editing a configuration.
- Invalid credentials produce a clear message that points users to the configuration editor.

### CLI Wizard and portable package

- Browser exports and generated PowerShell scripts use the same tenant-specific folder structure.
- Invalid characters in tenant names are automatically sanitized for Windows directories.
- The portable version still requires no separate Python installation.
- The portable ZIP contains no configurations, databases, passwords, or encryption keys.

## Verification

- 164 automated tests passed.
- Desktop and responsive browser views verified.
- Portable package successfully started as version `1.6.1`.
- SHA-256: `97a44173c00baa519261ab03c1b975eca65751ab1353698ec47e1daf27d5b3c5`
