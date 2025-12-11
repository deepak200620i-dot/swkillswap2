import os
import psycopg
from psycopg.rows import dict_row

from flask import g

# Render provides DATABASE_URL automatically
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set! Add it in Render → Environment.")


def get_db():
    if "db" not in g:
        g.db = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return g.db


def close_db(e=None):
    """Close connection after request ends"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    try:
        with db.cursor() as cur:
            cur.execute(sql_script)
        db.commit()
        print("PostgreSQL schema initialized.")
    except Exception as e:
        print(f"Schema error: {e}")
        db.rollback()


# For CLI usage (optional)
if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    with app.app_context():
        init_db()
