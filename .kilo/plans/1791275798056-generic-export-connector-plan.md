# Plan: Generic Export Connector Framework für Rule Sets

**Status:** Implementation-Ready  
**Date:** 2026-10-06  
**Owner:** Rule Export Architecture

---

## Übersicht

Ziel ist ein **generisches Export-Framework** für Regelsätze mit folgenden Zielformaten:
1. **MSSQL** – T-SQL Validierungsskript (wie aktuelles SQL, nur MSSQL-Syntax)
2. **JSON** – Austausch-/Dokumentationsformat (Regelmetadaten, nicht selbst validierend)
3. **InfoZoom** – Struktur + kaskadierte abgeleitete Attribute pro Feld (Text-Definition für manuellen Import)

Später optional: InfoZoom SDK Integration, Custom Connectors.

---

## Design-Entscheidungen (Geklärt)

| Entscheidung | Wert | Begründung |
|---|---|---|
| **Austausch-Format** | JSON (Pivot) | Neutral, alle Connectoren konvertieren intern über JSON |
| **InfoZoom-Export** | Regellogik-Übersetzung + Textbeschreibung Englisch | Nutzer mappen Daten später selbst in InfoZoom |
| **MSSQL-Export** | T-SQL Validierungsskript (CTEs, Cascade) | Gleiche Struktur wie aktuelles SQL, nur andere Syntax |
| **JSON-Sichtbarkeit** | User-sichtbar im UI (nicht nur intern) | Für technische Nutzer / API-Konsumenten |
| **Connector Registry** | Auto-discovery (Plugin-Pattern) | Einfach neue `.py`-Datei ablegen → wird geladen |
| **Fehlerbehandlung** | Validierung im Output (nicht vorher) | Versuch konvertieren, zeige Warnungen in Output |
| **External Libraries** | Standard-Library nur, SDK später optional | Minimale Dependencies jetzt, erweiterbar |
| **UI-Platzierung** | Dropdown-Menü "Export" im Expert-Mode (ersetzt "SQL exportieren") | Minimalistisch, alle Formate zugänglich |
| **UI-Optionen** | Modal pro Format (für MSSQL: "Create & Insert" Option) | Zukunftssicher für Format-spezifische Konfiguration |
| **Cascade-Reihenfolge** | Nach Editor-Reihenfolge (von oben nach unten) | Deterministisch, User kontrolliert via Editor |
| **JSON-Scope** | Nur Definitions-Metadaten (keine Cascade-Logik selbst) | Cascade ist Implementierungsdetail pro Target |

---

## Architektur

### 1. Core: `backend/export_connectors/`

```
backend/export_connectors/
├── __init__.py                    # Auto-discovery Registry
├── base.py                        # AbstractExportConnector (ABC)
├── json_connector.py              # JSONExportConnector
├── mssql_connector.py             # MSSQLExportConnector
├── infozoom_connector.py          # InfoZoomExportConnector
└── utils/
    ├── condition_translator.py    # SQL/Bedingung → Format-agnostisch übersetzen
    └── field_cascader.py          # Kaskadierungs-Logik für abgeleitete Attribute
```

### 2. Registry Pattern (Auto-Discovery)

**`backend/export_connectors/__init__.py`:**
```python
# Laden aller Connector-Klassen automatisch
from pathlib import Path
import importlib

_CONNECTORS = {}

def register_connector(name: str, connector_class):
    """Registriere einen Connector global."""
    _CONNECTORS[name] = connector_class

def get_connectors() -> Dict[str, type]:
    """Alle verfügbaren Connectoren zurückgeben."""
    return _CONNECTORS.copy()

# Auto-discovery: Alle Module in diesem Paket durchsuchen
def _discover_connectors():
    module_dir = Path(__file__).parent
    for module_file in module_dir.glob("*_connector.py"):
        if module_file.name.startswith("_"):
            continue
        module_name = module_file.stem
        importlib.import_module(f"backend.export_connectors.{module_name}")

_discover_connectors()
```

