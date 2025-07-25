#!/usr/bin/env python3
"""
Zirar - Archive Password Cracker
A secure PySide6 desktop application for testing passwords against password-protected archives.
"""

import sys
import os
import zipfile
import rarfile
from pathlib import Path

# Configure rarfile to look for UnRAR in common locations
def setup_rarfile():
    """Setup rarfile with common UnRAR executable paths"""
    common_paths = [
        'unrar',
        'unrar.exe',
        r'C:\Program Files\WinRAR\UnRAR.exe',
        r'C:\Program Files (x86)\WinRAR\UnRAR.exe',
        '/usr/bin/unrar',
        '/usr/local/bin/unrar',
        '/opt/homebrew/bin/unrar'
    ]

    for path in common_paths:
        if os.path.isfile(path):
            rarfile.UNRAR_TOOL = path
            return True
        elif not os.path.sep in path:
            # Try to find in PATH
            try:
                if os.system(f'where {path} >nul 2>&1') == 0:
                    rarfile.UNRAR_TOOL = path
                    return True
            except:
                continue
    return False

# Try to setup rarfile
RAR_AVAILABLE = setup_rarfile()
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QProgressBar, QFileDialog, QTextEdit,
    QCheckBox, QGroupBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

try:
    import pyzipper
    PYZIPPER_AVAILABLE = True
except ImportError:
    PYZIPPER_AVAILABLE = False


