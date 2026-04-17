from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = Flask(__name__)

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

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    message = request.form.get('message')

    feedback_data = {
        "name": name if name else "Anonymous",
        "message": message
    }

    db.collection("feedbacks").add(feedback_data)

    return redirect('/')

@app.route('/admin')
def admin():
    feedbacks = db.collection("feedbacks").stream()
    feedback_list = [f.to_dict() for f in feedbacks]
    return {"feedbacks": feedback_list}

if __name__ == '__main__':
    app.run(debug=True)