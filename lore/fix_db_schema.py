# -*- coding: utf-8 -*-
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_NAME = "devel"  # Replace with your database name if different
DB_USER = "odoo"   # Replace with your database user if different
DB_PASSWORD = "odoo"  # Replace with your database password if different
DB_HOST = "localhost"
DB_PORT = "5432"

def fix_character_history_field():
    """Add the character_history column directly to the database"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # First check if the table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name='character_profile'
            );
        """)
        if not cursor.fetchone()[0]:
            print("Error: character_profile table does not exist!")
            return False

        # Check if the column already exists
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='character_profile' AND column_name='character_history';
        """)
        if not cursor.fetchone():
            # If column doesn't exist, create it
            cursor.execute("""
                ALTER TABLE character_profile
                ADD COLUMN character_history TEXT;
            """)
            print("Column character_history added successfully!")
        else:
            print("Column character_history already exists.")

        # Get the model ID for character.profile
        cursor.execute("""
            SELECT id FROM ir_model WHERE model='character.profile';
        """)
        model_id_result = cursor.fetchone()
        if not model_id_result:
            print("Error: Model 'character.profile' not found in ir_model!")
            return False

        model_id = model_id_result[0]

        # Make sure the field is registered in ir_model_fields
        cursor.execute("""
            SELECT id FROM ir_model_fields
            WHERE model='character.profile' AND name='character_history';
        """)
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO ir_model_fields (
                    name, model, model_id, field_description, ttype,
                    state, modules, relation, store, tracking
                )
                VALUES (
                    'character_history', 'character.profile',
                    %s, 'Historia del personaje', 'text',
                    'base', 'lore', null, true, true
                );
            """, (model_id,))
            print("Field added to ir_model_fields!")
        else:
            print("Field already exists in ir_model_fields.")

        # Clear caches and mark module for upgrade
        cursor.execute("DELETE FROM ir_attachment WHERE name LIKE '%character.profile%';")
        cursor.execute("UPDATE ir_module_module SET state='to upgrade' WHERE name='lore';")

        # Reset views that might reference this field
        cursor.execute("DELETE FROM ir_ui_view WHERE model='character.profile' AND arch_db LIKE '%character_history%';")

        cursor.close()
        conn.close()
        print("Database update completed successfully!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fix_character_history_field()
