'''

Copyright (C) 2026 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.

'''

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QTimer, QFileSystemWatcher
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
import codecs
import locale
import os

class LogViewer(QTextEdit):
    def __init__(self, log_file, parent=None, program=None):
        super().__init__(parent)
        self.log_file = log_file
        self.DAEDALUS = program  # Separate the program reference from the widget parent
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.last_position = 0
        self._file_identity = None
        self._file_mtime_ns = None
        self._lines_read = 0
        self._pending_text = ""
        self._decoder = self._new_decoder()

        # Set monospaced font
        # font = QFont("Courier New")
        # font.setStyleHint(QFont.Monospace)
        # font.setPointSize(10)  # Adjust font size as needed
        # self.setFont(font)

        # File system watcher for instant updates
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.on_file_changed)
        if os.path.exists(self.log_file):
            self.watcher.addPath(os.path.abspath(self.log_file))

        # Fallback timer for updates in case file watcher fails
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(500)  # Check every 500ms as fallback

        self.update_log()

    def on_file_changed(self, path):
        """Called when file system detects file change"""
        self.update_log()
        # Re-add the path to ensure continued monitoring (needed on some systems)
        if path not in self.watcher.files():
            self.watcher.addPath(path)

    def update_log(self):
        if not os.path.exists(self.log_file):
            self._reset_file_state(clear_widget=False)
            if self.toPlainText() != "Log file not found.":
                self.setPlainText("Log file not found.")
            return

        try:
            watch_path = os.path.abspath(self.log_file)
            if watch_path not in self.watcher.files():
                self.watcher.addPath(watch_path)

            with open(self.log_file, "rb") as file:
                stat = os.fstat(file.fileno())
                identity = (stat.st_dev, stat.st_ino)
                rewritten_at_same_size = (
                    self._file_mtime_ns is not None
                    and stat.st_size == self.last_position
                    and stat.st_mtime_ns != self._file_mtime_ns
                )
                if (
                    identity != self._file_identity
                    or stat.st_size < self.last_position
                    or rewritten_at_same_size
                ):
                    self._reset_file_state()
                    self._file_identity = identity

                file.seek(self.last_position)
                new_bytes = file.read()
                self.last_position = file.tell()
                self._file_mtime_ns = os.fstat(file.fileno()).st_mtime_ns

            text = self._pending_text + self._decoder.decode(new_bytes)
            lines = text.split("\n")
            self._pending_text = lines.pop()

            visible_lines = []
            for line in lines:
                if self._lines_read >= 11 and "DEBUG" not in line:
                    visible_lines.append(line)
                self._lines_read += 1

            if visible_lines:
                self.append_colored_lines(visible_lines)
        except OSError as e:
            self._reset_file_state(clear_widget=False)
            self.setPlainText(f"Error reading log file: {e}")

    def append_colored_line(self, line):
        self.append_colored_lines([line])

    def append_colored_lines(self, lines):
        # Default color scheme if program doesn't have one
        default_colors = {
            'LoggerError': '#FF6B6B',
            'LoggerWarning': '#FFD93D',
            'LoggerDebug': '#6BCB77',
            'LoggerMain': '#FFFFFF'
        }
        
        try:
            color_scheme = self.DAEDALUS.color_scheme if self.DAEDALUS else default_colors
        except (AttributeError, TypeError):
            color_scheme = default_colors

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        color_formats = {}
        for line in lines:
            if "ERROR" in line:
                color_key = 'LoggerError'
            elif "WARNING" in line:
                color_key = 'LoggerWarning'
            elif "DEBUG" in line:
                color_key = 'LoggerDebug'
            else:
                color_key = 'LoggerMain'

            if color_key not in color_formats:
                text_format = QTextCharFormat()
                text_format.setForeground(
                    QColor(color_scheme.get(color_key, default_colors[color_key]))
                )
                color_formats[color_key] = text_format

            cursor.insertText(line.strip() + '\n', color_formats[color_key])

        self.setTextCursor(cursor)
        if lines:
            self.ensureCursorVisible()

    def _new_decoder(self):
        return codecs.getincrementaldecoder(locale.getpreferredencoding(False))(errors="replace")

    def _reset_file_state(self, clear_widget=True):
        self.last_position = 0
        self._file_identity = None
        self._file_mtime_ns = None
        self._lines_read = 0
        self._pending_text = ""
        self._decoder = self._new_decoder()
        if clear_widget:
            self.setPlainText("")

    def __del__(self):
        """Cleanup file watcher and timer when widget is destroyed"""
        try:
            self.timer.stop()
            self.watcher.fileChanged.disconnect()
        except:
            pass
