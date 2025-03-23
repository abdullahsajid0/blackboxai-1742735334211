import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QStackedWidget, QPushButton, QLabel, 
                            QLineEdit, QComboBox, QSpinBox, QTableWidget, 
                            QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
                            QDoubleSpinBox, QTextEdit, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont
import sqlite3
from datetime import datetime, timedelta
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sales Management System")
        self.setMinimumSize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create sidebar
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                padding: 10px;
                text-align: left;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Create navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Cash Sale", "cash_sale"),
            ("Installment Sale", "installment_sale"),
            ("Inventory", "inventory"),
            ("Customers", "customers"),
            ("Installments", "installments"),
            ("Reports", "reports"),
            ("Settings", "settings")
        ]
        
        for text, page in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("page", page)
            btn.clicked.connect(self.navigate)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        sidebar_layout.addStretch()
        
        # Create stacked widget for different pages
        self.stack = QStackedWidget()
        
        # Create pages
        self.pages = {
            "dashboard": DashboardPage(),
            "cash_sale": CashSalePage(),
            "installment_sale": InstallmentSalePage(),
            "inventory": InventoryPage(),
            "customers": CustomersPage(),
            "installments": InstallmentsPage(),
            "reports": ReportsPage(),
            "settings": SettingsPage()
        }
        
        # Add pages to stack
        for page in self.pages.values():
            self.stack.addWidget(page)
        
        # Add sidebar and stack to main layout
        layout.addWidget(sidebar)
        layout.addWidget(self.stack)
        
        # Set initial page
        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentWidget(self.pages["dashboard"])

    def navigate(self):
        # Uncheck all buttons except the clicked one
        for btn in self.nav_buttons:
            if btn != self.sender():
                btn.setChecked(False)
        
        # Get page name and switch to it
        page = self.sender().property("page")
        self.stack.setCurrentWidget(self.pages[page])
        
        # Refresh page data
        self.pages[page].refresh_data()

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        # Total Sales Card
        sales_card = QWidget()
        sales_card.setStyleSheet("""
            QWidget {
                background-color: #3498db;
                border-radius: 10px;
                color: white;
            }
        """)
        sales_layout = QVBoxLayout(sales_card)
        self.total_sales_label = QLabel("Total Sales")
        self.total_sales_amount = QLabel("Rs. 0")
        self.total_sales_amount.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        sales_layout.addWidget(self.total_sales_label)
        sales_layout.addWidget(self.total_sales_amount)
        
        # Active Installments Card
        installments_card = QWidget()
        installments_card.setStyleSheet("""
            QWidget {
                background-color: #2ecc71;
                border-radius: 10px;
                color: white;
            }
        """)
        installments_layout = QVBoxLayout(installments_card)
        self.active_installments_label = QLabel("Active Installments")
        self.active_installments_count = QLabel("0")
        self.active_installments_count.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        installments_layout.addWidget(self.active_installments_label)
        installments_layout.addWidget(self.active_installments_count)
        
        # Low Stock Card
        stock_card = QWidget()
        stock_card.setStyleSheet("""
            QWidget {
                background-color: #e74c3c;
                border-radius: 10px;
                color: white;
            }
        """)
        stock_layout = QVBoxLayout(stock_card)
        self.low_stock_label = QLabel("Low Stock Items")
        self.low_stock_count = QLabel("0")
        self.low_stock_count.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        stock_layout.addWidget(self.low_stock_label)
        stock_layout.addWidget(self.low_stock_count)
        
        # Add cards to stats layout
        stats_layout.addWidget(sales_card)
        stats_layout.addWidget(installments_card)
        stats_layout.addWidget(stock_card)
        
        # Recent Sales Table
        sales_table = QTableWidget()
        sales_table.setColumnCount(5)
        sales_table.setHorizontalHeaderLabels(["Date", "Customer", "Product", "Amount", "Type"])
        
        # Due Installments Table
        installments_table = QTableWidget()
        installments_table.setColumnCount(5)
        installments_table.setHorizontalHeaderLabels(["Due Date", "Customer", "Product", "Amount", "Status"])
        
        # Add all widgets to main layout
        layout.addLayout(stats_layout)
        layout.addWidget(QLabel("Recent Sales"))
        layout.addWidget(sales_table)
        layout.addWidget(QLabel("Upcoming Installments"))
        layout.addWidget(installments_table)
    
    def refresh_data(self):
        # Update dashboard data from database
        pass

class CashSalePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Customer Details Section
        customer_group = QWidget()
        customer_layout = QFormLayout(customer_group)
        
        self.customer_name = QLineEdit()
        self.customer_phone = QLineEdit()
        self.customer_address = QTextEdit()
        
        customer_layout.addRow("Customer Name:", self.customer_name)
        customer_layout.addRow("Phone Number:", self.customer_phone)
        customer_layout.addRow("Address:", self.customer_address)
        
        # Product Selection Section
        product_group = QWidget()
        product_layout = QFormLayout(product_group)
        
        self.product_combo = QComboBox()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.price_label = QLabel("Rs. 0")
        
        product_layout.addRow("Select Product:", self.product_combo)
        product_layout.addRow("Quantity:", self.quantity_spin)
        product_layout.addRow("Price:", self.price_label)
        
        # Add sections to main layout
        layout.addWidget(QLabel("Customer Details"))
        layout.addWidget(customer_group)
        layout.addWidget(QLabel("Product Details"))
        layout.addWidget(product_group)
        
        # Complete Sale Button
        complete_btn = QPushButton("Complete Sale")
        complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        complete_btn.clicked.connect(self.complete_sale)
        
        layout.addStretch()
        layout.addWidget(complete_btn)
    
    def complete_sale(self):
        # Handle sale completion
        pass
    
    def refresh_data(self):
        # Refresh product list
        pass

class InstallmentSalePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Customer Details Section
        customer_group = QWidget()
        customer_layout = QFormLayout(customer_group)
        
        self.customer_name = QLineEdit()
        self.customer_phone = QLineEdit()
        self.customer_cnic = QLineEdit()
        self.customer_address = QTextEdit()
        
        customer_layout.addRow("Customer Name:", self.customer_name)
        customer_layout.addRow("Phone Number:", self.customer_phone)
        customer_layout.addRow("CNIC:", self.customer_cnic)
        customer_layout.addRow("Address:", self.customer_address)
        
        # Witness Details Section
        witness_group = QWidget()
        witness_layout = QFormLayout(witness_group)
        
        self.witness_name = QLineEdit()
        self.witness_cnic = QLineEdit()
        self.witness_address = QTextEdit()
        
        witness_layout.addRow("Witness Name:", self.witness_name)
        witness_layout.addRow("Witness CNIC:", self.witness_cnic)
        witness_layout.addRow("Witness Address:", self.witness_address)
        
        # Product and Installment Details
        details_group = QWidget()
        details_layout = QFormLayout(details_group)
        
        self.product_combo = QComboBox()
        self.markup_spin = QDoubleSpinBox()
        self.markup_spin.setSuffix("%")
        self.markup_spin.setMaximum(100)
        
        self.months_spin = QSpinBox()
        self.months_spin.setMinimum(1)
        self.months_spin.setMaximum(36)
        
        self.advance_amount = QDoubleSpinBox()
        self.advance_amount.setMaximum(1000000)
        self.advance_amount.setPrefix("Rs. ")
        
        details_layout.addRow("Select Product:", self.product_combo)
        details_layout.addRow("Markup Percentage:", self.markup_spin)
        details_layout.addRow("Number of Months:", self.months_spin)
        details_layout.addRow("Advance Amount:", self.advance_amount)
        
        # Preview Button
        preview_btn = QPushButton("Preview Installment Plan")
        preview_btn.clicked.connect(self.preview_plan)
        
        # Complete Sale Button
        complete_btn = QPushButton("Complete Sale")
        complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        complete_btn.clicked.connect(self.complete_sale)
        
        # Add all sections to main layout
        layout.addWidget(QLabel("Customer Details"))
        layout.addWidget(customer_group)
        layout.addWidget(QLabel("Witness Details"))
        layout.addWidget(witness_group)
        layout.addWidget(QLabel("Product and Installment Details"))
        layout.addWidget(details_group)
        layout.addWidget(preview_btn)
        layout.addStretch()
        layout.addWidget(complete_btn)
    
    def preview_plan(self):
        # Show installment plan preview
        pass
    
    def complete_sale(self):
        # Handle installment sale completion
        pass
    
    def refresh_data(self):
        # Refresh product list
        pass

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search products...")
        
        # Add Product Button
        add_btn = QPushButton("Add Product")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_btn.clicked.connect(self.add_product)
        
        toolbar.addWidget(self.search_box)
        toolbar.addWidget(add_btn)
        
        # Products Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Product Name", "Brand", "Category", "Price",
            "Stock", "Status", "Actions"
        ])
        
        # Add widgets to layout
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
    
    def add_product(self):
        # Show add product dialog
        pass
    
    def refresh_data(self):
        # Refresh inventory table
        pass

class CustomersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search customers...")
        
        # Customers Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Phone", "CNIC", "Address",
            "Total Purchases", "Actions"
        ])
        
        # Add widgets to layout
        layout.addWidget(self.search_box)
        layout.addWidget(self.table)
    
    def refresh_data(self):
        # Refresh customers table
        pass

class InstallmentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Filters
        filters = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by customer or product...")
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Overdue", "Paid"])
        
        filters.addWidget(self.search_box)
        filters.addWidget(self.status_combo)
        
        # Installments Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Due Date", "Customer", "Product", "Installment",
            "Amount", "Remaining", "Status", "Actions"
        ])
        
        # Add widgets to layout
        layout.addLayout(filters)
        layout.addWidget(self.table)
    
    def refresh_data(self):
        # Refresh installments table
        pass

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Report Types
        report_types = QHBoxLayout()
        
        sales_report_btn = QPushButton("Sales Report")
        inventory_report_btn = QPushButton("Inventory Report")
        customer_report_btn = QPushButton("Customer Report")
        
        report_types.addWidget(sales_report_btn)
        report_types.addWidget(inventory_report_btn)
        report_types.addWidget(customer_report_btn)
        
        # Date Range
        date_range = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        
        date_range.addWidget(QLabel("From:"))
        date_range.addWidget(self.start_date)
        date_range.addWidget(QLabel("To:"))
        date_range.addWidget(self.end_date)
        
        # Report Content Area
        self.report_area = QWidget()
        
        # Add widgets to layout
        layout.addLayout(report_types)
        layout.addLayout(date_range)
        layout.addWidget(self.report_area)
    
    def refresh_data(self):
        # Refresh current report
        pass

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Business Information
        business_group = QWidget()
        business_layout = QFormLayout(business_group)
        
        self.business_name = QLineEdit()
        self.business_address = QTextEdit()
        self.business_phone = QLineEdit()
        
        business_layout.addRow("Business Name:", self.business_name)
        business_layout.addRow("Address:", self.business_address)
        business_layout.addRow("Phone:", self.business_phone)
        
        # Backup Settings
        backup_group = QWidget()
        backup_layout = QVBoxLayout(backup_group)
        
        backup_btn = QPushButton("Backup Database")
        restore_btn = QPushButton("Restore Database")
        
        backup_layout.addWidget(backup_btn)
        backup_layout.addWidget(restore_btn)
        
        # Add groups to main layout
        layout.addWidget(QLabel("Business Information"))
        layout.addWidget(business_group)
        layout.addWidget(QLabel("Database Backup"))
        layout.addWidget(backup_group)
        layout.addStretch()
    
    def refresh_data(self):
        # Load current settings
        pass

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()