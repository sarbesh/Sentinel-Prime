#!/usr/bin/env python3
"""
Add name column to devices table and set it to hostname.
"""
import sys
sys.path.insert(0, '/home/sarbesh/workspace/sentinel-prime/backend')

from sqlmodel import SQLModel, create_engine, Session, select, text
from models import Device
from datetime import datetime

DATABASE_URL = "sqlite:///./data/sentinel_prime.db"

def add_name_column():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Add the column if it doesn't exist
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("PRAGMA table_info(devices)"))
        columns = [row[1] for row in result.fetchall()]
        if 'name' not in columns:
            print("Adding 'name' column to devices table...")
            conn.execute(text("ALTER TABLE devices ADD COLUMN name VARCHAR NOT NULL DEFAULT ''"))
            # Update existing rows: set name to hostname if hostname is not null, else to a default
            conn.execute(text("UPDATE devices SET name = hostname WHERE hostname IS NOT NULL AND hostname != ''"))
            # For rows where hostname is null or empty, set name to a default like 'Unknown Device'
            conn.execute(text("UPDATE devices SET name = 'Unknown Device' WHERE name IS NULL OR name = ''"))
            # Make sure the column is not null (we already set a default, but let's ensure)
            # Note: SQLite doesn't allow altering a column to NOT NULL directly, but we can set a default and then update.
            # We already set a default and updated all rows, so it should be fine.
            print("Added and populated 'name' column.")
        else:
            print("'name' column already exists.")
    
    # Also, we might want to make sure the column is not null by setting a default and updating nulls.
    # But we already did that above.
    
    print("Done.")

if __name__ == '__main__':
    add_name_column()
