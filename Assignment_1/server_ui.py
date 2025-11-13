# server_ui.py
import sys
import threading
import logging
import time
from PyQt6.QtCore import Qt, QTimer, QDateTime, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QFrame, QSplitter, QMessageBox, QGraphicsDropShadowEffect
)

# ----------------------------------------------------------------------
# Backend imports
# ----------------------------------------------------------------------
from server import (
    run_server,
    active_clients,
    client_lock,
    discover_peer_files,
    ping_peer,
    check_peer_online,
)


# ----------------------------------------------------------------------
# Logging → UI
# ----------------------------------------------------------------------
class QtLogHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        self.callback(msg)


# ----------------------------------------------------------------------
# Animated Button Factory
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

    glow = QGraphicsDropShadowEffect()
    glow.setBlurRadius(0)
    glow.setColor(QColor(3, 218, 198))  # teal
    glow.setOffset(0, 0)
    btn.setGraphicsEffect(glow)

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
# Main Server Window
# ----------------------------------------------------------------------
class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P File Sharer – Server")
        self.resize(920, 660)
        self.setStyleSheet(self._stylesheet())

        self._status_cache = {}
        self._status_lock = threading.Lock()
        self._status_thread = None
        self._status_check_interval = 5.0  # seconds
        self._last_status_check = 0.0

        self._setup_ui()
        self._start_server()
        self._start_refresh_timer()

    # ------------------------------------------------------------------
    # Clean Stylesheet (Teal focus!)
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
        QLineEdit:focus { 
            border:1px solid #03dac6; 
            background:#1e1e1e; 
        }
        QTreeWidget {
            background:#1a1a1a; border-radius:12px; font-size:13px;
        }
        QTreeWidget::item { padding:10px; }
        QTreeWidget::item:selected { background:#03dac6; color:black; }
        QTreeWidget::item:hover { background:#252525; }
        QTextEdit {
            background:#1a1a1a; border-radius:12px; padding:12px;
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
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("P2P File Sharing Server")
        title.setStyleSheet("font-size:26px; font-weight:bold;")
        self.status_lbl = QLabel("Running")
        self.status_lbl.setStyleSheet("color:#4caf50; font-size:14px;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.status_lbl)
        layout.addLayout(hdr)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left: Clients
        left = QFrame()
        left.setStyleSheet("background:#1a1a1a; border-radius:16px; padding:16px;")
        left_lay = QVBoxLayout(left)
        left_lay.addWidget(QLabel("Connected Clients"))
        self.client_tree = QTreeWidget()
        self.client_tree.setHeaderLabels(["Hostname", "IP", "Status"])
        self.client_tree.setColumnWidth(0, 200)
        left_lay.addWidget(self.client_tree)
        splitter.addWidget(left)

        # Right: Admin + Log
        right = QFrame()
        right_lay = QVBoxLayout(right)

        # Admin Panel
        admin = QFrame()
        admin.setStyleSheet("background:#1f1f1f; border-radius:12px; padding:12px;")
        admin_lay = QHBoxLayout(admin)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Enter hostname…")
        self._add_focus_glow(self.host_input, QColor(3, 218, 198))  # TEAL GLOW

        disc_btn = create_animated_button(self, "Discover Files", "#03dac6", "#66fff4", "#00bfa5")
        ping_btn = create_animated_button(self, "Ping",  "#03dac6", "#66fff4", "#00bfa5")

        disc_btn.clicked.connect(self._discover)
        ping_btn.clicked.connect(self._ping)

        admin_lay.addWidget(self.host_input)
        admin_lay.addWidget(disc_btn)
        admin_lay.addWidget(ping_btn)
        right_lay.addWidget(admin)

        # Log
        log_box = QFrame()
        log_box.setStyleSheet("background:#1a1a1a; border-radius:12px;")
        log_lay = QVBoxLayout(log_box)
        log_lay.addWidget(QLabel("Server Log"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_lay.addWidget(self.log_view)
        right_lay.addWidget(log_box)

        splitter.addWidget(right)
        splitter.setSizes([420, 500])

        # Status bar
        self.statusBar().showMessage("Server started")

        # Logging
        handler = QtLogHandler(self._log)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # Focus glow for QLineEdit (TEAL)
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
    # Logging
    # ------------------------------------------------------------------
    def _log(self, msg):
        ts = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.log_view.append(f"[{ts}] {msg}")
        self.statusBar().showMessage(msg.split("\n")[-1][:120])

    # ------------------------------------------------------------------
    # Server & Refresh
    # ------------------------------------------------------------------
    def _start_server(self):
        threading.Thread(target=run_server, daemon=True).start()

    def _start_refresh_timer(self):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._on_refresh_tick)
        self._refresh_timer.start(2500)
        self._on_refresh_tick()

    def _on_refresh_tick(self):
        self._refresh_clients()
        self._ensure_status_worker()

    def _ensure_status_worker(self):
        now = time.monotonic()
        active_thread = self._status_thread and self._status_thread.is_alive()
        if active_thread or now - self._last_status_check < self._status_check_interval:
            return

        self._status_thread = threading.Thread(target=self._update_statuses, daemon=True)
        self._status_thread.start()

    def _update_statuses(self):
        try:
            with client_lock:
                hostnames = list(active_clients.keys())

            new_cache = {}
            for hostname in hostnames:
                online, ip_addr, detail = check_peer_online(hostname)
                new_cache[hostname] = {
                    "online": online,
                    "detail": detail or "",
                    "ip": ip_addr or "",
                }

            with self._status_lock:
                self._status_cache = new_cache

            self._last_status_check = time.monotonic()
        finally:
            self._status_thread = None

    def _refresh_clients(self):
        with client_lock:
            current = dict(active_clients)
        with self._status_lock:
            status_snapshot = dict(self._status_cache)
        self.client_tree.clear()
        for hn, sock in current.items():
            try:
                ip = sock.getpeername()[0]
            except OSError:
                ip = "?"

            status_info = status_snapshot.get(hn)
            if status_info is None:
                status_text = "Checking…"
                color = QColor("#ffa000")
                detail = ""
            elif status_info["online"]:
                status_text = "Online"
                color = QColor("#4caf50")
                detail = ""
            else:
                status_text = "Offline"
                color = QColor("#f44336")
                detail = status_info["detail"]

            item = QTreeWidgetItem([hn, ip, status_text])
            item.setForeground(2, color)
            if detail:
                item.setToolTip(2, detail)
            self.client_tree.addTopLevelItem(item)

    # ------------------------------------------------------------------
    # Admin Actions
    # ------------------------------------------------------------------
    def _discover(self):
        hn = self.host_input.text().strip()
        if not hn:
            QMessageBox.warning(self, "Empty", "Enter a hostname.")
            return
        threading.Thread(target=discover_peer_files, args=(hn,), daemon=True).start()

    def _ping(self):
        hn = self.host_input.text().strip()
        if not hn:
            QMessageBox.warning(self, "Empty", "Enter a hostname.")
            return
        threading.Thread(target=ping_peer, args=(hn,), daemon=True).start()

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._log("Shutting down server…")
        import os, signal
        os.kill(os.getpid(), signal.SIGINT)
        event.accept()


# ----------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ServerWindow()
    win.show()
    sys.exit(app.exec())
