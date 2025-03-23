#!/usr/bin/env python3
import os
import sys
import webbrowser
from models import Database, ProductModel, SettingsModel
from app import app

def init_database():
    """Initialize the database with tables"""
    print("Initializing database...")
    db = Database()
    db.init_db()
    print("Database initialized successfully!")

def add_sample_data():
    """Add sample data to the database"""
    print("Adding sample data...")
    db = Database()
    
    # Add sample products
    product_model = ProductModel(db)
    sample_products = [
        {
            'name': 'Samsung Smart TV',
            'brand': 'Samsung',
            'model': 'UA55TU8000',
            'category': 'electronics',
            'price': 89999.99,
            'stock': 10,
            'description': '55-inch 4K UHD Smart LED TV',
            'features': ['4K Resolution', 'Smart TV Features', 'HDR'],
            'tags': ['TV', 'Smart TV', 'Samsung']
        },
        {
            'name': 'LG Split AC',
            'brand': 'LG',
            'model': 'MS-Q18KNYA',
            'category': 'appliances',
            'price': 75999.99,
            'stock': 8,
            'description': '1.5 Ton Split Air Conditioner',
            'features': ['Inverter Technology', 'Energy Efficient', 'Auto Restart'],
            'tags': ['AC', 'Air Conditioner', 'LG']
        }
    ]
    
    for product in sample_products:
        product_model.add_product(product)
    
    # Add sample settings
    settings_model = SettingsModel(db)
    settings_model.update_settings({
        'business_name': 'Electronics & Appliances Store',
        'business_address': '123 Main Street, City',
        'business_phone': '+92 300 1234567'
    })
    
    print("Sample data added successfully!")

def main():
    """Main function to run the application"""
    # Create necessary directories
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Initialize database
    init_database()
    
    # Add sample data if database is empty
    db = Database()
    product_model = ProductModel(db)
    products = product_model.get_products()
    if not products:
        add_sample_data()
    
    # Start the Flask application
    port = 8000
    url = f'http://localhost:{port}'
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║                   Sales Management System                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  The application is starting...                                ║
║                                                                ║
║  Access the system at: {url}                           ║
║                                                                ║
║  Features available:                                           ║
║  - Cash and Installment Sales Management                       ║
║  - Inventory Management                                        ║
║  - Customer Management                                         ║
║  - Installment Tracking                                        ║
║  - Reports Generation                                          ║
║                                                                ║
║  Press Ctrl+C to stop the server                              ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Run the application
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        sys.exit(0)