# InfoZoom SDK Integration – Setup Guide

## Overview

The NEMO Deficiencies export backend integrates with **InfoZoom SDK 9.100** (32-bit) to generate `.fox` binary files that can be opened directly in InfoZoom.

## Prerequisites

1. **Windows OS** (SDK is Windows-only; Linux/macOS not supported)
2. **InfoZoom SDK 9.100 (32-bit)** installed
3. **Python 3.10+** on Windows
4. **pywin32** package: `pip install pywin32`

## Installation Steps

### Step 1: Install InfoZoom SDK 9.100 (32-bit)

Run the installer:
```
InfoZoom_SDK_64_2026_0_5_0_de-DE\InfoZoom_SDK_x64_2026_de-DE.exe
```

⚠️ **Note**: Despite the filename containing "64", this is the correct 32-bit SDK for Python integration.

Post-installation, the SDK DLLs are located at:
```
C:\Program Files (x86)\Common Files\nemo\InfoZoom SDK\9.100\
```

### Step 2: Register SDK DLLs

The SDK requires COM registration for Python access. Run these commands in an **Administrator** Command Prompt:

```batch
cd "C:\Program Files (x86)\Common Files\nemo\InfoZoom SDK\9.100"
regsvr32.exe Table2COM.dll
regsvr32.exe izsdk.dll
regsvr32.exe ItfTable.dll
regsvr32.exe AxTable.dll
```

### Step 3: Activate License in InfoZoom

1. Open **InfoZoom 2026** (the main application, not the SDK)
2. Go to **Tools → Lizenzen** (or **Tools → Licenses** in English version)
3. Enter the license code: `YESSQ-VM8UG-NJELF-P5SXC-UYEW4`
4. Click **Speichern** (Save) or **Aktivieren** (Activate)

The license is stored in the system registry and is read by the SDK automatically.

### Step 4: Install pywin32

```bash
pip install pywin32
```

If running in an existing Python environment, you may also need:
```bash
python -m pip install --upgrade pywin32
python Scripts/pyinstall.py  # Or follow pywin32 post-install instructions
```

## Usage

### Via FastAPI Backend

The export endpoint supports `sdk_native` mode:

```bash
curl -X POST http://localhost:8000/api/export_editor_model \
  -H "Content-Type: application/json" \
  -d '{
    "format": "infozoom",
    "options": {
      "mode": "sdk_native"
    },
    "editor_model": { ... }
  }' \
  --output export.fox
```

The response is a binary `.fox` file suitable for opening in InfoZoom.

### Via Python

```python
from backend.export_connectors.infozoom_connector import InfoZoomExportConnector

connector = InfoZoomExportConnector()

# Create .fox file
result = connector.export_to_file(
    model=editor_model,
    output_path="/path/to/export.fox",
    options={"mode": "sdk_native"}
)

print(f"Exported to: {result}")
```

## Troubleshooting

### "API_FUNCTION_NOT_LICENSED"

**Cause**: License not activated in InfoZoom GUI.

**Solution**:
1. Open InfoZoom 2026
2. Go to **Tools → Lizenzen**
3. Ensure the license code is entered and saved
4. Try the export again

### "Cannot find COM object 'humanIT.Table2COM.Manager'"

**Cause**: SDK DLLs not registered.

**Solution**: Re-run the `regsvr32.exe` commands from Step 2 (as Administrator).

### "pywin32 module not found"

**Cause**: pywin32 not installed.

**Solution**:
```bash
pip install pywin32
```

### Export returns zero-byte `.fox` file

**Cause**: Attributes were not added correctly (e.g., due to license issue).

**Solution**: Check the server logs for `InfoZoomLicenseError` or `AddAttribute failed` messages.

## Architecture

- **`backend/export_connectors/infozoom_sdk_wrapper.py`**
  - Low-level COM wrapper
  - Manages `Manager.CreateNew`, `table.Attributes.AddAttribute()`, `Refresh()`, `SaveFileAs()`
  - Thread-safe singleton pattern for COM manager

- **`backend/export_connectors/infozoom_connector.py`**
  - High-level connector using the wrapper
  - Converts NEMO model structure to InfoZoom attributes
  - Translates cascaded validation rules to InfoZoom expressions

- **`backend/main.py` export endpoint**
  - Routes binary (`.fox`) responses differently from text responses
  - Returns `application/octet-stream` with `.fox` filename

## Testing

Unit tests are fully mocked and do not require SDK installation:

```bash
pytest tests/test_export_connectors.py -v
```

Integration tests would require the SDK and license to be active.

---

**Last Updated**: October 6, 2026  
**SDK Version**: 9.100 (32-bit)  
**License**: YESSQ-VM8UG-NJELF-P5SXC-UYEW4