### 3. Base Class: `backend/export_connectors/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ExportConnector(ABC):
    """Basis-Klasse für alle Export-Connectoren."""
    
    # Metadata
    name: str                    # z.B. "mssql", "json", "infozoom"
    display_name: str            # z.B. "Microsoft SQL Server (T-SQL)"
    description: str
    version: str                 # z.B. "1.0"
    
    @abstractmethod
    def validate(self, model: Dict[str, Any]) -> List[str]:
        """
        Validiere, ob das Modell exportierbar ist.
        Returns: Liste von Warnungen (oder leer wenn alles OK).
        """
        pass
    
    @abstractmethod
    def export(self, model: Dict[str, Any], options: Dict[str, Any] = None) -> str:
        """
        Exportiere das Modell ins Zielformat.
        
        Args:
            model: Editor-Modell (mit checks.groups, source.attributes, etc.)
            options: Format-spezifische Optionen (z.B. {"mssql_mode": "create_and_insert"})
        
        Returns: Export-String (SQL, JSON, Text, etc.)
        
        Raises: ExportConnectorError bei nicht behebbaren Fehlern
        """
        pass
    
    def get_options_schema(self) -> Dict[str, Any]:
        """
        Optional: Rückgabe des Optionen-Schemas für UI-Modal.
        z.B. {"mssql_mode": {"type": "select", "options": ["create_and_insert", "insert_only"]}}
        """
        return {}

class ExportConnectorError(Exception):
    pass
```

### 4. Connectoren (Konkrete Implementierung)

#### A. JSON Connector
**`backend/export_connectors/json_connector.py`:**
- Export: `{version, report, groups[{internalName, displayName, rules[]}], ...}`
- Scope: Nur Definitions-Metadaten (kein Cascade-Output)
- Format-spezifische Logik: Minimal
- Warnungen: Keine (JSON sollte immer exportierbar sein)

#### B. MSSQL Connector
**`backend/export_connectors/mssql_connector.py`:**
- **Eingabe:** Editor-Modell + `checks.groups[]` mit Regeln
- **Prozess:** 
  1. Konvertiere SQL-Bedingungen von NEMO-Syntax zu T-SQL
  2. Baue kaskadierte `CASE WHEN` pro Feld (wie aktuelles SQL)
  3. Generiere T-SQL CTEs + Final SELECT
  4. Warnungen für nicht konvertierbare Bedingungen hinzufügen
- **Output:** T-SQL Validierungsskript
- **Optionen:** `{"mode": "create_and_insert"}` oder `{"mode": "insert_only"}`
- **Warnungen:** Bei CASE WHEN, komplexen Expressions, etc.

#### C. InfoZoom Connector
**`backend/export_connectors/infozoom_connector.py`:**
- **Eingabe:** Editor-Modell + `source.attributes[]` (Feldstruktur)
- **Prozess:**
  1. **Phase 1: Struktur-Definition** – Definiere Basis-Attribute (Spalten) aus `source.attributes`
  2. **Phase 2: Abgeleitete Attribute** – Pro Feld (z.B. `ZipCode`), baue ein Attribut `ZipCode_Validation`:
     - Kaskadiere Regeln nach Editor-Reihenfolge
     - Übersetze Bedingungen zu Englisch (readable descriptions)
     - Output: "ZipCode empty" oder "ZipCode not 5 digits (DE)" oder leer
  3. Format als Text-Definition für manuellen Import in InfoZoom
- **Output:** Text-formatierte Struktur + Attribute für manuellen InfoZoom-Import
- **Optionen:** Optional später `{"include_descriptions": true}`
- **Warnungen:** Bei komplexen Bedingungen, die nicht sinnvoll beschreibbar sind

### 5. Utility-Module

#### A. `backend/export_connectors/utils/condition_translator.py`
Konvertiert NEMO-SQL-Bedingungen zu verschiedenen Ziel-Syntaxen:
```python
class ConditionTranslator:
    def to_mssql(self, condition: str) -> (str, Optional[str]):
        """Übersetze NEMO-Bedingung zu T-SQL. Rückgabe: (sql, warning)"""
        pass
    
    def to_description_en(self, condition: str, field_name: str) -> str:
        """Übersetze zu English-Textbeschreibung für InfoZoom."""
        # z.B. "FIELD_A IS NOT NULL" → "Field A is required"
        pass
