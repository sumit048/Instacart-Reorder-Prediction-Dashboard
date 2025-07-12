import pandas as pd
import sqlite3
import os

# Define the path to the SQLite DB file
db_file = "instacart.db"

# Folder where your CSVs are located
csv_folder = os.path.join(os.getcwd(), "data")

# Map table names to CSV files
csv_files = {
    "orders": "orders.csv",
    "order_products__prior": "order_products__prior.csv",
    "order_products__train": "order_products__train.csv",
    "products": "products.csv",
    "aisles": "aisles.csv",
    "departments": "departments.csv"
}

# Connect to SQLite and insert each CSV as a table
conn = sqlite3.connect(db_file)

for table_name, file_name in csv_files.items():
    file_path = os.path.join(csv_folder, file_name)
    if os.path.exists(file_path):
        print(f"Inserting data into table: {table_name}")
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    else:
        print(f"⚠️ File not found: {file_path}")

conn.close()
print("✅ All data inserted successfully into instacart.db")