class PasswordCrackingWorker(QThread):
    """Worker thread for password cracking to keep UI responsive"""

    # Signals for communication with main thread
    progress_updated = Signal(int, int, str)  # current, total, current_password
    password_found = Signal(str)  # successful password
    finished_unsuccessfully = Signal()  # no password found
    error_occurred = Signal(str)  # error message

    def __init__(self, archive_path, password_list_path):
        super().__init__()
        self.archive_path = archive_path
        self.password_list_path = password_list_path
        self.should_stop = False

    def run(self):
        """Main worker thread execution"""
        try:
            # Load passwords
            passwords = self.load_passwords()
            if not passwords:
                self.error_occurred.emit("No passwords found in the password list file.")
                return

            total_passwords = len(passwords)
            archive_ext = Path(self.archive_path).suffix.lower()

            # Test each password
            for i, password in enumerate(passwords):
                if self.should_stop:
                    return

                self.progress_updated.emit(i + 1, total_passwords, password)

                try:
                    if archive_ext == '.zip':
                        if self.test_zip_password(password):
                            self.password_found.emit(password)
                            return
                    elif archive_ext == '.rar':
                        if self.test_rar_password(password):
                            self.password_found.emit(password)
                            return
                except Exception as e:
                    # Continue with next password on specific errors
                    # For debugging, you might want to emit this error
                    continue

            # If we get here, no password worked
            self.finished_unsuccessfully.emit()

        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)}")

    def load_passwords(self):
        """Load passwords from the password list file"""
        try:
            with open(self.password_list_path, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            return passwords
        except Exception as e:
            self.error_occurred.emit(f"Could not load password list: {str(e)}")
            return []

    def test_zip_password(self, password):
        """Test password against ZIP file"""
        try:
            # Try pyzipper first (better for encrypted ZIPs)
            if PYZIPPER_AVAILABLE:
                try:
                    with pyzipper.AESZipFile(self.archive_path, 'r') as zip_file:
                        zip_file.setpassword(password.encode('utf-8'))
                        # Test by trying to read file info
                        zip_file.testzip()
                        return True
                except (pyzipper.BadZipFile, pyzipper.LargeZipFile, RuntimeError):
                    return False
            else:
                # Fallback to standard zipfile
                with zipfile.ZipFile(self.archive_path, 'r') as zip_file:
                    zip_file.setpassword(password.encode('utf-8'))
                    # Test by trying to read the zip
                    result = zip_file.testzip()
                    return result is None  # testzip returns None if all files are OK
        except (RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile):
            # Wrong password or corrupted file
            return False
        except UnicodeEncodeError:
            # Password contains characters that can't be encoded
            return False
        except Exception:
            # Other errors, continue trying
            return False

    def test_rar_password(self, password):
        """Test password against RAR file"""
        try:
            with rarfile.RarFile(self.archive_path, 'r') as rar_file:
                # Set password - try both string and bytes
                try:
                    rar_file.setpassword(password)
                except:
                    # Some versions might need bytes
                    rar_file.setpassword(password.encode('utf-8'))

                # Try to get file info first (faster than reading)
                names = rar_file.namelist()
                if not names:
                    return False

                # Try to get info about the first file
                info = rar_file.getinfo(names[0])

                # If we can get info without error, try reading a small portion
                try:
                    # Try to read just the first few bytes to verify password
                    with rar_file.open(names[0]) as f:
                        f.read(1)  # Read just 1 byte to test
                    return True
                except:
                    return False

        except rarfile.RarWrongPassword:
            # Specifically wrong password
            return False
        except rarfile.BadRarFile:
            # Corrupted RAR file
            return False
        except Exception as e:
            # Log other errors for debugging but continue
            # In production, you might want to log this
            return False

    def stop(self):
        """Signal the worker to stop"""
        self.should_stop = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.archive_path = None
        self.password_list_path = None
        self.worker_thread = None
        self.is_cracking = False

        self.setWindowTitle("Zirar - Archive Password Cracker")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)

        # Set application style with proper contrast
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                color: #212529;
            }
            QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            QLabel {
                color: #212529;
                background-color: transparent;
            }
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
                background-color: #ffffff;
            }
            QPushButton {
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px 16px;
                background-color: #ffffff;
                color: #495057;
                min-width: 100px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
                border-color: #6c757d;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #adb5bd;
                border-color: #e9ecef;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 6px;
                text-align: center;
                background-color: #f8f9fa;
                color: #495057;
                font-weight: 500;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 5px;
            }
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: #ffffff;
                color: #495057;
                padding: 8px;
            }
            QCheckBox {
                color: #495057;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
            }
        """)

        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Archive Password Cracker")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Archive file selection
        archive_layout = QHBoxLayout()
        archive_layout.addWidget(QLabel("Archive File:"))
        self.archive_label = QLabel("No file selected")
        self.archive_label.setStyleSheet("color: #6c757d; font-style: italic;")
        archive_layout.addWidget(self.archive_label, 1)
        
        self.browse_archive_btn = QPushButton("Browse...")
        self.clear_archive_btn = QPushButton("Clear")
        self.clear_archive_btn.setEnabled(False)
        archive_layout.addWidget(self.browse_archive_btn)
        archive_layout.addWidget(self.clear_archive_btn)
        
        file_layout.addLayout(archive_layout)
        
        # Password list file selection
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password List:"))
        self.password_label = QLabel("No file selected")
        self.password_label.setStyleSheet("color: #6c757d; font-style: italic;")
        password_layout.addWidget(self.password_label, 1)
        
        self.browse_password_btn = QPushButton("Browse...")
        self.clear_password_btn = QPushButton("Clear")
        self.clear_password_btn.setEnabled(False)
        password_layout.addWidget(self.browse_password_btn)
        password_layout.addWidget(self.clear_password_btn)
        
        file_layout.addLayout(password_layout)
        main_layout.addWidget(file_group)
        
        # Controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Start/Stop buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Password Testing")
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 10px; }")

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; font-weight: bold; padding: 10px; }")
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        controls_layout.addLayout(button_layout)
        
        # Progress bar
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        controls_layout.addLayout(progress_layout)
        
        main_layout.addWidget(controls_group)
        
        # Password feedback group
        feedback_group = QGroupBox("Password Testing")
        feedback_layout = QVBoxLayout(feedback_group)
        
        # Show current attempt checkbox
        self.show_password_cb = QCheckBox("Show current password attempt")
        feedback_layout.addWidget(self.show_password_cb)
        
        # Current password display
        self.current_password_label = QLabel("Current attempt: (not started)")
        self.current_password_label.setStyleSheet("font-family: monospace; padding: 8px; background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; color: #495057;")
        feedback_layout.addWidget(self.current_password_label)

        # Result display
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-weight: bold; padding: 12px; color: #495057;")
        self.result_label.setAlignment(Qt.AlignCenter)
        feedback_layout.addWidget(self.result_label)
        
        main_layout.addWidget(feedback_group)
        
        # Security notes
        security_group = QGroupBox("Security & Ethical Use")
        security_layout = QVBoxLayout(security_group)
        
        security_text = QTextEdit()
        security_text.setMaximumHeight(120)
        security_text.setReadOnly(True)
        security_text.setHtml("""
        <b>Ethical Use Only:</b> This tool is for legitimate purposes only - testing your own passwords, 
        authorized security auditing, or educational use.<br><br>
        <b>Password Strength Tips (NIST Guidelines):</b><br>
        • Length matters more than complexity<br>
        • Minimum 8 characters recommended<br>
        • Use unique passwords for different accounts<br>
        • Consider using a password manager
        """)
        security_layout.addWidget(security_text)
        
        main_layout.addWidget(security_group)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select archive and password list files to begin")
        
    def setup_connections(self):
        """Set up signal connections"""
        self.browse_archive_btn.clicked.connect(self.browse_archive_file)
        self.clear_archive_btn.clicked.connect(self.clear_archive_file)
        self.browse_password_btn.clicked.connect(self.browse_password_file)
        self.clear_password_btn.clicked.connect(self.clear_password_file)
        self.start_btn.clicked.connect(self.start_cracking)
        self.stop_btn.clicked.connect(self.stop_cracking)
        self.show_password_cb.toggled.connect(self.toggle_password_display)
        
    def browse_archive_file(self):
        """Open file dialog to select archive file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Archive File",
            "",
            "Archive Files (*.zip *.rar);;ZIP Files (*.zip);;RAR Files (*.rar);;All Files (*)"
        )

        if file_path:
            # Validate file exists and has correct extension
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "File Error", "Selected file does not exist.")
                return

            file_ext = Path(file_path).suffix.lower()
            if file_ext not in ['.zip', '.rar']:
                reply = QMessageBox.question(
                    self,
                    "File Type Warning",
                    f"Selected file has extension '{file_ext}'. Continue anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            self.archive_path = file_path
            filename = Path(file_path).name
            self.archive_label.setText(filename)
            self.archive_label.setStyleSheet("color: #212529; font-style: normal; font-weight: 500;")
            self.clear_archive_btn.setEnabled(True)
            self.check_ready_state()
            self.statusBar().showMessage(f"Archive selected: {filename}")
            
    def clear_archive_file(self):
        """Clear selected archive file"""
        self.archive_path = None
        self.archive_label.setText("No file selected")
        self.archive_label.setStyleSheet("color: #6c757d; font-style: italic;")
        self.clear_archive_btn.setEnabled(False)
        self.check_ready_state()
        
    def browse_password_file(self):
        """Open file dialog to select password list file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Password List File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            # Validate file exists and is readable
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "File Error", "Selected file does not exist.")
                return

            try:
                # Try to read the file and count passwords
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    passwords = [line.strip() for line in f if line.strip()]
                    password_count = len(passwords)

                if password_count == 0:
                    QMessageBox.warning(self, "File Error", "Password file appears to be empty.")
                    return

                self.password_list_path = file_path
                filename = Path(file_path).name
                self.password_label.setText(f"{filename} ({password_count:,} passwords)")
                self.password_label.setStyleSheet("color: #212529; font-style: normal; font-weight: 500;")
                self.clear_password_btn.setEnabled(True)
                self.check_ready_state()
                self.statusBar().showMessage(f"Password list selected: {password_count:,} passwords loaded")

            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Could not read password file:\n{str(e)}")
            
    def clear_password_file(self):
        """Clear selected password list file"""
        self.password_list_path = None
        self.password_label.setText("No file selected")
        self.password_label.setStyleSheet("color: #6c757d; font-style: italic;")
        self.clear_password_btn.setEnabled(False)
        self.check_ready_state()
        
    def check_ready_state(self):
        """Check if both files are selected and enable/disable start button"""
        self.update_ui_state()

        ready = self.archive_path is not None and self.password_list_path is not None
        if ready and not self.is_cracking:
            self.statusBar().showMessage("Ready to start password testing")
        elif not ready:
            self.statusBar().showMessage("Select both archive and password list files to begin")
            
    def start_cracking(self):
        """Start the password cracking process"""
        if not self.archive_path or not self.password_list_path:
            QMessageBox.warning(self, "Missing Files", "Please select both archive and password list files.")
            return

        # Additional security and validation checks
        if not self.validate_files():
            return

        # Show ethical use confirmation
        if not self.show_ethical_confirmation():
            return

        # Update UI state
        self.is_cracking = True
        self.update_ui_state()

        # Visual feedback for start
        self.start_btn.setText("Testing...")
        self.start_btn.setStyleSheet("QPushButton { background-color: #fd7e14; color: white; font-weight: bold; padding: 10px; }")

        # Reset UI elements
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        self.current_password_label.setText("Current attempt: (starting)")
        self.result_label.setText("")
        self.result_label.setStyleSheet("font-weight: bold; padding: 12px; color: #495057;")

        # Create and start worker thread
        self.worker_thread = PasswordCrackingWorker(self.archive_path, self.password_list_path)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.password_found.connect(self.password_found)
        self.worker_thread.finished_unsuccessfully.connect(self.password_not_found)
        self.worker_thread.error_occurred.connect(self.handle_error)
        self.worker_thread.finished.connect(self.cracking_finished)

        self.worker_thread.start()
        self.statusBar().showMessage("Password testing in progress...")

    def stop_cracking(self):
        """Stop the password cracking process"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait(3000)  # Wait up to 3 seconds
            if self.worker_thread.isRunning():
                self.worker_thread.terminate()
                self.worker_thread.wait()

        self.cracking_finished()
        self.statusBar().showMessage("Password testing stopped by user")

    def update_progress(self, current, total, current_password):
        """Update progress bar and current password display"""
        progress_percent = int((current / total) * 100)
        self.progress_bar.setValue(progress_percent)
        self.progress_label.setText(f"{current:,} of {total:,} passwords tried ({progress_percent}%)")

        # Update current password display
        if self.show_password_cb.isChecked():
            self.current_password_label.setText(f"Current attempt: {current_password}")
        else:
            self.current_password_label.setText(f"Current attempt: {'*' * len(current_password)}")

    def password_found(self, password):
        """Handle successful password discovery"""
        self.result_label.setText(f"✔ Password found: {password}")
        self.result_label.setStyleSheet("font-weight: bold; padding: 12px; color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px;")
        self.statusBar().showMessage("Password found successfully!")

    def password_not_found(self):
        """Handle case where no password worked"""
        self.result_label.setText("❌ No password found")
        self.result_label.setStyleSheet("font-weight: bold; padding: 12px; color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px;")
        self.statusBar().showMessage("Password testing completed - no password found")

    def handle_error(self, error_message):
        """Handle errors from worker thread"""
        self.result_label.setText(f"⚠ Error: {error_message}")
        self.result_label.setStyleSheet("font-weight: bold; padding: 12px; color: #856404; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px;")
        self.statusBar().showMessage("Error occurred during password testing")
        QMessageBox.critical(self, "Error", error_message)

    def cracking_finished(self):
        """Reset UI state when cracking is finished"""
        self.is_cracking = False
        self.update_ui_state()

        # Reset start button appearance
        self.start_btn.setText("Start Password Testing")
        self.start_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 10px; }")

        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def update_ui_state(self):
        """Update UI controls based on current state"""
        files_selected = bool(self.archive_path and self.password_list_path)

        # File selection controls
        self.browse_archive_btn.setEnabled(not self.is_cracking)
        self.browse_password_btn.setEnabled(not self.is_cracking)
        self.clear_archive_btn.setEnabled(not self.is_cracking and bool(self.archive_path))
        self.clear_password_btn.setEnabled(not self.is_cracking and bool(self.password_list_path))

        # Action buttons
        self.start_btn.setEnabled(not self.is_cracking and files_selected)
        self.stop_btn.setEnabled(self.is_cracking)

    def validate_files(self):
        """Validate selected files before starting"""
        # Check archive file
        if not os.path.exists(self.archive_path):
            QMessageBox.critical(self, "File Error", "Archive file no longer exists.")
            return False

        if not os.access(self.archive_path, os.R_OK):
            QMessageBox.critical(self, "Permission Error", "Cannot read archive file. Check permissions.")
            return False

        # Check password list file
        if not os.path.exists(self.password_list_path):
            QMessageBox.critical(self, "File Error", "Password list file no longer exists.")
            return False

        if not os.access(self.password_list_path, os.R_OK):
            QMessageBox.critical(self, "Permission Error", "Cannot read password list file. Check permissions.")
            return False

        # Check for RAR support
        archive_ext = Path(self.archive_path).suffix.lower()
        if archive_ext == '.rar':
            if not RAR_AVAILABLE:
                reply = QMessageBox.question(
                    self,
                    "RAR Support Required",
                    "RAR support requires the UnRAR executable, which was not found.\n\n"
                    "Would you like to continue anyway? (This may fail)\n\n"
                    "To install UnRAR:\n"
                    "• Windows: Download from https://www.rarlab.com/rar_add.htm\n"
                    "• Linux: sudo apt-get install unrar\n"
                    "• macOS: brew install unrar",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return False

            try:
                # Test if we can open the RAR file
                with rarfile.RarFile(self.archive_path, 'r') as test_rar:
                    # Just try to get the file list to verify RAR support
                    test_rar.namelist()
            except Exception as e:
                QMessageBox.critical(self, "RAR File Error", f"Cannot open RAR file: {str(e)}")
                return False

        return True

    def show_ethical_confirmation(self):
        """Show ethical use confirmation dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ethical Use Confirmation")
        msg.setIcon(QMessageBox.Question)
        msg.setText("Please confirm that you are using this tool ethically and legally.")
        msg.setInformativeText(
            "This tool should only be used for:\n"
            "• Testing your own forgotten passwords\n"
            "• Authorized security auditing\n"
            "• Educational purposes\n\n"
            "Using this tool on files you don't own or without proper authorization "
            "may violate laws and ethical guidelines."
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        return msg.exec() == QMessageBox.Yes

    def toggle_password_display(self, checked):
        """Toggle password display visibility"""
        # Update current display if we're currently running
        if self.worker_thread and self.worker_thread.isRunning():
            current_text = self.current_password_label.text()
            if "Current attempt:" in current_text:
                # This will be updated on next progress signal
                pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Zirar")
    app.setApplicationVersion("1.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
