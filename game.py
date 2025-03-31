from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from flask_cors import CORS

app = Flask(_name_)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bank.db"
app.config["JWT_SECRET_KEY"] = "supersecretkey"

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Float, default=0.0)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user = User(username=data["username"], password=data["password"], balance=1000)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"], password=data["password"]).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "balance": user.balance})

@app.route("/transfer", methods=["POST"])
@jwt_required()
def transfer():
    data = request.get_json()
    sender = User.query.get(data["sender_id"])
    receiver = User.query.get(data["receiver_id"])

    if sender.balance >= data["amount"]:
        sender.balance -= data["amount"]
        receiver.balance += data["amount"]
        db.session.commit()
        return jsonify({"message": "Transfer successful!"})
    return jsonify({"error": "Insufficient balance"}), 400

if _name_ == "_main_":
    db.create_all()
    app.run(debug=True)