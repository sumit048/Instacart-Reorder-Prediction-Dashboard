# utils/db_import.py

import pandas as pd
import sqlalchemy
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_data_from_db(db_url, table_name):
    """
    Load data from a SQL database table into a Pandas DataFrame.

    Args:
        db_url (str): Database URL (e.g., postgresql://user:pass@localhost/dbname)
        table_name (str): Name of the table to load

    Returns:
        pd.DataFrame: DataFrame containing the table data
    """
    try:
        logging.info(f"Connecting to database: {db_url}")
        engine = sqlalchemy.create_engine(db_url)
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
        logging.info(f"Loaded {len(df)} rows from table: {table_name}")
        return df

    except Exception as e:
        logging.error(f"Failed to load data from {table_name}: {e}")
        return pd.DataFrame()
