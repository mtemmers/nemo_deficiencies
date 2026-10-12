# 64-bit InfoZoom SDK Installation Guide

## Quick Answer

**JA — 64-bit SDK sollte funktionieren!** ✅

Wenn du einen 64-bit SDK Installer hast, wird er mit 64-bit Python kompatibel sein.

---

## What We Found

✅ **64-bit Redistributable DLLs exist**: `C:\Program Files (x86)\NEMO\InfoZoom SDK 2026\Redistributable Code 64-bit\`
  - `Table2COM.dll` (566 KB 64-bit version)
  - `izsdk.dll` (11.5 MB 64-bit version)
  - `ItfTable.dll` (173 KB)
  - `AxTable.dll` (182 KB)

✅ **Universal Installer found**: `InfoZoom_SDK_2026_de-DE.exe` (56 MB)

❌ **Current issue**: Redistributable DLLs alone don't register properly
  - Error: "Klasse nicht registriert" (Class not registered)
  - Root cause: 64-bit DLLs need proper installer to register COM objects

---

## Solution: Re-run Installer for 64-bit

### Option A: Fresh 64-bit Installation (Recommended)

1. **Close any InfoZoom applications**
2. **Run**: `InfoZoom_SDK_2026_de-DE.exe`
3. **Choose**: 64-bit version during installation
4. **Let it install** to Program Files (64-bit paths)
5. **Reboot** if necessary
6. **Test with Python**:

```python
import win32com.client
manager = win32com.client.Dispatch("humanIT.Table2COM.Manager")
# Should work now!
```

### Option B: Side-by-Side 32-bit + 64-bit

Keep 32-bit and add 64-bit:

1. Run installer again
2. Choose "Install 64-bit components alongside 32-bit"
3. Let it install to appropriate directories
4. Both should work after COM registration

---

## After Installation: Run Tests

```bash
# Run integration tests
python -m pytest tests/test_integration_infozoom_sdk.py -v -s

# Expected: All 5 tests should PASS
# - test_fox_export_creates_file ✓
# - test_cache_populated_after_export ✓
# - test_text_mode_still_works ✓
# - test_error_log_recorded ✓
# - test_cache_reuse_on_second_export ✓
```

---

## What Happens After 64-bit Installation

1. **Python 64-bit** ↔ **64-bit COM DLL** ✓ (bitness match)
2. `win32com.Dispatch()` finds the COM object ✓
3. Manager is instantiated ✓
4. `.fox` files are generated ✓
5. Cache system works ✓

---

## If Installation Has Multiple Options

When running the installer, it may ask:

- **"Choose installation location"** → Accept default or choose Program Files (64-bit)
- **"Select components"** → Make sure "SDK 64-bit" or similar is checked
- **"Bitness"** → Choose 64-bit
- **"License type"** → Evaluation or existing license code

---

## Technical Details: Why 64-bit Works

| Aspect | 32-bit | 64-bit |
|--------|--------|--------|
| Python | 32-bit | **64-bit** ✓ |
| COM DLL | 32-bit | **64-bit** ✓ |
| Bitness Match | ❌ | ✅ |
| Result | COM access fails | COM access works |

**The key issue we had**: 64-bit Python trying to load 32-bit DLL = bitness mismatch.  
**Solution**: Install 64-bit SDK so DLLs match Python bitness.

---

## If Installer Doesn't Offer 64-bit Option

It might be an old installer. In that case:

1. Check if a newer SDK 64-bit installer exists
2. Or use 32-bit Python (as backup, already documented)
3. Contact humanIT support for 64-bit SDK availability

---

## Quick Checklist

- [ ] Run `InfoZoom_SDK_2026_de-DE.exe` installer
- [ ] Choose **64-bit** components during installation
- [ ] Complete installation
- [ ] Restart if prompted
- [ ] Set license code in InfoZoom GUI (Tools → Lizenzen)
- [ ] Run: `pytest tests/test_integration_infozoom_sdk.py -v`
- [ ] All tests should pass ✓

---

## Success Indicators

After 64-bit installation and running tests, you should see:

```
test_fox_export_creates_file PASSED
test_cache_populated_after_export PASSED
test_text_mode_still_works PASSED
test_error_log_recorded PASSED
test_cache_reuse_on_second_export PASSED

===== 5 PASSED in 2.3s =====
```

And `.fox` files will be generated successfully! 🎉

---

**Status**: Ready to install 64-bit SDK → Code will work immediately.
