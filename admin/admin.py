from flask import Blueprint,request,redirect,url_for,flash,render_template,session,g
import sqlite3

admin = Blueprint("admin" , __name__ , static_folder="static" , template_folder="templates")

menu = [{'url': '.index', 'title': 'PANEL'},
        {'url':'.listpubs','title': "LIST OF ARTICLES"},
        {'url': '.list_users' , 'title' : "LIST OF USERS"},
        {'url': 'index' , 'title' : "GO TO MAIN PAGE"},
        {'url': '.logout', 'title': 'LOGOUT'}]

db = None
@admin.before_request
def before_request():
    global db
    db = g.get("link_db")

@admin.teardown_request
def teardown_request(request):
    global db
    db= None
    return request

def login_admin():
    session["admin_logged"] = 1

def is_logged():
    return bool(session.get("admin_logged"))

def logout_admin():
    session.pop("admin_logged")

@admin.route("/")
def index():
    if not is_logged():
        return redirect(url_for(".login"))
    return render_template("admin/index.html", menu=menu , title = "Admin-panel")

@admin.route("/login" , methods = ["POST","GET"])
def login():
    if is_logged():
        return redirect(url_for(".index"))

    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["psw"] == "12345":
            login_admin()
            return redirect(url_for(".index")) # точка означет что функцию представления следует брать из Blueprint, а не глобальную
        else:
            flash("Incorrect pair user/password" , "error")

    return render_template("admin/login.html",title="Admin-panel")

@admin.route("/logout", methods = ["POST","GET"])
def logout():
    if not is_logged():
        return redirect(url_for(".login"))

    logout_admin()
    return redirect(url_for(".login"))

@admin.route("/listpubs")
def listpubs():
    if not is_logged():
        return redirect(url_for(".login"))

    lst = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            lst = cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting articles from db {e}")

    return render_template("admin/listpubs.html" , title="List of articles" , menu=menu , lst=lst)

@admin.route("/list_users")
def list_users():
    if not is_logged():
        return redirect(url_for(".login"))
    lst = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name,email FROM users ORDER BY time desc")
            lst = cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting articles from db {e}")

    return render_template("admin/listusers.html", title="List of users", menu=menu, lst=lst)


