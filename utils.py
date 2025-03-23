from datetime import datetime, timedelta
import json
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QDate
import sqlite3

def format_currency(amount):
    """Format amount in Pakistani Rupees"""
    return f"Rs. {amount:,.2f}"

def calculate_installments(total_amount, advance_payment, number_of_installments, markup_percentage):
    """Calculate installment plan details"""
    markup_amount = (total_amount * markup_percentage) / 100
    total_with_markup = total_amount + markup_amount
    remaining_amount = total_with_markup - advance_payment
    installment_amount = round(remaining_amount / number_of_installments, 2)

    installments = []
    remaining_balance = remaining_amount
    today = datetime.now()

    # First installment is the advance payment
    installments.append({
        'number': 1,
        'due_date': today.date(),
        'amount': advance_payment,
        'status': 'Paid',
        'remaining_balance': remaining_balance
    })

    # Calculate remaining installments
    for i in range(number_of_installments):
        due_date = today + timedelta(days=(i + 1) * 30)  # Monthly installments
        remaining_balance -= installment_amount
        if remaining_balance < 0:
            remaining_balance = 0

        installments.append({
            'number': i + 2,  # +2 because first installment is advance
            'due_date': due_date.date(),
            'amount': installment_amount,
            'status': 'Pending',
            'remaining_balance': remaining_balance
        })

    return {
        'total_with_markup': total_with_markup,
        'markup_amount': markup_amount,
        'installment_amount': installment_amount,
        'installments': installments
    }

def show_error_message(parent, message, title="Error"):
    """Show error message dialog"""
    QMessageBox.critical(parent, title, message)

def show_success_message(parent, message, title="Success"):
    """Show success message dialog"""
    QMessageBox.information(parent, title, message)

def show_confirmation_dialog(parent, message, title="Confirm"):
    """Show confirmation dialog"""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes

def validate_required_fields(data, required_fields):
    """Validate required fields in a dictionary"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            missing_fields.append(field.replace('_', ' ').title())
    return missing_fields

def format_date(date):
    """Format date for display"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    return date.strftime('%d %b, %Y')

def qdate_to_python(qdate):
    """Convert QDate to Python date"""
    return datetime(qdate.year(), qdate.month(), qdate.day()).date()

def python_to_qdate(date):
    """Convert Python date to QDate"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    return QDate(date.year, date.month, date.day)

def backup_database(db_path, backup_path):
    """Create a backup of the database"""
    try:
        # Connect to source database
        source = sqlite3.connect(db_path)
        # Connect to backup database
        backup = sqlite3.connect(backup_path)
        
        # Copy data
        source.backup(backup)
        
        # Close connections
        source.close()
        backup.close()
        
        return True, "Backup created successfully"
    except Exception as e:
        return False, f"Backup failed: {str(e)}"

def restore_database(backup_path, db_path):
    """Restore database from backup"""
    try:
        # Connect to backup database
        backup = sqlite3.connect(backup_path)
        # Connect to target database
        target = sqlite3.connect(db_path)
        
        # Copy data
        backup.backup(target)
        
        # Close connections
        backup.close()
        target.close()
        
        return True, "Database restored successfully"
    except Exception as e:
        return False, f"Restore failed: {str(e)}"

def generate_receipt_html(sale_data, business_info):
    """Generate HTML receipt for printing"""
    receipt_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 20px;
            }
            .business-info {
                text-align: center;
                margin-bottom: 30px;
            }
            .receipt-details {
                margin-bottom: 20px;
            }
            .receipt-details table {
                width: 100%;
                border-collapse: collapse;
            }
            .receipt-details td {
                padding: 5px;
            }
            .installment-schedule {
                margin-top: 20px;
            }
            .installment-schedule table {
                width: 100%;
                border-collapse: collapse;
            }
            .installment-schedule th, .installment-schedule td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .footer {
                margin-top: 30px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Sales Receipt</h2>
        </div>
        
        <div class="business-info">
            <h3>{business_name}</h3>
            <p>{business_address}</p>
            <p>Phone: {business_phone}</p>
        </div>
        
        <div class="receipt-details">
            <table>
                <tr>
                    <td><strong>Receipt No:</strong></td>
                    <td>{receipt_no}</td>
                    <td><strong>Date:</strong></td>
                    <td>{date}</td>
                </tr>
                <tr>
                    <td><strong>Customer Name:</strong></td>
                    <td>{customer_name}</td>
                    <td><strong>Contact:</strong></td>
                    <td>{customer_contact}</td>
                </tr>
                <tr>
                    <td><strong>Product:</strong></td>
                    <td colspan="3">{product_name}</td>
                </tr>
                <tr>
                    <td><strong>Sale Type:</strong></td>
                    <td>{sale_type}</td>
                    <td><strong>Amount:</strong></td>
                    <td>{amount}</td>
                </tr>
            </table>
        </div>
        
        {installment_section}
        
        <div class="footer">
            <p>Thank you for your business!</p>
        </div>
    </body>
    </html>
    """
    
    # Format installment section if applicable
    installment_section = ""
    if sale_data['sale_type'] == 'installment':
        installment_rows = ""
        for inst in sale_data['installments']:
            installment_rows += f"""
                <tr>
                    <td>{inst['number']}</td>
                    <td>{format_date(inst['due_date'])}</td>
                    <td>{format_currency(inst['amount'])}</td>
                    <td>{format_currency(inst['remaining_balance'])}</td>
                    <td>{inst['status']}</td>
                </tr>
            """
        
        installment_section = f"""
            <div class="installment-schedule">
                <h3>Installment Schedule</h3>
                <table>
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Due Date</th>
                            <th>Amount</th>
                            <th>Remaining</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {installment_rows}
                    </tbody>
                </table>
            </div>
        """
    
    # Format the receipt
    return receipt_template.format(
        business_name=business_info['business_name'],
        business_address=business_info['business_address'],
        business_phone=business_info['business_phone'],
        receipt_no=sale_data['id'],
        date=format_date(sale_data['created_at']),
        customer_name=sale_data['customer_name'],
        customer_contact=sale_data['customer_contact'],
        product_name=sale_data['product_name'],
        sale_type=sale_data['sale_type'].title(),
        amount=format_currency(sale_data['amount']),
        installment_section=installment_section
    )

def generate_report_html(report_data, report_type, date_range):
    """Generate HTML report for printing"""
    # Implementation of report generation based on report type
    pass