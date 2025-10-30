import sys
import os
import json
import socket
import threading
from pathlib import Path
from PyQt6.QtCore import (
    Qt, QDateTime, QPropertyAnimation, QRect, QEasingCurve, QObject, pyqtSignal
)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QFrame, QMessageBox,
    QGraphicsDropShadowEffect
)

# ----------------------------------------------------------------------
# Backend imports
# ----------------------------------------------------------------------
from client import (
    shutdown_event, run_file_sharing_service, register_with_server,
    announce_file_to_server, download_file_from_peer
)


# ----------------------------------------------------------------------
# Worker Signals
# ----------------------------------------------------------------------
class WorkerSignals(QObject):
    log = pyqtSignal(str)
    peers = pyqtSignal(list)
    connected = pyqtSignal(bool)


# ----------------------------------------------------------------------
# Animated Button Factory (Teal like Server)
# ----------------------------------------------------------------------
def create_animated_button(parent, text, base_color="#03dac6", hover_color="#66fff4", press_color="#00bfa5"):
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)

    btn.setStyleSheet(f"""
        QPushButton {{
            background:{base_color}; color:black; border-radius:12px;
            padding:12px 24px; font-weight:bold; font-size:14px;
            border: none;
        }}
        QPushButton:hover {{ background:{hover_color}; }}
        QPushButton:pressed {{ background:{press_color}; }}
    """)

    # Glow
    glow = QGraphicsDropShadowEffect()
    glow.setBlurRadius(0)
    glow.setColor(QColor(3, 218, 198))  # teal glow
    glow.setOffset(0, 0)
    btn.setGraphicsEffect(glow)

    # Animations
    glow_anim = QPropertyAnimation(glow, b"blurRadius", parent)
    glow_anim.setDuration(200)
    glow_anim.setStartValue(0)
    glow_anim.setEndValue(25)
    glow_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    scale_anim = QPropertyAnimation(btn, b"geometry", parent)
    scale_anim.setDuration(100)
    scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    original_rect = None

    def on_enter(e):
        nonlocal original_rect
        if original_rect is None:
            original_rect = btn.geometry()
        glow_anim.setDirection(QPropertyAnimation.Direction.Forward)
        glow_anim.start()
        r = btn.geometry()
        new_rect = r.adjusted(-5, -5, 5, 5)
        scale_anim.setStartValue(r)
        scale_anim.setEndValue(new_rect)
        scale_anim.start()

    def on_leave(e):
        glow_anim.setDirection(QPropertyAnimation.Direction.Backward)
        glow_anim.start()
        if original_rect:
            scale_anim.setStartValue(btn.geometry())
            scale_anim.setEndValue(original_rect)
            scale_anim.start()

    btn.enterEvent = on_enter
    btn.leaveEvent = on_leave
    return btn


