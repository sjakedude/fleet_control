"""Add purchase form for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                  QLineEdit, QPushButton, QMessageBox, QFormLayout, QRadioButton, QButtonGroup)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                  QLineEdit, QPushButton, QMessageBox, QFormLayout, QRadioButton, QButtonGroup)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests
from datetime import datetime


class PurchaseSubmitWorker(QThread):
    """Worker thread to submit purchase data"""
    
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
            self.error.emit(f"Failed to submit purchase: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")


class AddPurchaseForm(QWidget):
    """Form to add a new purchase"""

    def __init__(self, vehicle, on_back=None, on_success=None):
        """
        Initialize the add purchase form
        
        Args:
            vehicle: The vehicle object
            on_back: Callback to go back
            on_success: Callback when purchase is successfully added
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
        
        title = QLabel("Add Purchase")
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

        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Enter item/part name")
        form_layout.addRow("Item:", self.item_input)

        self.date_purchased_input = QLineEdit()
        self.date_purchased_input.setText(datetime.now().strftime("%m/%d/%Y"))
        self.date_purchased_input.setPlaceholderText("MM/DD/YYYY")
        form_layout.addRow("Date Purchased:", self.date_purchased_input)

        # Installed radio buttons
        installed_layout = QHBoxLayout()
        self.installed_group = QButtonGroup()
        self.installed_yes = QRadioButton("Yes")
        self.installed_no = QRadioButton("No")
        self.installed_no.setChecked(True)  # Default to No
        self.installed_group.addButton(self.installed_yes, 1)
        self.installed_group.addButton(self.installed_no, 0)
        installed_layout.addWidget(self.installed_yes)
        installed_layout.addWidget(self.installed_no)
        installed_layout.addStretch()
        form_layout.addRow("Installed:", installed_layout)

        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        form_layout.addRow("Cost:", self.cost_input)

        self.store_input = QLineEdit()
        self.store_input.setPlaceholderText("Store/vendor name")
        form_layout.addRow("Store:", self.store_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Submit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedWidth(120)
        submit_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        submit_btn.clicked.connect(self.submit_purchase)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def submit_purchase(self):
        """Collect form data and submit to API"""
        # Gather form data
        installed_value = "Yes" if self.installed_yes.isChecked() else "No"
        data = {
            "item": self.item_input.text().strip(),
            "date_purchased": self.date_purchased_input.text().strip(),
            "installed": installed_value,
            "cost": self.cost_input.text().strip(),
            "store": self.store_input.text().strip()
        }
        # Basic validation
        if not data["item"]:
            QMessageBox.warning(self, "Validation Error", "Item is required")
            return

        # Submit via worker thread
        url = f"http://theconeportal.net:5000/fleet_control/vehicle_purchases?vehicle_name={self.vehicle['name'].replace(' ', '_').replace('.', '_').lower()}"
        self.submit_worker = PurchaseSubmitWorker(url, data)
        self.submit_worker.success.connect(self.on_submit_success)
        self.submit_worker.error.connect(self.on_submit_error)
        self.submit_worker.start()

    def on_submit_success(self):
        """Handle successful submission"""
        QMessageBox.information(self, "Success", "Purchase added successfully!")
        if self.on_success:
            self.on_success()

    def on_submit_error(self, message: str):
        """Handle submission error"""
        QMessageBox.critical(self, "Error", message)
