from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Ticket

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE CONFIG ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------- LOGIN REQUIRED ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login first!")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or Email already exists!")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            fullname=fullname,
            username=username,
            email=email,
            password=hashed_password,
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful!")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("home"))

        flash("Invalid email or password")

    return render_template("login.html")
# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():

    session.clear()
    flash("Logged out successfully")
    return redirect(url_for("home"))


# ---------------- DASHBOARD PAGE ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------- PAGE ROUTES ----------------
@app.route("/create-ticket")
@login_required
def create_ticket():
    return render_template("create_ticket.html")


@app.route("/active-tickets")
@login_required
def active_tickets():
    return render_template("active_tickets.html")


@app.route("/closed-tickets")
@login_required
def closed_tickets():
    return render_template("closed_tickets.html")


@app.route("/profile")
@login_required
def profile():

    user = User.query.get(session["user_id"])

    return render_template("profile.html", user=user)


@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- DASHBOARD API ----------------
@app.route("/api/dashboard")
def dashboard_api():

    total = Ticket.query.count()

    open_tickets = Ticket.query.filter_by(status="Open").count()

    closed_tickets = Ticket.query.filter_by(status="Closed").count()

    high_priority = Ticket.query.filter_by(priority="High").count()

    return jsonify({
        "total": total,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "high_priority": high_priority
    })


# ---------------- CREATE TICKET API ----------------
@app.route("/api/create-ticket", methods=["POST"])
@login_required
def api_create_ticket():

    data = request.get_json(silent=True)

    if data:
        title = data.get("title")
        description = data.get("description")
    else:
        title = request.form.get("title")
        description = request.form.get("description")

    ticket = Ticket(
        title=title,
        description=description,
        status="Open"
    )

    db.session.add(ticket)
    db.session.commit()

    # If API request
    if data:
        return jsonify({
            "message": "Ticket created successfully",
            "ticket_id": ticket.id
        })

    # If HTML form
    flash("Ticket created successfully!")
    return redirect(url_for("active_tickets"))


# ---------------- ACTIVE TICKETS API ----------------
@app.route("/api/active-tickets")
@login_required
def api_active_tickets():

    tickets = Ticket.query.filter(Ticket.status != "Closed").all()

    result = []

    for t in tickets:
        result.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status
        })

    return jsonify({"tickets": result})

@app.route("/api/update-status", methods=["POST"])
@login_required
def update_ticket_status():

    ticket_id = request.form.get("ticket_id")
    status = request.form.get("status")

    ticket = Ticket.query.get(ticket_id)

    if ticket:
        ticket.status = status
        db.session.commit()

    flash("Ticket status updated!")

    return redirect(url_for("active_tickets"))


# ---------------- CLOSED TICKETS API ----------------
@app.route("/api/closed-tickets")
def api_closed_tickets():

    tickets = Ticket.query.filter_by(status="Closed").all()

    data = []

    for t in tickets:
        data.append({
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "priority": t.priority
        })

    return jsonify(data)
# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)