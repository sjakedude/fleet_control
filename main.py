"""Main entry point for the Fleet Control application"""

import sys
from ui.main_window import MainWindow
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication


def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
