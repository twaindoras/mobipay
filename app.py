from flask import Flask, jsonify, send_from_directory
from flask.helpers import send_file
from src.db import init_db
from src.routes.users import users_bp
from src.routes.wallet import wallet_bp
from src.routes.transactions import transactions_bp
import os

app = Flask(__name__, static_folder="public")

app.register_blueprint(users_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(transactions_bp)

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "MobiPay API", "version": "1.0.0"})

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    static_folder = os.path.join(os.path.dirname(__file__), "public")
    file_path = os.path.join(static_folder, path)
    if path and os.path.exists(file_path):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, "index.html")

if __name__ == "__main__":
    init_db()
    print("\n MobiPay API running at http://localhost:5000")
    print(" Dashboard at        http://localhost:5000\n")
    app.run(debug=True, port=5000)
