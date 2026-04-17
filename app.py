from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = Flask(__name__)
app = Flask(__name__)

# 🔐 Secret key for session management
app.secret_key = "supersecretkey"

# 🔐 Admin password
ADMIN_PASSWORD = "Shifa123"
@app.route("/")
def home():
    return render_template("index.html", success=False)

# Firebase Initialization (Render + Local Compatible)

if os.environ.get("FIREBASE_KEY"):
    firebase_key = json.loads(os.environ.get("FIREBASE_KEY"))
    cred = credentials.Certificate(firebase_key)
else:
    cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    message = request.form.get("message")
    rating = int(request.form.get("rating"))

    feedback_data = {
        "name": name if name else "Anonymous",
        "message": message,
        "rating": rating,
        "timestamp": datetime.now()
    }

    db.collection("feedback").add(feedback_data)

    return render_template("index.html", success=True)
@app.route('/admin')
def admin():
    feedbacks = db.collection("feedbacks").stream()
    feedback_list = [f.to_dict() for f in feedbacks]
    return {"feedbacks": feedback_list}

if __name__ == '__main__':
    app.run(debug=True)
