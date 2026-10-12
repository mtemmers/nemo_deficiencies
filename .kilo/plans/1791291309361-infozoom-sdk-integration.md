# InfoZoom SDK Integration Plan

**Goal:** Integrate InfoZoom SDK 9.100 with Python to programmatically create InfoZoom data files containing deficiency/validation data from the nemo_deficiencies system.

**License:** V3559-9JHW4-TRWXY-RBEND-KVAB5 (provided)

---

## 1. Current State Analysis

### What Exists
- **Backend export connector system** (`backend/export_connectors/`) with pluggable format handlers
- **InfoZoomExportConnector** (`infozoom_connector.py`) - generates text-format structure definitions for manual import
- **Export API endpoint** (`backend/main.py`) - handles format-specific exports
- **Test coverage** (`tests/test_export_connectors.py`) - validates current text export

### What's Missing
- Python wrapper for InfoZoom COM interface
- License activation mechanism
- Programmatic file creation (currently only text export exists)
- Integration between nemo data model and InfoZoom SDK objects

---

## 2. Technical Architecture

### InfoZoom SDK Integration Layer
**New module:** `backend/export_connectors/infozoom_sdk_wrapper.py`

Purpose: Encapsulate all COM/pywin32 interactions with InfoZoom SDK

**Responsibilities:**
1. Load and register license code (`V3559-9JHW4-TRWXY-RBEND-KVAB5`)
2. Create InfoZoom COM objects via `win32com.client`
3. Expose methods for:
   - Creating new InfoZoom projects
   - Adding base attributes (columns)
   - Adding derived attributes (calculated fields)
   - Setting up validation rules
   - Persisting to file format

**Key Decisions:**
- Use `pywin32` library for COM automation (standard Windows Python integration)
- Separate licensing concern from data manipulation logic
- Handle COM initialization errors gracefully (SDK not installed, license invalid, etc.)
- No direct dependency on InfoZoom file format internals — rely on COM API

### Enhanced InfoZoomExportConnector
**File:** `backend/export_connectors/infozoom_connector.py` (modify existing)

**Changes:**
1. Add new export mode: `"sdk_native"` (creates actual InfoZoom files, requires SDK + license)
2. Keep existing `"text_definition"` mode (text export, no SDK required)
3. Add `get_options_schema()` to expose mode selection to UI
4. Detect SDK availability at runtime and warn if unavailable

**Integration points:**
- New method: `export_to_file()` - writes binary InfoZoom file using SDK
- Existing method: `export()` - returns text (used for non-SDK mode)
- Leverage existing `_cascader` utilities for rule descriptions

---

## 3. Data Flow: nemo → InfoZoom

### Input Data Structure (from nemo)
```
Editor Model:
  - report: {id, displayName, internalName}
  - source.attributes: [{name, comment, type}, ...]
  - checks.groups[]: 
      - field: attribute name
      - displayName: user-friendly label
      - rules: [{condition, message, dimension, active}, ...]
```

### Output: InfoZoom File Structure
```
InfoZoom Project:
  [Base Attributes]
    CUSTOMER_ID
    EMAIL
    ZIP_CODE
    ... (maps to source.attributes)

  [Derived Attributes / Validation Fields]
    CUSTOMER_ID_Validation
      ├─ Source field: CUSTOMER_ID
      ├─ Rule 1: IF (condition) THEN (message)
      ├─ Rule 2: IF (condition) THEN (message)
      └─ ... cascaded evaluation

    EMAIL_Validation
      ├─ Source field: EMAIL
      └─ ... (similar structure)
```

---

## 4. Implementation Tasks

### Phase 1: Dependency & License Setup
1. Install `pywin32` (`pip install pywin32`)
2. Run post-install script for COM registration
3. Create license credential store (environment variable or config file)
4. Write unit test for license activation

