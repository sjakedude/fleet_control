"""Add hidden cost form for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                  QLineEdit, QPushButton, QMessageBox, QFormLayout, QTextEdit)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                  QLineEdit, QPushButton, QMessageBox, QFormLayout, QTextEdit)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests
from datetime import datetime


class HiddenCostSubmitWorker(QThread):
    """Worker thread to submit hidden cost data"""
    
    success = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url: str, data: dict):
        super().__init__()
        self.url = url
        self.data = data

    def run(self):
        try:
            resp = requests.post(self.url, json=self.data, timeout=15)
            resp.raise_for_status()
            self.success.emit()
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Failed to submit hidden cost: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")


class AddHiddenCostForm(QWidget):
    """Form to add a new hidden cost"""

    def __init__(self, vehicle, on_back=None, on_success=None):
        """
        Initialize the add hidden cost form
        
        Args:
            vehicle: The vehicle object
            on_back: Callback to go back
            on_success: Callback when hidden cost is successfully added
        """
        super().__init__()
        self.vehicle = vehicle
        self.on_back = on_back
        self.on_success = on_success
        self.submit_worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_bar = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(80)
        if self.on_back:
            back_btn.clicked.connect(self.on_back)
        title_bar.addWidget(back_btn)
        title_bar.addSpacing(10)
        
        title = QLabel("Add Hidden Cost")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_bar.addWidget(title)
        title_bar.addStretch()
        layout.addLayout(title_bar)

        # Vehicle name display
        vehicle_name = self.vehicle.get("name", str(self.vehicle)) if isinstance(self.vehicle, dict) else str(self.vehicle)
        vehicle_label = QLabel(f"Vehicle: {vehicle_name}")
        vehicle_label.setStyleSheet("font-size: 14px; color: gray;")
        layout.addWidget(vehicle_label)

        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter cost name/title")
        form_layout.addRow("Name:", self.name_input)

        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        form_layout.addRow("Cost:", self.cost_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter description or details about this cost")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)

        self.date_input = QLineEdit()
        self.date_input.setText(datetime.now().strftime("%m/%d/%Y"))
        self.date_input.setPlaceholderText("MM/DD/YYYY")
        form_layout.addRow("Date:", self.date_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Submit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedWidth(120)
        submit_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        submit_btn.clicked.connect(self.submit_hidden_cost)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def submit_hidden_cost(self):
        """Collect form data and submit to API"""
        # Gather form data
        data = {
            "name": self.name_input.text().strip(),
            "cost": self.cost_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "date": self.date_input.text().strip()
        }

        # Basic validation
        if not data["name"]:
            QMessageBox.warning(self, "Validation Error", "Name is required")
            return

        if not data["cost"]:
            QMessageBox.warning(self, "Validation Error", "Cost is required")
            return

        # Try to validate amount is a number
        try:
            float(data["cost"])
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Cost must be a valid number")
            return

        # Submit via worker thread
        vehicle_name = self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
        url = f"http://theconeportal.net:5000/fleet_control/vehicle_hidden_costs?vehicle_name={vehicle_name}"
        self.submit_worker = HiddenCostSubmitWorker(url, data)
        self.submit_worker.success.connect(self.on_submit_success)
        self.submit_worker.error.connect(self.on_submit_error)
        self.submit_worker.start()

    def on_submit_success(self):
        """Handle successful submission"""
        QMessageBox.information(self, "Success", "Hidden cost added successfully!")
        if self.on_success:
            self.on_success()

    def on_submit_error(self, message: str):
        """Handle submission error"""
        QMessageBox.critical(self, "Error", message)