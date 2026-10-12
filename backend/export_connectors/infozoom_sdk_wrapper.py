r"""
InfoZoom SDK 9.100 wrapper for .fox file creation.

Uses COM (pywin32) to interact with the 32-bit Table2COM.Manager object.
Requires:
  1. InfoZoom SDK 9.100 (32-bit) installed
  2. All DLLs registered: regsvr32 Table2COM.dll, izsdk.dll, ItfTable.dll, AxTable.dll
  3. License activated in InfoZoom GUI before use (Tools > Lizenzen)
  4. Registry key: HKCU:\Software\humanIT\InfoZoom SDK\9.100
"""

import os
import tempfile
import threading
from typing import Any, Optional

# Platform check
import sys
if sys.platform != "win32":
    _HAS_WIN32COM = False
else:
    try:
        import win32com.client as win32
        import pywintypes
        _HAS_WIN32COM = True
    except ImportError:
        _HAS_WIN32COM = False


class InfoZoomSDKError(Exception):
    """Base InfoZoom SDK error."""
    pass


class InfoZoomSDKNotInstalledError(InfoZoomSDKError):
    """SDK or win32com not available."""
    pass


class InfoZoomLicenseError(InfoZoomSDKError):
    """License not activated."""
    pass


FOX_EXTENSION = ".fox"


def sdk_available() -> bool:
    """Check if SDK is available and properly registered."""
    if not _HAS_WIN32COM:
        return False
    try:
        _get_or_create_manager()
        return True
    except (InfoZoomSDKError, Exception):
        return False


class InfoZoomSDKWrapper:
    """COM wrapper for InfoZoom SDK table creation and export."""

    _manager_instance: Optional[Any] = None
    _init_lock = threading.Lock()
    _registry_path = "WOW6432Node\\humanIT\\InfoZoom SDK\\9.100"
    _progid = "humanIT.Table2COM.Manager"

    def create_document(
        self,
        output_path: str,
        base_attributes: list[dict],
        derived_attributes: list[dict],
    ) -> str:
        """
        Create and save an InfoZoom .fox document.

        Args:
            output_path: Full path to save .fox file
            base_attributes: List of {name, display_name, ...} dicts
            derived_attributes: List of {name, expression} dicts

        Returns:
            output_path on success

        Raises:
            InfoZoomSDKError: On SDK error
            InfoZoomLicenseError: If license not activated
        """
        if not _HAS_WIN32COM:
            raise InfoZoomSDKNotInstalledError(
                "pywin32 not installed. Run: pip install pywin32"
            )

        try:
            manager = _get_or_create_manager()
            table = manager.CreateNew

            # Add base attributes
            try:
                for attr in base_attributes:
                    table.Attributes.AddAttribute(attr.get("name", ""))
            except Exception as exc:
                if "API_FUNCTION_NOT_LICENSED" in str(exc) or "-2147221474" in str(exc):
                    raise InfoZoomLicenseError(
                        f"License not activated. Activate via InfoZoom GUI: Tools > Lizenzen. "
                        f"Code: YESSQ-VM8UG-NJELF-P5SXC-UYEW4"
                    ) from exc
                raise InfoZoomSDKError(f"AddAttribute failed: {exc}") from exc

            # Add derived attributes (expressions)
            try:
                for derived in derived_attributes:
                    table.Attributes.AddExpression(
                        derived.get("name", ""),
                        derived.get("expression", "1=1"),
                    )
            except Exception as exc:
                raise InfoZoomSDKError(f"AddExpression failed: {exc}") from exc

            # Refresh and save
            try:
                table.Refresh()
            except Exception as exc:
                raise InfoZoomSDKError(f"Refresh failed: {exc}") from exc

            try:
                # SaveFileAs with just path parameter (format auto-detected from extension)
                table.SaveFileAs(output_path)
            except Exception as exc:
                raise InfoZoomSDKError(
                    f"SaveFileAs failed: {exc}. Ensure .fox file has write permissions."
                ) from exc

            return output_path

        except (InfoZoomSDKError, InfoZoomLicenseError):
            raise
        except Exception as exc:
            raise InfoZoomSDKError(f"Unexpected error: {exc}") from exc

    def create_temp_document(
        self,
        base_attributes: list[dict],
        derived_attributes: list[dict],
    ) -> str:
        """Create .fox in temp directory. Returns path."""
        fd, tmp_path = tempfile.mkstemp(suffix=FOX_EXTENSION, prefix="nemo_infozoom_")
        os.close(fd)
        return self.create_document(tmp_path, base_attributes, derived_attributes)


def _get_or_create_manager() -> Any:
    """
    Get or create the COM manager singleton.

    Thread-safe double-checked locking pattern.
    """
    if InfoZoomSDKWrapper._manager_instance is not None:
        return InfoZoomSDKWrapper._manager_instance

    with InfoZoomSDKWrapper._init_lock:
        if InfoZoomSDKWrapper._manager_instance is not None:
            return InfoZoomSDKWrapper._manager_instance

        try:
            manager = win32.Dispatch(InfoZoomSDKWrapper._progid)
        except Exception as exc:
            raise InfoZoomSDKNotInstalledError(
                f"Failed to create COM object '{InfoZoomSDKWrapper._progid}'. "
                f"Ensure SDK DLLs are registered: "
                f"regsvr32 Table2COM.dll izsdk.dll ItfTable.dll AxTable.dll"
            ) from exc

        InfoZoomSDKWrapper._manager_instance = manager
        return manager
