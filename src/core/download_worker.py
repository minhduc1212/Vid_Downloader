# src/core/download_worker.py

from PySide6.QtCore import QThread, Signal
from ..downloader import VideoDownloader # Use relative import

class DownloadWorker(QThread):
    """
    A dedicated QThread to handle blocking network operations for video downloads.
    This prevents the main UI thread from freezing.

    Signals:
        progress_updated(int): Emits download progress percentage (0-100).
        finished(): Emitted on successful completion.
        error(str): Emitted when an exception occurs during download.
    """
    progress_updated = Signal(int)
    finished         = Signal()
    error            = Signal(str)

    def __init__(self, url: str, output_folder: str):
        super().__init__()
        self.url           = url
        self.output_folder = output_folder

    def run(self):
        """The main execution method for the thread."""
        try:
            downloader = VideoDownloader(output_folder=self.output_folder)
            downloader.download_video(self.url, progress_callback=self.progress_updated.emit)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))