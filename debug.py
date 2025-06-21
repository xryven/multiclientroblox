"""
Multiclient Debug Application
============================

A comprehensive debugging version of the multiclient system tray application
with extensive logging, dark theme UI, and detailed control capabilities.

Features:
- Singleton application using Windows mutex
- System tray integration with context menu
- Real-time logging of all events and actions
- Control panel for application management
- Dark theme UI for better visual experience
- Comprehensive error handling and reporting

Author: Generated for debugging purposes
"""

import sys
import win32event
import win32api
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import QTimer, QDateTime, pyqtSignal, QObject, Qt
import traceback
import os


# =============================================================================
# LOGGER CLASS - Handles all application logging
# =============================================================================

class Logger(QObject):
    """
    Custom logger class that handles all application logging.
    
    This class provides centralized logging functionality with different log levels
    and emits Qt signals to update the GUI in real-time. All log messages are
    timestamped and formatted consistently.
    
    Signals:
        log_signal: Emitted when a new log entry is created
    """
    
    # Qt signal that carries log messages to GUI components
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the logger object."""
        super().__init__()
        self.log("Logger initialized", "SYSTEM")
        
    def log(self, message, level="INFO"):
        """
        Log a message with specified level.
        
        Args:
            message (str): The message to log
            level (str): Log level (INFO, ERROR, WARNING, ACTION, EVENT, SYSTEM)
        """
        # Create timestamp with millisecond precision
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss.zzz")
        
        # Format the complete log message
        formatted_message = f"[{timestamp}] [{level:8}] {message}"
        
        # Emit signal for GUI updates (if connected)
        self.log_signal.emit(formatted_message)
        
        # Also print to console for backup/debugging
        print(formatted_message)
        
        # Log critical errors to system as well
        if level == "ERROR":
            print(f"CRITICAL: {message}", file=sys.stderr)


# =============================================================================
# LOG WINDOW CLASS - Displays all application events
# =============================================================================

class LogWindow(QWidget):
    """
    Debug log window that displays all application events in real-time.
    
    This window provides a comprehensive view of everything happening in the
    application, with features for log management and export functionality.
    """
    
    def __init__(self, logger):
        """
        Initialize the log window.
        
        Args:
            logger (Logger): The logger instance to connect to
        """
        super().__init__()
        self.logger = logger
        self.log_entry_count = 0  # Track number of log entries for statistics
        
        # Log the creation of this window
        self.logger.log("Initializing Log Window", "SYSTEM")
        
        # Setup the user interface
        self.init_ui()
        
        # Apply dark theme styling
        self.apply_dark_theme()
        
        self.logger.log("Log Window initialized successfully", "SYSTEM")
        
    def init_ui(self):
        """Initialize the user interface components."""
        self.logger.log("Setting up Log Window UI components", "SYSTEM")
        
        # Window configuration
        self.setWindowTitle("Multiclient - Debug Log [DARK MODE]")
        self.setGeometry(100, 100, 900, 700)  # Larger window for better visibility
        self.setMinimumSize(600, 400)  # Prevent window from being too small
        
        # Main layout container
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # Add spacing between elements
        main_layout.setContentsMargins(15, 15, 15, 15)  # Add margins
        
        # === HEADER SECTION ===
        header_layout = QHBoxLayout()
        
        # Main title
        header = QLabel("🔍 DEBUG LOG - REAL-TIME EVENT MONITORING")
        header_font = QFont("Arial", 14, QFont.Bold)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header)
        
        # Status indicator
        self.status_indicator = QLabel("● ACTIVE")
        self.status_indicator.setStyleSheet("color: #00ff00; font-weight: bold;")
        header_layout.addWidget(self.status_indicator)
        
        main_layout.addLayout(header_layout)
        
        # === STATISTICS SECTION ===
        stats_layout = QHBoxLayout()
        
        self.entry_count_label = QLabel("Entries: 0")
        self.entry_count_label.setStyleSheet("color: #888888; font-size: 12px;")
        stats_layout.addWidget(self.entry_count_label)
        
        stats_layout.addStretch()  # Push elements to sides
        
        self.session_start_label = QLabel(f"Session started: {QDateTime.currentDateTime().toString('hh:mm:ss')}")
        self.session_start_label.setStyleSheet("color: #888888; font-size: 12px;")
        stats_layout.addWidget(self.session_start_label)
        
        main_layout.addLayout(stats_layout)
        
        # === LOG DISPLAY AREA ===
        self.logger.log("Creating log text display area", "SYSTEM")
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)  # Prevent accidental editing
        
        # Configure font for better readability
        log_font = QFont("Consolas", 10)  # Monospace font for aligned columns
        log_font.setStyleHint(QFont.TypeWriter)
        self.log_text.setFont(log_font)
        
        # Set maximum block count to prevent memory issues with large logs
        self.log_text.document().setMaximumBlockCount(10000)
        
        main_layout.addWidget(self.log_text)
        
        # === CONTROL BUTTONS SECTION ===
        self.logger.log("Creating log window control buttons", "SYSTEM")
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Clear log button
        self.clear_btn = QPushButton("🗑️ Clear Log")
        self.clear_btn.setToolTip("Clear all log entries from display")
        self.clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_btn)
        
        # Save log button
        self.save_btn = QPushButton("💾 Save Log")
        self.save_btn.setToolTip("Save current log to a text file")
        self.save_btn.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_btn)
        
        # Auto-scroll toggle
        self.autoscroll_cb = QCheckBox("Auto-scroll")
        self.autoscroll_cb.setChecked(True)
        self.autoscroll_cb.setToolTip("Automatically scroll to newest log entries")
        button_layout.addWidget(self.autoscroll_cb)
        
        # Filter controls
        button_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ALL", "ERROR", "WARNING", "INFO", "ACTION", "EVENT", "SYSTEM"])
        self.filter_combo.setToolTip("Filter log entries by level")
        self.filter_combo.currentTextChanged.connect(self.apply_log_filter)
        button_layout.addWidget(self.filter_combo)
        
        # Stretch to push buttons to left
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Apply the main layout
        self.setLayout(main_layout)
        
        # === CONNECT LOGGER SIGNALS ===
        self.logger.log_signal.connect(self.add_log_entry)
        self.logger.log("Log Window UI setup completed", "SYSTEM")
        
    def apply_dark_theme(self):
        """Apply dark theme styling to the log window."""
        self.logger.log("Applying dark theme to Log Window", "SYSTEM")
        
        # Main window dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QTextEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                selection-background-color: #404040;
            }
            
            QPushButton {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 6px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #505050;
                border-color: #707070;
            }
            
            QPushButton:pressed {
                background-color: #353535;
            }
            
            QComboBox {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                min-width: 80px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #ffffff;
                width: 6px;
                height: 6px;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #106ebe;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)
        
    def add_log_entry(self, message):
        """
        Add a new log entry to the display.
        
        Args:
            message (str): The formatted log message to add
        """
        # Increment entry counter
        self.log_entry_count += 1
        self.entry_count_label.setText(f"Entries: {self.log_entry_count}")
        
        # Color-code messages based on log level
        colored_message = self.colorize_log_message(message)
        
        # Add the message to the display
        self.log_text.append(colored_message)
        
        # Auto-scroll to bottom if enabled
        if self.autoscroll_cb.isChecked():
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    def colorize_log_message(self, message):
        """
        Apply color coding to log messages based on their level.
        
        Args:
            message (str): The log message to colorize
            
        Returns:
            str: HTML-formatted message with color coding
        """
        # Define color scheme for different log levels
        if "[ERROR   ]" in message:
            return f'<span style="color: #ff6b6b; font-weight: bold;">{message}</span>'
        elif "[WARNING ]" in message:
            return f'<span style="color: #ffd93d; font-weight: bold;">{message}</span>'
        elif "[ACTION  ]" in message:
            return f'<span style="color: #6bcf7f;">{message}</span>'
        elif "[EVENT   ]" in message:
            return f'<span style="color: #74c0fc;">{message}</span>'
        elif "[SYSTEM  ]" in message:
            return f'<span style="color: #da77f2;">{message}</span>'
        else:  # INFO and others
            return f'<span style="color: #ffffff;">{message}</span>'
            
    def apply_log_filter(self, filter_level):
        """
        Apply filtering to log display based on selected level.
        
        Args:
            filter_level (str): The log level to filter by ("ALL" shows everything)
        """
        self.logger.log(f"Applying log filter: {filter_level}", "ACTION")
        
        # This is a simplified implementation - in a full version you'd
        # maintain separate storage and filter the display accordingly
        if filter_level == "ALL":
            self.log_text.setPlainText(self.log_text.toPlainText())  # Refresh display
        
    def clear_log(self):
        """Clear all log entries from the display."""
        self.logger.log("User requested log clear", "ACTION")
        self.log_text.clear()
        self.log_entry_count = 0
        self.entry_count_label.setText("Entries: 0")
        self.logger.log("Log display cleared", "ACTION")
        
    def save_log(self):
        """Save the current log to a text file."""
        self.logger.log("User requested log save", "ACTION")
        
        try:
            # Generate default filename with timestamp
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            default_filename = f"multiclient_log_{timestamp}.txt"
            
            # Show file dialog
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Log File", 
                default_filename, 
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if filename:
                # Write log content to file
                with open(filename, 'w', encoding='utf-8') as f:
                    # Add header information
                    f.write("Multiclient Debug Log\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Saved: {QDateTime.currentDateTime().toString()}\n")
                    f.write(f"Total Entries: {self.log_entry_count}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Write actual log content (plain text, no HTML)
                    f.write(self.log_text.toPlainText())
                    
                self.logger.log(f"Log saved successfully to: {filename}", "ACTION")
                
                # Show success message
                QMessageBox.information(self, "Save Successful", 
                                      f"Log saved to:\n{filename}")
            else:
                self.logger.log("Log save cancelled by user", "ACTION")
                
        except Exception as e:
            error_msg = f"Error saving log file: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            QMessageBox.critical(self, "Save Error", error_msg)
            
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.log("Log Window close requested", "EVENT")
        # Hide instead of closing to keep it available
        self.hide()
        event.ignore()


# =============================================================================
# CONTROL WINDOW CLASS - Application management interface
# =============================================================================

class ControlWindow(QWidget):
    """
    Control panel window for managing the application.
    
    This window provides comprehensive control over the application's behavior,
    including monitoring toggles, statistics, and management functions.
    """
    
    def __init__(self, app, tray_icon, logger):
        """
        Initialize the control window.
        
        Args:
            app (QApplication): The main application instance
            tray_icon (QSystemTrayIcon): The system tray icon instance
            logger (Logger): The logger instance
        """
        super().__init__()
        
        # Store references to main application components
        self.app = app
        self.tray_icon = tray_icon
        self.logger = logger
        
        # Control flags
        self.monitoring_enabled = True
        self.detailed_logging = True
        
        self.logger.log("Initializing Control Window", "SYSTEM")
        
        # Setup user interface
        self.init_ui()
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Setup monitoring timers
        self.setup_monitoring()
        
        self.logger.log("Control Window initialized successfully", "SYSTEM")
        
    def init_ui(self):
        """Initialize the user interface components."""
        self.logger.log("Setting up Control Window UI components", "SYSTEM")
        
        # Window configuration
        self.setWindowTitle("Multiclient - Control Panel [DARK MODE]")
        self.setGeometry(200, 200, 500, 600)  # Larger for more controls
        self.setMinimumSize(400, 500)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # === HEADER SECTION ===
        header = QLabel("⚙️ CONTROL PANEL")
        header_font = QFont("Arial", 16, QFont.Bold)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # === STATUS GROUP ===
        self.logger.log("Creating status monitoring group", "SYSTEM")
        
        status_group = QGroupBox("📊 System Status")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)
        
        # Application status
        self.status_label = QLabel("🟢 Status: Running")
        self.status_label.setStyleSheet("color: #6bcf7f; font-weight: bold; font-size: 14px;")
        status_layout.addWidget(self.status_label)
        
        # Mutex status
        self.mutex_label = QLabel("🔒 Mutex: Active (Singleton Mode)")
        self.mutex_label.setStyleSheet("color: #74c0fc; font-size: 12px;")
        status_layout.addWidget(self.mutex_label)
        
        # System tray status
        self.tray_status_label = QLabel("📍 Tray Icon: Visible")
        self.tray_status_label.setStyleSheet("color: #74c0fc; font-size: 12px;")
        status_layout.addWidget(self.tray_status_label)
        
        # Memory usage (placeholder for actual implementation)
        self.memory_label = QLabel("💾 Memory: Monitoring...")
        self.memory_label.setStyleSheet("color: #ffd93d; font-size: 12px;")
        status_layout.addWidget(self.memory_label)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # === CONTROL GROUP ===
        self.logger.log("Creating application control group", "SYSTEM")
        
        control_group = QGroupBox("🎛️ Application Controls")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)
        
        # Monitoring controls
        monitoring_layout = QHBoxLayout()
        self.monitor_cb = QCheckBox("Enable System Monitoring")
        self.monitor_cb.setChecked(True)
        self.monitor_cb.setToolTip("Enable/disable system event monitoring")
        self.monitor_cb.stateChanged.connect(self.toggle_monitoring)
        monitoring_layout.addWidget(self.monitor_cb)
        control_layout.addLayout(monitoring_layout)
        
        # Detailed logging toggle
        logging_layout = QHBoxLayout()
        self.detailed_log_cb = QCheckBox("Detailed Logging")
        self.detailed_log_cb.setChecked(True)
        self.detailed_log_cb.setToolTip("Enable detailed event logging")
        self.detailed_log_cb.stateChanged.connect(self.toggle_detailed_logging)
        logging_layout.addWidget(self.detailed_log_cb)
        control_layout.addLayout(logging_layout)
        
        # Tray icon controls
        tray_layout = QHBoxLayout()
        self.tray_cb = QCheckBox("Show Tray Icon")
        self.tray_cb.setChecked(True)
        self.tray_cb.setToolTip("Show/hide system tray icon")
        self.tray_cb.stateChanged.connect(self.toggle_tray_icon)
        tray_layout.addWidget(self.tray_cb)
        control_layout.addLayout(tray_layout)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # === TESTING GROUP ===
        self.logger.log("Creating testing and diagnostics group", "SYSTEM")
        
        test_group = QGroupBox("🧪 Testing & Diagnostics")
        test_layout = QVBoxLayout()
        test_layout.setSpacing(8)
        
        # Test buttons layout
        test_buttons_layout = QHBoxLayout()
        
        # Test tray icon
        self.test_tray_btn = QPushButton("Test Tray Icon")
        self.test_tray_btn.setToolTip("Test tray icon functionality")
        self.test_tray_btn.clicked.connect(self.test_tray_icon)
        test_buttons_layout.addWidget(self.test_tray_btn)
        
        # Generate test log entries
        self.test_log_btn = QPushButton("Generate Test Logs")
        self.test_log_btn.setToolTip("Generate sample log entries for testing")
        self.test_log_btn.clicked.connect(self.generate_test_logs)
        test_buttons_layout.addWidget(self.test_log_btn)
        
        test_layout.addLayout(test_buttons_layout)
        
        # System info button
        self.sysinfo_btn = QPushButton("📋 System Information")
        self.sysinfo_btn.setToolTip("Display detailed system information")
        self.sysinfo_btn.clicked.connect(self.show_system_info)
        test_layout.addWidget(self.sysinfo_btn)
        
        test_group.setLayout(test_layout)
        main_layout.addWidget(test_group)
        
        # === STATISTICS GROUP ===
        self.logger.log("Creating statistics monitoring group", "SYSTEM")
        
        stats_group = QGroupBox("📈 Statistics")
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(8)
        
        # Uptime display
        self.uptime_label = QLabel("⏱️ Uptime: 00:00:00")
        self.uptime_label.setStyleSheet("color: #74c0fc; font-size: 12px; font-family: 'Consolas';")
        stats_layout.addWidget(self.uptime_label)
        
        # Event counters
        self.events_label = QLabel("📊 Events Logged: 0")
        self.events_label.setStyleSheet("color: #74c0fc; font-size: 12px;")
        stats_layout.addWidget(self.events_label)
        
        # Tray interactions
        self.tray_interactions_label = QLabel("🖱️ Tray Interactions: 0")
        self.tray_interactions_label.setStyleSheet("color: #74c0fc; font-size: 12px;")
        stats_layout.addWidget(self.tray_interactions_label)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # === ACTION BUTTONS ===
        self.logger.log("Creating main action buttons", "SYSTEM")
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Restart button
        self.restart_btn = QPushButton("🔄 Restart App")
        self.restart_btn.setToolTip("Restart the application")
        self.restart_btn.clicked.connect(self.restart_app)
        self.restart_btn.setStyleSheet("background-color: #0078d4;")
        button_layout.addWidget(self.restart_btn)
        
        # Exit button
        self.exit_btn = QPushButton("❌ Exit App")
        self.exit_btn.setToolTip("Exit the application safely")
        self.exit_btn.clicked.connect(self.exit_app)
        self.exit_btn.setStyleSheet("background-color: #d13438;")
        button_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(button_layout)
        
        # Add stretch to push everything up
        main_layout.addStretch()
        
        # Apply layout
        self.setLayout(main_layout)
        
        self.logger.log("Control Window UI setup completed", "SYSTEM")
        
    def apply_dark_theme(self):
        """Apply dark theme styling to the control window."""
        self.logger.log("Applying dark theme to Control Window", "SYSTEM")
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #ffffff;
            }
            
            QPushButton {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 6px;
                padding: 10px 16px;
                color: #ffffff;
                font-weight: bold;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #505050;
                border-color: #707070;
            }
            
            QPushButton:pressed {
                background-color: #353535;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
                font-size: 12px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 4px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #106ebe;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)
        
    def setup_monitoring(self):
        """Setup monitoring timers and counters."""
        self.logger.log("Setting up monitoring systems", "SYSTEM")
        
        # Track application start time
        self.start_time = QDateTime.currentDateTime()
        
        # Initialize counters
        self.event_count = 0
        self.tray_interaction_count = 0
        
        # Setup uptime timer (updates every second)
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)
        self.logger.log("Uptime monitoring started (1s interval)", "SYSTEM")
        
        # Setup system monitoring timer (updates every 5 seconds)
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system_stats)
        self.system_timer.start(5000)
        self.logger.log("System statistics monitoring started (5s interval)", "SYSTEM")
        
    def toggle_monitoring(self, state):
        """
        Toggle system monitoring on/off.
        
        Args:
            state (int): Checkbox state (0=unchecked, 2=checked)
        """
        self.monitoring_enabled = state == Qt.Checked
        status = "enabled" if self.monitoring_enabled else "disabled"
        
        self.logger.log(f"System monitoring {status} by user", "ACTION")
        
        # Update status display
        if self.monitoring_enabled:
            self.status_label.setText("🟢 Status: Running (Monitoring Active)")
            self.status_label.setStyleSheet("color: #6bcf7f; font-weight: bold; font-size: 14px;")
        else:
            self.status_label.setText("🟡 Status: Running (Monitoring Paused)")
            self.status_label.setStyleSheet("color: #ffd93d; font-weight: bold; font-size: 14px;")
            
    def toggle_detailed_logging(self, state):
        """
        Toggle detailed logging on/off.
        
        Args:
            state (int): Checkbox state (0=unchecked, 2=checked)
        """
        self.detailed_logging = state == Qt.Checked
        status = "enabled" if self.detailed_logging else "disabled"
        
        self.logger.log(f"Detailed logging {status} by user", "ACTION")
        
    def toggle_tray_icon(self, state):
        """
        Toggle tray icon visibility.
        
        Args:
            state (int): Checkbox state (0=unchecked, 2=checked)
        """
        if state == Qt.Checked:
            self.tray_icon.show()
            self.tray_status_label.setText("📍 Tray Icon: Visible")
            self.tray_status_label.setStyleSheet("color: #6bcf7f; font-size: 12px;")
            self.logger.log("Tray icon shown by user", "ACTION")
        else:
            self.tray_icon.hide()
            self.tray_status_label.setText("📍 Tray Icon: Hidden")
            self.tray_status_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
            self.logger.log("Tray icon hidden by user", "ACTION")
            
    def test_tray_icon(self):
        """Test tray icon functionality."""
        self.logger.log("Tray icon test initiated by user", "ACTION")
        
        if self.tray_icon.isVisible():
            # Update tooltip with current timestamp
            test_timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            new_tooltip = f"Multiclient - Test at {test_timestamp}"
            self.tray_icon.setToolTip(new_tooltip)
            
            self.logger.log(f"Tray icon tooltip updated: {new_tooltip}", "ACTION")
            
            # Show confirmation message
            QMessageBox.information(self, "Test Successful", 
                                  f"Tray icon test completed!\nTooltip updated to: {new_tooltip}")
        else:
            self.logger.log("Cannot test tray icon - icon is hidden", "WARNING")
            QMessageBox.warning(self, "Test Failed", 
                              "Cannot test tray icon because it is currently hidden.\n"
                              "Enable 'Show Tray Icon' first.")
            
    def generate_test_logs(self):
        """Generate sample log entries for testing purposes."""
        self.logger.log("Generating test log entries", "ACTION")
        
        # Generate various types of test logs
        test_messages = [
            ("Test INFO message - Application checkpoint", "INFO"),
            ("Test WARNING message - Minor issue detected", "WARNING"),
            ("Test ERROR message - Simulated error condition", "ERROR"),
            ("Test ACTION message - User performed action", "ACTION"),
            ("Test EVENT message - System event occurred", "EVENT"),
            ("Test SYSTEM message - Internal system operation", "SYSTEM")
        ]
        
        for message, level in test_messages:
            self.logger.log(message, level)
            
        self.logger.log("Test log generation completed", "ACTION")
        
    def show_system_info(self):
        """Display detailed system information."""
        self.logger.log("System information requested by user", "ACTION")
        
        try:
            # Gather system information
            info_text = f"""System Information
{'=' * 50}

