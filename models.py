import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_file="sales_management.db"):
        self.db_file = db_file
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()

        # Create Products table
        c.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                description TEXT,
                features TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Customers table
        c.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                cnic TEXT,
                address TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Sales table
        c.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                sale_type TEXT NOT NULL,
                amount REAL NOT NULL,
                markup_percentage REAL,
                total_with_markup REAL,
                advance_payment REAL,
                installment_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Create Witnesses table for installment sales
        c.execute('''
            CREATE TABLE IF NOT EXISTS witnesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                cnic TEXT NOT NULL,
                address TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales (id)
            )
        ''')

        # Create Installments table
        c.execute('''
            CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                installment_number INTEGER NOT NULL,
                amount REAL NOT NULL,
                due_date DATE NOT NULL,
                status TEXT DEFAULT 'Pending',
                paid_date DATE,
                remaining_balance REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales (id)
            )
        ''')

        # Create Settings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT,
                business_address TEXT,
                business_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

class ProductModel:
    def __init__(self, db):
        self.db = db

    def add_product(self, data):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO products (
                    name, brand, model, category, price, stock,
                    description, features, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'], data['brand'], data['model'],
                data['category'], data['price'], data['stock'],
                data['description'],
                json.dumps(data['features']),
                json.dumps(data['tags'])
            ))
            product_id = c.lastrowid
            conn.commit()
            return product_id
        finally:
            conn.close()

    def update_product(self, product_id, data):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                UPDATE products SET
                    name = ?, brand = ?, model = ?, category = ?,
                    price = ?, stock = ?, description = ?,
                    features = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data['name'], data['brand'], data['model'],
                data['category'], data['price'], data['stock'],
                data['description'],
                json.dumps(data['features']),
                json.dumps(data['tags']),
                product_id
            ))
            conn.commit()
            return True
        finally:
            conn.close()

    def get_products(self, search_term=None):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            if search_term:
                query = '''
                    SELECT * FROM products 
                    WHERE name LIKE ? OR brand LIKE ? 
                    OR model LIKE ? OR tags LIKE ?
                '''
                search_pattern = f'%{search_term}%'
                products = c.execute(query, (
                    search_pattern, search_pattern,
                    search_pattern, search_pattern
                )).fetchall()
            else:
                products = c.execute('SELECT * FROM products').fetchall()
            
            return [dict(product) for product in products]
        finally:
            conn.close()

    def get_low_stock_products(self, threshold=5):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            products = c.execute(
                'SELECT * FROM products WHERE stock <= ?',
                (threshold,)
            ).fetchall()
            return [dict(product) for product in products]
        finally:
            conn.close()

