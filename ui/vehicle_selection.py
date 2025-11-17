"""Vehicle selection screen for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests


class VehicleFetchWorker(QThread):
    """Worker thread to fetch vehicles from API"""
    
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        """Fetch vehicles from the API"""
        try:
            response = requests.get("http://theconeportal.net:5000/fleet_control/vehicle_list")
            response.raise_for_status()
            vehicles = response.json()
            self.finished.emit(vehicles)
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Failed to fetch vehicles: {str(e)}")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


class VehicleSelectionScreen(QWidget):
    """Screen to select and manage vehicles"""

    def __init__(self, on_back, on_next=None):
        """
        Initialize the vehicle selection screen
        
        Args:
            on_back: Callback function to return to main menu
        """
        super().__init__()
        self.on_back = on_back
        self.on_next = on_next
        self.vehicles = []
        self.selected_vehicle = None
        self.fetch_worker = None
        self.init_ui()
        self.load_vehicles()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Select a Vehicle")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)


        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.load_vehicles)
        layout.addWidget(refresh_btn)

        # Vehicle list
        self.vehicle_list = QListWidget()
        self.vehicle_list.itemClicked.connect(self.on_vehicle_selected)
        layout.addWidget(self.vehicle_list)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Back button

        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(100)
        back_btn.clicked.connect(self.on_back)
        button_layout.addWidget(back_btn)

        # Next button
        next_btn = QPushButton("Next")
        next_btn.setFixedWidth(100)
        next_btn.clicked.connect(self.handle_next)
        button_layout.addWidget(next_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_vehicles(self):
        """Load vehicles from the API"""
        # Show loading message
        self.vehicle_list.clear()
        loading_item = QListWidgetItem("Loading vehicles...")
        self.vehicle_list.addItem(loading_item)

        # Start fetch worker thread
        self.fetch_worker = VehicleFetchWorker()
        self.fetch_worker.finished.connect(self.on_vehicles_loaded)
        self.fetch_worker.error.connect(self.on_fetch_error)
        self.fetch_worker.start()

    def on_vehicles_loaded(self, vehicles):
        """Handle vehicles loaded from API"""
        self.vehicles = vehicles
        self.vehicle_list.clear()

        if not vehicles:
            no_vehicles_item = QListWidgetItem("No vehicles available")
            self.vehicle_list.addItem(no_vehicles_item)
            return

        # Populate list with vehicles
        for vehicle in vehicles:
            # Handle both dict and object responses
            if isinstance(vehicle, dict):
                vehicle_name = vehicle.get("name", vehicle.get("id", "Unknown"))
            else:
                vehicle_name = str(vehicle)
            
            item = QListWidgetItem(vehicle_name)
            item.setData(Qt.ItemDataRole.UserRole, vehicle)
            self.vehicle_list.addItem(item)

    def on_fetch_error(self, error_message):
        """Handle API fetch error"""
        self.vehicle_list.clear()
        error_item = QListWidgetItem(f"Error: {error_message}")
        error_item.setFlags(error_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.vehicle_list.addItem(error_item)
        
        # Show error dialog
        QMessageBox.critical(self, "Error", error_message)

    def on_vehicle_selected(self, item):
        """Handle vehicle selection"""
        vehicle = item.data(Qt.ItemDataRole.UserRole)
        self.selected_vehicle = vehicle
        print(f"Selected vehicle: {vehicle}")

    def handle_next(self):
        if self.on_next and self.selected_vehicle:
            self.on_next(self.selected_vehicle)
