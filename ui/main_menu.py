"""Main menu widget for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
    from PyQt6.QtCore import Qt
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
    from PyQt5.QtCore import Qt


class MainMenu(QWidget):
    """Main menu screen with navigation buttons"""

    def __init__(self, on_navigate):
        """
        Initialize the main menu
        
        Args:
            on_navigate: Callback function to handle navigation
        """
        super().__init__()
        self.on_navigate = on_navigate
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Main menu buttons
        buttons = [
            ("Manage Fleet", "fleet"),
            ("View Reports", "reports"),
            ("Settings", "settings"),
            ("Exit", "exit"),
        ]

        for button_text, action in buttons:
            btn = QPushButton(button_text)
            btn.setFixedHeight(50)
            btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            btn.clicked.connect(lambda checked, a=action: self.on_navigate(a))
            layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)
