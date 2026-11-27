# NEMO Deficiencies v1.7.2

## Deutsch

### Neu

- **Schalter „Nur prozessrelevante Datensätze (pa_export)"** direkt vor der SQL-Vorschau. Er erscheint bei Berichten mit der pa_export-Einschränkung (z. B. Kunden, Lieferanten, Kontakte, Teile).
  - **an**: Die Einschränkung bleibt im SQL erhalten (Standardverhalten des Bestands-SQL).
  - **aus**: Die CTEs `process_source` und `joined` entfallen, die Prüfungen laufen auf allen Datensätzen.
- Der Schalterwert wird **pro Config** gespeichert. Ohne gespeicherten Wert gilt der Stand aus dem Bestands-SQL. Standardmäßig steht die Einstellung auf **aus**, wie in der Planung festgelegt.
- Eine Änderung des Schalters setzt die SQL-Vorschau zurück, damit keine veraltete Vorschau verwendet wird.
- Der Schalter wirkt auf die SQL-Vorschau und auf „In NEMO speichern".

### Neue API-Endpunkte

```text
GET /api/configs/{config_id}/pa-export-filter
PUT /api/configs/{config_id}/pa-export-filter
```

### Verbesserungen

- Fehlermeldungen unten rechts bleiben 25 Sekunden sichtbar, solange die Maus nicht darüber steht. Sie sind markierbar und lassen sich über **Kopieren** in die Zwischenablage übernehmen.

### Unverändert

- Adressen-Berichte enthalten keine pa_export-Einschränkung, dort wird kein Schalter angezeigt.
- Alle übrigen Funktionen (In NEMO speichern, TOP-25-Logik, Regelwerksbericht, CLI-Wizard, KI-Übersetzung) sind unverändert.

## English

### New

- **Toggle "Only process-relevant records (pa_export)"** directly before the SQL preview. It appears for reports that contain the pa_export restriction (e.g. customers, suppliers, contacts, parts).
  - **on**: the restriction stays in the SQL (default behaviour of the existing SQL).
  - **off**: the CTEs `process_source` and `joined` are removed, checks run on all records.
- The toggle value is stored **per config**. Without a stored value the state from the existing SQL applies. The default for configs is **off**.
- Changing the toggle resets the SQL preview so an outdated preview is not used.
- The toggle affects the SQL preview and "Save to NEMO".

### New API endpoints

```text
GET /api/configs/{config_id}/pa-export-filter
PUT /api/configs/{config_id}/pa-export-filter
```

### Improvements

- Error messages at the bottom right stay visible for 25 seconds while the mouse is not over them. They can be selected and copied with **Copy**.

### Unchanged

- Address reports contain no pa_export restriction, no toggle is shown there.
- All other functions are unchanged.

## Verification

- Automated test suite run as part of the build (see build output).
