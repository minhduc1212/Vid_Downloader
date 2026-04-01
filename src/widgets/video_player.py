import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, QUrl, Signal, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from .. import theme
from .. import utils
from .buttons import PlayButton, BackButton, HoverSvgButton
from .sliders import SeekSlider


class VideoPlayerWidget(QWidget):
    """
    The core video player widget. It combines a video display with custom
    transport controls (play, pause, skip, seek) and handles all media
    playback logic, including a robust, glitch-free seeking implementation.

    Signals:
        back_requested(): Emitted when the user clicks the 'Back' button.
    """
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {theme.BG_VOID};")
        self.setMouseTracking(True)

        # ── Scrubbing & Seek State ───────────────────
        self._is_scrubbing = False
        self._was_playing_before_seek = False
        self._pending_seek_pos = -1

        # Debounce rapid skips to protect the decoder from being overwhelmed.
        self._seek_timer = QTimer(self)
        self._seek_timer.setSingleShot(True)
        self._seek_timer.setInterval(150)
        self._seek_timer.timeout.connect(self._do_real_seek)

        # Mute audio during seek to prevent audible glitches/chirps.
        self._unmute_timer = QTimer(self)
        self._unmute_timer.setSingleShot(True)
        self._unmute_timer.setInterval(300)
        self._unmute_timer.timeout.connect(lambda: self.audio_output.setMuted(False))

        # ── Media engine ────────────────────────────
        self.player       = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        # ── Root layout ─────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TOP BAR ─────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(48)
        top_bar.setStyleSheet(f"background-color: {theme.BG_SURFACE}; border: none;")

        top_row = QHBoxLayout(top_bar)
        top_row.setContentsMargins(16, 0, 20, 0)
        top_row.setSpacing(12)

        self.back_btn = BackButton()
        self.back_btn.clicked.connect(self.stop_and_go_back)

        self.title_lbl = QLabel("")
        self.title_lbl.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title_lbl.setStyleSheet(
            f"color: {theme.TEXT_SECONDARY}; font-size: 11px; letter-spacing: 0.5px;"
            f" background: transparent; border: none; font-family: {theme.FONT_MONO};"
        )

        top_row.addWidget(self.back_btn)
        top_row.addWidget(self.title_lbl)

        # ── VIDEO AREA ──────────────────────────────
        self.video_widget = QVideoWidget(self)
        self.video_widget.setStyleSheet(f"background-color: {theme.BG_VOID};")
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.player.setVideoOutput(self.video_widget)

        # ── CONTROLS BAR ────────────────────────────
        ctrl_bar = QFrame()
        ctrl_bar.setFixedHeight(90)
        ctrl_bar.setStyleSheet(
            f"background-color: {theme.BG_CONTROLS}; border: none;"
            f" border-top: 1px solid {theme.ACCENT_MUTED};"
        )

        ctrl_col = QVBoxLayout(ctrl_bar)
        ctrl_col.setContentsMargins(28, 12, 28, 14)
        ctrl_col.setSpacing(10)

        # — Seek row —
        seek_row = QHBoxLayout()
        seek_row.setSpacing(14)
        seek_row.setContentsMargins(0, 0, 0, 0)

        self.seek_slider = SeekSlider()
        self.seek_slider.scrub_started.connect(self._on_scrub_started)
        self.seek_slider.seek_preview.connect(self._on_seek_preview)
        self.seek_slider.seek_committed.connect(self._on_seek_committed)

        self.time_lbl = QLabel("00:00 / 00:00")
        self.time_lbl.setFixedWidth(108)
        self.time_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.time_lbl.setStyleSheet(
            f"color: {theme.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;"
            f" font-family: {theme.FONT_MONO}; background: transparent; border: none;"
        )

        seek_row.addWidget(self.seek_slider)
        seek_row.addWidget(self.time_lbl)

        # — Transport row —
        transport_row = QHBoxLayout()
        transport_row.setSpacing(0)
        transport_row.setContentsMargins(0, 0, 0, 0)

        self.skip_back_btn = HoverSvgButton(
            theme.ICON_SKIP_BACK, 44, 34, tip=f"−{theme.SKIP_MS // 1000}s  (←)"
        )
        self.play_btn = PlayButton(44, 34)
        self.skip_fwd_btn = HoverSvgButton(
            theme.ICON_SKIP_FWD, 44, 34, tip=f"+{theme.SKIP_MS // 1000}s  (→)"
        )

        self.skip_back_btn.clicked.connect(self.skip_back)
        self.play_btn.clicked.connect(self.toggle_play)
        self.skip_fwd_btn.clicked.connect(self.skip_forward)

        transport_row.addStretch()
        transport_row.addWidget(self.skip_back_btn)
        transport_row.addSpacing(8)
        transport_row.addWidget(self.play_btn)
        transport_row.addSpacing(8)
        transport_row.addWidget(self.skip_fwd_btn)
        transport_row.addStretch()

        ctrl_col.addLayout(seek_row)
        ctrl_col.addLayout(transport_row)

        # ── Assemble root ───────────────────────────
        root.addWidget(top_bar)
        root.addWidget(self.video_widget, stretch=1)
        root.addWidget(ctrl_bar)

        # ── Player signals ──────────────────────────
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration)
        self.player.playbackStateChanged.connect(self._on_state)
        self.player.errorOccurred.connect(self._on_player_error)

        # Smooth slider poll — skipped during active seek
        self._poll = QTimer(self)
        self._poll.setInterval(250)
        self._poll.timeout.connect(self._sync_slider)
        self._poll.start()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for playback control."""
        k = event.key()
        if k == Qt.Key_Space:
            self.toggle_play()
        elif k == Qt.Key_Left:
            self.skip_back()
        elif k == Qt.Key_Right:
            self.skip_forward()
        else:
            super().keyPressEvent(event)

    def play_file(self, filepath: str):
        """Loads and starts playing a video from a local file path."""
        if not os.path.exists(filepath):
            return
        self.title_lbl.setText(os.path.basename(filepath))
        self.player.setSource(QUrl.fromLocalFile(os.path.abspath(filepath)))
        self.player.play()
        self.setFocus()

    def toggle_play(self):
        """Toggles the playback state (Play/Pause)."""
        if self._seek_timer.isActive() or self._is_scrubbing:
            self._was_playing_before_seek = not self._was_playing_before_seek
            self.play_btn.set_playing(self._was_playing_before_seek)
        else:
            if self.player.playbackState() == QMediaPlayer.PlayingState:
                self.player.pause()
            else:
                self.player.play()

    def skip_back(self):
        """Seeks the video backward by a fixed duration."""
        base = self._pending_seek_pos if self._pending_seek_pos >= 0 else self.player.position()
        self._request_seek(max(0, base - theme.SKIP_MS))

    def skip_forward(self):
        """Seeks the video forward by a fixed duration."""
        base = self._pending_seek_pos if self._pending_seek_pos >= 0 else self.player.position()
        self._request_seek(min(self.player.duration(), base + theme.SKIP_MS))

    def stop_and_go_back(self):
        """Stops playback and emits the signal to return to the previous screen."""
        self._seek_timer.stop()
        self._unmute_timer.stop()
        self.player.stop()
        self.back_requested.emit()

    def _request_seek(self, pos: int):
        """Initiates a debounced seek operation to prevent decoder lag."""
        self._pending_seek_pos = pos
        self.audio_output.setMuted(True)
        self._unmute_timer.stop()

        if not self._seek_timer.isActive():
            self._was_playing_before_seek = (self.player.playbackState() == QMediaPlayer.PlayingState)
            if self._was_playing_before_seek:
                self.player.pause()

        self.seek_slider.blockSignals(True)
        self.seek_slider.setValue(pos)
        self.seek_slider.blockSignals(False)
        dur = self.player.duration()
        self.time_lbl.setText(f"{utils.format_time(pos)} / {utils.format_time(dur) if dur else '00:00'}")

        self._seek_timer.start()

    def _do_real_seek(self):
        """Executes the actual seek after the debounce timer fires."""
        if self._pending_seek_pos >= 0:
            self.player.setPosition(self._pending_seek_pos)
            self._pending_seek_pos = -1

        if self._was_playing_before_seek:
            self.player.play()

        self._unmute_timer.start()

    def _on_scrub_started(self):
        self._is_scrubbing = True
        self.audio_output.setMuted(True)
        self._unmute_timer.stop()

        if not self._seek_timer.isActive():
            self._was_playing_before_seek = (self.player.playbackState() == QMediaPlayer.PlayingState)
            if self._was_playing_before_seek:
                self.player.pause()

    def _on_seek_preview(self, value: int):
        dur = self.player.duration()
        self.time_lbl.setText(f"{utils.format_time(value)} / {utils.format_time(dur) if dur else '00:00'}")
        
    def _on_seek_committed(self, value: int):
        self._is_scrubbing = False
        self._pending_seek_pos = value
        self._do_real_seek()

    def _on_state(self, state):
        if self._seek_timer.isActive() or self._is_scrubbing:
            return
        self.play_btn.set_playing(state == QMediaPlayer.PlayingState)

    def _on_position(self, pos: int):
        if self._is_scrubbing or self._seek_timer.isActive() or self._pending_seek_pos >= 0:
            return
        dur = self.player.duration()
        self.time_lbl.setText(f"{utils.format_time(pos)} / {utils.format_time(dur) if dur else '00:00'}")

    def _on_duration(self, dur: int):
        self.seek_slider.setRange(0, dur)

    def _sync_slider(self):
        if self._is_scrubbing or self._seek_timer.isActive() or self._pending_seek_pos >= 0:
            return
        self.seek_slider.blockSignals(True)
        self.seek_slider.setValue(self.player.position())
        self.seek_slider.blockSignals(False)

    def _on_player_error(self, error, error_string: str):
        BENIGN = ("timestamps for skipped", "Could not update timestamps", "aac @", "non monotonous")
        for pat in BENIGN:
            if pat.lower() in error_string.lower():
                print(f"[video_player] suppressed codec warning: {error_string}")
                return
        if error != QMediaPlayer.Error.NoError:
            self.title_lbl.setText(f"⚠  {error_string[:60]}")
            self.title_lbl.setStyleSheet(f"color: #FF4444; font-size: 11px; background: transparent; border: none;")