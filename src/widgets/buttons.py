# src/widgets/buttons.py

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from .. import theme
from .. import utils

class HoverSvgButton(QPushButton):
    """
    A custom QPushButton that displays an SVG icon and changes its color on hover.
    The background also changes color on hover to match the player's accent theme.
    """
    def __init__(self, icon_path: str, w: int, h: int, tip: str = ""):
        super().__init__()
        self.icon_path = icon_path
        self.setFixedSize(w, h)
        self.setCursor(Qt.PointingHandCursor)
        if tip:
            self.setToolTip(tip)
        
        self.setIconSize(theme.ICON_SIZE_TRANSPORT)
        # Default state: White icon
        self.setIcon(utils.colorize_svg_icon(self.icon_path, theme.TEXT_PRIMARY, theme.ICON_SIZE_TRANSPORT))
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color : transparent;
                border           : none;
                border-radius    : 4px;
            }}
            QPushButton:hover   {{ background-color: {theme.ACCENT_PRIMARY}; }}
            QPushButton:pressed {{ background-color: #B8CC00; }}
        """)

    def enterEvent(self, event):
        """On hover, change icon to black to contrast with the yellow background."""
        self.setIcon(utils.colorize_svg_icon(self.icon_path, "#000000", theme.ICON_SIZE_TRANSPORT))
        super().enterEvent(event)

    def leaveEvent(self, event):
        """On leave, revert icon to white."""
        self.setIcon(utils.colorize_svg_icon(self.icon_path, theme.TEXT_PRIMARY, theme.ICON_SIZE_TRANSPORT))
        super().leaveEvent(event)

class PlayButton(QPushButton):
    """
    A specialized button for Play/Pause functionality. It manages its own icon
    state (Play vs. Pause) and hover effects to match the transport controls.
    """
    def __init__(self, w: int = 44, h: int = 34):
        super().__init__()
        self.setFixedSize(w, h)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Play / Pause  (Space)")
        self.setIconSize(theme.ICON_SIZE_TRANSPORT)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color : transparent;
                border           : none;
                border-radius    : 4px;
            }}
            QPushButton:hover   {{ background-color: {theme.ACCENT_PRIMARY}; }}
            QPushButton:pressed {{ background-color: #B8CC00; }}
        """)
        self.playing = False
        self.is_hovered = False
        self.set_playing(False)

    def set_playing(self, playing: bool):
        """Updates the button's icon to reflect the new playback state."""
        self.playing = playing
        self._update_icon()

    def _update_icon(self):
        """Internal method to set the correct icon and color based on state."""
        path = theme.ICON_PAUSE if self.playing else theme.ICON_PLAY
        color = "#000000" if self.is_hovered else theme.TEXT_PRIMARY
        self.setIcon(utils.colorize_svg_icon(path, color, theme.ICON_SIZE_TRANSPORT))

    def enterEvent(self, event):
        self.is_hovered = True
        self._update_icon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self._update_icon()
        super().leaveEvent(event)

class BackButton(QPushButton):
    """
    A specialized button for the 'Back' navigation in the video player.
    It synchronizes the color of its text and SVG icon on hover.
    """
    def __init__(self):
        super().__init__(" BACK")
        self.setIconSize(theme.ICON_SIZE_NAV)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(34)
        self.setStyleSheet(f"""
            QPushButton {{
                background  : transparent;
                color       : {theme.TEXT_SECONDARY};
                border      : none;
                font-size   : 11px;
                font-weight : 700;
                letter-spacing : 2px;
                font-family : {theme.FONT_SANS};
                padding     : 0 10px;
                border-radius : 4px;
            }}
            QPushButton:hover   {{ color: {theme.ACCENT_PRIMARY}; background: {theme.BG_CARD}; }}
            QPushButton:pressed {{ background: {theme.ACCENT_MUTED}; }}
        """)
        self._update_icon(False)

    def _update_icon(self, hovered: bool):
        """Internal method to set the icon color based on hover state."""
        color = theme.ACCENT_PRIMARY if hovered else theme.TEXT_SECONDARY
        self.setIcon(utils.colorize_svg_icon(theme.ICON_BACK, color, theme.ICON_SIZE_NAV))

    def enterEvent(self, event):
        self._update_icon(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._update_icon(False)
        super().leaveEvent(event)