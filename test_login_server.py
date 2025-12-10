import os
import sys
import subprocess
import threading
import webbrowser
import signal
import time
from datetime import datetime
import queue
import psutil

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QSplitter, QStatusBar,
    QMessageBox, QGroupBox, QProgressBar, QTabWidget, QGridLayout,
    QToolButton, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette, QIcon, QPainter, QLinearGradient, QBrush

# === 1. AUTO-INSTALL REQUIRED DEPENDENCIES ===
required_modules = [
    "django",
    "djangorestframework",
    "djangorestframework-simplejwt",
    "django-cors-headers",
    "PyQt6",
    "psutil"
]

print("[INFO] Checking and installing required packages...\n")
for module in required_modules:
    try:
        __import__(module.split("-")[0])
    except ImportError:
        print(f"[INSTALL] Installing missing module: {module}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# === 2. PROJECT PATH ===
script_dir = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(script_dir, "loginlogout")

if not os.path.exists(project_path):
    possible_paths = [
        project_path,
        os.path.join(os.path.dirname(script_dir), "loginlogout"),
        os.path.join(script_dir, "..", "loginlogout"),
        r"c:\Users\Shalini Sharma\PycharmProjects\pythonProject3\general_work\web_code\tcl webpage\login\login\loginlogout"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            project_path = path
            print(f"[SUCCESS] Found project at: {project_path}")
            break
    else:
        error_msg = f"[ERROR] Project path not found. Tried:\n"
        for path in possible_paths:
            error_msg += f"  - {path}\n"
        raise FileNotFoundError(error_msg)

print(f"[INFO] Using project path: {project_path}")
os.chdir(project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loginlogout.settings")

# === Custom Styled Button ===
class EDAButton(QPushButton):
    """Professional EDA-style button with hover effects"""
    def __init__(self, text="", color="#3498db", parent=None):
        super().__init__(text, parent)
        self.default_color = color
        self.hover_color = self.adjust_color(color, 30)
        self.pressed_color = self.adjust_color(color, -30)
        self.disabled_color = "#424242"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.default_color};
                color: white;
                padding: 14px 28px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                border: none;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_color};
                padding-top: 15px;
                padding-bottom: 13px;
            }}
            QPushButton:disabled {{
                background-color: {self.disabled_color};
                color: #757575;
            }}
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    
    def adjust_color(self, color, amount):
        """Adjust color brightness"""
        color = QColor(color)
        if amount > 0:
            return color.lighter(100 + amount).name()
        else:
            return color.darker(100 - amount).name()

# === Django Server Thread ===
class DjangoServerThread(QThread):
    """Thread for running Django server"""
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.process = None
    
    def run(self):
        """Main thread execution"""
        try:
            import django
            from django.core.management import execute_from_command_line
            
            django.setup()
            self.log_signal.emit("[SYSTEM] Starting Django server...", "info")
            self.status_signal.emit("Starting...")
            
            execute_from_command_line(["manage.py", "runserver", "--noreload"])
            
        except Exception as e:
            error_msg = f"[ERROR] Server error: {str(e)}"
            self.log_signal.emit(error_msg, "error")
            self.status_signal.emit("Error")
        finally:
            self.log_signal.emit("[SYSTEM] Server stopped", "info")
            self.status_signal.emit("Stopped")
    
    def stop(self):
        """Stop the server thread"""
        self.is_running = False
        self.terminate()
        self.wait()