```

#### B. `backend/export_connectors/utils/field_cascader.py`
Kaskadierungs-Logik pro Feld:
```python
class FieldCascader:
    def build_cascade(self, field: Dict, rules: List[Dict], target_format: str) -> str:
        """
        Baue kaskadierte Regel-Ausgabe für ein Feld.
        
        target_format: "mssql", "infozoom", etc.
        
        Returns: T-SQL CASE WHEN oder Text-Beschreibung
        """
        pass
```

---

## API-Änderungen

### 1. Neuer Endpoint: `POST /api/editor/{report_ref}/export`

**Request:**
```json
{
  "model": { /* Editor-Modell */ },
  "format": "mssql|json|infozoom",
  "options": {
    "mssql_mode": "create_and_insert",
    "language": "en"
  }
}
```

**Response:**
```json
{
  "success": true,
  "format": "mssql",
  "filename": "report_validation.sql",
  "content": "/* SQL Content */",
  "warnings": [
    "Rule 'Rule_X' uses CASE WHEN (simplified for MSSQL)"
  ],
  "validation_summary": {
    "total_rules": 42,
    "exportable_rules": 40,
    "with_warnings": 2
  }
}
```

### 2. UI: Export-Dropdown (ersetzt "SQL exportieren")

**Vorher (Expert-Mode):**
```
Button "SQL exportieren" → direkter Download
```

**Nachher (Expert-Mode):**
```
Dropdown "Export ▼"
├─ SQL (MSSQL)        → öffnet Modal mit Optionen
├─ JSON               → direkter Download
└─ InfoZoom           → direkter Download (Text)
```

**Modal Struktur (für MSSQL):**
```
Title: "Export als MSSQL"
Field: "Export-Modus"
  - Radio "Create Table + Inserts" (default)
  - Radio "Inserts only (für bestehende Tabelle)"
Button "Exportieren"
```

---

## Implementierungs-Sequenz

### Phase 1: Foundation (Core Framework)
1. Erstelle `backend/export_connectors/base.py` – AbstractExportConnector
2. Erstelle `backend/export_connectors/__init__.py` – Auto-discovery Registry
3. Erstelle `backend/export_connectors/utils/condition_translator.py` – Basis-Translator
4. Erstelle `backend/export_connectors/utils/field_cascader.py` – Cascade-Logik

### Phase 2: Connectoren (einfach → komplex)
5. Implementiere `backend/export_connectors/json_connector.py`
6. Implementiere `backend/export_connectors/mssql_connector.py`
7. Implementiere `backend/export_connectors/infozoom_connector.py`

### Phase 3: API & Integration
8. Neuer Endpoint `POST /api/editor/{report_ref}/export` in `backend/main.py`
9. Tests schreiben: `tests/test_export_connectors.py`

### Phase 4: UI
10. Frontend-Dropdown "Export" (ersetzt "SQL exportieren") in `backend/frontend/index.html`
11. JavaScript Export-Handler + Modal in `backend/frontend/app.js`

### Phase 5: Validierung & Dokumentation
12. Tests für jeden Connector mit Sample-Modellen
13. Dokumentation: README für Custom Connector Development

---

## Datenfluss

```
Editor-Modell (checks.groups, source.attributes, etc.)
    ↓
POST /api/editor/{ref}/export?format=mssql&options={...}
    ↓
ExportConnector Registry.get("mssql")
    ↓
MSSQLConnector.validate() → Warnungen?
    ↓
MSSQLConnector.export() → T-SQL String
    ↓
Warnungen + Content zurückgeben
    ↓
Frontend: Modal "Export fertig, X Warnungen"
    ↓
