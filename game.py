from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bank.db"
app.config["JWT_SECRET_KEY"] = "supersecretkey"

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the Bank API!"  # Simple message for the root URL

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Increased length for hashed password
    balance = db.Column(db.Float, default=0.0)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data["password"])
    user = User(username=data["username"], password=hashed_password, balance=1000)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "balance": user.balance})

@app.route("/transfer", methods=["POST"])
@jwt_required()
def transfer():
    data = request.get_json()
    sender = User.query.get(data["sender_id"])  # Ensure this matches the incoming data structure
    receiver = User.query.get(data["receiver_id"])  # Ensure this matches the incoming data structure

    if sender and receiver and sender.balance >= data["amount"]:
        sender.balance -= data["amount"]
        receiver.balance += data["amount"]
        db.session.commit()
        return jsonify({"message": "Transfer successful!"})
    
    return jsonify({"error": "Invalid transaction"}), 400

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures that the database tables are created
    app.run(debug=True)
