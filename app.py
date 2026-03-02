from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Ticket
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# ---------------- LOGIN REQUIRED ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- SIMPLE AI ----------------
def predict_ticket(description):
    description = description.lower()
    if "password" in description or "login" in description:
        return "Account", "Medium"
    elif "payment" in description or "refund" in description:
        return "Billing", "High"
    elif "error" in description or "not working" in description:
        return "Technical", "High"
    else:
        return "General", "Low"

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)

        new_user = User(fullname=fullname, username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    total = Ticket.query.count()
    open_tickets = Ticket.query.filter_by(status="Open").count()
    closed_tickets = Ticket.query.filter_by(status="Closed").count()
    high_priority = Ticket.query.filter_by(priority="High").count()

    return render_template(
        "dashboard.html",
        total=total,
        open_tickets=open_tickets,
        closed_tickets=closed_tickets,
        high_priority=high_priority
    )

# ---------------- CREATE TICKET ----------------
@app.route("/create_ticket", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        category, priority = predict_ticket(description)

        new_ticket = Ticket(
            title=title,
            description=description,
            category=category,
            priority=priority,
            status="Open",
            date_created=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(new_ticket)
        db.session.commit()

        flash("Ticket created successfully!")
        return redirect(url_for("dashboard"))

    return render_template("create_ticket.html")

# ---------------- ACTIVE TICKETS ----------------
@app.route("/active_tickets", methods=["GET", "POST"])

def active_tickets():
    if request.method == "POST":
        ticket_id = request.form.get("ticket_id")
        new_status = request.form.get("status")

        ticket = Ticket.query.get(ticket_id)
        if ticket:
            ticket.status = new_status
            ticket.updated_at = datetime.now()
            db.session.commit()

        return redirect(url_for("active_tickets"))

    tickets = Ticket.query.filter(Ticket.status != "Closed").all()
    return render_template("active_tickets.html", tickets=tickets, now=datetime.now())

@app.route("/closed_tickets")
@login_required
def closed_tickets():
    tickets = Ticket.query.filter_by(status="Closed").all()
    return render_template("closed_tickets.html", tickets=tickets)

# ---------------- PROFILE ----------------
@app.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)