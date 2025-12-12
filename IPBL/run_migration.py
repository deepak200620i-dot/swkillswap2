from database import get_db, init_db
from flask import Flask
import os

app = Flask(__name__)

# Add context to use current app config
def run_migration():
    # Read the migration file
    migration_file = "database/migrations/add_email_verification.sql"
    
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
            
        print(f"Executing migration from {migration_file}...")
        
        # Connect to DB using existing utility
        # We need to set up the app context for get_db to work if it uses 'g'
        # Or we can just use psycopg directly if we import the config
        
        # Let's try to use the existing init_db logic partially or just connect directly
        from config import config
        # Assuming development config for local
        app.config.from_object(config['development'])
        
        # Establish connection manually to avoid flask context issues if simple
        import psycopg
        from psycopg.rows import dict_row
        
        # Get DB URL from environment or config
        db_url = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/skillswap")
        print(f"Connecting to database...")
        
        with psycopg.connect(db_url, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            print("Migration executed successfully!")
            
    except FileNotFoundError:
        print(f"Error: Migration file {migration_file} not found.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    # Load env vars first
    from dotenv import load_dotenv
    load_dotenv()
    
    run_migration()
