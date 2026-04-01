# src/pages/player_page.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from ..import theme
from ..widgets.video_player import VideoPlayerWidget

class VideoPlayerPage(QWidget):
    """
    A simple wrapper widget to host the VideoPlayerWidget.
    This ensures the player correctly fills the entire area provided by the
    QStackedWidget in the main window.

    Signals:
        back_requested(): Relayed from the underlying VideoPlayerWidget.
    """
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {theme.BG_VOID};")

        # A layout with zero margins to make the player fill the page.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.player_widget = VideoPlayerWidget()
        self.player_widget.back_requested.connect(self.back_requested)
        layout.addWidget(self.player_widget)

    def play_file(self, filepath: str):
        """Public method to start playing a video file."""
        self.player_widget.play_file(filepath)