# === Main Window ===
class DjangoServerController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.is_running = False
        self.start_time = None
        self.setup_ui()
        self.setup_signals()
        
    def setup_ui(self):
        """Setup the user interface with dark EDA theme"""
        self.setWindowTitle("TCLFORGE Server Controller - Professional Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        self.set_dark_theme()
        
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # === TOP BAR - Header Section ===
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(80)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 10, 20, 10)
        
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        main_title = QLabel("TCLFORGE SERVER CONTROLLER")
        main_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        main_title.setStyleSheet("color: #64B5F6; margin-bottom: 2px;")
        
        sub_title = QLabel("Professional Development Dashboard")
        sub_title.setFont(QFont("Segoe UI", 10))
        sub_title.setStyleSheet("color: #90A4AE;")
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        
        project_widget = QWidget()
        project_layout = QVBoxLayout(project_widget)
        project_layout.setContentsMargins(0, 0, 0, 0)
        
        project_info = QLabel(f"Project: {os.path.basename(project_path)}")
        project_info.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        project_info.setStyleSheet("color: #B0BEC5; padding: 2px;")
        
        url_info = QLabel("URL: http://127.0.0.1:8000")
        url_info.setFont(QFont("Segoe UI", 9))
        url_info.setStyleSheet("color: #4FC3F7; padding: 2px; background-color: #263238; border-radius: 3px; padding: 3px 8px;")
        
        project_layout.addWidget(project_info)
        project_layout.addWidget(url_info)
        
        top_bar_layout.addWidget(title_widget)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(project_widget)
        
        # === STATUS INDICATOR BAR ===
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        status_bar.setFixedHeight(60)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(20, 8, 20, 8)
        
        self.status_indicator = QLabel("SERVER STOPPED")
        self.status_indicator.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.status_indicator.setStyleSheet("""
            QLabel {
                background-color: #F44336;
                color: white;
                padding: 10px 25px;
                border-radius: 4px;
                font-weight: bold;
                border-left: 4px solid #D32F2F;
            }
        """)
        
        self.uptime_label = QLabel("UPTIME: --:--:--")
        self.uptime_label.setFont(QFont("Segoe UI", 10))
        self.uptime_label.setStyleSheet("""
            QLabel {
                color: #B0BEC5;
                background-color: #263238;
                padding: 8px 15px;
                border-radius: 4px;
                border: 1px solid #37474F;
            }
        """)
        
        self.cpu_label = QLabel("CPU: --%")
        self.cpu_label.setFont(QFont("Segoe UI", 10))
        self.cpu_label.setStyleSheet("""
            QLabel {
                color: #B0BEC5;
                background-color: #263238;
                padding: 8px 15px;
                border-radius: 4px;
                border: 1px solid #37474F;
            }
        """)
        
        self.memory_label = QLabel("MEMORY: --%")
        self.memory_label.setFont(QFont("Segoe UI", 10))
        self.memory_label.setStyleSheet("""
            QLabel {
                color: #B0BEC5;
                background-color: #263238;
                padding: 8px 15px;
                border-radius: 4px;
                border: 1px solid #37474F;
            }
        """)
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        status_layout.addWidget(self.uptime_label)
        status_layout.addWidget(self.cpu_label)
        status_layout.addWidget(self.memory_label)
        
        # === CONTROL PANEL ===
        control_panel = QFrame()
        control_panel.setObjectName("controlPanel")
        control_panel.setFixedHeight(100)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 15, 20, 15)
        control_layout.setSpacing(20)
        
        self.start_button = EDAButton("START SERVER", "#4CAF50")
        self.start_button.clicked.connect(self.start_server)
        self.start_button.setToolTip("Start Django development server")
        
        self.stop_button = EDAButton("STOP SERVER", "#F44336")
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stop the running server")
        
        self.open_button = EDAButton("OPEN BROWSER", "#2196F3")
        self.open_button.clicked.connect(self.open_browser)
        self.open_button.setEnabled(False)
        self.open_button.setToolTip("Open server in default web browser")
        
        self.restart_button = EDAButton("RESTART", "#FF9800")
        self.restart_button.clicked.connect(self.restart_server)
        self.restart_button.setToolTip("Restart the server")
        
        self.exit_button = EDAButton("EXIT", "#607D8B")
        self.exit_button.clicked.connect(self.exit_app)
        self.exit_button.setToolTip("Exit application")
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.restart_button)
        control_layout.addWidget(self.exit_button)
        
        # === MAIN CONTENT AREA ===
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(2)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #37474F;
            }
        """)
        
        # Left Panel - Logs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        log_header = QFrame()
        log_header.setFixedHeight(40)
        log_header_layout = QHBoxLayout(log_header)
        log_header_layout.setContentsMargins(10, 0, 10, 0)
        
        log_title = QLabel("LIVE SERVER LOGS")
        log_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        log_title.setStyleSheet("color: #64B5F6;")
        
        log_controls = QHBoxLayout()
        self.clear_log_btn = QPushButton("Clear")
        self.clear_log_btn.setFixedSize(80, 30)
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #455A64;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        self.clear_log_btn.clicked.connect(self.clear_logs)
        
        self.save_log_btn = QPushButton("Save")
        self.save_log_btn.setFixedSize(80, 30)
        self.save_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #0288D1;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #039BE5;
            }
        """)
        self.save_log_btn.clicked.connect(self.save_logs)
        
        log_header_layout.addWidget(log_title)
        log_header_layout.addStretch()
        log_header_layout.addWidget(self.clear_log_btn)
        log_header_layout.addWidget(self.save_log_btn)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0D1B2A;
                color: #E0E1DD;
                border: 2px solid #1B263B;
                border-radius: 4px;
                padding: 10px;
                selection-background-color: #415A77;
            }
        """)
        
        left_layout.addWidget(log_header)
        left_layout.addWidget(self.log_text)
        
        # Right Panel - Stats and Info
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        stats_group = QGroupBox("SERVER STATISTICS")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #90A4AE;
                border: 2px solid #37474F;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1E282C;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(10)
        
        self.stats_labels = {}
        stats_info = [
            ("Project", f"Project: {os.path.basename(project_path)}", "#4FC3F7"),
            ("Status", "Stopped", "#F44336"),
            ("URL", "URL: http://127.0.0.1:8000", "#4FC3F7"),
            ("Port", "Port: 8000", "#4FC3F7"),
            ("Log Count", "Logs: 0", "#FFB74D"),
            ("Last Started", "Started: --:--:--", "#FFB74D"),
            ("Python", f"Python: {sys.version.split()[0]}", "#81C784"),
            ("Django", "Django: Checking...", "#81C784"),
        ]
        
        for i, (title, value, color) in enumerate(stats_info):
            title_label = QLabel(title.upper())
            title_label.setStyleSheet(f"color: #78909C; font-size: 9px; font-weight: bold;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            stats_layout.addWidget(title_label, i, 0)
            stats_layout.addWidget(value_label, i, 1)
            self.stats_labels[title] = value_label
        
        stats_group.setLayout(stats_layout)
        
        actions_group = QGroupBox("QUICK ACTIONS")
        actions_group.setStyleSheet(stats_group.styleSheet())
        
        actions_layout = QVBoxLayout()
        
        action_buttons = [
            ("Open Project Folder", self.open_project_folder),
            ("Django Admin", self.open_django_admin),
            ("Documentation", self.open_docs),
            ("Clear Cache", self.clear_cache),
        ]
        
        for text, callback in action_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #37474F;
                    color: #CFD8DC;
                    padding: 8px;
                    border: 1px solid #455A64;
                    border-radius: 4px;
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover {
                    background-color: #455A64;
                    border-color: #546E7A;
                }
            """)
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn)
        
        actions_group.setLayout(actions_layout)
        
        right_layout.addWidget(stats_group)
        right_layout.addWidget(actions_group)
        right_layout.addStretch()
        
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([800, 400])
        
        # === ASSEMBLE MAIN LAYOUT ===
        main_layout.addWidget(top_bar)
        main_layout.addWidget(status_bar)
        main_layout.addWidget(control_panel)
        main_layout.addWidget(content_splitter, 1)
        
        self.statusBar().showMessage("Ready - Professional TCLFORGE Server Controller")
        
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        
        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self.update_resources)
        self.resource_timer.start(2000)
        
        self.add_log("=" * 70, "system")
        self.add_log("PROFESSIONAL TCLFORGE SERVER CONTROLLER STARTED", "system")
        self.add_log(f"Project: {project_path}", "info")
        self.add_log(f"Directory: {os.getcwd()}", "info")
        self.add_log(f"Python: {sys.version.split()[0]}", "info")
        self.add_log("=" * 70, "system")
        
        self.update_stats()
        self.update_resources()
    
    def set_dark_theme(self):
        """Set dark theme for the application"""
        dark_palette = QPalette()
        
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(33, 33, 33))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(dark_palette)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A1A;
            }
            QFrame#topBar {
                background-color: #212121;
                border-bottom: 2px solid #37474F;
            }
            QFrame#statusBar {
                background-color: #263238;
                border-bottom: 1px solid #37474F;
            }
            QFrame#controlPanel {
                background-color: #212121;
                border-bottom: 1px solid #37474F;
            }
            QMenu {
                background-color: #263238;
                color: #E0E0E0;
                border: 1px solid #37474F;
            }
            QMenu::item:selected {
                background-color: #37474F;
            }
            QScrollBar:vertical {
                background: #263238;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #546E7A;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #78909C;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def setup_signals(self):
        """Setup signal connections"""
        pass

    def add_log(self, message, log_type="info"):
        """Add a formatted log message to both GUI and console with proper newlines."""
        from datetime import datetime
        from PyQt6.QtGui import QTextCursor

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Color and prefix mapping
        colors = {
            "info": "#4FC3F7",
            "success": "#81C784",
            "warning": "#FFB74D",
            "error": "#F44336",
            "system": "#BA68C8"
        }
        prefixes = {
            "info": "[INFO]",
            "success": "[OK]",
            "warning": "[WARN]",
            "error": "[ERROR]",
            "system": "[SYSTEM]"
        }

        color = colors.get(log_type, "#4FC3F7")
        prefix = prefixes.get(log_type, "[INFO]")

        # Ensure message is text-safe
        safe_message = str(message).replace("<", "&lt;").replace(">", "&gt;").strip()

        # GUI log formatting
        html = (
            f'<div style="margin-bottom:4px;">'
            f'<span style="color:#9ca3af;">[{timestamp}]</span> '
            f'<span style="color:{color};font-weight:bold;">{prefix}</span> '
            f'<span style="color:#e5e7eb;">{safe_message}</span>'
            f'</div>'
        )

        # Append to GUI log panel
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
        self.log_text.insertHtml(html + "<br>")  # ensures visual line break
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
        self.log_text.ensureCursorVisible()

        # === Console logging ===
        console_line = f"\n[{timestamp}] {prefix} {safe_message}"
        sys.stdout.write(console_line + "\n")  # guaranteed newline separation
        sys.stdout.flush()

    def update_stats(self):
        """Update statistics panel"""
        if self.is_running:
            self.stats_labels["Status"].setText("Running")
            self.stats_labels["Status"].setStyleSheet("color: #81C784; font-size: 11px; font-weight: bold;")
            if self.start_time:
                last_started = self.start_time.strftime("%H:%M:%S")
                self.stats_labels["Last Started"].setText(f"Started: {last_started}")
        else:
            self.stats_labels["Status"].setText("Stopped")
            self.stats_labels["Status"].setStyleSheet("color: #F44336; font-size: 11px; font-weight: bold;")
        
        try:
            import django
            self.stats_labels["Django"].setText(f"Django: {django.get_version()}")
        except:
            pass
    
    def update_uptime(self):
        """Update uptime display"""
        if self.start_time and self.is_running:
            uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            self.uptime_label.setText(f"UPTIME: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.update_stats()
    
    def update_resources(self):
        """Update CPU and memory usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            cpu_color = "#81C784" if cpu_percent < 70 else "#FFB74D" if cpu_percent < 90 else "#F44336"
            mem_color = "#81C784" if memory_percent < 70 else "#FFB74D" if memory_percent < 90 else "#F44336"
            
            self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
            self.cpu_label.setStyleSheet(f"""
                QLabel {{
                    color: {cpu_color};
                    background-color: #263238;
                    padding: 8px 15px;
                    border-radius: 4px;
                    border: 1px solid #37474F;
                }}
            """)
            
            self.memory_label.setText(f"MEMORY: {memory_percent:.1f}%")
            self.memory_label.setStyleSheet(f"""
                QLabel {{
                    color: {mem_color};
                    background-color: #263238;
                    padding: 8px 15px;
                    border-radius: 4px;
                    border: 1px solid #37474F;
                }}
            """)
            
        except Exception as e:
            self.cpu_label.setText("CPU: --%")
            self.memory_label.setText("MEMORY: --%")
    
    def start_server(self):
        """Start the Django server"""
        if self.is_running:
            self.add_log("Server is already running!", "warning")
            return
        
        manage_py = os.path.join(project_path, "manage.py")
        if not os.path.exists(manage_py):
            self.add_log(f"ERROR: manage.py not found at: {manage_py}", "error")
            QMessageBox.critical(self, "Error", 
                               f"manage.py not found at:\n{manage_py}\n\n"
                               "Please ensure this is a valid Django project.")
            return
        
        self.add_log("Checking Django project...", "system")
        self.add_log(f"Found manage.py at: {manage_py}", "success")
        
        try:
            self.server_thread = DjangoServerThread()
            self.server_thread.log_signal.connect(self.handle_server_log)
            self.server_thread.status_signal.connect(self.handle_server_status)
            self.server_thread.start()
            
            self.is_running = True
            self.start_time = datetime.now()
            
            self.status_indicator.setText("SERVER RUNNING")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 25px;
                    border-radius: 4px;
                    font-weight: bold;
                    border-left: 4px solid #388E3C;
                }
            """)
            
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.open_button.setEnabled(True)
            
            self.add_log("Starting Django server...", "info")
            self.add_log("Server will be available at: http://127.0.0.1:8000/", "success")
            self.add_log("Monitoring server logs...", "system")
            
            self.uptime_timer.start(1000)
            
            self.update_stats()
            
        except Exception as e:
            self.add_log(f"Failed to start server: {str(e)}", "error")
            QMessageBox.critical(self, "Error", f"Failed to start server:\n{str(e)}")
            self.is_running = False
            self.update_button_states()
    
    def stop_server(self):
        """Stop the Django server"""
        if not self.is_running:
            self.add_log("Server is not running!", "warning")
            return
        
        reply = QMessageBox.question(self, "Stop Server",
                                   "Are you sure you want to stop the server?\n\n"
                                   "This will terminate the Django process.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.add_log("Stopping server...", "warning")
            
            if self.server_thread:
                self.server_thread.stop()
                self.server_thread = None
            
            self.is_running = False
            
            self.status_indicator.setText("SERVER STOPPED")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    background-color: #F44336;
                    color: white;
                    padding: 10px 25px;
                    border-radius: 4px;
                    font-weight: bold;
                    border-left: 4px solid #D32F2F;
                }
            """)
            
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.open_button.setEnabled(False)
            
            self.uptime_timer.stop()
            self.uptime_label.setText("UPTIME: --:--:--")
            
            self.add_log("Server stopped successfully", "success")
            self.update_stats()
    
    def restart_server(self):
        """Restart the server"""
        if self.is_running:
            self.stop_server()
            time.sleep(1)
        self.start_server()
    
    def open_browser(self):
        """Open server URL in web browser"""
        if not self.is_running:
            self.add_log("Cannot open browser: Server is not running!", "warning")
            QMessageBox.warning(self, "Warning", "Server is not running. Please start the server first.")
            return
        
        try:
            url = "http://127.0.0.1:8000/"
            webbrowser.open(url)
            self.add_log(f"Opening browser to: {url}", "success")
            self.statusBar().showMessage(f"Opened {url} in browser", 3000)
        except Exception as e:
            self.add_log(f"Failed to open browser: {str(e)}", "error")
            QMessageBox.critical(self, "Error", f"Failed to open browser:\n{str(e)}")
    
    def handle_server_log(self, message, log_type):
        """Handle log messages from server thread"""
        self.add_log(message, log_type)
    
    def handle_server_status(self, status):
        """Handle status updates from server thread"""
        if status == "Error":
            self.is_running = False
            self.update_button_states()
            self.status_indicator.setText("SERVER ERROR")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    background-color: #FF9800;
                    color: white;
                    padding: 10px 25px;
                    border-radius: 4px;
                    font-weight: bold;
                    border-left: 4px solid #F57C00;
                }
            """)
            self.uptime_timer.stop()
    
    def update_button_states(self):
        """Update button enabled states"""
        self.start_button.setEnabled(not self.is_running)
        self.stop_button.setEnabled(self.is_running)
        self.open_button.setEnabled(self.is_running)
        self.update_stats()
    
    def clear_logs(self):
        """Clear all logs"""
        reply = QMessageBox.question(self, "Clear Logs",
                                   "Are you sure you want to clear all logs?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_text.clear()
            self.add_log("Logs cleared", "system")
            self.stats_labels["Log Count"].setText("Logs: 0")
    
    def save_logs(self):
        """Save logs to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"django_server_logs_{timestamp}.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            
            self.add_log(f"Logs saved to: {log_file}", "success")
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText(f"Logs saved to:\n{log_file}")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #263238;
                }
                QLabel {
                    color: #E0E0E0;
                }
            """)
            msg.exec()
            
        except Exception as e:
            self.add_log(f"Failed to save logs: {str(e)}", "error")
            QMessageBox.critical(self, "Error", f"Failed to save logs:\n{str(e)}")
    
    # === Quick Actions ===
    def open_project_folder(self):
        """Open project folder in file explorer"""
        try:
            if sys.platform == "win32":
                os.startfile(project_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", project_path])
            else:
                subprocess.Popen(["xdg-open", project_path])
            self.add_log(f"Opened project folder: {project_path}", "success")
        except Exception as e:
            self.add_log(f"Failed to open folder: {str(e)}", "error")
    
    def open_django_admin(self):
        """Open Django admin panel"""
        if self.is_running:
            url = "http://127.0.0.1:8000/admin/"
            webbrowser.open(url)
            self.add_log(f"Opening Django admin: {url}", "success")
        else:
            self.add_log("Server must be running to open admin panel!", "warning")
    
    def open_docs(self):
        """Open Django documentation"""
        try:
            webbrowser.open("https://docs.djangoproject.com/")
            self.add_log("Opening Django documentation", "success")
        except Exception as e:
            self.add_log(f"Failed to open docs: {str(e)}", "error")
    
    def clear_cache(self):
        """Clear Django cache"""
        try:
            for root, dirs, files in os.walk(project_path):
                for dir in dirs:
                    if dir == "__pycache__":
                        pycache_path = os.path.join(root, dir)
                        import shutil
                        shutil.rmtree(pycache_path)
                        self.add_log(f"Cleared cache: {pycache_path}", "success")
            
            self.add_log("Cache cleared successfully", "success")
        except Exception as e:
            self.add_log(f"Failed to clear cache: {str(e)}", "error")
    
    def exit_app(self):
        """Exit the application"""
        if self.is_running:
            reply = QMessageBox.question(self, "Exit Application",
                                       "Server is still running!\n\n"
                                       "Are you sure you want to exit?\n"
                                       "This will stop the server.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_server()
                time.sleep(1)
                QApplication.quit()
        else:
            reply = QMessageBox.question(self, "Exit Application",
                                       "Exit TCLFORGE Server Controller?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.add_log("Application closing...", "system")
                QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.exit_app()
        event.ignore()

# === Main execution ===
if __name__ == "__main__":
    print("=" * 70)
    print("PROFESSIONAL TCLFORGE SERVER CONTROLLER")
    print("=" * 70)
    print(f"Project Path: {project_path}")
    print(f"Current Directory: {os.getcwd()}")
    print("\nProfessional Features:")
    print("   - Dark EDA-Themed Professional Interface")
    print("   - Live Resource Monitoring (CPU/Memory)")
    print("   - Real-time Color-coded Log Panel")
    print("   - Server Statistics Dashboard")
    print("   - Quick Action Panel")
    print("   - Professional Button Animations")
    print("=" * 70)
    
    manage_py = os.path.join(project_path, "manage.py")
    if not os.path.exists(manage_py):
        print(f"ERROR: manage.py not found at: {manage_py}")
        print("   Please ensure you're in the correct Django project directory.")
        print("   The directory should contain manage.py file.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print(f"Found manage.py at: {manage_py}")
    
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        app.setFont(QFont("Segoe UI", 9))
        
        controller = DjangoServerController()
        controller.show()
        
        print("Professional PyQt6 GUI created successfully")
        print("Application ready - Professional Dashboard should appear")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Failed to create PyQt6 GUI: {e}")
        input("\nPress Enter to exit...")