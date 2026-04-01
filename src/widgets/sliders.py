# src/widgets/sliders.py

from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt, Signal
from .. import theme

class SeekSlider(QSlider):
    """
    A custom QSlider for video seeking. It provides a modern, flat look and
    emits signals for a smooth, responsive scrubbing experience. It handles
    mouse events to provide a value based on click position.

    Signals:
        seek_preview(int): Emitted continuously as the user drags the handle.
        seek_committed(int): Emitted only when the user releases the mouse.
        scrub_started(): Emitted when the user first presses the mouse down.
    """
    seek_preview = Signal(int)
    seek_committed = Signal(int)
    scrub_started = Signal()

    def __init__(self):
        super().__init__(Qt.Horizontal)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(20)
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 3px; background: {theme.ACCENT_MUTED};
                border-radius: 2px; margin: 0px;
            }}
            QSlider::sub-page:horizontal {{
                background: {theme.ACCENT_PRIMARY}; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {theme.ACCENT_PRIMARY};
                width: 12px; height: 12px;
                margin: -5px 0px; border-radius: 6px; border: none;
            }}
            QSlider::handle:horizontal:hover {{
                background: #FFFFFF;
                width: 14px; height: 14px;
                margin: -6px 0px; border-radius: 7px;
            }}
        """)

    def _value_at(self, x: float) -> int:
        """Calculates the slider value corresponding to a horizontal mouse position."""
        pct = x / max(self.width(), 1)
        return int(max(0.0, min(1.0, pct)) * self.maximum())

    def mousePressEvent(self, event):
        """On press, start scrubbing and emit a preview."""
        if event.button() == Qt.LeftButton and self.maximum() > 0:
            self.scrub_started.emit()
            v = self._value_at(event.position().x())
            self.setValue(v)
            self.seek_preview.emit(v)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """While dragging, continuously update the preview."""
        if self.maximum() > 0 and (event.buttons() & Qt.LeftButton):
            v = self._value_at(event.position().x())
            self.setValue(v)
            self.seek_preview.emit(v)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """On release, commit the final seek position."""
        if event.button() == Qt.LeftButton and self.maximum() > 0:
            self.seek_committed.emit(self.value())
            event.accept()
        else:
            super().mouseReleaseEvent(event)