Application Details:
- Name: Multiclient Debug Version
- Version: 1.0.0
- Python Version: {sys.version}
- PyQt5 Version: Available
- Platform: {sys.platform}

Current Status:
- Monitoring: {'Enabled' if self.monitoring_enabled else 'Disabled'}
- Detailed Logging: {'Enabled' if self.detailed_logging else 'Disabled'}
- Tray Icon: {'Visible' if self.tray_icon.isVisible() else 'Hidden'}
- Uptime: {self.get_uptime_string()}

Statistics:
- Events Logged: {self.event_count}
- Tray Interactions: {self.tray_interaction_count}

Process Information:
- Process ID: {os.getpid()}
- Working Directory: {os.getcwd()}
"""
            
            # Create and show information dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("System Information")
            dialog.setModal(True)
            dialog.resize(600, 500)
            
            layout = QVBoxLayout()
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(info_text)
            text_edit.setFont(QFont("Consolas", 10))
            layout.addWidget(text_edit)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            
            # Apply dark theme to dialog
            dialog.setStyleSheet(self.styleSheet())
            
            dialog.exec_()
            
            self.logger.log("System information dialog displayed", "ACTION")
            
        except Exception as e:
            error_msg = f"Error gathering system information: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            QMessageBox.critical(self, "Error", error_msg)
            
    def restart_app(self):
        """Handle application restart request."""
        self.logger.log("Application restart requested by user", "ACTION")
        
        reply = QMessageBox.question(
            self, "Restart Application", 
            "Are you sure you want to restart the application?\n\n"
            "This will close all windows and restart the process.",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logger.log("Application restart confirmed by user", "ACTION")
            
            # In a real implementation, you would:
            # 1. Save current state
            # 2. Close all windows properly
            # 3. Restart the process using subprocess or os.execl
            
            QMessageBox.information(self, "Restart", 
                                  "Restart functionality is implemented as a placeholder.\n"
                                  "In a production version, this would restart the process.")
            
            self.logger.log("Restart operation completed (placeholder)", "ACTION")
        else:
            self.logger.log("Application restart cancelled by user", "ACTION")
            
    def exit_app(self):
        """Handle application exit request."""
        self.logger.log("Application exit requested by user", "ACTION")
        
        reply = QMessageBox.question(
            self, "Exit Application", 
            "Are you sure you want to exit the application?\n\n"
            "This will close all windows and terminate the process.",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logger.log("Application exit confirmed by user - initiating shutdown", "ACTION")
            
            # Perform cleanup operations
            self.cleanup_before_exit()
            
            # Exit the application
            self.app.quit()
        else:
            self.logger.log("Application exit cancelled by user", "ACTION")
            
    def cleanup_before_exit(self):
        """Perform cleanup operations before application exit."""
        self.logger.log("Performing cleanup operations before exit", "SYSTEM")
        
        try:
            # Stop all timers
            if hasattr(self, 'uptime_timer'):
                self.uptime_timer.stop()
                self.logger.log("Uptime timer stopped", "SYSTEM")
                
            if hasattr(self, 'system_timer'):
                self.system_timer.stop()
                self.logger.log("System monitoring timer stopped", "SYSTEM")
                
            # Hide tray icon
            if self.tray_icon.isVisible():
                self.tray_icon.hide()
                self.logger.log("Tray icon hidden", "SYSTEM")
                
            self.logger.log("Cleanup operations completed successfully", "SYSTEM")
            
        except Exception as e:
            self.logger.log(f"Error during cleanup: {str(e)}", "ERROR")
            
    def update_uptime(self):
        """Update the uptime display."""
        if self.monitoring_enabled and self.detailed_logging:
            # Only log uptime updates if detailed logging is enabled
            pass  # Removed frequent uptime logging to reduce spam
            
        # Calculate uptime
        uptime_string = self.get_uptime_string()
        self.uptime_label.setText(f"⏱️ Uptime: {uptime_string}")
        
    def get_uptime_string(self):
        """
        Get formatted uptime string.
        
        Returns:
            str: Formatted uptime string (HH:MM:SS)
        """
        current_time = QDateTime.currentDateTime()
        uptime_ms = self.start_time.msecsTo(current_time)
        uptime_seconds = uptime_ms // 1000
        
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    def update_system_stats(self):
        """Update system statistics display."""
        if self.monitoring_enabled:
            try:
                # Update event counter (this would be connected to actual event counting)
                self.event_count += 1  # Placeholder increment
                self.events_label.setText(f"📊 Events Logged: {self.event_count}")
                
                # Update memory usage (placeholder - in real implementation use psutil)
                self.memory_label.setText("💾 Memory: ~15MB (Estimated)")
                
                if self.detailed_logging:
                    self.logger.log("System statistics updated", "SYSTEM")
                    
            except Exception as e:
                self.logger.log(f"Error updating system stats: {str(e)}", "ERROR")
                
    def increment_tray_interactions(self):
        """Increment tray interaction counter."""
        self.tray_interaction_count += 1
        self.tray_interactions_label.setText(f"🖱️ Tray Interactions: {self.tray_interaction_count}")
        
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.log("Control Window close requested", "EVENT")
        # Hide instead of closing to keep it available
        self.hide()
        event.ignore()


# =============================================================================
# MAIN APPLICATION CLASS - Core application logic
# =============================================================================

class MulticlientDebug:
    """
    Main application class that orchestrates all components.
    
    This class handles:
    - Application initialization and mutex management
    - System tray icon creation and management
    - Debug window coordination
    - Event handling and logging
    - Application lifecycle management
    """
    
    def __init__(self):
        """Initialize the main application."""
        # Create logger first so we can log everything
        self.logger = Logger()
        self.logger.log("=== MULTICLIENT DEBUG APPLICATION STARTING ===", "SYSTEM")
        
        # Initialize all application components
        self.init_app()
        
    def init_app(self):
        """Initialize all application components."""
        try:
            self.logger.log("Beginning application initialization sequence", "SYSTEM")
            
            # === STEP 1: MUTEX MANAGEMENT ===
            self.logger.log("Step 1: Checking for existing application instances", "SYSTEM")
            self.setup_mutex()
            
            # === STEP 2: QT APPLICATION SETUP ===
            self.logger.log("Step 2: Setting up Qt Application framework", "SYSTEM")
            self.setup_qt_application()
            
            # === STEP 3: SYSTEM TRAY VERIFICATION ===
            self.logger.log("Step 3: Verifying system tray availability", "SYSTEM")
            self.verify_system_tray()
            
            # === STEP 4: CREATE SYSTEM TRAY ICON ===
            self.logger.log("Step 4: Creating and configuring system tray icon", "SYSTEM")
            self.create_tray_icon()
            
            # === STEP 5: CREATE DEBUG WINDOWS ===
            self.logger.log("Step 5: Creating debug interface windows", "SYSTEM")
            self.create_debug_windows()
            
            # === STEP 6: SETUP EVENT HANDLERS ===
            self.logger.log("Step 6: Setting up event handlers and signals", "SYSTEM")
            self.setup_event_handlers()
            
            # === STEP 7: SHOW INTERFACE ===
            self.logger.log("Step 7: Displaying user interface components", "SYSTEM")
            self.show_interface()
            
            self.logger.log("=== APPLICATION INITIALIZATION COMPLETED SUCCESSFULLY ===", "SYSTEM")
            
        except Exception as e:
            error_msg = f"CRITICAL ERROR during initialization: {str(e)}\n{traceback.format_exc()}"
            self.logger.log(error_msg, "ERROR")
            sys.exit(1)
            
    def setup_mutex(self):
        """Setup Windows mutex for singleton application behavior."""
        self.logger.log("Creating Windows mutex for singleton enforcement", "SYSTEM")
        
        try:
            # Create named mutex
            self.mutex = win32event.CreateMutex(None, 1, 'multiclient_singletonMutex')
            
            # Check if another instance is already running
            last_error = win32api.GetLastError()
            if last_error == 183:  # ERROR_ALREADY_EXISTS
                self.logger.log("Another instance of the application is already running", "ERROR")
                self.logger.log("Application will now exit to maintain singleton behavior", "ERROR")
                sys.exit(0)
            else:
                self.logger.log("Mutex acquired successfully - this is the only running instance", "SYSTEM")
                
        except Exception as e:
            error_msg = f"Error creating mutex: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            raise
            
    def setup_qt_application(self):
        """Setup the Qt application framework."""
        self.logger.log("Creating QApplication instance", "SYSTEM")
        
        try:
            # Create QApplication with empty arguments list
            self.app = QApplication([])
            
            # Configure application behavior
            self.app.setQuitOnLastWindowClosed(False)  # Don't quit when windows close
            self.logger.log("QApplication configured to continue running when windows close", "SYSTEM")
            
            # Set application properties
            self.app.setApplicationName("Multiclient Debug")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("Debug Tools")
            
            self.logger.log("QApplication created and configured successfully", "SYSTEM")
            
        except Exception as e:
            error_msg = f"Error setting up Qt application: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            raise
            
    def verify_system_tray(self):
        """Verify that system tray is available on this system."""
        self.logger.log("Checking system tray availability", "SYSTEM")
        
        if not QSystemTrayIcon.isSystemTrayAvailable():
            error_msg = "System tray is not available on this system"
            self.logger.log(error_msg, "ERROR")
            self.logger.log("Application cannot continue without system tray support", "ERROR")
            QMessageBox.critical(None, "System Tray Error", 
                               "System tray is not available on this system.\n"
                               "The application requires system tray support to function.")
            sys.exit(1)
        else:
            self.logger.log("System tray is available and ready for use", "SYSTEM")
            
    def create_tray_icon(self):
        """Create and configure the system tray icon."""
        self.logger.log("Creating system tray icon", "SYSTEM")
        
        try:
            # Create system tray icon with standard maximize button icon
            standard_icon = self.app.style().standardIcon(self.app.style().SP_TitleBarMaxButton)
            self.tray_icon = QSystemTrayIcon(standard_icon)
            
            self.logger.log("System tray icon object created", "SYSTEM")
            
            # Create context menu for tray icon
            self.create_tray_menu()
            
            # Set initial tooltip
            self.tray_icon.setToolTip('Multiclient (Debug Mode) - Right-click for options')
            self.logger.log("Tray icon tooltip configured", "SYSTEM")
            
        except Exception as e:
            error_msg = f"Error creating tray icon: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            raise
            
    def create_tray_menu(self):
        """Create the system tray context menu."""
        self.logger.log("Creating system tray context menu", "SYSTEM")
        
        try:
            self.tray_menu = QMenu()
            
            # === DEBUG WINDOW OPTIONS ===
            self.logger.log("Adding debug window menu options", "SYSTEM")
            
            # Show log window option
            show_log_action = QAction('📋 Show Log Window', self.tray_menu)
            show_log_action.setToolTip("Open the debug log window")
            show_log_action.triggered.connect(lambda: self.show_debug_window('log'))
            self.tray_menu.addAction(show_log_action)
            
            # Show control window option
            show_control_action = QAction('⚙️ Show Control Panel', self.tray_menu)
            show_control_action.setToolTip("Open the application control panel")
            show_control_action.triggered.connect(lambda: self.show_debug_window('control'))
            self.tray_menu.addAction(show_control_action)
            
            # Separator
            self.tray_menu.addSeparator()
            
            # === QUICK ACTIONS ===
            self.logger.log("Adding quick action menu options", "SYSTEM")
            
            # Generate test logs
            test_logs_action = QAction('🧪 Generate Test Logs', self.tray_menu)
            test_logs_action.setToolTip("Generate sample log entries")
            test_logs_action.triggered.connect(self.generate_quick_test_logs)
            self.tray_menu.addAction(test_logs_action)
            
            # System information
            sysinfo_action = QAction('ℹ️ System Info', self.tray_menu)
            sysinfo_action.setToolTip("Show system information")
            sysinfo_action.triggered.connect(self.show_quick_system_info)
            self.tray_menu.addAction(sysinfo_action)
            
            # Another separator
            self.tray_menu.addSeparator()
            
            # === EXIT OPTION ===
            self.logger.log("Adding exit menu option", "SYSTEM")
            
            exit_action = QAction('❌ Exit Application', self.tray_menu)
            exit_action.setToolTip("Exit the application completely")
            exit_action.triggered.connect(self.safe_exit)
            self.tray_menu.addAction(exit_action)
            
            # Assign menu to tray icon
            self.tray_icon.setContextMenu(self.tray_menu)
            
            self.logger.log("System tray context menu created with all options", "SYSTEM")
            
        except Exception as e:
            error_msg = f"Error creating tray menu: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            raise
            
    def create_debug_windows(self):
        """Create the debug interface windows."""
        self.logger.log("Creating debug interface windows", "SYSTEM")
        
        try:
            # Create log window
            self.logger.log("Creating debug log window", "SYSTEM")
            self.log_window = LogWindow(self.logger)
            
            # Create control window
            self.logger.log("Creating control panel window", "SYSTEM")
            self.control_window = ControlWindow(self.app, self.tray_icon, self.logger)
            
            self.logger.log("Debug windows created successfully", "SYSTEM")
            
        except Exception as e:
            error_msg = f"Error creating debug windows: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            raise
            
    def setup_event_handlers(self):
        """Setup event handlers and signal connections."""
        self.logger.log("Setting up event handlers and signal connections", "SYSTEM")
        
        try:
            # Connect tray icon signals
            self.tray_icon.activated.connect(self.handle_tray_activation)
            self.logger.log("Tray icon activation signal connected", "SYSTEM")
            
            # Connect application signals
            self.app.aboutToQuit.connect(self.handle_app_quit)
            self.logger.log("Application quit signal connected", "SYSTEM")
            
            self.logger.log("All event handlers configured successfully", "SYSTEM")
            
        except Exception as e:
            error_msg = f"Error setting up event handlers: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            raise
            
    def show_interface(self):
        """Display the user interface components."""
        self.logger.log("Displaying user interface components", "SYSTEM")
        
        try:
            # Show debug windows
            self.log_window.show()
            self.logger.log("Debug log window displayed", "SYSTEM")
            
            self.control_window.show()
            self.logger.log("Control panel window displayed", "SYSTEM")
            
            # Show and activate tray icon
            self.tray_icon.show()
            self.logger.log("System tray icon displayed and activated", "SYSTEM")
            
            # Position windows nicely
            self.position_windows()
            
        except Exception as e:
            error_msg = f"Error showing interface: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            raise
            
    def position_windows(self):
        """Position debug windows in a nice arrangement."""
        self.logger.log("Positioning debug windows", "SYSTEM")
        
        try:
            # Get screen geometry
            screen = self.app.primaryScreen().geometry()
            screen_width = screen.width()
            screen_height = screen.height()
            
            # Position log window on the left
            log_width = 900
            log_height = 700
            log_x = 50
            log_y = 50
            self.log_window.setGeometry(log_x, log_y, log_width, log_height)
            
            # Position control window on the right
            control_width = 500
            control_height = 600
            control_x = log_x + log_width + 20
            control_y = 50
            
            # Ensure control window fits on screen
            if control_x + control_width > screen_width:
                control_x = screen_width - control_width - 50
                
            self.control_window.setGeometry(control_x, control_y, control_width, control_height)
            
            self.logger.log("Debug windows positioned successfully", "SYSTEM")
            
        except Exception as e:
            error_msg = f"Error positioning windows: {str(e)}"
            self.logger.log(error_msg, "WARNING")  # Non-critical error
            
    def show_debug_window(self, window_type):
        """
        Show and activate a specific debug window.
        
        Args:
            window_type (str): Type of window to show ('log' or 'control')
        """
        self.logger.log(f"Debug window display requested: {window_type}", "ACTION")
        
        try:
            if window_type == 'log':
                self.log_window.show()
                self.log_window.raise_()
                self.log_window.activateWindow()
                self.logger.log("Log window displayed and activated", "ACTION")
                
            elif window_type == 'control':
                self.control_window.show()
                self.control_window.raise_()
                self.control_window.activateWindow()
                self.logger.log("Control window displayed and activated", "ACTION")
                
            else:
                self.logger.log(f"Unknown window type requested: {window_type}", "WARNING")
                
        except Exception as e:
            error_msg = f"Error showing debug window '{window_type}': {str(e)}"
            self.logger.log(error_msg, "ERROR")
            
    def handle_tray_activation(self, reason):
        """
        Handle system tray icon activation events.
        
        Args:
            reason (QSystemTrayIcon.ActivationReason): The activation reason
        """
        # Map activation reasons to readable strings
        activation_reasons = {
            QSystemTrayIcon.Trigger: "Single Left Click",
            QSystemTrayIcon.DoubleClick: "Double Left Click", 
            QSystemTrayIcon.MiddleClick: "Middle Click",
            QSystemTrayIcon.Context: "Right Click (Context Menu)"
        }
        
        reason_str = activation_reasons.get(reason, f"Unknown Activation ({reason})")
        self.logger.log(f"Tray icon activated: {reason_str}", "EVENT")
        
        # Update interaction counter in control window
        if hasattr(self, 'control_window'):
            self.control_window.increment_tray_interactions()
            
        # Handle double-click to show control panel
        if reason == QSystemTrayIcon.DoubleClick:
            self.logger.log("Double-click detected - showing control panel", "EVENT")
            self.show_debug_window('control')
            
    def generate_quick_test_logs(self):
        """Generate test logs from tray menu."""
        self.logger.log("Quick test log generation requested from tray menu", "ACTION")
        
        # Generate a few quick test messages
        test_messages = [
            "Quick test: Application status check",
            "Quick test: Memory usage verification", 
            "Quick test: Network connectivity check",
            "Quick test: File system access verification"
        ]
        
        for i, message in enumerate(test_messages, 1):
            level = ["INFO", "ACTION", "EVENT", "SYSTEM"][i % 4]
            self.logger.log(f"{message} ({i}/4)", level)
            
        self.logger.log("Quick test log generation completed", "ACTION")
        
    def show_quick_system_info(self):
        """Show quick system information from tray menu."""
        self.logger.log("Quick system information requested from tray menu", "ACTION")
        
        try:
            uptime = self.control_window.get_uptime_string() if hasattr(self, 'control_window') else "Unknown"
            
            info_msg = f"""Multiclient Debug - Quick Info
            
