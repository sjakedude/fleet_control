"""Theme manager for Fleet Control GUI application"""

class ThemeManager:
    """Manages application themes and styles"""
    
    def __init__(self):
        """Initialize the theme manager"""
        self.current_theme = "light"
        
    def get_light_theme(self):
        """Get light theme stylesheet"""
        return """
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        
        QWidget {
            background-color: #ffffff;
            color: #000000;
        }
        
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 8px 16px;
            color: #000000;
        }
        
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        QLabel {
            color: #000000;
            background-color: transparent;
        }
        
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
            color: #000000;
        }
        
        QLineEdit:focus {
            border: 2px solid #0078d4;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
            color: #000000;
        }
        
        QComboBox:hover {
            border: 1px solid #0078d4;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #666666;
        }
        
        QCheckBox {
            color: #000000;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #cccccc;
            border-radius: 3px;
            background-color: #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }
        
        QGroupBox {
            border: 2px solid #cccccc;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            color: #000000;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            background-color: #ffffff;
        }
        
        QScrollArea {
            background-color: #ffffff;
            border: 1px solid #cccccc;
        }
        
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 16px;
            border-radius: 8px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #cccccc;
            border-radius: 8px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #999999;
        }
        
        /* Table styling for light mode */
        QTableWidget {
            background-color: #ffffff;
            color: #000000;
            gridline-color: #cccccc;
            border: 1px solid #cccccc;
        }
        
        QTableWidget::item {
            background-color: #ffffff;
            color: #000000;
            border: none;
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        
        QTableWidget::item:alternate {
            background-color: #f5f5f5;
        }
        
        QHeaderView::section {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 8px;
            font-weight: bold;
        }
        
        QHeaderView::section:hover {
            background-color: #e0e0e0;
        }
        """
    
    def get_dark_theme(self):
        """Get dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 8px 16px;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: #505050;
        }
        
        QPushButton:pressed {
            background-color: #353535;
        }
        
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        
        QLineEdit {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 2px solid #0078d4;
        }
        
        QComboBox {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
            color: #ffffff;
        }
        
        QComboBox:hover {
            border: 1px solid #0078d4;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #cccccc;
        }
        
        QComboBox QAbstractItemView {
            background-color: #404040;
            border: 1px solid #555555;
            color: #ffffff;
            selection-background-color: #0078d4;
        }
        
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #555555;
            border-radius: 3px;
            background-color: #404040;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }
        
        QGroupBox {
            border: 2px solid #555555;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            color: #ffffff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            background-color: #2b2b2b;
        }
        
        QScrollArea {
            background-color: #2b2b2b;
            border: 1px solid #555555;
        }
        
        QScrollBar:vertical {
            background-color: #404040;
            width: 16px;
            border-radius: 8px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #666666;
            border-radius: 8px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #888888;
        }
        
        /* Table styling for dark mode */
        QTableWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            gridline-color: #555555;
            border: 1px solid #555555;
        }
        
        QTableWidget::item {
            background-color: #2b2b2b;
            color: #ffffff;
            border: none;
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        
        QTableWidget::item:alternate {
            background-color: #353535;
        }
        
        QHeaderView::section {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 8px;
            font-weight: bold;
        }
        
        QHeaderView::section:hover {
            background-color: #505050;
        }
        
        /* Custom styles for specific elements */
        .error-button {
            background-color: #ff4444;
            color: white;
            border: 1px solid #cc3333;
        }
        
        .error-button:hover {
            background-color: #ff6666;
        }
        
        .gray-text {
            color: #aaaaaa;
        }
        
        .disabled-input {
            background-color: #333333;
            color: #888888;
        }
        """
    
    def apply_theme(self, app, is_dark_mode=False):
        """Apply theme to the application"""
        if is_dark_mode:
            self.current_theme = "dark"
            stylesheet = self.get_dark_theme()
        else:
            self.current_theme = "light" 
            stylesheet = self.get_light_theme()
            
        app.setStyleSheet(stylesheet)
        
    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme
        
    def is_dark_mode(self):
        """Check if current theme is dark mode"""
        return self.current_theme == "dark"