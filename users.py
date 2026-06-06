import uuid
import hashlib
import datetime
from flask import Blueprint, request, jsonify
from src.db import get_db
from src.auth import generate_token

users_bp = Blueprint("users", __name__)

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

@users_bp.post("/api/auth/register")
def register():
    data = request.get_json()
    required = ["full_name", "phone", "pin"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    phone = data["phone"].strip()
    pin = data["pin"].strip()

    if len(pin) != 4 or not pin.isdigit():
        return jsonify({"error": "PIN must be exactly 4 digits"}), 400

    if not phone.startswith(("07", "01", "+254")):
        return jsonify({"error": "Enter a valid Kenyan phone number"}), 400

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Phone number already registered"}), 409

    user_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()
    initial_balance = 1000.00  # demo starting balance

    conn.execute(
        "INSERT INTO users (id, full_name, phone, pin_hash, balance, created_at) VALUES (?,?,?,?,?,?)",
        (user_id, data["full_name"].strip(), phone, hash_pin(pin), initial_balance, now)
    )
    conn.commit()
    conn.close()

    token = generate_token(user_id)
    return jsonify({
        "message": "Account created successfully",
        "token": token,
        "user": {"id": user_id, "full_name": data["full_name"], "phone": phone, "balance": initial_balance}
    }), 201


@users_bp.post("/api/auth/login")
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    phone = (data.get("phone") or "").strip()
    pin = (data.get("pin") or "").strip()

    if not phone or not pin:
        return jsonify({"error": "Phone and PIN are required"}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    conn.close()

    if not user or user["pin_hash"] != hash_pin(pin):
        return jsonify({"error": "Invalid phone number or PIN"}), 401

    token = generate_token(user["id"])

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "phone": user["phone"],
            "balance": user["balance"]
        }
    }), 200