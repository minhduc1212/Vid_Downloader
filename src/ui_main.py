import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt

from . import theme
from .core.download_worker import DownloadWorker
from .pages.dashboard_page import DashboardPage
from .pages.collection_page import CollectionPage
from .pages.player_page import VideoPlayerPage
from .widgets.cards import _label_qss # For error message


# ══════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════
class FlatDesignUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VidDownloader")
        self.resize(1100, 700)
        self.setMinimumSize(900, 580)
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {theme.BG_VOID};
                font-family: {theme.FONT_SANS};
                font-size: 13px;
                color: {theme.TEXT_PRIMARY};
            }}
            QToolTip {{
                background-color: {theme.BG_CARD};
                color: {theme.TEXT_SECONDARY};
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
            }}
        """)

        self.output_folder = "Output"
        os.makedirs(self.output_folder, exist_ok=True)
        self.workers = []

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ──────────────────────────────────────────
        #  SIDEBAR
        # ──────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(64)
        sidebar.setStyleSheet(f"background-color: {theme.BG_VOID}; border: none;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 24, 0, 24)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(Qt.AlignTop)

        wordmark = QLabel("V")
        wordmark.setFixedSize(64, 48)
        wordmark.setAlignment(Qt.AlignCenter)
        wordmark.setStyleSheet(
            f"color: {theme.ACCENT_PRIMARY}; font-size: 22px; font-weight: 900;"
            f" letter-spacing: -1px; border: none; background: transparent;"
        )
        sidebar_layout.addWidget(wordmark)
        sidebar_layout.addSpacing(20)

        nav_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme.TEXT_SECONDARY};
                font-size: 28px;
                border-radius: 0px;
                padding: 0px;
            }}
            QPushButton:hover {{
                color: {theme.TEXT_PRIMARY};
                background-color: {theme.BG_SURFACE};
            }}
            QPushButton:checked {{
                color: {theme.ACCENT_PRIMARY};
                background-color: {theme.BG_SURFACE};
                border-left: 2px solid {theme.ACCENT_PRIMARY};
            }}
        """

        self.btn_dash = QPushButton("⊞")
        self.btn_coll = QPushButton("◧")
        for btn in [self.btn_dash, self.btn_coll]:
            btn.setFixedSize(64, 64)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setStyleSheet(nav_btn_style)
            btn.setCursor(Qt.PointingHandCursor)

        self.btn_dash.setChecked(True)
        self.btn_dash.setToolTip("Dashboard")
        self.btn_coll.setToolTip("Collection")

        # Sidebar nav only switches between page 0 and 1.
        # Page 2 (player) is entered via play button, exited via back button.
        self.btn_dash.clicked.connect(lambda: self._go_to(0))
        self.btn_coll.clicked.connect(lambda: (self._go_to(1),
                                                self.collection_page.refresh()))

        sidebar_layout.addWidget(self.btn_dash)
        sidebar_layout.addWidget(self.btn_coll)
        sidebar_layout.addStretch()

        avatar = QLabel("U")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {theme.BG_CARD};
            color: {theme.TEXT_SECONDARY};
            border-radius: 18px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {theme.ACCENT_MUTED};
        """)
        aw = QHBoxLayout()
        aw.setContentsMargins(14, 0, 14, 0)
        aw.addWidget(avatar)
        sidebar_layout.addLayout(aw)

        # ──────────────────────────────────────────
        #  CONTENT STACK
        # ──────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {theme.BG_VOID};")

        # PAGE 0 — Dashboard
        self.dashboard_page = DashboardPage()
        self.dashboard_page.download_requested.connect(self.on_download_clicked)

        # PAGE 1 — Collection
        self.collection_page = CollectionPage(self.output_folder)
        self.collection_page.play_requested.connect(self.show_player)

        # PAGE 2 — Video Player
        self.video_player_page = VideoPlayerPage()
        self.video_player_page.back_requested.connect(self.hide_player)

        self.stack.addWidget(self.dashboard_page)    # index 0
        self.stack.addWidget(self.collection_page) # index 1
        self.stack.addWidget(self.video_player_page) # index 2

        # Separator
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background-color: {theme.ACCENT_MUTED}; border: none;")

        root.addWidget(sidebar)
        root.addWidget(sep)
        root.addWidget(self.stack, stretch=1)

    # ──────────────────────────────────────────────────
    #  NAVIGATION
    # ──────────────────────────────────────────────────
    def _go_to(self, index: int):
        self.stack.setCurrentIndex(index)

    def show_player(self, filepath: str):
        self.video_player_page.play_file(filepath)
        self.stack.setCurrentIndex(2)

    def hide_player(self):
        # Go back to collection after watching
        self.stack.setCurrentIndex(1)
        self.btn_coll.setChecked(True)

    # ──────────────────────────────────────────────────
    #  DOWNLOAD LOGIC
    # ──────────────────────────────────────────────────
    def on_download_clicked(self, url: str):
        """Slot to handle a download request from the dashboard."""
        card = self.dashboard_page.add_download_card(url)

        worker = DownloadWorker(url, self.output_folder)
        worker.progress_updated.connect(card.progress.setValue)
        worker.finished.connect(lambda: self.on_download_finished(card, worker))
        worker.error.connect(lambda err: self.on_download_error(card, worker, err))
        worker.start()
        self.workers.append(worker)

    def on_download_finished(self, card, worker):
        """Slot for successful download completion."""
        card.deleteLater()
        if worker in self.workers:
            self.workers.remove(worker)
        self.collection_page.refresh()

    def on_download_error(self, card, worker, error_msg):
        """Slot to handle download errors."""
        card.name_lbl.setText(f"Failed — {error_msg[:48]}")
        card.name_lbl.setStyleSheet(_label_qss("#FF3B3B", 12, "600"))
        card.status_dot.setText("●")
        card.status_dot.setStyleSheet(
            "color: #FF3B3B; font-size: 10px; border: none; background: transparent;"
        )
        if worker in self.workers:
            self.workers.remove(worker)