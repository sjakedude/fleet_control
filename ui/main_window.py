"""Main window for the Fleet Control GUI application"""

try:
    from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget
    from PyQt6.QtCore import Qt
except ImportError:
    from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget
    from PyQt5.QtCore import Qt

from ui.main_menu import MainMenu
from ui.vehicle_selection import VehicleSelectionScreen
from ui.vehicle_details import VehicleDetailsScreen
from ui.add_purchase_form import AddPurchaseForm
from ui.add_maintenance_form import AddMaintenanceForm
from ui.add_hidden_cost_form import AddHiddenCostForm
from ui.settings_screen import SettingsScreen
from ui.reports_screen import ReportsScreen
from ui.theme_manager import ThemeManager


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        """Initialize the main window"""
        super().__init__()
        self.stacked_widget = None
        self.vehicle_details_screen = None
        self.add_purchase_screen = None
        self.add_maintenance_screen = None
        self.add_hidden_cost_screen = None
        self.settings_screen = None
        self.reports_screen = None
        self.current_vehicle = None
        self.theme_manager = ThemeManager()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Fleet Control")
        self.setGeometry(100, 100, 800, 600)

        # Stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Welcome screen
        welcome_widget = self.create_welcome_screen()
        self.stacked_widget.addWidget(welcome_widget)

        # Main menu screen
        main_menu = MainMenu(self.on_navigate)
        self.stacked_widget.addWidget(main_menu)

        # Vehicle selection screen
        self.vehicle_selection = VehicleSelectionScreen(self.show_main_menu, self.show_vehicle_details)
        self.stacked_widget.addWidget(self.vehicle_selection)
        
        # Load and apply initial theme settings
        self.load_initial_theme()

    def create_welcome_screen(self):
        """Create the welcome screen"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Welcome label
        label = QLabel("Welcome to Fleet Control")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addStretch()
        layout.addWidget(label)

        # Enter button
        enter_btn = QPushButton("Enter")
        enter_btn.setFixedHeight(50)
        enter_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        enter_btn.clicked.connect(self.show_main_menu)
        layout.addWidget(enter_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def show_main_menu(self):
        """Switch to main menu"""
        self.stacked_widget.setCurrentIndex(1)

    def on_navigate(self, action):
        """Handle navigation from main menu"""
        if action == "exit":
            self.close()
        elif action == "fleet":
            self.stacked_widget.setCurrentIndex(2)
        elif action == "reports":
            self.show_reports_screen()
        elif action == "settings":
            self.show_settings_screen()

    def show_reports_screen(self):
        """Show the reports screen"""
        if self.reports_screen:
            self.stacked_widget.removeWidget(self.reports_screen)
            self.reports_screen.deleteLater()
        self.reports_screen = ReportsScreen(on_back=self.show_main_menu)
        self.stacked_widget.addWidget(self.reports_screen)
        self.stacked_widget.setCurrentWidget(self.reports_screen)
        
    def show_settings_screen(self):
        """Show the settings screen"""
        if self.settings_screen:
            self.stacked_widget.removeWidget(self.settings_screen)
            self.settings_screen.deleteLater()
        self.settings_screen = SettingsScreen(on_back=self.show_main_menu)
        self.settings_screen.dark_mode_changed.connect(self.on_dark_mode_changed)
        self.stacked_widget.addWidget(self.settings_screen)
        self.stacked_widget.setCurrentWidget(self.settings_screen)
        
    def on_dark_mode_changed(self, is_dark_mode):
        """Handle dark mode toggle"""
        app = self.window().parent() if self.window().parent() else None
        if not app:
            # Try to get the application instance
            try:
                from PyQt6.QtWidgets import QApplication
                app = QApplication.instance()
            except ImportError:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
        
        if app:
            self.theme_manager.apply_theme(app, is_dark_mode)
            
    def load_initial_theme(self):
        """Load and apply the initial theme from settings"""
        import json
        import os
        
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", 'r') as f:
                    settings = json.load(f)
                is_dark_mode = settings.get("dark_mode", False)
                
                # Get the application instance and apply theme
                try:
                    from PyQt6.QtWidgets import QApplication
                    app = QApplication.instance()
                except ImportError:
                    from PyQt5.QtWidgets import QApplication
                    app = QApplication.instance()
                
                if app:
                    self.theme_manager.apply_theme(app, is_dark_mode)
        except Exception as e:
            print(f"Error loading initial theme: {e}")

    def show_vehicle_details(self, vehicle):
        """Show the vehicle details screen for the selected vehicle"""
        self.current_vehicle = vehicle
        if self.vehicle_details_screen:
            self.stacked_widget.removeWidget(self.vehicle_details_screen)
            self.vehicle_details_screen.deleteLater()
        self.vehicle_details_screen = VehicleDetailsScreen(
            vehicle, 
            self.show_vehicle_selection,
            on_add_purchase=self.show_add_purchase_form,
            on_add_maintenance=self.show_add_maintenance_form,
            on_add_hidden_cost=self.show_add_hidden_cost_form
        )
        self.stacked_widget.addWidget(self.vehicle_details_screen)
        self.stacked_widget.setCurrentWidget(self.vehicle_details_screen)

    def show_vehicle_selection(self):
        """Switch to vehicle selection screen"""
        self.stacked_widget.setCurrentIndex(2)

    def show_add_purchase_form(self):
        """Show the add purchase form"""
        if self.add_purchase_screen:
            self.stacked_widget.removeWidget(self.add_purchase_screen)
            self.add_purchase_screen.deleteLater()
        self.add_purchase_screen = AddPurchaseForm(
            self.current_vehicle,
            on_back=self.return_to_vehicle_details,
            on_success=self.return_to_vehicle_details
        )
        self.stacked_widget.addWidget(self.add_purchase_screen)
        self.stacked_widget.setCurrentWidget(self.add_purchase_screen)

    def return_to_vehicle_details(self):
        """Return to vehicle details and refresh data"""
        if self.current_vehicle:
            self.show_vehicle_details(self.current_vehicle)

    def show_add_maintenance_form(self):
        """Show the add maintenance form"""
        if self.add_maintenance_screen:
            self.stacked_widget.removeWidget(self.add_maintenance_screen)
            self.add_maintenance_screen.deleteLater()
        
        # Get tracking type from vehicle details screen
        tracking_type = "Mileage"
        if self.vehicle_details_screen and hasattr(self.vehicle_details_screen, 'tracking_type'):
            tracking_type = self.vehicle_details_screen.tracking_type
            
        self.add_maintenance_screen = AddMaintenanceForm(
            self.current_vehicle,
            on_back=self.return_to_vehicle_details,
            on_success=self.return_to_vehicle_details,
            tracking_type=tracking_type
        )
        self.stacked_widget.addWidget(self.add_maintenance_screen)
        self.stacked_widget.setCurrentWidget(self.add_maintenance_screen)

    def show_add_hidden_cost_form(self):
        """Show the add hidden cost form"""
        if self.add_hidden_cost_screen:
            self.stacked_widget.removeWidget(self.add_hidden_cost_screen)
            self.add_hidden_cost_screen.deleteLater()
        
        self.add_hidden_cost_screen = AddHiddenCostForm(
            self.current_vehicle,
            on_back=self.return_to_vehicle_details,
            on_success=self.return_to_vehicle_details
        )
        self.stacked_widget.addWidget(self.add_hidden_cost_screen)
        self.stacked_widget.setCurrentWidget(self.add_hidden_cost_screen)
