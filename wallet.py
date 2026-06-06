import uuid
import datetime
from flask import Blueprint, request, jsonify
from src.db import get_db
from src.auth import require_auth

wallet_bp = Blueprint("wallet", __name__)

@wallet_bp.get("/api/wallet/balance")
@require_auth
def get_balance():
    conn = get_db()
    user = conn.execute(
        "SELECT id, full_name, phone, balance FROM users WHERE id = ?",
        (request.user_id,)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "phone": user["phone"],
        "full_name": user["full_name"],
        "balance": round(user["balance"], 2),
        "currency": "KES"
    }), 200


@wallet_bp.post("/api/wallet/deposit")
@require_auth
def deposit():
    data = request.get_json()
    amount = data.get("amount")

    if not amount or float(amount) <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400
    if float(amount) > 150000:
        return jsonify({"error": "Maximum deposit is KES 150,000"}), 400

    amount = float(amount)
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (request.user_id,)).fetchone()

    new_balance = user["balance"] + amount
    tx_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()

    conn.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, request.user_id))
    conn.execute(
        "INSERT INTO transactions (id, sender_id, receiver_id, amount, type, description, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (tx_id, None, request.user_id, amount, "deposit", data.get("description", "Wallet top-up"), "success", now)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "message": f"KES {amount:,.2f} deposited successfully",
        "transaction_id": tx_id,
        "new_balance": round(new_balance, 2)
    }), 200
