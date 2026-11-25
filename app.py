
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "MITS_student_management_2026"

# Temporary in-memory storage
students = {}

# Admin credentials
ADMIN_ID = "riya"
ADMIN_PASSWORD = generate_password_hash("riya08")


# ---------------- LOGIN PROTECTION ----------------

def login_required(role):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "role" not in session:
                return redirect(url_for("home"))

            if session["role"] != role:
                return redirect(url_for("home"))

            return function(*args, **kwargs)

        return wrapper

    return decorator


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("home.html")


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        admin_id = request.form.get("admin_id", "").strip()
        password = request.form.get("password", "")

        if admin_id == ADMIN_ID and check_password_hash(
            ADMIN_PASSWORD, password
        ):

            session.clear()
            session["role"] = "admin"
            session["username"] = admin_id

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid Admin ID or Password!"
        )

    return render_template("admin_login.html")


# ---------------- STUDENT LOGIN ----------------

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        student_id = request.form.get("student_id", "").strip()
        password = request.form.get("password", "")

        student = students.get(student_id)

        if student and check_password_hash(
            student["password"], password
        ):

            session.clear()
            session["role"] = "student"
            session["student_id"] = student_id

            return redirect(url_for("student_dashboard"))

        return render_template(
            "student_login.html",
            error="Invalid Student ID or Password!"
        )

    return render_template("student_login.html")


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin-dashboard")
@login_required("admin")
def admin_dashboard():

    return render_template("admin_dashboard.html")


# ---------------- ADD STUDENT ----------------

@app.route("/add-student", methods=["GET", "POST"])
@login_required("admin")
def add_student():

    if request.method == "POST":

        student_id = request.form.get("student_id", "").strip()

        if student_id in students:

            return render_template(
                "add_student.html",
                error="Student ID already exists!"
            )

        name = request.form.get("name", "").strip()
        branch = request.form.get("branch", "").strip()
        programme = request.form.get("programme", "").strip()
        semester = request.form.get("semester", "").strip()
        year = request.form.get("year", "").strip()
        batch = request.form.get("batch", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not all([
            student_id, name, branch, programme,
            semester, year, batch, email, phone, password
        ]):

            return render_template(
                "add_student.html",
                error="Please fill all the fields!"
            )

        students[student_id] = {

            "student_id": student_id,
            "name": name,
            "branch": branch,
            "programme": programme,
            "semester": semester,
            "year": year,
            "batch": batch,
            "email": email,
            "phone": phone,
            "password": generate_password_hash(password)
        }

        return redirect(url_for("view_students"))

    return render_template("add_student.html")


# ---------------- VIEW STUDENTS ----------------

@app.route("/view-students")
@login_required("admin")
def view_students():

    # Sort records by Branch, Year and Semester
    sorted_students = sorted(
        students.values(),
        key=lambda s: (
            s["branch"].lower(),
            s["year"].lower(),
            s["semester"].lower(),
            s["name"].lower()
        )
    )

    # Group students by Branch, Year and Semester
    grouped_students = {}

    for student in sorted_students:

        branch = student["branch"]
        year = student["year"]
        semester = student["semester"]

        if branch not in grouped_students:
            grouped_students[branch] = {}

        if year not in grouped_students[branch]:
            grouped_students[branch][year] = {}

        if semester not in grouped_students[branch][year]:
            grouped_students[branch][year][semester] = []

        grouped_students[branch][year][semester].append(student)

    return render_template(
        "view_students.html",
        grouped_students=grouped_students,
        total=len(students)
    )


# ---------------- DELETE STUDENT ----------------

@app.route("/delete-student/<student_id>", methods=["POST"])
@login_required("admin")
def delete_student(student_id):

    students.pop(student_id, None)

    return redirect(url_for("view_students"))


# ---------------- STUDENT DASHBOARD ----------------

@app.route("/student-dashboard")
@login_required("student")
def student_dashboard():

    student_id = session.get("student_id")

    student = students.get(student_id)

    if not student:
        session.clear()
        return redirect(url_for("student_login"))

    return render_template(
        "student_dashboard.html",
        student=student
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
