# src/pages/collection_page.py

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, Signal
from .. import theme
from ..widgets.cards import CompletedDownloadCard

class CollectionPage(QWidget):
    """
    A page widget that displays a scrollable list of completed downloads.
    It scans the output directory and creates a `CompletedDownloadCard` for each video file.

    Signals:
        play_requested(str): Emitted when a video's play button is clicked,
                             passing the file path.
    """
    play_requested = Signal(str)

    def __init__(self, output_folder: str):
        super().__init__()
        self.output_folder = output_folder
        self.setStyleSheet(f"background-color: {theme.BG_VOID};")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 36, 32, 32)
        root.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("COLLECTION")
        title.setStyleSheet(
            f"color: {theme.TEXT_PRIMARY}; font-weight: 800; font-size: 11px;"
            f" letter-spacing: 4px; background: transparent; border: none;"
        )
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: transparent; }}
            QScrollBar:vertical {{ background: transparent; width: 3px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {theme.ACCENT_MUTED}; border-radius: 2px; min-height: 30px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(8)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll)
        self.refresh()

    def refresh(self):
        """
        Clears the current list and re-scans the output folder to rebuild the
        list of completed download cards.
        """
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        files = []
        if os.path.exists(self.output_folder):
            files = [f for f in os.listdir(self.output_folder)
                     if f.lower().endswith(('.mp4', '.mkv', '.webm', '.m4a'))]

        if not files:
            empty = QLabel("No downloads yet.")
            empty.setStyleSheet(f"color: {theme.TEXT_DIM}; font-size: 13px;")
            empty.setAlignment(Qt.AlignCenter)
            self.container_layout.addWidget(empty)
            return

        for filename in reversed(files):
            filepath = os.path.join(self.output_folder, filename)
            card = CompletedDownloadCard(filename, filepath, self.play_requested.emit)
            self.container_layout.addWidget(card)