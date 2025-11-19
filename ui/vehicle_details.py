"""Vehicle details screen for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QDialog
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QDialog
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests
from ui.delete_dialog import DeleteConfirmDialog, DeleteWorker
from ui.add_hidden_cost_form import AddHiddenCostForm

class UpdateWorker(QThread):
    success = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url: str, data: dict):
        super().__init__()
        self.url = url
        self.data = data

    def run(self):
        try:
            resp = requests.put(self.url, json=self.data, timeout=15)
            resp.raise_for_status()
            self.success.emit()
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Failed to update record: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")

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

class HiddenCostsFetchWorker(QThread):
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
            self.error.emit(f"Failed to fetch hidden costs: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")

class VehicleDetailsScreen(QWidget):
    """Screen to show details for a selected vehicle"""

    def __init__(self, vehicle, on_back=None, on_add_purchase=None, on_add_maintenance=None, on_add_hidden_cost=None):
        super().__init__()
        self.vehicle = vehicle
        self.on_back = on_back
        self.on_add_purchase = on_add_purchase
        self.on_add_maintenance = on_add_maintenance
        self.on_add_hidden_cost = on_add_hidden_cost
        self.fetch_worker = None
        self.purchases_worker = None
        self.hidden_costs_worker = None
        self.delete_worker = None
        self.update_worker = None
        self.selected_maintenance = None
        self.selected_purchase = None
        self.selected_hidden_cost = None
        self.tracking_type = "Mileage"  # Default tracking type
        self.init_ui()
        self.load_maintenance()
        self.load_purchases()
        self.load_hidden_costs()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Top bar with back button, vehicle name, and refresh button
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
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self.refresh_data)
        top_bar.addWidget(refresh_btn)
        layout.addLayout(top_bar)

        # Maintenance table
        maint_label = QLabel("Maintenance")
        maint_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(maint_label)
        self.maint_table = QTableWidget(0, 7)
        # Headers will be set dynamically based on API response
        self.maint_table.setHorizontalHeaderLabels([
            "ID", "Job", "Date Started", "Date Completed", "Tracking", "Cost", "Notes"
        ])
        self.maint_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.maint_table.verticalHeader().setVisible(False)
        self.maint_table.itemSelectionChanged.connect(self.on_maintenance_selection_changed)
        # Show initial loading row
        self.maint_table.setRowCount(1)
        self.maint_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        layout.addWidget(self.maint_table)

        # Maintenance buttons
        maint_btn_layout = QHBoxLayout()
        add_maint_btn = QPushButton("Add Maintenance")
        if self.on_add_maintenance:
            add_maint_btn.clicked.connect(self.on_add_maintenance)
        update_maint_btn = QPushButton("Update Maintenance")
        update_maint_btn.clicked.connect(self.update_maintenance)
        delete_maint_btn = QPushButton("Delete Maintenance")
        delete_maint_btn.clicked.connect(self.delete_maintenance)
        
        maint_btn_layout.addWidget(add_maint_btn)
        maint_btn_layout.addWidget(update_maint_btn)
        maint_btn_layout.addWidget(delete_maint_btn)
        maint_btn_layout.addStretch()  # Push buttons to the left
        layout.addLayout(maint_btn_layout)

        # Purchases table
        purch_label = QLabel("Purchases")
        purch_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(purch_label)
        self.purch_table = QTableWidget(0, 6)
        self.purch_table.setHorizontalHeaderLabels([
            "ID", "Item", "Date Purchased", "Installed", "Cost", "Store"
        ])
        self.purch_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.purch_table.verticalHeader().setVisible(False)
        self.purch_table.itemSelectionChanged.connect(self.on_purchase_selection_changed)
        # initial loading row
        self.purch_table.setRowCount(1)
        self.purch_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        layout.addWidget(self.purch_table)

        # Purchases buttons
        purch_btn_layout = QHBoxLayout()
        add_purch_btn = QPushButton("Add Purchase")
        if self.on_add_purchase:
            add_purch_btn.clicked.connect(self.on_add_purchase)
        update_purch_btn = QPushButton("Update Purchase")
        update_purch_btn.clicked.connect(self.update_purchase)
        delete_purch_btn = QPushButton("Delete Purchase")
        delete_purch_btn.clicked.connect(self.delete_purchase)
        
        purch_btn_layout.addWidget(add_purch_btn)
        purch_btn_layout.addWidget(update_purch_btn)
        purch_btn_layout.addWidget(delete_purch_btn)
        purch_btn_layout.addStretch()  # Push buttons to the left
        layout.addLayout(purch_btn_layout)

        # Hidden Costs table
        hidden_costs_label = QLabel("Hidden Costs")
        hidden_costs_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(hidden_costs_label)
        self.hidden_costs_table = QTableWidget(0, 5)
        self.hidden_costs_table.setHorizontalHeaderLabels([
            "ID", "Name", "Cost", "Description", "Date"
        ])
        self.hidden_costs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.hidden_costs_table.verticalHeader().setVisible(False)
        self.hidden_costs_table.itemSelectionChanged.connect(self.on_hidden_cost_selection_changed)
        # initial loading row
        self.hidden_costs_table.setRowCount(1)
        self.hidden_costs_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        layout.addWidget(self.hidden_costs_table)



        # Hidden Costs buttons
        hidden_costs_btn_layout = QHBoxLayout()
        add_hidden_cost_btn = QPushButton("Add Hidden Cost")
        if self.on_add_hidden_cost:
            add_hidden_cost_btn.clicked.connect(self.add_hidden_cost)
        update_hidden_cost_btn = QPushButton("Update Hidden Cost")
        update_hidden_cost_btn.clicked.connect(self.update_hidden_cost)
        delete_hidden_cost_btn = QPushButton("Delete Hidden Cost")
        delete_hidden_cost_btn.clicked.connect(self.delete_hidden_cost)
        
        hidden_costs_btn_layout.addWidget(add_hidden_cost_btn)
        hidden_costs_btn_layout.addWidget(update_hidden_cost_btn)
        hidden_costs_btn_layout.addWidget(delete_hidden_cost_btn)
        hidden_costs_btn_layout.addStretch()  # Push buttons to the left
        layout.addLayout(hidden_costs_btn_layout)

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
            item_id = get_any(rec, ["id", "_id"])
            itm = get_any(rec, ["item", "name", "part"])
            date_purchased = get_any(rec, ["date_purchased", "purchased", "date"])
            installed = get_any(rec, ["installed", "is_installed", "status"])
            cost = get_any(rec, ["cost", "price", "amount"])
            store = get_any(rec, ["store", "vendor", "shop"]) 

            self.purch_table.insertRow(row_idx)
            self.purch_table.setItem(row_idx, 0, QTableWidgetItem(str(item_id)))
            self.purch_table.setItem(row_idx, 1, QTableWidgetItem(str(itm)))
            self.purch_table.setItem(row_idx, 2, QTableWidgetItem(str(date_purchased)))
            self.purch_table.setItem(row_idx, 3, QTableWidgetItem(str(installed)))
            self.purch_table.setItem(row_idx, 4, QTableWidgetItem(str(cost)))
            self.purch_table.setItem(row_idx, 5, QTableWidgetItem(str(store)))

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
        
        # Check if maintenance record has an id
        if "id" not in self.selected_maintenance:
            QMessageBox.warning(self, "No ID", "Selected maintenance record does not have an ID.")
            return
        
        dialog = DeleteConfirmDialog("maintenance", self.selected_maintenance, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Prepare delete data
            data = dict(self.selected_maintenance)
            
            # Start delete worker with id parameter
            vehicle_name = self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
            maintenance_id = self.selected_maintenance["id"]
            url = f"http://theconeportal.net:5000/fleet_control/vehicle_maintenance?vehicle_name={vehicle_name}&id={maintenance_id}"
            self.delete_worker = DeleteWorker(url, data)
            self.delete_worker.success.connect(self.on_delete_success)
            self.delete_worker.error.connect(self.on_delete_error)
            self.delete_worker.start()

    def delete_purchase(self):
        """Delete selected purchase record"""
        if not self.selected_purchase:
            QMessageBox.warning(self, "No Selection", "Please select a purchase record to delete.")
            return
        
        # Check if purchase record has an id
        if "id" not in self.selected_purchase:
            QMessageBox.warning(self, "No ID", "Selected purchase record does not have an ID.")
            return
        
        dialog = DeleteConfirmDialog("purchase", self.selected_purchase, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Prepare delete data
            data = dict(self.selected_purchase)
            
            # Start delete worker with id parameter
            vehicle_name = self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
            purchase_id = self.selected_purchase["id"]
            url = f"http://theconeportal.net:5000/fleet_control/vehicle_purchases?vehicle_name={vehicle_name}&id={purchase_id}"
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
        self.load_hidden_costs()

    def on_delete_error(self, message: str):
        """Handle deletion error"""
        QMessageBox.critical(self, "Error", message)

    def update_maintenance(self):
        """Update selected maintenance record"""
        selected_rows = self.maint_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a maintenance record to update.")
            return
        
        row = selected_rows[0].row()
        if not hasattr(self, 'maintenance_data') or row >= len(self.maintenance_data):
            QMessageBox.warning(self, "Invalid Selection", "Selected maintenance record is invalid.")
            return
        
        original_data = self.maintenance_data[row]
        if "id" not in original_data:
            QMessageBox.warning(self, "No ID", "Selected maintenance record does not have an ID.")
            return
        
        # Read current values from table cells
        data = {
            "id": self.maint_table.item(row, 0).text() if self.maint_table.item(row, 0) else "",
            "job": self.maint_table.item(row, 1).text() if self.maint_table.item(row, 1) else "",
            "date_started": self.maint_table.item(row, 2).text() if self.maint_table.item(row, 2) else "",
            "date_completed": self.maint_table.item(row, 3).text() if self.maint_table.item(row, 3) else "",
        }
        
        # Add tracking value based on type (hours or mileage)
        tracking_value = self.maint_table.item(row, 4).text() if self.maint_table.item(row, 4) else ""
        if self.tracking_type == "Hours":
            data["hours"] = tracking_value
        else:
            data["mileage"] = tracking_value
        
        data["cost"] = self.maint_table.item(row, 5).text() if self.maint_table.item(row, 5) else ""
        data["notes"] = self.maint_table.item(row, 6).text() if self.maint_table.item(row, 6) else ""
        
        # Start update worker with id parameter
        vehicle_name = self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
        maintenance_id = data["id"]
        url = f"http://theconeportal.net:5000/fleet_control/vehicle_maintenance?vehicle_name={vehicle_name}&id={maintenance_id}"
        self.update_worker = UpdateWorker(url, data)
        self.update_worker.success.connect(self.on_update_success)
        self.update_worker.error.connect(self.on_update_error)
        self.update_worker.start()

    def update_purchase(self):
        """Update selected purchase record"""
        selected_rows = self.purch_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a purchase record to update.")
            return
        
        row = selected_rows[0].row()
        if not hasattr(self, 'purchases_data') or row >= len(self.purchases_data):
            QMessageBox.warning(self, "Invalid Selection", "Selected purchase record is invalid.")
            return
        
        original_data = self.purchases_data[row]
        if "id" not in original_data:
            QMessageBox.warning(self, "No ID", "Selected purchase record does not have an ID.")
            return
        
        # Read current values from table cells
        data = {
            "id": self.purch_table.item(row, 0).text() if self.purch_table.item(row, 0) else "",
            "item": self.purch_table.item(row, 1).text() if self.purch_table.item(row, 1) else "",
            "date_purchased": self.purch_table.item(row, 2).text() if self.purch_table.item(row, 2) else "",
            "installed": self.purch_table.item(row, 3).text() if self.purch_table.item(row, 3) else "",
            "cost": self.purch_table.item(row, 4).text() if self.purch_table.item(row, 4) else "",
            "store": self.purch_table.item(row, 5).text() if self.purch_table.item(row, 5) else ""
        }
        
        # Start update worker with id parameter
        vehicle_name = self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
        purchase_id = data["id"]
        url = f"http://theconeportal.net:5000/fleet_control/vehicle_purchases?vehicle_name={vehicle_name}&id={purchase_id}"
        self.update_worker = UpdateWorker(url, data)
        self.update_worker.success.connect(self.on_update_success)
        self.update_worker.error.connect(self.on_update_error)
        self.update_worker.start()

    def on_update_success(self):
        """Handle successful update"""
        QMessageBox.information(self, "Success", "Record updated successfully!")
        # Reload data
        self.load_maintenance()
        self.load_purchases()
        self.load_hidden_costs()

    def on_update_error(self, message: str):
        """Handle update error"""
        QMessageBox.critical(self, "Error", message)

    def refresh_data(self):
        """Refresh maintenance, purchases, and hidden costs data"""
        # Show loading indicators
        self.maint_table.setRowCount(1)
        self.maint_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        self.purch_table.setRowCount(1)
        self.purch_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        self.hidden_costs_table.setRowCount(1)
        self.hidden_costs_table.setItem(0, 0, QTableWidgetItem("Loading..."))
        
        # Reload data
        self.load_maintenance()
        self.load_purchases()
        self.load_hidden_costs()

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
        headers = ["ID", "Job", "Date Started", "Date Completed", tracking_header, "Cost", "Notes"]
        self.maint_table.setHorizontalHeaderLabels(headers)
        
        for row_idx, item in enumerate(items):
            # Accept dict-like inputs
            rec = item if isinstance(item, dict) else {}
            item_id = get_any(rec, ["id", "_id"])
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
            self.maint_table.setItem(row_idx, 0, QTableWidgetItem(str(item_id)))
            self.maint_table.setItem(row_idx, 1, QTableWidgetItem(str(job)))
            self.maint_table.setItem(row_idx, 2, QTableWidgetItem(str(date_started)))
            self.maint_table.setItem(row_idx, 3, QTableWidgetItem(str(date_completed)))
            self.maint_table.setItem(row_idx, 4, QTableWidgetItem(str(tracking_value)))
            self.maint_table.setItem(row_idx, 5, QTableWidgetItem(str(cost)))
            self.maint_table.setItem(row_idx, 6, QTableWidgetItem(str(notes)))

    def on_maintenance_error(self, message: str):
        # Indicate error in the table
        self.maint_table.setRowCount(1)
        self.maint_table.setItem(0, 0, QTableWidgetItem(f"Error: {message}"))

    def load_hidden_costs(self):
        params = {}
        if isinstance(self.vehicle, dict):
            if "name" in self.vehicle:
                params["vehicle_name"] = self.vehicle.get("name")
        else:
            params["vehicle_name"] = str(self.vehicle)

        url = "http://theconeportal.net:5000/fleet_control/vehicle_hidden_costs"
        self.hidden_costs_worker = HiddenCostsFetchWorker(url, params)
        self.hidden_costs_worker.finished.connect(self.on_hidden_costs_loaded)
        self.hidden_costs_worker.error.connect(self.on_hidden_costs_error)
        self.hidden_costs_worker.start()

    def on_hidden_costs_loaded(self, items: list):
        self.hidden_costs_table.setRowCount(0)
        if not items:
            self.hidden_costs_table.setRowCount(1)
            self.hidden_costs_table.setItem(0, 0, QTableWidgetItem("No hidden costs"))
            return

        def get_any(d, keys, default=""):
            for k in keys:
                if k in d and d[k] is not None:
                    return d[k]
            return default

        # Store hidden costs data for operations
        self.hidden_costs_data = items
        
        for row_idx, item in enumerate(items):
            rec = item if isinstance(item, dict) else {}
            item_id = get_any(rec, ["id", "_id"])
            name = get_any(rec, ["name", "title", "item_name"])
            amount = get_any(rec, ["amount", "cost", "price"])
            description = get_any(rec, ["description", "desc", "details"])
            date = get_any(rec, ["date", "date_incurred", "created_date"])

            self.hidden_costs_table.insertRow(row_idx)
            self.hidden_costs_table.setItem(row_idx, 0, QTableWidgetItem(str(item_id)))
            self.hidden_costs_table.setItem(row_idx, 1, QTableWidgetItem(str(name)))
            self.hidden_costs_table.setItem(row_idx, 2, QTableWidgetItem(str(amount)))
            self.hidden_costs_table.setItem(row_idx, 3, QTableWidgetItem(str(description)))
            self.hidden_costs_table.setItem(row_idx, 4, QTableWidgetItem(str(date)))

    def on_hidden_costs_error(self, message: str):
        self.hidden_costs_table.setRowCount(1)
        self.hidden_costs_table.setItem(0, 0, QTableWidgetItem(f"Error: {message}"))

    def on_hidden_cost_selection_changed(self):
        """Handle hidden costs table selection changes"""
        selected_rows = self.hidden_costs_table.selectionModel().selectedRows()
        if selected_rows and hasattr(self, 'hidden_costs_data'):
            row = selected_rows[0].row()
            if 0 <= row < len(self.hidden_costs_data):
                self.selected_hidden_cost = self.hidden_costs_data[row]
            else:
                self.selected_hidden_cost = None
        else:
            self.selected_hidden_cost = None

    def add_hidden_cost(self):
        """Show add hidden cost form"""
        if self.on_add_hidden_cost:
            self.on_add_hidden_cost()

    def update_hidden_cost(self):
        """Update selected hidden cost record"""
        selected_rows = self.hidden_costs_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a hidden cost record to update.")
            return
        
        row = selected_rows[0].row()
        if not hasattr(self, 'hidden_costs_data') or row >= len(self.hidden_costs_data):
            QMessageBox.warning(self, "Invalid Selection", "Selected hidden cost record is invalid.")
            return
        
        original_data = self.hidden_costs_data[row]
        if "id" not in original_data:
            QMessageBox.warning(self, "No ID", "Selected hidden cost record does not have an ID.")
            return
        
        # Read current values from table cells
        data = {
            "id": self.hidden_costs_table.item(row, 0).text() if self.hidden_costs_table.item(row, 0) else "",
            "name": self.hidden_costs_table.item(row, 1).text() if self.hidden_costs_table.item(row, 1) else "",
            "amount": self.hidden_costs_table.item(row, 2).text() if self.hidden_costs_table.item(row, 2) else "",
            "description": self.hidden_costs_table.item(row, 3).text() if self.hidden_costs_table.item(row, 3) else "",
            "date": self.hidden_costs_table.item(row, 4).text() if self.hidden_costs_table.item(row, 4) else ""
        }
        
        # Start update worker with id parameter
        vehicle_name = self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
        hidden_cost_id = data["id"]
        url = f"http://theconeportal.net:5000/fleet_control/vehicle_hidden_costs?vehicle_name={vehicle_name}&id={hidden_cost_id}"
        self.update_worker = UpdateWorker(url, data)
        self.update_worker.success.connect(self.on_update_success)
        self.update_worker.error.connect(self.on_update_error)
        self.update_worker.start()

    def delete_hidden_cost(self):
        """Delete selected hidden cost record"""
        if not self.selected_hidden_cost:
            QMessageBox.warning(self, "No Selection", "Please select a hidden cost record to delete.")
            return
        
        # Check if hidden cost record has an id
        if "id" not in self.selected_hidden_cost:
            QMessageBox.warning(self, "No ID", "Selected hidden cost record does not have an ID.")
            return
        
        dialog = DeleteConfirmDialog("hidden cost", self.selected_hidden_cost, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Prepare delete data
            data = dict(self.selected_hidden_cost)
            
            # Start delete worker with id parameter
            vehicle_name = self.vehicle["name"].replace(" ", "_").replace(".", "_").lower()
            hidden_cost_id = self.selected_hidden_cost["id"]
            url = f"http://theconeportal.net:5000/fleet_control/vehicle_hidden_costs?vehicle_name={vehicle_name}&id={hidden_cost_id}"
            self.delete_worker = DeleteWorker(url, data)
            self.delete_worker.success.connect(self.on_delete_success)
            self.delete_worker.error.connect(self.on_delete_error)
            self.delete_worker.start()
