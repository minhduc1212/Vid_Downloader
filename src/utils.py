# src/utils.py

import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtSvg import QSvgRenderer
from . import theme

# ==================================================================================================
#  GENERAL HELPERS
# ==================================================================================================

def format_time(ms: int) -> str:
    """Converts milliseconds to a formatted time string (HH:MM:SS or MM:SS)."""
    s = max(0, ms) // 1000
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02}:{sec:02}" if h else f"{m:02}:{sec:02}"

def get_platform_info(url: str) -> tuple[str, str]:
    """
    Extracts platform label and color from a video URL.
    
    Returns:
        A tuple containing (label, color_hex).
    """
    url_lower = url.lower()
    for key, (color, label) in theme.PLATFORM_COLORS.items():
        if key in url_lower:
            return label, color
    # Return label, color for the default case
    return theme.PLATFORM_COLORS["default"][1], theme.PLATFORM_COLORS["default"][0]

# ==================================================================================================
#  QT-SPECIFIC WIDGET HELPERS
# ==================================================================================================

def colorize_svg_icon(svg_path: str, color: str, size: QSize) -> QIcon:
    """
    Renders an SVG file at a specific size and tints it with the given color.
    This allows for dynamic icon coloring based on state (e.g., hover).
    """
    renderer = QSvgRenderer(svg_path)
    if not renderer.isValid():
        return QIcon()

    # 1. Render the original SVG into a pixmap.
    px = QPixmap(size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    renderer.render(p)
    p.end()

    # 2. Create a new pixmap and use CompositionMode_SourceIn to apply the tint.
    tinted = QPixmap(size)
    tinted.fill(Qt.transparent)
    p2 = QPainter(tinted)
    p2.drawPixmap(0, 0, px)
    p2.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p2.fillRect(tinted.rect(), QColor(color))
    p2.end()

    return QIcon(tinted)

def apply_shadow(widget, blur=18, opacity=120, offset_y=4):
    """Applies a standard drop shadow effect to a widget."""
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, offset_y)
    fx.setColor(QColor(0, 0, 0, opacity))
    widget.setGraphicsEffect(fx)