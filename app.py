from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

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

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Wrong Password!"

    return '''
        <h2>Admin Login</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter Password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/admin")
def admin():

    # 🔐 Protect dashboard
    if not session.get("admin"):
        return redirect("/admin-login")

    feedbacks = db.collection("feedback").stream()

    feedback_list = []
    total = 0
    total_rating = 0

    for doc in feedbacks:
        data = doc.to_dict()
        feedback_list.append(data)
        total += 1
        total_rating += data.get("rating", 0)

    average = round(total_rating / total, 2) if total > 0 else 0

    return render_template("admin.html",
                           feedbacks=feedback_list,
                           total=total,
                           average=average)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")
    
@app.route("/admin")
def admin():

    # 🔐 Protect route
    if not session.get("admin"):
        return redirect("/admin-login")

    feedbacks = db.collection("feedback").stream()

    feedback_list = []
    total = 0
    total_rating = 0

    for doc in feedbacks:
        data = doc.to_dict()
        feedback_list.append(data)
        total += 1
        total_rating += data.get("rating", 0)

    average = round(total_rating / total, 2) if total > 0 else 0

    return render_template("admin.html",
                           feedbacks=feedback_list,
                           total=total,
                           average=average)
    feedbacks = db.collection("feedbacks").stream()
    feedback_list = [f.to_dict() for f in feedbacks]
    return {"feedbacks": feedback_list}

if __name__ == '__main__':
    app.run(debug=True)
