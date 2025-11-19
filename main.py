"""Main entry point for the Fleet Control application"""

import sys
import json
import os
from ui.main_window import MainWindow
from ui.theme_manager import ThemeManager
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication


def load_initial_settings():
    """Load initial settings from file"""
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading initial settings: {e}")
    return {}


def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    
    # Load initial settings and apply theme
    settings = load_initial_settings()
    theme_manager = ThemeManager()
    is_dark_mode = settings.get("dark_mode", False)
    theme_manager.apply_theme(app, is_dark_mode)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
