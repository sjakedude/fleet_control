"""Settings screen widget for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QCheckBox, QGroupBox, QSpacerItem, QSizePolicy)
    from PyQt6.QtCore import Qt, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QCheckBox, QGroupBox, QSpacerItem, QSizePolicy)
    from PyQt5.QtCore import Qt, pyqtSignal

import json
import os


class SettingsScreen(QWidget):
    """Settings screen with various application settings"""
    
    # Signal emitted when dark mode is toggled
    dark_mode_changed = pyqtSignal(bool)
    
    def __init__(self, on_back=None):
        """
        Initialize the settings screen
        
        Args:
            on_back: Callback function to handle back navigation
        """
        super().__init__()
        self.on_back = on_back
        self.settings_file = "settings.json"
        self.settings = self.load_settings()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Title
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Appearance settings group
        appearance_group = QGroupBox("Appearance")
        appearance_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")
        appearance_layout = QVBoxLayout()
        
        # Dark mode checkbox
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.setStyleSheet("font-size: 14px; padding: 5px;")
        self.dark_mode_checkbox.setChecked(self.settings.get("dark_mode", False))
        self.dark_mode_checkbox.stateChanged.connect(self.on_dark_mode_changed)
        
        dark_mode_description = QLabel("Enable dark mode for a darker interface theme")
        dark_mode_description.setStyleSheet("font-size: 12px; color: gray; margin-left: 25px;")
        
        appearance_layout.addWidget(self.dark_mode_checkbox)
        appearance_layout.addWidget(dark_mode_description)
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Add spacer to push buttons to bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.setFixedHeight(40)
        back_btn.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 100px;")
        back_btn.clicked.connect(self.go_back)
        
        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setFixedHeight(40)
        reset_btn.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 120px;")
        reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(back_btn)
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {}
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def on_dark_mode_changed(self, state):
        """Handle dark mode checkbox change"""
        # Handle both PyQt5 and PyQt6 checkbox states
        try:
            # PyQt6 style
            is_dark = state == Qt.CheckState.Checked.value
        except AttributeError:
            # PyQt5 style (state is an integer: 0=unchecked, 2=checked)
            is_dark = state == 2
        
        self.settings["dark_mode"] = is_dark
        self.save_settings()
        self.dark_mode_changed.emit(is_dark)
        
    def reset_settings(self):
        """Reset all settings to defaults"""
        self.settings = {"dark_mode": False}
        self.save_settings()
        self.dark_mode_checkbox.setChecked(False)
        self.dark_mode_changed.emit(False)
        
    def go_back(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
            
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)