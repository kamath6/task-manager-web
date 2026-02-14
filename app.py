from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey123"


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            conn.close()
            return "Username already exists!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials!"

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        cursor.execute(
            "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
            (session["user_id"], title)
        )
        conn.commit()

    cursor.execute(
        "SELECT id, title, completed FROM tasks WHERE user_id=?",
        (session["user_id"],)
    )
    tasks = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", tasks=tasks)


@app.route("/complete/<int:task_id>")
def complete(task_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET completed=1 WHERE id=? AND user_id=?",
        (task_id, session["user_id"])
    )

    conn.commit()
    conn.close()
    return redirect("/dashboard")


@app.route("/delete/<int:task_id>")
def delete(task_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=? AND user_id=?",
        (task_id, session["user_id"])
    )

    conn.commit()
    conn.close()
    return redirect("/dashboard")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
