from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = "bookmarks.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            link_name TEXT NOT NULL,
            link_url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("fname", "").strip()

    if not username:
        flash("Username cannot be empty", "error")
        return redirect(url_for("index"))

    session["username"] = username
    flash(f"Welcome, {username}!", "success")
    return redirect(url_for("bookmarks"))


@app.route("/bookmarks")
def bookmarks():
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    data = conn.execute(
        "SELECT * FROM bookmarks WHERE username = ? ORDER BY id DESC",
        (session["username"],)
    ).fetchall()
    conn.close()

    return render_template("bookmarks.html", data=data, user=session["username"])


@app.route("/add")
def add():
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("index"))

    return render_template("add_form.html")


@app.route("/insert", methods=["POST"])
def insert():
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("index"))

    link_name = request.form.get("link_n", "").strip()
    link_url = request.form.get("link", "").strip()

    if not link_name or not link_url:
        flash("Both fields are required", "error")
        return redirect(url_for("add"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO bookmarks (username, link_name, link_url) VALUES (?, ?, ?)",
        (session["username"], link_name, link_url)
    )
    conn.commit()
    conn.close()

    flash("Bookmark added successfully", "success")
    return redirect(url_for("bookmarks"))


@app.route("/delete", methods=["POST"])
def delete():
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("index"))

    bookmark_id = request.form.get("id")

    conn = get_db_connection()
    conn.execute(
        "DELETE FROM bookmarks WHERE id = ? AND username = ?",
        (bookmark_id, session["username"])
    )
    conn.commit()
    conn.close()

    flash("Bookmark deleted successfully", "success")
    return redirect(url_for("bookmarks"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)