# ----------------------------------------------------------------------
# Main Client Window
# ----------------------------------------------------------------------
class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P File Sharer – Client")
        self.resize(820, 640)
        self.setStyleSheet(self._stylesheet())
        self.signals = WorkerSignals()

        self.server_sock = None
        self.service_thread = None
        self.peer_data = []

        self._setup_ui()
        self._start_background()

        self.signals.log.connect(self._append_log)
        self.signals.peers.connect(self._update_peers)
        self.signals.connected.connect(self._update_status)

    # ------------------------------------------------------------------
    # Clean Stylesheet (Same as Server)
    # ------------------------------------------------------------------
    def _stylesheet(self):
        return """
        QMainWindow { background:#0d0d0d; color:#e0e0e0; }
        QLabel { color:#ffffff; font-weight:500; }
        QLineEdit {
            padding:12px; border-radius:12px; background:#1a1a1a;
            border:1px solid #333; font-size:14px; color:#ffffff;
        }
        QLineEdit::placeholder { color:#888; }
        QLineEdit:focus { border:1px solid #03dac6; background:#1e1e1e; }
        QTreeWidget {
            background:#1a1a1a; border:none; border-radius:12px;
            alternate-background-color:#252525; font-size:13px;
        }
        QTreeWidget::item { padding:8px; }
        QTreeWidget::item:selected { background:#03dac6; color:black; }
        QTreeWidget::item:hover { background:#252525; }
        QTextEdit {
            background:#1a1a1a; border-radius:12px; padding:10px;
            font-family:'Consolas'; font-size:12px; color:#b0b0b0;
        }
        QStatusBar { background:#1a1a1a; color:#aaa; }
        """

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setSpacing(16)
        main.setContentsMargins(20, 20, 20, 20)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("P2P File Sharer – Client")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        self.status_lbl = QLabel("Connecting…")
        self.status_lbl.setStyleSheet("font-size:12px; color:#888;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.status_lbl)
        main.addLayout(hdr)

        # Publish
        pub_box = QFrame()
        pub_box.setStyleSheet("background:#1a1a1a; border-radius:16px; padding:16px;")
        pub_lay = QVBoxLayout(pub_box)
        pub_lay.addWidget(QLabel("Publish a file"))

        row1 = QHBoxLayout()
        self.local_path = QLineEdit()
        self.local_path.setPlaceholderText("Local file path…")
        self._add_focus_glow(self.local_path, QColor(3, 218, 198))
        browse_btn = create_animated_button(self, "Browse", "#03dac6", "#66fff4", "#00bfa5")
        browse_btn.clicked.connect(self._browse_file)
        row1.addWidget(self.local_path)
        row1.addWidget(browse_btn)
        pub_lay.addLayout(row1)

        row2 = QHBoxLayout()
        self.shared_name = QLineEdit()
        self.shared_name.setPlaceholderText("Shared name (e.g. myphoto)")
        self._add_focus_glow(self.shared_name, QColor(3, 218, 198))
        publish_btn = create_animated_button(self, "Publish", "#03dac6", "#66fff4", "#00bfa5")
        publish_btn.clicked.connect(self._publish)
        row2.addWidget(self.shared_name)
        row2.addWidget(publish_btn)
        pub_lay.addLayout(row2)
        main.addWidget(pub_box)

        # Search & Download
        search_box = QFrame()
        search_box.setStyleSheet("background:#1a1a1a; border-radius:16px; padding:16px;")
        search_lay = QVBoxLayout(search_box)
        search_lay.addWidget(QLabel("Search & Download"))

        srow = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("File name to fetch…")
        self._add_focus_glow(self.search_input, QColor(3, 218, 198))
        search_btn = create_animated_button(self, "Search", "#03dac6", "#66fff4", "#00bfa5")
        search_btn.clicked.connect(self._search)
        srow.addWidget(self.search_input)
        srow.addWidget(search_btn)
        search_lay.addLayout(srow)

        self.peer_tree = QTreeWidget()
        self.peer_tree.setHeaderLabels(["IP", "Hostname", "File", "Ext"])
        self.peer_tree.setAlternatingRowColors(True)
        search_lay.addWidget(self.peer_tree)

        dl_btn = create_animated_button(self, "Download Selected", "#03dac6", "#66fff4", "#00bfa5")
        dl_btn.clicked.connect(self._download_selected)
        search_lay.addWidget(dl_btn)
        main.addWidget(search_box)

        # Log
        log_box = QFrame()
        log_box.setStyleSheet("background:#1a1a1a; border-radius:16px;")
        log_lay = QVBoxLayout(log_box)
        log_lay.addWidget(QLabel("Activity Log"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_lay.addWidget(self.log_view)
        main.addWidget(log_box)

        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------
    # Focus Glow (Teal)
    # ------------------------------------------------------------------
    def _add_focus_glow(self, widget, color):
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(0)
        effect.setColor(color)
        effect.setOffset(0, 0)
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"blurRadius", self)
        anim.setDuration(200)
        anim.setStartValue(0)
        anim.setEndValue(20)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        def focus_in(e):
            QLineEdit.focusInEvent(widget, e)
            anim.setDirection(QPropertyAnimation.Direction.Forward)
            anim.start()

        def focus_out(e):
            QLineEdit.focusOutEvent(widget, e)
            anim.setDirection(QPropertyAnimation.Direction.Backward)
            anim.start()

        widget.focusInEvent = focus_in
        widget.focusOutEvent = focus_out

    # ------------------------------------------------------------------
    # UI Helpers
    # ------------------------------------------------------------------
    def _append_log(self, msg):
        ts = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.log_view.append(f"[{ts}] {msg}")
        self.statusBar().showMessage(msg.split("\n")[-1][:100])

    def _update_status(self, ok: bool):
        self.status_lbl.setText("Connected" if ok else "Disconnected")
        self.status_lbl.setStyleSheet("color:#4caf50;" if ok else "color:#f44336;")

    # ------------------------------------------------------------------
    # Background (Auto-connect to localhost)
    # ------------------------------------------------------------------
    def _start_background(self):
        self.service_thread = threading.Thread(target=run_file_sharing_service, daemon=True)
        self.service_thread.start()

        def connect():
            try:
                self.server_sock = register_with_server("172.28.14.116", 65432) # replace with your server IP
                self.signals.connected.emit(True)
                self.signals.log.emit("Connected to server")
            except Exception as e:
                self.signals.connected.emit(False)
                self.signals.log.emit(f"Connection failed: {e}")

        threading.Thread(target=connect, daemon=True).start()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file to share")
        if path:
            self.local_path.setText(path)
            name = Path(path).stem
            self.shared_name.setText(name)

    def _publish(self):
        local = self.local_path.text().strip()
        shared = self.shared_name.text().strip()
        if not local or not shared:
            QMessageBox.warning(self, "Missing", "Both fields are required.")
            return
        if not os.path.isfile(local):
            QMessageBox.critical(self, "Error", "File not found.")
            return

        def worker():
            try:
                announce_file_to_server(self.server_sock, local, shared)
                self.signals.log.emit(f"Published '{shared}'")
            except Exception as e:
                self.signals.log.emit(f"Publish error: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _search(self):
        fname = self.search_input.text().strip()
        if not fname:
            QMessageBox.warning(self, "Empty", "Enter a file name.")
            return
        self.peer_tree.clear()

        def worker():
            try:
                query = {"action": "fetch", "fname": fname}
                self.server_sock.sendall(json.dumps(query).encode() + b'\n')
                raw = self.server_sock.recv(4096).decode().strip()
                resp = json.loads(raw)
                peers = resp.get("addresses", [])
                self.signals.peers.emit(peers)
                self.signals.log.emit(f"Found {len(peers)} peer(s)")
            except Exception as e:
                self.signals.log.emit(f"Search error: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _update_peers(self, peers):
        self.peer_tree.clear()
        self.peer_data = peers
        for p in peers:
            item = QTreeWidgetItem([
                p['ip'],
                p['hostname'],
                os.path.basename(p.get('lname', ''))[:30],
                p.get('extension', '')
            ])
            self.peer_tree.addTopLevelItem(item)

    def _download_selected(self):
        item = self.peer_tree.currentItem()
        if not item:
            QMessageBox.information(self, "Select", "Choose a peer first.")
            return
        idx = self.peer_tree.indexOfTopLevelItem(item)
        peer = self.peer_data[idx]

        fname = self.search_input.text()
        ext = peer.get('extension', '')
        default = f"{fname}.{ext}" if ext else fname
        save_path, _ = QFileDialog.getSaveFileName(self, "Save As", default)
        if not save_path:
            return

        def worker():
            try:
                download_file_from_peer(peer['ip'], peer['lname'], save_path)
                self.signals.log.emit(f"Downloaded: {os.path.basename(save_path)}")
            except Exception as e:
                self.signals.log.emit(f"Download failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        shutdown_event.set()
        if self.server_sock:
            try:
                self.server_sock.close()
            except:
                pass
        event.accept()


# ----------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ClientWindow()
    win.show()
    sys.exit(app.exec())