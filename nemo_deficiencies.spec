# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_all, collect_submodules

project_root = Path(SPEC).resolve().parent
datas = [(str(project_root / "backend" / "frontend"), "backend/frontend")]
binaries = []
hiddenimports = collect_submodules("uvicorn")

for package_name in ("nemo_library",):
    package_datas, package_binaries, package_hiddenimports = collect_all(package_name)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += [
        module_name
        for module_name in package_hiddenimports
        if not module_name.startswith("nemo_library.ui")
    ]

conda_runtime_dir = Path(sys.prefix) / "Library" / "bin"
for dll_name in (
    "liblzma.dll",
    "libbz2.dll",
    "libmpdec-4.dll",
    "libcrypto-3-x64.dll",
    "libssl-3-x64.dll",
    "ffi.dll",
    "libexpat.dll",
):
    dll_path = conda_runtime_dir / dll_name
    if dll_path.exists():
        binaries.append((str(dll_path), "."))

a = Analysis(
    ["backend/desktop.py"],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="NEMO Deficiencies",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="NEMO Deficiencies",
)
