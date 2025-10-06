import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Config
PORT = int(os.getenv("PORT", "4000"))
CORS_ORIGINS = os.getenv("CORS_ORIGIN", "*")

# Database URL - compatible with AWS RDS
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGDATABASE = os.getenv("PGDATABASE", "space")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "postgres")
PGSSL = os.getenv("PGSSL", "disable")

ssl_query = "?sslmode=require" if PGSSL in ("require", "true", "1") else ""
DATABASE_URL = f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}{ssl_query}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS.split(",") if CORS_ORIGINS != "*" else "*")

# --- DB Migration ---
with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS spaces (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    ))


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


@app.get("/api/spaces")
def list_spaces():
    try:
        with engine.begin() as conn:
            result = conn.execute(text(
                "SELECT id, name, description, image_url, created_at FROM spaces ORDER BY created_at DESC"
            ))
            rows = [dict(r._mapping) for r in result]
        return jsonify(rows)
    except SQLAlchemyError:
        return jsonify({"error": "Internal Server Error"}), 500


@app.get("/api/spaces/<uuid>")
def get_space(uuid):
    try:
        with engine.begin() as conn:
            result = conn.execute(text(
                "SELECT id, name, description, image_url, created_at FROM spaces WHERE id = :id"
            ), {"id": str(uuid)})
            row = result.mappings().first()
            if not row:
                return jsonify({"error": "Not found"}), 404
            return jsonify(dict(row))
    except SQLAlchemyError:
        return jsonify({"error": "Internal Server Error"}), 500


@app.post("/api/spaces")
def create_space():
    body = request.get_json(silent=True) or {}
    name = body.get("name", "").strip()
    description = body.get("description")
    image_url = body.get("image_url")
    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        with engine.begin() as conn:
            result = conn.execute(text(
                """
                INSERT INTO spaces (name, description, image_url)
                VALUES (:name, :description, :image_url)
                RETURNING id, name, description, image_url, created_at
                """
            ), {"name": name, "description": description, "image_url": image_url})
            row = result.mappings().first()
            return jsonify(dict(row)), 201
    except SQLAlchemyError:
        return jsonify({"error": "Internal Server Error"}), 500


@app.delete("/api/spaces/<uuid>")
def delete_space(uuid):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("DELETE FROM spaces WHERE id = :id"), {"id": str(uuid)})
            if result.rowcount == 0:
                return jsonify({"error": "Not found"}), 404
            return ("", 204)
    except SQLAlchemyError:
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