User: "Exportieren bestätigen" → Download
```

---

## Fehlerbehandlung & Validierung

### Validierung im Output (nicht vorher)
- Jeder Connector versucht **bestmöglich zu konvertieren**
- Nicht konvertierbare Regeln bekommen `[WARNING: ...]` Markierungen im Output
- Summary am Anfang/Ende des Exports: "42 rules, 2 with warnings"
- User entscheidet selbst, ob Output brauchbar ist

### Beispiel MSSQL-Warning:
```sql
-- WARNING: Rule 'Rule_5' uses CASE WHEN syntax (simplified)
-- Original: CASE WHEN [X] > 0 THEN 'A' ELSE 'B' END
-- Simplified to: CASE WHEN [X] > 0 THEN 1 ELSE 0 END
```

---

## Erweiterbarkeit: Custom Connector Example

Ein Nutzer kann einen **eigenen Connector** hinzufügen:

**`backend/export_connectors/custom_xml_connector.py`:**
```python
from backend.export_connectors.base import ExportConnector, register_connector

class XMLExportConnector(ExportConnector):
    name = "xml"
    display_name = "XML (Custom)"
    version = "1.0"
    
    def validate(self, model):
        return []  # Immer OK
    
    def export(self, model, options=None):
        # XML-Generierung...
        return "<rules>...</rules>"

register_connector("xml", XMLExportConnector)
```

Beim nächsten Start: Auto-discovery lädt es → verfügbar im UI Dropdown.

---

## Testing-Strategie

### Unit Tests: `tests/test_export_connectors.py`
- **JSON Connector:** Sample Model → Valides JSON Schema
- **MSSQL Connector:** Sample Model → Valides T-SQL (parse + validate syntax)
- **InfoZoom Connector:** Sample Model → Readable Attribute Descriptions

### Integration Tests
- End-to-End: Editor Model → API Call → Export Download
- Warnungs-Handling: Komplexe Bedingungen → Warnings im Output

### Validierungsmuster
```python
def test_mssql_export_with_warnings(sample_model):
    connector = MSSQLConnector()
    result = connector.export(sample_model, {"mode": "create_and_insert"})
    assert "CREATE TABLE" in result
    assert "WARNING" in result
    assert "[ERROR:" not in result  # Sollte trotz Warnings durchlaufen
```

---

## Offene Fragen (Out-of-Scope, aber dokumentiert)

1. **InfoZoom SDK Integration** – Später: API-Calls statt Text-Export?
2. **Performance bei sehr großen Regelsets** – Später: Caching/Optimization?
3. **Custom Field Mapping** – Später: Nutzer mappen NEMO-Felder zu anderen Namen?
4. **Versioning der Export-Formate** – Später: Backup-Kompatibilität bei Schema-Änderungen?

---

## Abhängigkeiten & Risiken

### Abhängigkeiten
- `sql_model.py` & `sql_generator.py` müssen geklärt sein (Condition-Struktur, Feld-Metadaten)
- Bestehender SQL-Export-Code als Referenz für MSSQL-Connector

### Risiken
- **SQL-Konvertierung:** NEMO-Syntax → T-SQL ist komplex. Lösung: Starker Test-Fall-Katalog.
- **InfoZoom Text-Format:** Unklar, wie InfoZoom-Nutzer das importiert. Lösung: Dokumentation + Beispiel.
- **Zukünftige Format-Anforderungen:** Viele neue Connectoren geplant? Lösung: Auto-discovery + Plugin-Pattern macht es einfach.

---

## Rollout

1. **Phase 1-3** implementieren (Framework + 3 Connectoren + API)
2. **Phase 4** UI hinzufügen
3. **Phase 5** Tests + QA
4. **Go-Live:** Export-Dropdown im Expert-Mode, SQL-Button ersetzt

---

## Success Criteria

- ✅ Nutzer kann im Editor "Export" Dropdown nutzen
- ✅ MSSQL-Export erzeugt valides T-SQL (validierbar mit SQL Server)
- ✅ JSON-Export importierbar von Downstream-Systemen
- ✅ InfoZoom-Export liefert lesbare Struktur für manuellen Import
- ✅ Neue Connectoren können einfach hinzugefügt werden (kein Core-Change nötig)
- ✅ Warnungen werden transparent im Output gezeigt