class CustomerModel:
    def __init__(self, db):
        self.db = db

    def add_customer(self, data):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO customers (
                    name, contact_number, cnic, address
                ) VALUES (?, ?, ?, ?)
            ''', (
                data['name'], data['contact_number'],
                data.get('cnic'), data['address']
            ))
            customer_id = c.lastrowid
            conn.commit()
            return customer_id
        finally:
            conn.close()

    def get_customers(self, search_term=None):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            if search_term:
                query = '''
                    SELECT * FROM customers 
                    WHERE name LIKE ? OR contact_number LIKE ? 
                    OR cnic LIKE ?
                '''
                search_pattern = f'%{search_term}%'
                customers = c.execute(query, (
                    search_pattern, search_pattern, search_pattern
                )).fetchall()
            else:
                customers = c.execute('SELECT * FROM customers').fetchall()
            
            return [dict(customer) for customer in customers]
        finally:
            conn.close()

class SaleModel:
    def __init__(self, db):
        self.db = db

    def create_cash_sale(self, data):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            # Create customer
            c.execute('''
                INSERT INTO customers (name, contact_number, address)
                VALUES (?, ?, ?)
            ''', (data['customer_name'], data['contact_number'], data['address']))
            customer_id = c.lastrowid

            # Create sale
            c.execute('''
                INSERT INTO sales (
                    customer_id, product_id, sale_type, amount
                ) VALUES (?, ?, 'cash', ?)
            ''', (customer_id, data['product_id'], data['amount']))
            sale_id = c.lastrowid

            # Update product stock
            c.execute('''
                UPDATE products 
                SET stock = stock - ? 
                WHERE id = ?
            ''', (data['quantity'], data['product_id']))

            conn.commit()
            return sale_id
        finally:
            conn.close()

    def create_installment_sale(self, data):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            # Create customer
            c.execute('''
                INSERT INTO customers (
                    name, contact_number, cnic, address
                ) VALUES (?, ?, ?, ?)
            ''', (
                data['customer_name'], data['contact_number'],
                data['cnic'], data['address']
            ))
            customer_id = c.lastrowid

            # Create sale
            c.execute('''
                INSERT INTO sales (
                    customer_id, product_id, sale_type,
                    amount, markup_percentage, total_with_markup,
                    advance_payment, installment_count
                ) VALUES (?, ?, 'installment', ?, ?, ?, ?, ?)
            ''', (
                customer_id, data['product_id'],
                data['amount'], data['markup_percentage'],
                data['total_with_markup'], data['advance_payment'],
                data['installment_count']
            ))
            sale_id = c.lastrowid

            # Create witness record
            c.execute('''
                INSERT INTO witnesses (
                    sale_id, name, cnic, address
                ) VALUES (?, ?, ?, ?)
            ''', (
                sale_id, data['witness_name'],
                data['witness_cnic'], data['witness_address']
            ))

            # Create installment records
            for installment in data['installments']:
                c.execute('''
                    INSERT INTO installments (
                        sale_id, installment_number,
                        amount, due_date, remaining_balance
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    sale_id, installment['number'],
                    installment['amount'], installment['due_date'],
                    installment['remaining_balance']
                ))

            # Update product stock
            c.execute('''
                UPDATE products 
                SET stock = stock - 1 
                WHERE id = ?
            ''', (data['product_id'],))

            conn.commit()
            return sale_id
        finally:
            conn.close()

    def get_sales_summary(self, start_date=None, end_date=None):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            query = '''
                SELECT 
                    s.sale_type,
                    COUNT(*) as count,
                    SUM(CASE 
                        WHEN s.sale_type = 'cash' THEN s.amount 
                        ELSE s.total_with_markup 
                    END) as total_amount
                FROM sales s
            '''
            
            params = []
            if start_date and end_date:
                query += ' WHERE s.created_at BETWEEN ? AND ?'
                params.extend([start_date, end_date])
            
            query += ' GROUP BY s.sale_type'
            
            results = c.execute(query, params).fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()

class InstallmentModel:
    def __init__(self, db):
        self.db = db

    def get_installments(self, status=None, search_term=None):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            query = '''
                SELECT 
                    i.*, s.*, c.name as customer_name,
                    p.name as product_name, p.brand, p.model
                FROM installments i
                JOIN sales s ON i.sale_id = s.id
                JOIN customers c ON s.customer_id = c.id
                JOIN products p ON s.product_id = p.id
                WHERE 1=1
            '''
            
            params = []
            if status:
                query += ' AND i.status = ?'
                params.append(status)
            
            if search_term:
                query += '''
                    AND (c.name LIKE ? OR p.name LIKE ? 
                    OR p.brand LIKE ? OR p.model LIKE ?)
                '''
                search_pattern = f'%{search_term}%'
                params.extend([search_pattern] * 4)
            
            installments = c.execute(query, params).fetchall()
            return [dict(installment) for installment in installments]
        finally:
            conn.close()

    def mark_installment_paid(self, sale_id, installment_number):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                UPDATE installments 
                SET status = 'Paid',
                    paid_date = CURRENT_DATE
                WHERE sale_id = ? 
                AND installment_number = ?
            ''', (sale_id, installment_number))
            conn.commit()
            return True
        finally:
            conn.close()

class SettingsModel:
    def __init__(self, db):
        self.db = db

    def get_settings(self):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            settings = c.execute(
                'SELECT * FROM settings ORDER BY id DESC LIMIT 1'
            ).fetchone()
            return dict(settings) if settings else None
        finally:
            conn.close()

    def update_settings(self, data):
        conn = self.db.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT OR REPLACE INTO settings (
                    id, business_name, business_address,
                    business_phone, updated_at
                ) VALUES (
                    1, ?, ?, ?, CURRENT_TIMESTAMP
                )
            ''', (
                data['business_name'],
                data['business_address'],
                data['business_phone']
            ))
            conn.commit()
            return True
        finally:
            conn.close()