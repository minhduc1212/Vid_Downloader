# src/pages/dashboard_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLineEdit, QPushButton, QLabel, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from ..import theme
from ..widgets.cards import CurrentDownloadCard

class DashboardPage(QWidget):
    """
    The main dashboard page containing the URL input field, fetch button,
    and a scrollable list for active downloads.

    Signals:
        download_requested(str): Emitted when the 'FETCH' button is clicked,
                                 passing the URL string.
    """
    download_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {theme.BG_VOID};")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- Top Bar (URL Input & Fetch Button) ---
        topbar = QFrame()
        topbar.setFixedHeight(72)
        topbar.setStyleSheet(f"background-color: {theme.BG_SURFACE}; border: none;")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(28, 0, 24, 0)
        topbar_layout.setSpacing(12)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Drop a link — Instagram, TikTok, Facebook…")
        self.url_input.setFixedHeight(42)
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_CARD}; color: {theme.TEXT_PRIMARY};
                border: none; border-radius: 4px;
                padding: 0px 16px; font-size: 14px;
            }}
            QLineEdit:focus {{ background-color: #1A1A1A; }}
        """)

        self.download_btn = QPushButton("FETCH")
        self.download_btn.setFixedSize(96, 42)
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY}; color: #000000;
                font-size: 11px; font-weight: 800; letter-spacing: 2px;
                border: none; border-radius: 4px;
            }}
            QPushButton:hover   {{ background-color: #D4E800; }}
            QPushButton:pressed {{ background-color: #B8CC00; }}
        """)
        self.download_btn.clicked.connect(self._on_fetch)

        topbar_layout.addWidget(self.url_input)
        topbar_layout.addWidget(self.download_btn)
        root.addWidget(topbar)

        # --- Active Downloads Section ---
        section_lbl = QLabel("ACTIVE")
        section_lbl.setStyleSheet(
            f"color: {theme.TEXT_SECONDARY}; font-size: 9px; font-weight: 700;"
            f" letter-spacing: 5px; background: transparent; border: none;"
        )
        section_lbl.setContentsMargins(28, 24, 0, 8)
        root.addWidget(section_lbl)

        self.current_scroll = QScrollArea()
        self.current_scroll.setWidgetResizable(True)
        self.current_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: transparent; }}
            QScrollBar:vertical {{ background: transparent; width: 3px; }}
            QScrollBar::handle:vertical {{ background: {theme.ACCENT_MUTED}; border-radius: 2px; min-height: 30px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        self.current_container = QWidget()
        self.current_container.setStyleSheet("background-color: transparent;")
        self.current_layout = QVBoxLayout(self.current_container)
        self.current_layout.setAlignment(Qt.AlignTop)
        self.current_layout.setSpacing(8)
        self.current_layout.setContentsMargins(28, 0, 28, 28)
        self.current_scroll.setWidget(self.current_container)
        root.addWidget(self.current_scroll, stretch=1)

    def _on_fetch(self):
        """Internal slot to handle fetch button click and emit signal."""
        url = self.url_input.text().strip()
        if url:
            self.download_requested.emit(url)
            self.url_input.clear()

    def add_download_card(self, url: str) -> CurrentDownloadCard:
        """Creates and adds a new download card to the active list."""
        card = CurrentDownloadCard(url, "Fetching…")
        self.current_layout.addWidget(card)
        return card