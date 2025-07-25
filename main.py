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


class PasswordEnhancer:
    """Enhances password lists by generating variations with common substitutions"""

    # Common character substitutions used in passwords
    SUBSTITUTIONS = {
        'a': ['@', '4'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['$', '5'],
        't': ['7'],
        'l': ['1'],
        'g': ['9'],
        'b': ['6'],
        'A': ['@', '4'],
        'E': ['3'],
        'I': ['1', '!'],
        'O': ['0'],
        'S': ['$', '5'],
        'T': ['7'],
        'L': ['1'],
        'G': ['9'],
        'B': ['6']
    }

    @staticmethod
    def generate_variations(password, max_variations=10):
        """Generate password variations using character substitutions"""
        variations = set()
        variations.add(password)  # Include original

        # Single character substitutions
        for i, char in enumerate(password):
            if char in PasswordEnhancer.SUBSTITUTIONS:
                for replacement in PasswordEnhancer.SUBSTITUTIONS[char]:
                    new_password = password[:i] + replacement + password[i+1:]
                    variations.add(new_password)
                    if len(variations) >= max_variations:
                        break
                if len(variations) >= max_variations:
                    break

        # Common endings (years, numbers)
        base_variations = list(variations)
        for base_pwd in base_variations[:5]:  # Limit to avoid explosion
            for suffix in ['123', '!', '1', '12', '2023', '2024', '01']:
                variations.add(base_pwd + suffix)
                if len(variations) >= max_variations:
                    break
            if len(variations) >= max_variations:
                break

        # Capitalize first letter variations
        for base_pwd in list(variations)[:5]:
            if base_pwd and base_pwd[0].islower():
                variations.add(base_pwd.capitalize())
            if len(variations) >= max_variations:
                break

        return list(variations)[:max_variations]

    @staticmethod
    def enhance_password_list(passwords, enhancement_factor=3):
        """Enhance a list of passwords with variations added to the end"""
        # Start with all original passwords
        enhanced_passwords = list(passwords)

        # Collect all variations
        all_variations = []
        for password in passwords:
            variations = PasswordEnhancer.generate_variations(password, enhancement_factor)
            for variation in variations:
                if variation != password:  # Don't duplicate original
                    all_variations.append(variation)

        # Add variations to the end, removing duplicates
        seen = set(enhanced_passwords)  # Track originals
        for variation in all_variations:
            if variation not in seen:
                seen.add(variation)
                enhanced_passwords.append(variation)

        return enhanced_passwords


class PasswordCrackingWorker(QThread):
    """Worker thread for password cracking to keep UI responsive"""

    # Signals for communication with main thread
    progress_updated = Signal(int, int, str)  # current, total, current_password
    password_found = Signal(str)  # successful password
    finished_unsuccessfully = Signal()  # no password found
    error_occurred = Signal(str)  # error message

    def __init__(self, archive_path, password_list_path, enhance_passwords=True):
        super().__init__()
        self.archive_path = archive_path
        self.password_list_path = password_list_path
        self.enhance_passwords = enhance_passwords
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
                original_passwords = [line.strip() for line in f if line.strip()]

            if not original_passwords:
                return []

            # Enhance passwords if enabled
            if self.enhance_passwords:
                enhanced_passwords = PasswordEnhancer.enhance_password_list(original_passwords)
                return enhanced_passwords
            else:
                return original_passwords

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


class ThemeManager:
    """Manages application themes"""

    DARK_THEME = {
        'background': '#121212',
        'surface': '#1E1E1E',
        'surface_variant': '#2A2A2A',
        'primary_text': '#E0E0E0',
        'secondary_text': '#B3B3B3',
        'disabled_text': '#999999',
        'accent_green': "#24923f",
        'accent_cyan': '#8be9fd',
        'accent_orange': '#ffb86c',
        'success': '#50fa7b',
        'error': "#9B2F2F",
        'warning': '#ffb86c',
        'success_bg': '#1a4d2e',
        'error_bg': '#4d1a1a',
        'warning_bg': '#4d3d1a'
    }

    LIGHT_THEME = {
        'background': '#F5F5F5',
        'surface': '#FFFFFF',
        'surface_variant': '#E0E0E0',
        'primary_text': '#333333',
        'secondary_text': '#666666',
        'disabled_text': '#999999',
        'accent_green': '#28a745',
        'accent_cyan': '#17a2b8',
        'accent_orange': '#fd7e14',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#fd7e14',
        'success_bg': '#d4edda',
        'error_bg': '#f8d7da',
        'warning_bg': '#fff3cd'
    }

    @staticmethod
    def get_stylesheet(theme_colors):
        """Generate stylesheet for the given theme colors"""
        return f"""
            QMainWindow {{
                background-color: {theme_colors['background']};
                color: {theme_colors['primary_text']};
            }}
            QWidget {{
                background-color: {theme_colors['background']};
                color: {theme_colors['primary_text']};
            }}
            QLabel {{
                color: {theme_colors['primary_text']};
                background-color: transparent;
            }}
            QGroupBox {{
                font-weight: bold;
                color: {theme_colors['primary_text']};
                border: 2px solid {theme_colors['surface_variant']};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: {theme_colors['surface']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {theme_colors['primary_text']};
                background-color: {theme_colors['surface']};
            }}
            QPushButton {{
                border: 1px solid {theme_colors['surface_variant']};
                border-radius: 6px;
                padding: 8px 16px;
                background-color: {theme_colors['surface']};
                color: {theme_colors['primary_text']};
                min-width: 100px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme_colors['surface_variant']};
                border-color: {theme_colors['secondary_text']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['surface_variant']};
                border-color: {theme_colors['primary_text']};
            }}
            QPushButton:disabled {{
                background-color: {theme_colors['surface']};
                color: {theme_colors['disabled_text']};
                border-color: {theme_colors['surface_variant']};
            }}
            QProgressBar {{
                border: 1px solid {theme_colors['surface_variant']};
                border-radius: 6px;
                text-align: center;
                background-color: {theme_colors['surface']};
                color: {theme_colors['primary_text']};
                font-weight: 500;
            }}
            QProgressBar::chunk {{
                background-color: {theme_colors['accent_green']};
                border-radius: 5px;
            }}
            QTextEdit {{
                border: 1px solid {theme_colors['surface_variant']};
                border-radius: 6px;
                background-color: {theme_colors['surface']};
                color: {theme_colors['primary_text']};
                padding: 8px;
            }}
            QCheckBox {{
                color: {theme_colors['primary_text']};
                background-color: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme_colors['surface_variant']};
                border-radius: 3px;
                background-color: {theme_colors['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme_colors['accent_cyan']};
                border-color: {theme_colors['accent_cyan']};
            }}
            QMenuBar {{
                background-color: {theme_colors['surface']};
                color: {theme_colors['primary_text']};
                border-bottom: 1px solid {theme_colors['surface_variant']};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{
                background-color: {theme_colors['surface_variant']};
            }}
            QMenu {{
                background-color: {theme_colors['surface']};
                color: {theme_colors['primary_text']};
                border: 1px solid {theme_colors['surface_variant']};
            }}
            QMenu::item {{
                padding: 6px 12px;
            }}
            QMenu::item:selected {{
                background-color: {theme_colors['surface_variant']};
            }}
            QStatusBar {{
                background-color: {theme_colors['surface']};
                color: {theme_colors['secondary_text']};
                border-top: 1px solid {theme_colors['surface_variant']};
            }}
        """


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.archive_path = None
        self.password_list_path = None
        self.worker_thread = None
        self.is_cracking = False
        self.current_theme = 'light'  # Default to light theme

        self.setWindowTitle("Zirar - Archive Password Cracker")
        self.setMinimumSize(650, 700)  # Increased minimum height to ensure all content is visible
        self.resize(650, 750)

        self.setup_menu()
        self.setup_ui()
        self.setup_connections()

        # Apply initial theme after UI is set up
        self.apply_theme()

        # Center the window on the screen
        self.center_window()

    def center_window(self):
        """Center the window on the screen"""
        # Get the screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Get the window geometry
        window_geometry = self.frameGeometry()

        # Calculate the center point
        center_point = screen_geometry.center()

        # Move the window's center to the screen's center
        window_geometry.moveCenter(center_point)

        # Move the window to the calculated position
        self.move(window_geometry.topLeft())

    def setup_menu(self):
        """Set up the menu bar"""
        menubar = self.menuBar()

        # View menu for theme switching
        view_menu = menubar.addMenu('View')

        # Theme submenu
        theme_menu = view_menu.addMenu('Theme')

        # Light theme action
        light_action = theme_menu.addAction('Light Theme')
        light_action.setCheckable(True)
        light_action.setChecked(self.current_theme == 'light')
        light_action.triggered.connect(lambda: self.switch_theme('light'))

        # Dark theme action
        dark_action = theme_menu.addAction('Dark Theme')
        dark_action.setCheckable(True)
        dark_action.setChecked(self.current_theme == 'dark')
        dark_action.triggered.connect(lambda: self.switch_theme('dark'))

        # Store actions for later reference
        self.light_theme_action = light_action
        self.dark_theme_action = dark_action

    def apply_theme(self):
        """Apply the current theme"""
        if self.current_theme == 'dark':
            theme_colors = ThemeManager.DARK_THEME
        else:
            theme_colors = ThemeManager.LIGHT_THEME

        stylesheet = ThemeManager.get_stylesheet(theme_colors)
        self.setStyleSheet(stylesheet)

        # Update specific elements that need theme-aware colors
        self.update_themed_elements(theme_colors)

    def switch_theme(self, theme_name):
        """Switch to the specified theme"""
        if theme_name == self.current_theme:
            return

        self.current_theme = theme_name

        # Update menu checkboxes
        self.light_theme_action.setChecked(theme_name == 'light')
        self.dark_theme_action.setChecked(theme_name == 'dark')

        # Apply the new theme
        self.apply_theme()

    def update_themed_elements(self, theme_colors):
        """Update elements that need specific theme colors"""
        # Update file selection labels
        if hasattr(self, 'archive_label'):
            if self.archive_path:
                self.archive_label.setStyleSheet(f"color: {theme_colors['primary_text']}; font-style: normal; font-weight: 500;")
            else:
                self.archive_label.setStyleSheet(f"color: {theme_colors['secondary_text']}; font-style: italic;")

        if hasattr(self, 'password_label'):
            if self.password_list_path:
                self.password_label.setStyleSheet(f"color: {theme_colors['primary_text']}; font-style: normal; font-weight: 500;")
            else:
                self.password_label.setStyleSheet(f"color: {theme_colors['secondary_text']}; font-style: italic;")

        # Update action buttons with higher specificity
        if hasattr(self, 'start_btn'):
            if self.is_cracking:
                self.start_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {theme_colors['accent_orange']} !important;
                        color: white !important;
                        font-weight: bold;
                        padding: 10px;
                        border: 1px solid {theme_colors['accent_orange']};
                        border-radius: 6px;
                        min-width: 100px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme_colors['accent_orange']};
                        opacity: 0.8;
                    }}
                """)
            else:
                self.start_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {theme_colors['accent_green']} !important;
                        color: white !important;
                        font-weight: bold;
                        padding: 10px;
                        border: 1px solid {theme_colors['accent_green']};
                        border-radius: 6px;
                        min-width: 100px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme_colors['accent_green']};
                        opacity: 0.8;
                    }}
                """)

        if hasattr(self, 'stop_btn'):
            self.stop_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme_colors['error']} !important;
                    color: white !important;
                    font-weight: bold;
                    padding: 10px;
                    border: 1px solid {theme_colors['error']};
                    border-radius: 6px;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {theme_colors['error']};
                    opacity: 0.8;
                }}
            """)

        # Update current password display
        if hasattr(self, 'current_password_label'):
            self.current_password_label.setStyleSheet(f"font-family: monospace; padding: 8px; background-color: {theme_colors['surface']}; border: 1px solid {theme_colors['surface_variant']}; border-radius: 4px; color: {theme_colors['primary_text']};")

        # Update result label
        if hasattr(self, 'result_label'):
            current_text = self.result_label.text()
            if current_text and "✔ Password found:" in current_text:
                self.result_label.setStyleSheet(f"font-weight: bold; padding: 12px; color: {theme_colors['success']}; background-color: {theme_colors['success_bg']}; border: 1px solid {theme_colors['success']}; border-radius: 6px;")
            elif current_text and "❌ No password found" in current_text:
                self.result_label.setStyleSheet(f"font-weight: bold; padding: 12px; color: {theme_colors['error']}; background-color: {theme_colors['error_bg']}; border: 1px solid {theme_colors['error']}; border-radius: 6px;")
            elif current_text and "⚠ Error:" in current_text:
                self.result_label.setStyleSheet(f"font-weight: bold; padding: 12px; color: {theme_colors['warning']}; background-color: {theme_colors['warning_bg']}; border: 1px solid {theme_colors['warning']}; border-radius: 6px;")
            else:
                # Default styling for empty or other content
                self.result_label.setStyleSheet(f"font-weight: bold; padding: 12px; color: {theme_colors['primary_text']};")

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

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        
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

        # Password enhancement checkbox
        self.enhance_passwords_cb = QCheckBox("Enhance password list (generate variations with @, 3, 1, etc.)")
        self.enhance_passwords_cb.setChecked(True)  # Default enabled
        self.enhance_passwords_cb.setToolTip(
            "Generate password variations using common substitutions:\n"
            "• a/A → @, 4\n"
            "• e/E → 3\n"
            "• i/I → 1, !\n"
            "• o/O → 0\n"
            "• s/S → $, 5\n"
            "• Add common endings (123, !, 2024, etc.)\n"
            "• Capitalize first letter variations"
        )
        feedback_layout.addWidget(self.enhance_passwords_cb)
        
        # Current password display
        self.current_password_label = QLabel("Current attempt: (not started)")
        feedback_layout.addWidget(self.current_password_label)

        # Result display
        self.result_label = QLabel("")
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
        self.enhance_passwords_cb.toggled.connect(self.update_password_count_display)
        
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
            self.clear_archive_btn.setEnabled(True)
            self.check_ready_state()
            self.statusBar().showMessage(f"Archive selected: {filename}")
            # Update theme-aware styling
            self.update_themed_elements(self.get_current_theme_colors())
            
    def clear_archive_file(self):
        """Clear selected archive file"""
        self.archive_path = None
        self.archive_label.setText("No file selected")
        self.clear_archive_btn.setEnabled(False)
        self.check_ready_state()
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())
        
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
                    original_passwords = [line.strip() for line in f if line.strip()]
                    original_count = len(original_passwords)

                if original_count == 0:
                    QMessageBox.warning(self, "File Error", "Password file appears to be empty.")
                    return

                # Calculate enhanced count if enhancement is enabled
                if self.enhance_passwords_cb.isChecked():
                    enhanced_passwords = PasswordEnhancer.enhance_password_list(original_passwords)
                    enhanced_count = len(enhanced_passwords)
                    count_text = f"{original_count:,} passwords → {enhanced_count:,} enhanced"
                    status_text = f"Password list selected: {original_count:,} original + {enhanced_count - original_count:,} variations = {enhanced_count:,} total"
                else:
                    count_text = f"{original_count:,} passwords"
                    status_text = f"Password list selected: {original_count:,} passwords loaded"

                self.password_list_path = file_path
                filename = Path(file_path).name
                self.password_label.setText(f"{filename} ({count_text})")
                self.clear_password_btn.setEnabled(True)
                self.check_ready_state()
                self.statusBar().showMessage(status_text)
                # Update theme-aware styling
                self.update_themed_elements(self.get_current_theme_colors())

            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Could not read password file:\n{str(e)}")
            
    def clear_password_file(self):
        """Clear selected password list file"""
        self.password_list_path = None
        self.password_label.setText("No file selected")
        self.clear_password_btn.setEnabled(False)
        self.check_ready_state()
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())

    def get_current_theme_colors(self):
        """Get the current theme colors"""
        if self.current_theme == 'dark':
            return ThemeManager.DARK_THEME
        else:
            return ThemeManager.LIGHT_THEME

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
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())

        # Reset UI elements
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        self.current_password_label.setText("Current attempt: (starting)")
        self.result_label.setText("")
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())

        # Create and start worker thread
        enhance_passwords = self.enhance_passwords_cb.isChecked()
        self.worker_thread = PasswordCrackingWorker(self.archive_path, self.password_list_path, enhance_passwords)
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
        self.statusBar().showMessage("Password found successfully!")
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())

    def password_not_found(self):
        """Handle case where no password worked"""
        self.result_label.setText("❌ No password found")
        self.statusBar().showMessage("Password testing completed - no password found")
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())

    def handle_error(self, error_message):
        """Handle errors from worker thread"""
        self.result_label.setText(f"⚠ Error: {error_message}")
        self.statusBar().showMessage("Error occurred during password testing")
        QMessageBox.critical(self, "Error", error_message)
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())

    def cracking_finished(self):
        """Reset UI state when cracking is finished"""
        self.is_cracking = False
        self.update_ui_state()

        # Reset start button appearance
        self.start_btn.setText("Start Password Testing")
        # Update theme-aware styling
        self.update_themed_elements(self.get_current_theme_colors())

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

    def update_password_count_display(self):
        """Update the password count display when enhancement setting changes"""
        if not self.password_list_path:
            return

        try:
            # Re-read the password file to update count display
            with open(self.password_list_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_passwords = [line.strip() for line in f if line.strip()]
                original_count = len(original_passwords)

            # Calculate enhanced count if enhancement is enabled
            if self.enhance_passwords_cb.isChecked():
                enhanced_passwords = PasswordEnhancer.enhance_password_list(original_passwords)
                enhanced_count = len(enhanced_passwords)
                count_text = f"{original_count:,} passwords → {enhanced_count:,} enhanced"
                status_text = f"Enhancement enabled: {original_count:,} original + {enhanced_count - original_count:,} variations = {enhanced_count:,} total"
            else:
                count_text = f"{original_count:,} passwords"
                status_text = f"Enhancement disabled: {original_count:,} passwords"

            filename = Path(self.password_list_path).name
            self.password_label.setText(f"{filename} ({count_text})")
            self.statusBar().showMessage(status_text)

        except Exception as e:
            # If there's an error, just show a generic message
            self.statusBar().showMessage(f"Error updating password count: {str(e)}")

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
