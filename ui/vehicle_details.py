"""Vehicle details screen for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QDialog
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QDialog
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests
from ui.delete_dialog import DeleteConfirmDialog, DeleteWorker

class MaintenanceFetchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, url: str, params: dict | None = None):
        super().__init__()
        self.url = url
        self.params = params or {}

    def run(self):
        try:
            resp = requests.get(self.url, params=self.params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                # Normalize to list
                data = [data]
            self.finished.emit(data)
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Failed to fetch maintenance: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")

class PurchasesFetchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, url: str, params: dict | None = None):
        super().__init__()
        self.url = url
        self.params = params or {}

    def run(self):
        try:
            resp = requests.get(self.url, params=self.params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                data = [data]
            self.finished.emit(data)
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Failed to fetch purchases: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")

class VehicleDetailsScreen(QWidget):
    """Screen to show details for a selected vehicle"""

    def __init__(self, vehicle, on_back=None, on_add_purchase=None, on_add_maintenance=None):
        super().__init__()
        self.vehicle = vehicle
        self.on_back = on_back
        self.on_add_purchase = on_add_purchase
        self.on_add_maintenance = on_add_maintenance
        self.fetch_worker = None
        self.purchases_worker = None
        self.delete_worker = None
        self.selected_maintenance = None
        self.selected_purchase = None
        self.tracking_type = "Mileage"  # Default tracking type
        self.init_ui()
        self.load_maintenance()
        self.load_purchases()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Top bar with back button and vehicle name
        top_bar = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(80)
        if self.on_back:
            back_btn.clicked.connect(self.on_back)
        top_bar.addWidget(back_btn)
        top_bar.addSpacing(10)
        name = self.vehicle.get("name", str(self.vehicle)) if isinstance(self.vehicle, dict) else str(self.vehicle)
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_bar.addWidget(name_label)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Maintenance table
        maint_label = QLabel("Maintenance")
        maint_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(maint_label)
        self.maint_table = QTableWidget(0, 6)
        # Headers will be set dynamically based on API response
        self.maint_table.setHorizontalHeaderLabels([
            "Job", "Date Started", "Date Completed", "Tracking", "Cost", "Notes"
        ])
        self.maint_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.maint_table.itemSelectionChanged.connect(self.on_maintenance_selection_changed)
        # Show initial loading row
        self.maint_table.setRowCount(1)
        self.maint_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        layout.addWidget(self.maint_table)

        # Purchases table
        purch_label = QLabel("Purchases")
        purch_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(purch_label)
        self.purch_table = QTableWidget(0, 5)
        self.purch_table.setHorizontalHeaderLabels([
            "Item", "Date Purchased", "Installed", "Cost", "Store"
        ])
        self.purch_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.purch_table.itemSelectionChanged.connect(self.on_purchase_selection_changed)
        # initial loading row
        self.purch_table.setRowCount(1)
        self.purch_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        layout.addWidget(self.purch_table)

        # Buttons for adding/deleting entries
        btn_layout = QHBoxLayout()
        add_maint_btn = QPushButton("Add Maintenance")
        if self.on_add_maintenance:
            add_maint_btn.clicked.connect(self.on_add_maintenance)
        delete_maint_btn = QPushButton("Delete Maintenance")
        delete_maint_btn.clicked.connect(self.delete_maintenance)
        add_purch_btn = QPushButton("Add Purchase")
        delete_purch_btn = QPushButton("Delete Purchase")
        delete_purch_btn.clicked.connect(self.delete_purchase)
        if self.on_add_purchase:
            add_purch_btn.clicked.connect(self.on_add_purchase)
        
        btn_layout.addWidget(add_maint_btn)
        btn_layout.addWidget(delete_maint_btn)
        btn_layout.addWidget(add_purch_btn)
        btn_layout.addWidget(delete_purch_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_purchases(self):
        params = {}
        if isinstance(self.vehicle, dict):
            if "name" in self.vehicle:
                params["vehicle_name"] = self.vehicle.get("name")
        else:
            params["vehicle_name"] = str(self.vehicle)

        url = "http://theconeportal.net:5000/fleet_control/vehicle_purchases"
        self.purchases_worker = PurchasesFetchWorker(url, params)
        self.purchases_worker.finished.connect(self.on_purchases_loaded)
        self.purchases_worker.error.connect(self.on_purchases_error)
        self.purchases_worker.start()

    def on_purchases_loaded(self, items: list):
        self.purch_table.setRowCount(0)
        if not items:
            self.purch_table.setRowCount(1)
            self.purch_table.setItem(0, 0, QTableWidgetItem("No purchases"))
            return

        def get_any(d, keys, default=""):
            for k in keys:
                if k in d and d[k] is not None:
                    return d[k]
            return default

        # Store purchases data for deletion
        self.purchases_data = items
        
        for row_idx, item in enumerate(items):
            rec = item if isinstance(item, dict) else {}
            itm = get_any(rec, ["item", "name", "part"])
            date_purchased = get_any(rec, ["date_purchased", "purchased", "date"])
            installed = get_any(rec, ["installed", "is_installed", "status"])
            cost = get_any(rec, ["cost", "price", "amount"])
            store = get_any(rec, ["store", "vendor", "shop"]) 

            self.purch_table.insertRow(row_idx)
            self.purch_table.setItem(row_idx, 0, QTableWidgetItem(str(itm)))
            self.purch_table.setItem(row_idx, 1, QTableWidgetItem(str(date_purchased)))
            self.purch_table.setItem(row_idx, 2, QTableWidgetItem(str(installed)))
            self.purch_table.setItem(row_idx, 3, QTableWidgetItem(str(cost)))
            self.purch_table.setItem(row_idx, 4, QTableWidgetItem(str(store)))

    def on_purchases_error(self, message: str):
        self.purch_table.setRowCount(1)
        self.purch_table.setItem(0, 0, QTableWidgetItem(f"Error: {message}"))

    def on_maintenance_selection_changed(self):
        """Handle maintenance table selection changes"""
        selected_rows = self.maint_table.selectionModel().selectedRows()
        if selected_rows and hasattr(self, 'maintenance_data'):
            row = selected_rows[0].row()
            if 0 <= row < len(self.maintenance_data):
                self.selected_maintenance = self.maintenance_data[row]
            else:
                self.selected_maintenance = None
        else:
            self.selected_maintenance = None

    def on_purchase_selection_changed(self):
        """Handle purchases table selection changes"""
        selected_rows = self.purch_table.selectionModel().selectedRows()
        if selected_rows and hasattr(self, 'purchases_data'):
            row = selected_rows[0].row()
            if 0 <= row < len(self.purchases_data):
                self.selected_purchase = self.purchases_data[row]
            else:
                self.selected_purchase = None
        else:
            self.selected_purchase = None

    def delete_maintenance(self):
        """Delete selected maintenance record"""
        if not self.selected_maintenance:
            QMessageBox.warning(self, "No Selection", "Please select a maintenance record to delete.")
            return
        
        dialog = DeleteConfirmDialog("maintenance", self.selected_maintenance, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Prepare delete data
            data = dict(self.selected_maintenance)
            
            # Start delete worker
            url = "http://theconeportal.net:5000/fleet_control/vehicle_maintenance?vehicle_name=" + self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
            self.delete_worker = DeleteWorker(url, data)
            self.delete_worker.success.connect(self.on_delete_success)
            self.delete_worker.error.connect(self.on_delete_error)
            self.delete_worker.start()

    def delete_purchase(self):
        """Delete selected purchase record"""
        if not self.selected_purchase:
            QMessageBox.warning(self, "No Selection", "Please select a purchase record to delete.")
            return
        
        dialog = DeleteConfirmDialog("purchase", self.selected_purchase, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Prepare delete data
            data = dict(self.selected_purchase)
            
            # Start delete worker
            url = "http://theconeportal.net:5000/fleet_control/vehicle_purchases?vehicle_name=" + self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
            self.delete_worker = DeleteWorker(url, data)
            self.delete_worker.success.connect(self.on_delete_success)
            self.delete_worker.error.connect(self.on_delete_error)
            self.delete_worker.start()

    def on_delete_success(self):
        """Handle successful deletion"""
        QMessageBox.information(self, "Success", "Record deleted successfully!")
        # Reload data
        self.load_maintenance()
        self.load_purchases()

    def on_delete_error(self, message: str):
        """Handle deletion error"""
        QMessageBox.critical(self, "Error", message)

    def load_maintenance(self):
        # Determine vehicle identifier to send
        params = {}
        if isinstance(self.vehicle, dict):
            if "name" in self.vehicle:
                params["vehicle_name"] = self.vehicle.get("name")
        else:
            params["vehicle_name"] = str(self.vehicle)

        # Start worker to fetch maintenance data
        url = "http://theconeportal.net:5000/fleet_control/vehicle_maintenance?vehicle_name=" + params["vehicle_name"].replace(" ", "_").replace(".", "_").lower()
        self.fetch_worker = MaintenanceFetchWorker(url, params)
        self.fetch_worker.finished.connect(self.on_maintenance_loaded)
        self.fetch_worker.error.connect(self.on_maintenance_error)
        self.fetch_worker.start()

    def on_maintenance_loaded(self, items: list):
        # Clear table and populate rows
        self.maint_table.setRowCount(0)
        if not items:
            self.maint_table.setRowCount(1)
            self.maint_table.setItem(0, 0, QTableWidgetItem("No maintenance records"))
            return

        def get_any(d, keys, default=""):
            for k in keys:
                if k in d and d[k] is not None:
                    return d[k]
            return default

        # Store maintenance data for deletion
        self.maintenance_data = items
        
        # Determine tracking type (Hours vs Mileage) from first item
        tracking_header = "Tracking"
        if items:
            first_item = items[0] if isinstance(items[0], dict) else {}
            if any(key in first_item for key in ["hours", "hour", "engine_hours"]):
                tracking_header = "Hours"
                self.tracking_type = "Hours"
            elif any(key in first_item for key in ["mileage", "miles", "milage", "odometer"]):
                tracking_header = "Mileage"
                self.tracking_type = "Mileage"
        
        # Update table headers dynamically
        headers = ["Job", "Date Started", "Date Completed", tracking_header, "Cost", "Notes"]
        self.maint_table.setHorizontalHeaderLabels(headers)
        
        for row_idx, item in enumerate(items):
            # Accept dict-like inputs
            rec = item if isinstance(item, dict) else {}
            job = get_any(rec, ["job", "title", "task"]) 
            date_started = get_any(rec, ["date_started", "started", "start_date"]) 
            date_completed = get_any(rec, ["date_completed", "completed", "end_date"]) 
            
            # Dynamic tracking value - check for hours first, then mileage
            tracking_value = (
                get_any(rec, ["hours", "hour", "engine_hours"]) or
                get_any(rec, ["mileage", "miles", "milage", "odometer"])
            )
            
            cost = get_any(rec, ["cost", "price", "amount"]) 
            notes = get_any(rec, ["notes", "note", "details"]) 

            self.maint_table.insertRow(row_idx)
            self.maint_table.setItem(row_idx, 0, QTableWidgetItem(str(job)))
            self.maint_table.setItem(row_idx, 1, QTableWidgetItem(str(date_started)))
            self.maint_table.setItem(row_idx, 2, QTableWidgetItem(str(date_completed)))
            self.maint_table.setItem(row_idx, 3, QTableWidgetItem(str(tracking_value)))
            self.maint_table.setItem(row_idx, 4, QTableWidgetItem(str(cost)))
            self.maint_table.setItem(row_idx, 5, QTableWidgetItem(str(notes)))

    def on_maintenance_error(self, message: str):
        # Indicate error in the table
        self.maint_table.setRowCount(1)
        self.maint_table.setItem(0, 0, QTableWidgetItem(f"Error: {message}"))
