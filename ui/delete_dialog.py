"""Delete confirmation dialog for Fleet Control GUI"""

try:
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

import requests


class DeleteWorker(QThread):
    """Worker thread to delete items via API"""
    
    success = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url: str, data: dict):
        super().__init__()
        self.url = url
        self.data = data

    def run(self):
        try:
            print(self.data)
            resp = requests.delete(self.url, json=self.data, timeout=15)
            resp.raise_for_status()
            self.success.emit()
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Failed to delete: {e}")
        except Exception as e:
            self.error.emit(f"Error: {e}")


class DeleteConfirmDialog(QDialog):
    """Confirmation dialog for deleting items"""

    def __init__(self, item_type, item_info, parent=None):
        super().__init__(parent)
        self.item_type = item_type  # "maintenance" or "purchase"
        self.item_info = item_info
        self.setWindowTitle(f"Delete {item_type.title()}")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Confirmation message
        message = QLabel(f"Are you sure you want to delete this {self.item_type}?")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)
        
        # Item details
        if self.item_type == "maintenance":
            details = f"Job: {self.item_info.get('job', 'Unknown')}"
        else:  # purchase
            details = f"Item: {self.item_info.get('item', 'Unknown')}"
        
        details_label = QLabel(details)
        details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        details_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(details_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: #ff4444; color: white;")
        
        cancel_btn.clicked.connect(self.reject)
        delete_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)