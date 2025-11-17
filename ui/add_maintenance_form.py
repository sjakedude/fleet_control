"""Add maintenance form for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                  QLineEdit, QPushButton, QMessageBox, QFormLayout, QCheckBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                  QLineEdit, QPushButton, QMessageBox, QFormLayout, QCheckBox)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests
from datetime import datetime


class MaintenanceSubmitWorker(QThread):
    """Worker thread to submit maintenance data"""
    
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
            self.error.emit(f"Failed to submit maintenance: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")


class AddMaintenanceForm(QWidget):
    """Form to add a new maintenance record"""

    def __init__(self, vehicle, on_back=None, on_success=None, tracking_type="Mileage"):
        """
        Initialize the add maintenance form
        
        Args:
            vehicle: The vehicle object
            on_back: Callback to go back
            on_success: Callback when maintenance is successfully added
            tracking_type: "Hours" or "Mileage" to determine field type
        """
        super().__init__()
        self.vehicle = vehicle
        self.on_back = on_back
        self.on_success = on_success
        self.tracking_type = tracking_type
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
        
        title = QLabel("Add Maintenance")
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

        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Enter job/service description")
        form_layout.addRow("Job:", self.job_input)

        # Auto-populate with today's date
        today = datetime.now().strftime("%m/%d/%Y")
        
        self.date_started_input = QLineEdit()
        self.date_started_input.setText(today)
        self.date_started_input.setPlaceholderText("MM/DD/YYYY")
        form_layout.addRow("Date Started:", self.date_started_input)

        self.date_completed_input = QLineEdit()
        self.date_completed_input.setText(today)
        self.date_completed_input.setPlaceholderText("MM/DD/YYYY (optional)")
        form_layout.addRow("Date Completed:", self.date_completed_input)

        # Dynamic tracking field based on type
        self.tracking_input = QLineEdit()
        if self.tracking_type == "Hours":
            self.tracking_input.setPlaceholderText("Current hours")
            form_layout.addRow("Hours:", self.tracking_input)
        else:
            self.tracking_input.setPlaceholderText("Current mileage")
            form_layout.addRow("Mileage:", self.tracking_input)

        # Cost section with checkbox
        cost_layout = QHBoxLayout()
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        self.free_checkbox = QCheckBox("FREE")
        self.free_checkbox.stateChanged.connect(self.on_free_checkbox_changed)
        cost_layout.addWidget(self.cost_input)
        cost_layout.addWidget(self.free_checkbox)
        form_layout.addRow("Cost:", cost_layout)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Additional notes")
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Submit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedWidth(120)
        submit_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        submit_btn.clicked.connect(self.submit_maintenance)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def on_free_checkbox_changed(self, state):
        """Handle free checkbox state change"""
        if state == 2:  # Checked
            self.cost_input.setText("FREE")
            self.cost_input.setEnabled(False)
            self.cost_input.setStyleSheet("background-color: #f0f0f0; color: #666;")
        else:  # Unchecked
            self.cost_input.setText("")
            self.cost_input.setEnabled(True)
            self.cost_input.setStyleSheet("")
            self.cost_input.setPlaceholderText("0.00")

    def submit_maintenance(self):
        """Collect form data and submit to API"""
        # Gather form data
        data = {
            "job": self.job_input.text().strip(),
            "date_started": self.date_started_input.text().strip(),
            "date_completed": self.date_completed_input.text().strip(),
            "cost": self.cost_input.text().strip(),
            "notes": self.notes_input.text().strip()
        }
        
        # Add tracking field dynamically
        if self.tracking_type == "Hours":
            data["hours"] = self.tracking_input.text().strip()
        else:
            data["mileage"] = self.tracking_input.text().strip()

        # Add vehicle identifier
        if isinstance(self.vehicle, dict):
            if "name" in self.vehicle:
                data["vehicle_name"] = self.vehicle.get("name")
            if "id" in self.vehicle:
                data["vehicle_id"] = self.vehicle.get("id")
        else:
            data["vehicle_name"] = str(self.vehicle)

        # Basic validation
        if not data["job"]:
            QMessageBox.warning(self, "Validation Error", "Job description is required")
            return

        # Submit via worker thread
        url = "http://theconeportal.net:5000/fleet_control/vehicle_maintenance?vehicle_name={}".format(
            data["vehicle_name"].replace(" ", "_").replace(".", "_").lower()
        )
        self.submit_worker = MaintenanceSubmitWorker(url, data)
        self.submit_worker.success.connect(self.on_submit_success)
        self.submit_worker.error.connect(self.on_submit_error)
        self.submit_worker.start()

    def on_submit_success(self):
        """Handle successful submission"""
        QMessageBox.information(self, "Success", "Maintenance record added successfully!")
        if self.on_success:
            self.on_success()

    def on_submit_error(self, message: str):
        """Handle submission error"""
        QMessageBox.critical(self, "Error", message)