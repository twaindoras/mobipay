import uuid
import datetime
from flask import Blueprint, request, jsonify
from src.db import get_db
from src.auth import require_auth

transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.post("/api/transactions/send")
@require_auth
def send_money():
    data = request.get_json()
    receiver_phone = (data.get("receiver_phone") or "").strip()
    amount = data.get("amount")
    description = (data.get("description") or "").strip()

    if not receiver_phone or not amount:
        return jsonify({"error": "receiver_phone and amount are required"}), 400

    amount = float(amount)
    if amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400
    if amount < 10:
        return jsonify({"error": "Minimum transfer is KES 10"}), 400
    if amount > 70000:
        return jsonify({"error": "Maximum transfer per transaction is KES 70,000"}), 400

    conn = get_db()
    sender = conn.execute("SELECT * FROM users WHERE id = ?", (request.user_id,)).fetchone()
    receiver = conn.execute("SELECT * FROM users WHERE phone = ?", (receiver_phone,)).fetchone()

    if not receiver:
        conn.close()
        return jsonify({"error": "Recipient phone number not found"}), 404

    if sender["id"] == receiver["id"]:
        conn.close()
        return jsonify({"error": "You cannot send money to yourself"}), 400

    if sender["balance"] < amount:
        conn.close()
        return jsonify({"error": f"Insufficient balance. Available: KES {sender['balance']:,.2f}"}), 400

    tx_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()

    conn.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender["id"]))
    conn.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, receiver["id"]))
    conn.execute(
        "INSERT INTO transactions (id, sender_id, receiver_id, amount, type, description, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (tx_id, sender["id"], receiver["id"], amount, "transfer", description or f"Transfer to {receiver['phone']}", "success", now)
    )
    conn.commit()

    new_balance = conn.execute("SELECT balance FROM users WHERE id = ?", (sender["id"],)).fetchone()["balance"]
    conn.close()

    return jsonify({
        "message": f"KES {amount:,.2f} sent to {receiver['full_name']} ({receiver_phone})",
        "transaction_id": tx_id,
        "amount": amount,
        "recipient": {"name": receiver["full_name"], "phone": receiver_phone},
        "new_balance": round(new_balance, 2),
        "timestamp": now
    }), 200


@transactions_bp.get("/api/transactions/history")
@require_auth
def get_history():
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))

    conn = get_db()
    rows = conn.execute("""
        SELECT
            t.id, t.amount, t.type, t.description, t.status, t.created_at,
            s.full_name AS sender_name, s.phone AS sender_phone,
            r.full_name AS receiver_name, r.phone AS receiver_phone
        FROM transactions t
        LEFT JOIN users s ON t.sender_id = s.id
        LEFT JOIN users r ON t.receiver_id = r.id
        WHERE t.sender_id = ? OR t.receiver_id = ?
        ORDER BY t.created_at DESC
        LIMIT ? OFFSET ?
    """, (request.user_id, request.user_id, limit, offset)).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE sender_id = ? OR receiver_id = ?",
        (request.user_id, request.user_id)
    ).fetchone()[0]
    conn.close()

    transactions = []
    for row in rows:
        tx = {
            "id": row["id"],
            "amount": row["amount"],
            "type": row["type"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"],
            "sender": {"name": row["sender_name"], "phone": row["sender_phone"]},
            "receiver": {"name": row["receiver_name"], "phone": row["receiver_phone"]}
        }
        transactions.append(tx)

    return jsonify({
        "transactions": transactions,
        "total": total,
        "limit": limit,
        "offset": offset
    }), 200


@transactions_bp.get("/api/transactions/<tx_id>")
@require_auth
def get_transaction(tx_id):
    conn = get_db()
    row = conn.execute("""
        SELECT
            t.id, t.amount, t.type, t.description, t.status, t.created_at,
            s.full_name AS sender_name, s.phone AS sender_phone,
            r.full_name AS receiver_name, r.phone AS receiver_phone
        FROM transactions t
        LEFT JOIN users s ON t.sender_id = s.id
        LEFT JOIN users r ON t.receiver_id = r.id
        WHERE t.id = ? AND (t.sender_id = ? OR t.receiver_id = ?)
    """, (tx_id, request.user_id, request.user_id)).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify({
        "id": row["id"],
        "amount": row["amount"],
        "type": row["type"],
        "description": row["description"],
        "status": row["status"],
        "created_at": row["created_at"],
        "sender": {"name": row["sender_name"], "phone": row["sender_phone"]},
        "receiver": {"name": row["receiver_name"], "phone": row["receiver_phone"]}
    }), 200
