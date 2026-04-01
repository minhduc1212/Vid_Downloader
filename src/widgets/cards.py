# src/widgets/cards.py

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QVBoxLayout,
    QProgressBar, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from .. import theme
from .. import utils

def _card_qss(bg=theme.BG_CARD, radius=6):
    """Helper for card stylesheet."""
    return f"QFrame {{ background-color: {bg}; border: none; border-radius: {radius}px; }}"

def _label_qss(color=theme.TEXT_PRIMARY, size=13, weight="normal"):
    """Helper for label stylesheet."""
    return f"color: {color}; font-size: {size}px; font-weight: {weight}; border: none; background: transparent;"

class CurrentDownloadCard(QFrame):
    """
    A card widget to display the status of an in-progress download.
    Includes a platform icon, filename, progress bar, and status indicator.
    """
    def __init__(self, url: str, filename: str):
        super().__init__()
        self.setObjectName("MediaCard")
        self.setStyleSheet(_card_qss())
        self.setFixedHeight(72)
        utils.apply_shadow(self)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 0, 16, 0)
        root.setSpacing(16)

        plat_text, plat_color = utils.get_platform_info(url)
        badge = QLabel(plat_text)
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"background-color: {plat_color}; color: #FFFFFF;"
            f" font-weight: 800; font-size: 11px; border-radius: 4px; letter-spacing: 1px;"
        )

        centre = QVBoxLayout()
        centre.setSpacing(6)
        centre.setContentsMargins(0, 0, 0, 0)

        self.name_lbl = QLabel(filename)
        self.name_lbl.setStyleSheet(_label_qss(theme.TEXT_PRIMARY, 13, "600"))

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background-color: {theme.PROGRESS_BG}; border: none; border-radius: 2px; }}
            QProgressBar::chunk {{ background-color: {theme.PROGRESS_FILL}; border-radius: 2px; }}
        """)

        centre.addWidget(self.name_lbl)
        centre.addWidget(self.progress)

        self.status_dot = QLabel("●")
        self.status_dot.setFixedSize(20, 20)
        self.status_dot.setAlignment(Qt.AlignCenter)
        self.status_dot.setStyleSheet(
            f"color: {theme.ACCENT_PRIMARY}; font-size: 10px; border: none; background: transparent;"
        )

        root.addWidget(badge)
        root.addLayout(centre, stretch=5)
        root.addWidget(self.status_dot)

class CompletedDownloadCard(QFrame):
    """
    A card widget for a successfully downloaded video.
    Includes a play button, filename, and placeholder social icons.
    """
    def __init__(self, filename: str, filepath: str, play_callback=None):
        super().__init__()
        self.setObjectName("MediaCard")
        self.setStyleSheet(_card_qss())
        self.setFixedHeight(68)
        self.filepath = filepath

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 0, 16, 0)
        root.setSpacing(14)

        badge = QPushButton("▶")
        badge.setFixedSize(36, 36)
        badge.setCursor(Qt.PointingHandCursor)
        badge.setToolTip("Play Video")
        badge.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_VOID}; color: {theme.ACCENT_PRIMARY};
                font-size: 14px; border-radius: 4px; border: 1px solid {theme.ACCENT_MUTED};
            }}
            QPushButton:hover {{ background-color: {theme.SOCIAL_HOVER}; border: 1px solid {theme.ACCENT_PRIMARY}; }}
            QPushButton:pressed {{ background-color: {theme.ACCENT_PRIMARY}; color: {theme.BG_VOID}; }}
        """)
        if play_callback:
            badge.clicked.connect(lambda: play_callback(self.filepath))

        name = QLabel(filename)
        name.setStyleSheet(_label_qss(theme.TEXT_SECONDARY, 13, "500"))
        name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        social = QHBoxLayout()
        social.setSpacing(4)
        social.setContentsMargins(0, 0, 0, 0)
        for icon, tip in [("♥", "Like"), ("✦", "Comments"), ("⇪", "Share")]:
            btn = QPushButton(icon)
            btn.setToolTip(tip)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {theme.TEXT_SECONDARY}; background-color: transparent;
                    border: none; font-size: 14px; border-radius: 16px;
                }}
                QPushButton:hover {{ background-color: {theme.SOCIAL_HOVER}; color: {theme.TEXT_PRIMARY}; }}
            """)
            social.addWidget(btn)

        root.addWidget(badge)
        root.addWidget(name, stretch=4)
        root.addLayout(social)