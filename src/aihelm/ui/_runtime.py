"""Runtime helpers for Flet UI controls.

These helpers smooth over breaking changes between Flet versions, so the rest
of the UI code can express intent without sprinkling `try/except` blocks.
"""

from __future__ import annotations

import flet as ft


def is_mounted(control: ft.BaseControl) -> bool:
    """Return ``True`` if ``control`` is currently attached to a page.

    Flet 0.84+ raises ``RuntimeError`` when ``control.page`` is accessed on a
    detached control. This helper provides a safe boolean check that mirrors
    the previous ``control.page is not None`` semantics.
    """
    try:
        _ = control.page
    except RuntimeError:
        return False
    return True
