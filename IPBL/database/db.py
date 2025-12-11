import os
import psycopg2
import psycopg2.extras
from flask import g

# Render provides DATABASE_URL automatically
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set! Add it in Render → Environment.")


def get_db():
    """
    Get a PostgreSQL connection.
    Stored in Flask's g to reuse during request.
    """
    if "db" not in g:
        g.db = psycopg2.connect(
            DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor
        )
    return g.db


def close_db(e=None):
    """Close connection after request ends"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    Initialize database tables automatically on first startup.
    Reads schema.sql and executes it on PostgreSQL.
    Ignores errors if tables already exist.
    """
    db = get_db()
    cur = db.cursor()

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    try:
        cur.execute(sql_script)
        db.commit()
        print("✅ PostgreSQL schema initialized (or already existed).")
    except Exception as e:
        print(f"⚠️ Schema initialization skipped: {e}")
        db.rollback()


# For CLI usage (optional)
if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    with app.app_context():
        init_db()
