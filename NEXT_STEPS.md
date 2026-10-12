# Nächste Schritte: InfoZoom SDK Integration

## 🎯 Wo Du stehst

✅ **Fertig:**
- InfoZoom SDK 9.100 (32-bit) angebunden via COM (pywin32)
- `.fox`-Datei-Export architekturiert (API implementiert)
- Persistente Rule-Translation Cache (JSON)
- Error Logging & Fehler-Resilience
- 94 Unit Tests bestanden
- Setup-Dokumentation

❌ **Noch nicht getestet:**
- End-to-End `.fox`-Datei-Erzeugung mit echtem SDK
- SDK-Fehler in der Praxis
- .fox-Dateien in InfoZoom öffnen

---

## 🚀 Empfehlung: Das solltest du JETZT machen

### Option A: **Schnell & Praktisch** (Empfohlen)
Starte den Backend-Server und teste den Export über die API:

```bash
# 1. Backend starten
cd nemo_deficiencies
python -m uvicorn backend.main:app --reload

# 2. In anderem Terminal: Test-Export mit curl oder Postman
curl -X POST http://localhost:8000/api/export_editor_model \
  -H "Content-Type: application/json" \
  -d '{
    "format": "infozoom",
    "options": {"mode": "sdk_native"},
    "editor_model": {...}
  }' \
  --output export.fox

# 3. export.fox in InfoZoom 2026 öffnen und prüfen
```

**Resultat:** Du siehst sofort ob:
- Die .fox-Datei korrekt erzeugt wird
- Welche Fehler beim Export auftreten
- Ob die Regeln in InfoZoom richtig angezeigt werden

---

### Option B: **Gründlich & Strukturiert**
Schreib einen Integration-Test der echte .fox-Dateien erzeugt:

```python
# tests/test_integration_infozoom_sdk.py

def test_end_to_end_fox_creation():
    """Echte .fox-Datei mit echtem SDK erstellen und prüfen."""
    from backend.export_connectors.infozoom_connector import InfoZoomExportConnector
    import tempfile
    
    connector = InfoZoomExportConnector()
    
    # Echtes Model laden oder minimal model verwenden
    test_model = {...}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "export.fox"
        
        # Export starten
        result = connector.export_to_file(
            model=test_model,
            output_path=str(output),
            options={"mode": "sdk_native"}
        )
        
        # Prüfe ob Datei existiert und Größe > 0
        assert output.exists()
        assert output.stat().st_size > 100
```

**Resultat:** Automatisierter Test der vor jedem Commit läuft.

---

### Option C: **Fehlerbehandlung Verbessern**
Schaue welche Regeltypen in deinem echten Model nicht unterstützt sind:

1. Lade dein echtes NEMO-Modell
2. Führe Export aus
3. Schaue `.cache/infozoom_errors.json` für fehlgeschlagene Regeln
4. Erweitere `condition_translator.py` für diese Fälle

---

## 📋 Konkrete Aktions-Items (Priorisiert)

### 🔴 **MUST DO (Diese Woche)**
- [ ] SDK License in InfoZoom GUI aktivieren (einmalig!)
- [ ] Test-Export über API durchführen
- [ ] .fox-Datei in InfoZoom öffnen → funktioniert es?
- [ ] Fehler-Log prüfen und erste Fehler dokumentieren

### 🟡 **SHOULD DO (Nächste Woche)**
- [ ] Integration-Tests für SDK schreiben
- [ ] Alle Common-Regeltypen testen (IS NULL, LIKE, LENGTH, etc.)
- [ ] Frontend-UI für Mode-Auswahl hinzufügen
- [ ] Cache-Statistiken im Admin-Panel anzeigen

### 🟢 **NICE TO HAVE (Später)**
- [ ] Performance-Optimierung für große Models
- [ ] Cache-Management UI (Clear, View, Export)
- [ ] Support für Regelgruppen/Hierarchien in InfoZoom
- [ ] Reverse-Mapping: InfoZoom → NEMO

---

## 🛠️ Technische Details zum Starten

### Backend Server starten
```bash
cd "C:\Users\temmers_m\OneDrive - proALPHA Group\projekte\Dev\nemo_deficiencies"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Test-Model vorbereiten
Nutze dein echtes NEMO-Model oder das Minimal-Example aus den Tests:

```python
# Minimal model für ersten Test
model = {
    "name": "Test Export",
    "source": {
        "attributes": [
            {"name": "CUSTOMER_ID", "comment": "Kunde ID"},
            {"name": "NAME", "comment": "Kundenname"}
        ]
    },
    "checks": {
        "groups": [
            {
                "field": "CUSTOMER_ID",
                "displayName": "Customer ID",
                "internalName": "customer_id",
                "rules": [
                    {
                        "id": "rule_1",
                        "condition": "CUSTOMER_ID IS NOT NULL",
                        "message": "ID required",
                        "dimension": "Completeness",
                        "active": True
                    }
                ]
            }
        ]
    }
}
```

### Cache inspizieren nach Export
```bash
# Anschauen was gecacht wurde
type .cache\infozoom_rules.json

# Fehler anschauen
type .cache\infozoom_errors.json
```

---

## ✅ Checklist für Erfolg

Nach dem ersten erfolgreichen Test kannst du abhaken:

- [ ] SDK License aktiviert (InfoZoom GUI)
- [ ] Test-Export ohne Fehler durchgeführt
- [ ] .fox-Datei > 0 KB erstellt
- [ ] .fox-Datei in InfoZoom 2026 öffnet
- [ ] Attribute sind sichtbar
- [ ] Validierungsregeln sind übersetzt
- [ ] Cache wurde gefüllt (`.cache/infozoom_rules.json` existiert)
- [ ] Keine Fehler in `.cache/infozoom_errors.json`

---

## 🎓 Debugging bei Problemen

### Problem: "API_FUNCTION_NOT_LICENSED"
**Ursache:** License nicht in InfoZoom GUI aktiviert
**Lösung:** Tools → Lizenzen → YESSQ-VM8UG-NJELF-P5SXC-UYEW4 → Speichern

### Problem: ".fox-Datei ist 0 Bytes"
**Ursache:** SDK-Fehler beim create_document
**Lösung:** Schaue `.cache/infozoom_errors.json` und Backend-Logs

### Problem: "Cannot find COM object"
**Ursache:** DLLs nicht registriert
**Lösung:** Neu registrieren (als Admin):
```batch
regsvr32 "C:\Program Files (x86)\Common Files\nemo\InfoZoom SDK\9.100\Table2COM.dll"
regsvr32 "C:\Program Files (x86)\Common Files\nemo\InfoZoom SDK\9.100\izsdk.dll"
```

### Problem: "Regeln werden nicht übersetzt"
**Ursache:** Unsupported SQL-Syntax
**Lösung:** 
1. Fehler in `.cache/infozoom_errors.json` anschauen
2. `condition_translator.py` erweitern für neuen Regeltyp

---

## 📞 Nächster Checkpoint

Nach dem ersten erfolgreichen Export:
1. **Zeige mir die .fox-Datei-Größe und den Cache-Status**
2. **Liste alle Fehler aus dem Error-Log**
3. **Screenshot der .fox-Datei in InfoZoom (falls öffnet)**

Dann können wir:
- Fehlende SQL-Funktionen implementieren
- Performance weiter optimieren
- Frontend-Integration machen

---

**Startpunkt:** Backend starten und erste API-Anfrage senden! 🚀