### Phase 2: SDK Wrapper Development
1. Implement `InfoZoomSDKWrapper` class with:
   - `__init__(license_code: str)` - activate license
   - `create_project(name: str) -> Project` - new InfoZoom project object
   - `add_attribute(project, name: str, comment: str) -> Attribute`
   - `add_derived_attribute(project, name: str, expression: str) -> DerivedAttribute`
   - Error handling for:
     - SDK not installed (ImportError for win32com)
     - License invalid (COM exception from SDK)
     - File write failures
   - Documentation with COM API reference

2. Write integration tests (mocked COM objects if SDK not installed in CI)

### Phase 3: Connector Enhancement
1. Modify `InfoZoomExportConnector`:
   - Add `mode` option to `get_options_schema()`
   - Detect SDK availability in `validate()` method
   - Route to text export or SDK export based on mode

2. Create `export_to_file(model, output_path, options)`:
   - Use wrapper to create project
   - Populate base attributes
   - Build cascaded validation rules
   - Write to InfoZoom native format

3. Update tests to cover both modes

### Phase 4: API & Frontend Integration
1. Update export endpoint to support file write operations
2. Add mode selection UI (text vs. SDK native)
3. Add download handler for binary InfoZoom files
4. Update API documentation

### Phase 5: Validation & Testing
1. Test end-to-end with sample deficiency data
2. Verify file compatibility (open generated files in InfoZoom application)
3. Performance testing with large rule sets
4. Error handling for missing/invalid license

---

## 5. Configuration & Deployment

### Environment Setup
**Option A: Environment Variable (recommended for development)**
```
INFOZOOM_LICENSE_CODE=V3559-9JHW4-TRWXY-RBEND-KVAB5
```

**Option B: Configuration File (`config/infozoom.json`)**
```json
{
  "license_code": "V3559-9JHW4-TRWXY-RBEND-KVAB5"
}
```

### Windows Requirements
- Windows 64-bit OS (as per SDK spec)
- 4+ GB RAM
- InfoZoom SDK installed (`InfoZoom_SDK_x64_2026_de-DE.exe`)
- pywin32 (with COM enabled)

### Fallback Behavior
- If SDK unavailable: degrade to text export with warning
- If license invalid: raise clear error with remediation steps
- If file write fails: return error response, no partial files

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| InfoZoom COM API complexity | Implementation delay | Create minimal wrapper first, expand gradually |
| License binding to machine | License tied to hardware | Document activation process; use environment variable |
| File format compatibility | Generated files unreadable | Test early with InfoZoom application |
| Large rule set performance | Timeout/memory issues | Implement streaming/batch processing if needed |
| SDK not installed in deployment | Runtime failures | Graceful degradation to text export + clear warnings |
| Windows-only limitation | No cross-platform support | Document requirement; consider API-based alternative for future |

---

## 7. Success Criteria

✅ Python can successfully activate InfoZoom SDK with provided license code
✅ New connector mode generates valid InfoZoom files readable by InfoZoom application
✅ Text export mode remains unaffected (backward compatible)
✅ Both modes available in export API with clear option selection
✅ Error messages guide users when SDK unavailable
✅ End-to-end test: sample deficiency data → valid InfoZoom file
✅ All existing tests pass; new tests for SDK integration

---

## 8. Open Questions / Scope Boundaries

**Out of scope for this plan:**
- InfoZoom desktop application UI integration
- Real-time sync with InfoZoom
- Multi-file batch operations
- InfoZoom report generation (reports created from files separately)

**Assumptions:**
- InfoZoom SDK will be installed on the machine running nemo_deficiencies
- License code is valid and activation will succeed
- COM interface is stable across InfoZoom versions

---

## 9. Next Steps for Implementation

1. ✅ **Planning complete** - This document
2. → **Install SDK & dependencies** - Run InfoZoom installer and `pip install pywin32`
3. → **Build wrapper** - Implement `InfoZoomSDKWrapper` with basic project creation
4. → **Test wrapper** - Verify license activation and COM object creation
5. → **Enhance connector** - Add mode selection and SDK export path
6. → **End-to-end validation** - Generate test file and verify in InfoZoom app
