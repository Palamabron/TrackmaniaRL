"""Physical-pixel Windows client geometry for opt-in game capture.

Native APIs are loaded only when the Windows integration is instantiated.
The per-thread DPI context is restored after every operation.
"""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from ctypes import wintypes
from time import monotonic, sleep
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from trackmaniarl.core.environment_errors import EnvironmentPausedError


class WindowCaptureConfig(BaseModel):
    """Restore a fixed client size each episode; track its physical screen origin."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    title: str = Field(default="Trackmania", min_length=1)
    client_width: int = Field(default=1280, ge=320, le=8192)
    client_height: int = Field(default=720, ge=180, le=8192)
    resize_timeout_s: float = Field(default=2.0, gt=0, le=10)
    settle_s: float = Field(default=0.2, ge=0, le=2)


class CaptureWindowError(RuntimeError):
    """The client cannot be captured without changing the observation contract."""


class CaptureWindowUnavailableError(CaptureWindowError, EnvironmentPausedError):
    """Wait for the user to restore the window; never steal foreground focus."""


class _MonitorInfo(ctypes.Structure):
    _fields_ = [
        ("size", wintypes.DWORD),
        ("monitor", wintypes.RECT),
        ("work", wintypes.RECT),
        ("flags", wintypes.DWORD),
    ]


def _user32() -> Any:
    if sys.platform != "win32":
        raise RuntimeError(
            "window_capture requires Windows; use capture for a fixed desktop region"
        )
    loader = getattr(ctypes, "WinDLL", None)
    if loader is None:
        raise RuntimeError("Windows native API loader is unavailable")
    library = loader("user32", use_last_error=True)
    signatures = {
        "SetThreadDpiAwarenessContext": ([ctypes.c_void_p], ctypes.c_void_p),
        "GetClientRect": ([wintypes.HWND, ctypes.POINTER(wintypes.RECT)], wintypes.BOOL),
        "GetWindowRect": ([wintypes.HWND, ctypes.POINTER(wintypes.RECT)], wintypes.BOOL),
        "ClientToScreen": ([wintypes.HWND, ctypes.POINTER(wintypes.POINT)], wintypes.BOOL),
        "IsWindow": ([wintypes.HWND], wintypes.BOOL),
        "IsWindowVisible": ([wintypes.HWND], wintypes.BOOL),
        "IsIconic": ([wintypes.HWND], wintypes.BOOL),
        "GetForegroundWindow": ([], wintypes.HWND),
        "GetWindowTextLengthW": ([wintypes.HWND], ctypes.c_int),
        "GetWindowTextW": ([wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),
        "SetWindowPos": (
            [
                wintypes.HWND,
                wintypes.HWND,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                wintypes.UINT,
            ],
            wintypes.BOOL,
        ),
        "MonitorFromWindow": ([wintypes.HWND, wintypes.DWORD], wintypes.HANDLE),
        "GetMonitorInfoW": ([wintypes.HANDLE, ctypes.POINTER(_MonitorInfo)], wintypes.BOOL),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    return library


class WindowsClientCapture:
    """Locate a unique visible window, resize on reset, and validate every capture."""

    def __init__(self, config: WindowCaptureConfig) -> None:
        self.config = config
        self._api = _user32()
        self._handle: int | None = None

    @contextmanager
    def physical_pixels(self) -> Iterator[None]:
        """Use the same physical coordinate space for geometry and desktop capture."""
        previous = self._api.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
        if not previous:
            raise CaptureWindowError("Cannot enable per-monitor physical-pixel capture")
        try:
            yield
        finally:
            self._api.SetThreadDpiAwarenessContext(previous)

    def _find(self) -> int:
        matches: list[int] = []

        def visit(handle: int, parameter: int) -> bool:
            del parameter
            size = self._api.GetWindowTextLengthW(handle) + 1
            title = ctypes.create_unicode_buffer(size)
            self._api.GetWindowTextW(handle, title, size)
            if title.value == self.config.title and self._api.IsWindowVisible(handle):
                matches.append(handle)
            return True

        callback_factory = getattr(ctypes, "WINFUNCTYPE", None)
        if callback_factory is None:
            raise CaptureWindowError("Windows callback support is unavailable")
        callback_type = callback_factory(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        self._api.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
        self._api.EnumWindows.restype = wintypes.BOOL
        if not self._api.EnumWindows(callback_type(visit), 0):
            raise CaptureWindowError("Cannot enumerate capture windows")
        if not matches:
            raise CaptureWindowUnavailableError(f"Waiting for visible {self.config.title!r} window")
        if len(matches) != 1:
            raise CaptureWindowError(
                f"Expected one visible {self.config.title!r} window; found {len(matches)}"
            )
        return matches[0]

    def _bounds(self, *, check_monitor: bool = True) -> dict[str, int]:
        handle = self._handle
        if not handle or not self._api.IsWindow(handle) or self._api.IsIconic(handle):
            raise CaptureWindowUnavailableError("Game window is missing or minimized")
        if not self._api.IsWindowVisible(handle) or self._api.GetForegroundWindow() != handle:
            raise CaptureWindowUnavailableError(
                "Keep the game window visible and in the foreground"
            )
        rect, origin = wintypes.RECT(), wintypes.POINT()
        if not self._api.GetClientRect(handle, ctypes.byref(rect)) or not self._api.ClientToScreen(
            handle, ctypes.byref(origin)
        ):
            raise CaptureWindowError("Cannot read the game client rectangle")
        region = {"left": origin.x, "top": origin.y, "width": rect.right, "height": rect.bottom}
        if check_monitor:
            self._check_monitor(region)
        return region

    def _monitor_info(self) -> _MonitorInfo:
        monitor = self._api.MonitorFromWindow(self._handle, 2)
        info = _MonitorInfo()
        info.size = ctypes.sizeof(info)
        if not monitor or not self._api.GetMonitorInfoW(monitor, ctypes.byref(info)):
            raise CaptureWindowError("Game window is outside the available monitors")
        return info

    def _check_monitor(self, region: dict[str, int]) -> None:
        rect = self._monitor_info().monitor
        if (
            region["width"] <= 0
            or region["height"] <= 0
            or region["left"] < rect.left
            or region["top"] < rect.top
            or region["left"] + region["width"] > rect.right
            or region["top"] + region["height"] > rect.bottom
        ):
            raise CaptureWindowUnavailableError("Keep the entire game client area on one monitor")

    def prepare_episode(self) -> dict[str, int]:
        with self.physical_pixels():
            self._handle = self._find()
            region = self._bounds(check_monitor=False)
            outer = wintypes.RECT()
            if not self._api.GetWindowRect(self._handle, ctypes.byref(outer)):
                raise CaptureWindowError("Cannot determine the window frame size")
            width = self.config.client_width + outer.right - outer.left - region["width"]
            height = self.config.client_height + outer.bottom - outer.top - region["height"]
            work = self._monitor_info().work
            if width > work.right - work.left or height > work.bottom - work.top:
                raise CaptureWindowError("Configured game size does not fit the monitor work area")
            left = max(work.left, min(outer.left, work.right - width))
            top = max(work.top, min(outer.top, work.bottom - height))
            if self._correct_size(region) and (left, top) == (outer.left, outer.top):
                return self.bounds()
            # Preserve focus/z-order; move only when needed to fit on the monitor.
            if not self._api.SetWindowPos(self._handle, None, left, top, width, height, 0x0014):
                raise CaptureWindowError("Cannot resize the game; use a resizable windowed mode")
            deadline = monotonic() + self.config.resize_timeout_s
            while monotonic() < deadline:
                sleep(0.05)
                region = self._bounds()
                if self._correct_size(region):
                    sleep(self.config.settle_s)
                    return self.bounds()
            raise CaptureWindowError("Game rejected the configured client size; use windowed mode")

    def _correct_size(self, region: dict[str, int]) -> bool:
        return (region["width"], region["height"]) == (
            self.config.client_width,
            self.config.client_height,
        )

    def bounds(self) -> dict[str, int]:
        with self.physical_pixels():
            region = self._bounds()
            if not self._correct_size(region):
                raise CaptureWindowUnavailableError(
                    "Game resized during an episode; restart before collecting more data"
                )
            return region
