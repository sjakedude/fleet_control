"""Reports screen for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QGridLayout, QScrollArea, QFrame,
                                QTableWidget, QTableWidgetItem, QMessageBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QGridLayout, QScrollArea, QFrame,
                                QTableWidget, QTableWidgetItem, QMessageBox)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests
from collections import defaultdict, Counter


class ReportsDataWorker(QThread):
    """Worker thread to fetch all data for reports"""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # Fetch all vehicles first
            vehicles_resp = requests.get("http://theconeportal.net:5000/fleet_control/vehicle_list", timeout=15)
            vehicles_resp.raise_for_status()
            vehicles = vehicles_resp.json()
            
            all_maintenance = []
            all_purchases = []
            all_hidden_costs = []
            
            # Fetch data for each vehicle
            for vehicle in vehicles:
                vehicle_name = vehicle.get("name", str(vehicle)) if isinstance(vehicle, dict) else str(vehicle)
                normalized_name = vehicle_name.replace(" ", "_").replace(".", "_").lower()
                
                # Fetch maintenance records
                try:
                    maint_url = f"http://theconeportal.net:5000/fleet_control/vehicle_maintenance?vehicle_name={normalized_name}"
                    maint_resp = requests.get(maint_url, timeout=15)
                    maint_resp.raise_for_status()
                    maint_data = maint_resp.json()
                    if not isinstance(maint_data, list):
                        maint_data = [maint_data] if maint_data else []
                    # Add vehicle name to each record
                    for record in maint_data:
                        if isinstance(record, dict):
                            record['vehicle_name'] = vehicle_name
                    all_maintenance.extend(maint_data)
                except:
                    pass  # Skip if no maintenance data
                
                # Fetch purchase records
                try:
                    purch_url = f"http://theconeportal.net:5000/fleet_control/vehicle_purchases"
                    purch_resp = requests.get(purch_url, params={"vehicle_name": vehicle_name}, timeout=15)
                    purch_resp.raise_for_status()
                    purch_data = purch_resp.json()
                    if not isinstance(purch_data, list):
                        purch_data = [purch_data] if purch_data else []
                    # Add vehicle name to each record
                    for record in purch_data:
                        if isinstance(record, dict):
                            record['vehicle_name'] = vehicle_name
                    all_purchases.extend(purch_data)
                except:
                    pass  # Skip if no purchase data
                
                # Fetch hidden costs records
                try:
                    hidden_url = f"http://theconeportal.net:5000/fleet_control/vehicle_hidden_costs"
                    hidden_resp = requests.get(hidden_url, params={"vehicle_name": vehicle_name}, timeout=15)
                    hidden_resp.raise_for_status()
                    hidden_data = hidden_resp.json()
                    if not isinstance(hidden_data, list):
                        hidden_data = [hidden_data] if hidden_data else []
                    # Add vehicle name to each record
                    for record in hidden_data:
                        if isinstance(record, dict):
                            record['vehicle_name'] = vehicle_name
                    all_hidden_costs.extend(hidden_data)
                    print(f"Fetched {len(hidden_data)} hidden costs for {vehicle_name}")  # Debug
                except Exception as e:
                    print(f"Error fetching hidden costs for {vehicle_name}: {e}")  # Debug
                    pass  # Skip if no hidden costs data
            
            # Return all collected data
            print(f"Total data collected:")  # Debug
            print(f"  Vehicles: {len(vehicles)}")  # Debug
            print(f"  Maintenance: {len(all_maintenance)}")  # Debug
            print(f"  Purchases: {len(all_purchases)}")  # Debug
            print(f"  Hidden costs: {len(all_hidden_costs)}")  # Debug
            self.finished.emit({
                'vehicles': vehicles,
                'maintenance': all_maintenance,
                'purchases': all_purchases,
                'hidden_costs': all_hidden_costs
            })
            
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Failed to fetch reports data: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")


class MetricCard(QFrame):
    """A card widget to display a metric"""
    
    def __init__(self, title, value, subtitle=""):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
                background-color: rgba(255, 255, 255, 10);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #666;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Subtitle (optional)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("font-size: 10px; color: #888;")
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle_label)
        
        self.setLayout(layout)


class ReportsScreen(QWidget):
    """Reports screen showing fleet metrics and statistics"""

    def __init__(self, on_back=None):
        """
        Initialize the reports screen
        
        Args:
            on_back: Callback function to go back to main menu
        """
        super().__init__()
        self.on_back = on_back
        self.data_worker = None
        self.reports_data = None
        self.init_ui()
        self.load_reports_data()

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header with back button and title
        header_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(80)
        if self.on_back:
            back_btn.clicked.connect(self.on_back)
        header_layout.addWidget(back_btn)
        header_layout.addSpacing(10)
        
        title = QLabel("Fleet Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self.load_reports_data)
        header_layout.addWidget(refresh_btn)
        main_layout.addLayout(header_layout)

        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        
        # Loading message
        self.loading_label = QLabel("Loading reports data...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 16px; color: #666;")
        self.content_layout.addWidget(self.loading_label)
        
        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)

    def load_reports_data(self):
        """Load all reports data from API"""
        # Clear existing content and show loading
        self.clear_content()
        self.loading_label.setText("Loading reports data...")
        self.loading_label.show()
        
        # Start worker to fetch data
        self.data_worker = ReportsDataWorker()
        self.data_worker.finished.connect(self.on_data_loaded)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()

    def clear_content(self):
        """Clear all content widgets except loading label"""
        # Remove all widgets except loading label
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.loading_label:
                item.widget().setParent(None)

    def on_data_loaded(self, data):
        """Handle loaded reports data"""
        self.reports_data = data
        self.loading_label.hide()
        
        # Create reports sections
        self.create_metrics_section()
        self.create_top_vehicles_section()
        
        self.content_layout.addStretch()

    def on_data_error(self, error_message):
        """Handle data loading error"""
        self.loading_label.setText(f"Error loading data: {error_message}")
        QMessageBox.critical(self, "Error", error_message)

    def create_metrics_section(self):
        """Create the main metrics cards section"""
        if not self.reports_data:
            return
            
        # Section title
        metrics_title = QLabel("Fleet Overview")
        metrics_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.content_layout.addWidget(metrics_title)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        
        # Calculate metrics
        total_maintenance_jobs = len([m for m in self.reports_data['maintenance'] if isinstance(m, dict)])
        total_purchases = len([p for p in self.reports_data['purchases'] if isinstance(p, dict)])
        total_hidden_costs = len([h for h in self.reports_data['hidden_costs'] if isinstance(h, dict)])
        
        # Calculate total money from purchases and hidden costs
        total_purchase_amount = 0
        for purchase in self.reports_data['purchases']:
            if isinstance(purchase, dict):
                cost_str = str(purchase.get('cost', '0'))
                try:
                    # Handle "FREE" entries
                    if cost_str.upper() == 'FREE':
                        continue
                    # Remove any currency symbols and convert
                    cost_str = cost_str.replace('$', '').replace(',', '').strip()
                    if cost_str:
                        total_purchase_amount += float(cost_str)
                except (ValueError, AttributeError):
                    continue
        
        total_hidden_costs_amount = 0
        print(f"Processing {len(self.reports_data['hidden_costs'])} hidden cost records")  # Debug
        for hidden_cost in self.reports_data['hidden_costs']:
            if isinstance(hidden_cost, dict):
                # Use the same field matching as vehicle details screen
                def get_any(d, keys, default=""):
                    for k in keys:
                        if k in d and d[k] is not None:
                            return d[k]
                    return default
                
                amount_str = str(get_any(hidden_cost, ["amount", "cost", "price"], '0'))
                print(f"Hidden cost record: {hidden_cost}")  # Debug
                print(f"Amount string: '{amount_str}'")  # Debug
                try:
                    # Remove any currency symbols and convert
                    amount_str = amount_str.replace('$', '').replace(',', '').strip()
                    if amount_str and amount_str != '0':
                        amount_val = float(amount_str)
                        total_hidden_costs_amount += amount_val
                        print(f"Added {amount_val} to total, new total: {total_hidden_costs_amount}")  # Debug
                except (ValueError, AttributeError) as e:
                    print(f"Error parsing amount '{amount_str}': {e}")  # Debug
                    continue
        print(f"Final hidden costs total: {total_hidden_costs_amount}")  # Debug
        
        total_money = total_purchase_amount + total_hidden_costs_amount
        
        # Create metric cards - arranged in 2 rows of 3 columns
        metrics = [
            ("Total Maintenance Jobs", total_maintenance_jobs, ""),
            ("Total Vehicle Purchases", total_purchases, ""),
            ("Total Hidden Costs", total_hidden_costs, ""),
            ("Total Money Spent", f"${total_money:,.2f}", "Purchases + Hidden Costs"),
            ("Total Purchase Amount", f"${total_purchase_amount:,.2f}", ""),
            ("Total Hidden Cost", f"${total_hidden_costs_amount:,.2f}", "")
        ]
        
        # Arrange cards in grid (3 columns, 2 rows)
        for i, (title, value, subtitle) in enumerate(metrics):
            card = MetricCard(title, value, subtitle)
            row = i // 3
            col = i % 3
            metrics_layout.addWidget(card, row, col)
        
        # Add metrics layout to content
        metrics_widget = QWidget()
        metrics_widget.setLayout(metrics_layout)
        self.content_layout.addWidget(metrics_widget)

    def create_top_vehicles_section(self):
        """Create section showing top vehicles by maintenance and purchases"""
        if not self.reports_data:
            return
            
        # Section title
        top_title = QLabel("Top Vehicles")
        top_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px 0 10px 0;")
        self.content_layout.addWidget(top_title)
        
        # Create horizontal layout for tables
        tables_layout = QHBoxLayout()
        
        # Top vehicles by maintenance count
        self.create_maintenance_leaders_table(tables_layout)
        
        # Top vehicles by purchase count
        self.create_purchase_leaders_table(tables_layout)
        
        # Add tables layout to content
        tables_widget = QWidget()
        tables_widget.setLayout(tables_layout)
        self.content_layout.addWidget(tables_widget)

    def create_maintenance_leaders_table(self, parent_layout):
        """Create table showing vehicles with most maintenance jobs"""
        # Count maintenance jobs per vehicle
        maintenance_counts = Counter()
        for maintenance in self.reports_data['maintenance']:
            if isinstance(maintenance, dict):
                vehicle_name = maintenance.get('vehicle_name', 'Unknown')
                maintenance_counts[vehicle_name] += 1
        
        # Create table
        maint_table = QTableWidget()
        maint_table.setColumnCount(2)
        maint_table.setHorizontalHeaderLabels(["Vehicle", "Maintenance Jobs"])
        maint_table.verticalHeader().setVisible(False)
        maint_table.setAlternatingRowColors(True)
        maint_table.setSortingEnabled(True)
        
        # Get top 10 vehicles
        top_maintenance = maintenance_counts.most_common(10)
        maint_table.setRowCount(len(top_maintenance))
        
        for row, (vehicle, count) in enumerate(top_maintenance):
            maint_table.setItem(row, 0, QTableWidgetItem(vehicle))
            maint_table.setItem(row, 1, QTableWidgetItem(str(count)))
        
        # Resize columns to content
        maint_table.resizeColumnsToContents()
        maint_table.setMaximumHeight(300)
        
        # Add label and table
        maint_section = QVBoxLayout()
        maint_label = QLabel("Most Maintenance Jobs")
        maint_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        maint_section.addWidget(maint_label)
        maint_section.addWidget(maint_table)
        
        maint_widget = QWidget()
        maint_widget.setLayout(maint_section)
        parent_layout.addWidget(maint_widget)

    def create_purchase_leaders_table(self, parent_layout):
        """Create table showing vehicles with most purchases"""
        # Count purchases per vehicle
        purchase_counts = Counter()
        for purchase in self.reports_data['purchases']:
            if isinstance(purchase, dict):
                vehicle_name = purchase.get('vehicle_name', 'Unknown')
                purchase_counts[vehicle_name] += 1
        
        # Create table
        purch_table = QTableWidget()
        purch_table.setColumnCount(2)
        purch_table.setHorizontalHeaderLabels(["Vehicle", "Purchases"])
        purch_table.verticalHeader().setVisible(False)
        purch_table.setAlternatingRowColors(True)
        purch_table.setSortingEnabled(True)
        
        # Get top 10 vehicles
        top_purchases = purchase_counts.most_common(10)
        purch_table.setRowCount(len(top_purchases))
        
        for row, (vehicle, count) in enumerate(top_purchases):
            purch_table.setItem(row, 0, QTableWidgetItem(vehicle))
            purch_table.setItem(row, 1, QTableWidgetItem(str(count)))
        
        # Resize columns to content
        purch_table.resizeColumnsToContents()
        purch_table.setMaximumHeight(300)
        
        # Add label and table
        purch_section = QVBoxLayout()
        purch_label = QLabel("Most Purchases")
        purch_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        purch_section.addWidget(purch_label)
        purch_section.addWidget(purch_table)
        
        purch_widget = QWidget()
        purch_widget.setLayout(purch_section)
        parent_layout.addWidget(purch_widget)