🕐 Uptime: {uptime}
🖥️ Platform: {sys.platform}
🐍 Python: {sys.version.split()[0]}
💾 Process ID: {os.getpid()}
📍 Status: Running

Right-click tray icon for more options."""
            
            # Create a simple message box
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Quick System Info")
            msg_box.setText(info_msg)
            msg_box.setIcon(QMessageBox.Information)
            
            # Apply dark theme if possible
            if hasattr(self, 'control_window'):
                msg_box.setStyleSheet(self.control_window.styleSheet())
                
            msg_box.exec_()
            
            self.logger.log("Quick system information displayed", "ACTION")
            
        except Exception as e:
            error_msg = f"Error showing quick system info: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            
    def safe_exit(self):
        """Safely exit the application with confirmation."""
        self.logger.log("Safe exit requested from tray menu", "ACTION")
        
        try:
            # Show confirmation dialog
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Exit Confirmation")
            msg_box.setText("Are you sure you want to exit Multiclient Debug?")
            msg_box.setInformativeText("This will close all debug windows and terminate the application.")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            msg_box.setIcon(QMessageBox.Question)
            
            # Apply dark theme if available
            if hasattr(self, 'control_window'):
                msg_box.setStyleSheet(self.control_window.styleSheet())
                
            reply = msg_box.exec_()
            
            if reply == QMessageBox.Yes:
                self.logger.log("Exit confirmed by user - initiating shutdown", "ACTION")
                self.handle_app_quit()
                self.app.quit()
            else:
                self.logger.log("Exit cancelled by user", "ACTION")
                
        except Exception as e:
            error_msg = f"Error during safe exit: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            
    def handle_app_quit(self):
        """Handle application quit event."""
        self.logger.log("Application quit event received - performing cleanup", "SYSTEM")
        
        try:
            # Cleanup control window
            if hasattr(self, 'control_window'):
                self.control_window.cleanup_before_exit()
                
            # Hide tray icon
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.tray_icon.hide()
                self.logger.log("System tray icon hidden", "SYSTEM")
                
            self.logger.log("=== APPLICATION SHUTDOWN COMPLETED ===", "SYSTEM")
            
        except Exception as e:
            error_msg = f"Error during application cleanup: {str(e)}"
            self.logger.log(error_msg, "ERROR")
            
    def run(self):
        """
        Run the application main event loop.
        
        Returns:
            int: Application exit code
        """
        try:
            self.logger.log("Starting Qt application main event loop", "SYSTEM")
            
            # Start the Qt event loop
            exit_code = self.app.exec_()
            
            self.logger.log(f"Application event loop exited with code: {exit_code}", "SYSTEM")
            return exit_code
            
        except Exception as e:
            error_msg = f"CRITICAL ERROR in main event loop: {str(e)}\n{traceback.format_exc()}"
            self.logger.log(error_msg, "ERROR")
            return 1


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    Main entry point for the Multiclient Debug application.
    
    This is where the application starts execution. It creates the main
    application instance and runs it, handling any critical errors that
    might occur during startup or execution.
    """
    
    try:
        # Create the main application instance
        debug_app = MulticlientDebug()
        
        # Run the application and exit with its return code
        sys.exit(debug_app.run())
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        print(f"CRITICAL ERROR: Application failed to start: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)