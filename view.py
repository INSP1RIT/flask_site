from app import app
from FDataBase import FDataBase
from flask import render_template, url_for, request, flash, session, redirect, abort, g, \
    make_response
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from app import login_manager
from flask_login import login_required, login_user, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm,RegistarationForm

menu = [{"name": "Installation", "url": "install-flask"},
        {"name": "First Application", "url": "first-app"},
        {"name": "Feedback", "url": "contact"}]


def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource("sq_db.sql", 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().from_db(user_id, dbase)


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


'''@app.route("/")
@app.route("/index")
def index():
    print(url_for("index"))
    return render_template("index.html", menu=menu)'''


@app.route("/")
def index():
    # db = get_db()
    # dbase = FDataBase(db)
    return render_template("index.html", menu=dbase.get_menu(), posts=dbase.get_posts_announce())


@app.route("/about")
def about():
    print(url_for("about"))
    return render_template("about.html", title="About site", menu=menu)


# @app.route("/profile/<username>")
# def profile(username):
#     if "userLogged" not in session or session["userLogged"] != username:
#         abort(401)
#     return f"Profile of user: {username}"


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if len(request.form["username"]) > 2:
            flash("Message send", category="success")
        else:
            flash("Error while sending", category="error")

    return render_template("contact.html", title="Feedback", menu=menu)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template("page404.html", title="Page not found", menu=menu), 404


# for older lessons
"""@app.route("/login" , methods = ["POST" , "GET"]) 
def login():
    if "userLogged" in session:
        return redirect(url_for("profile",username = session["userLogged"]))
    elif request.method == "POST" and request.form["username"] == "inspirit" and request.form["psw"] == "123":
        session["userLogged"] = request.form["username"]
        return redirect(url_for("profile",username = session["userLogged"]))
    return render_template("login.html" , title = "Authorization" , menu=menu)"""


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:  # перейти на страницу профиля если данный атрибут возвращает True
        return redirect(url_for("profile"))
    form = LoginForm()
    if form.validate_on_submit(): #проверяет были ли отправлены данные post запросом
        if request.method == "POST":
            user = dbase.get_user_by_email(form.email.data)
            if user and check_password_hash(user['psw'], form.psw.data):
                user_login = UserLogin().create(user)
                rm = form.remember.data
                login_user(user_login, remember=rm)
                return redirect(request.args.get("next") or url_for("profile"))
            flash("Incorrect pair user/login", "error")
    return render_template("login.html", menu=dbase.get_menu(), title="Authorization", form=form)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistarationForm()
    if form.validate_on_submit():
            hash = generate_password_hash(form.psw.data)
            res = dbase.add_user(form.name.data, form.email.data, hash)
            if res:
                flash("You were successfully registered", "success")
                return redirect(url_for("login"))
            else:
                flash("Error of adding in DB", "error")
    return render_template("register.html", menu=dbase.get_menu(), title="Registration" , form=form)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()


@app.route("/add_post", methods=["POST", "GET"])
def add_post():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["post"]) > 10:
            res = dbase.addPost(request.form["name"], request.form["post"], request.form["url"])
            if not res:
                flash("Error of adding article", category="error")
            else:
                flash("Article successfully added", category="success")
        else:
            flash("Error of adding article", category="error")
    return render_template("add_post.html", menu=dbase.get_menu(), title="Article adding")


@app.route("/post/<alias>")
@login_required
def show_post(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.get_post(alias)
    if not title:
        abort(404)
    return render_template("post.html", menu=dbase.get_menu(), title=title, post=post)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logout from profile", category="success")
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", menu=dbase.get_menu(), title="Profile")


@app.route("/userava")
@login_required
def userava():
    img = current_user.get_avatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers["Content-Type"] = "img/png"
    return h


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file and current_user.verify_exit(file.filename):
            try:
                img = file.read()
                res = dbase.update_user_avatar(img, current_user.get_id())
                if not res:
                    flash("Error of updating avatar", "error")
                flash("Avatar updated", "success")
            except FileNotFoundError as e:
                flash("Error of reading file", "error")
        else:
            flash("Error of updating avatar", "error")

    return redirect(url_for("profile"))


@app.route("/info")
def info():
    db = get_db()
    dbase = FDataBase(db)
    content = render_template("index.html", menu=dbase.get_menu(), posts=[])
    res = make_response(content)
    res.headers["Content-Type"] = "text/plain"
    res.headers["Server"] = "flaskapp"
    return res


@app.route("/transfer")
def transfer():
    return redirect(url_for("index"), 301)


@app.route("/test_login")
def logins():
    logged = request.cookies.get("logged")
    log = logged if logged else ""

    res = make_response(f"<h1>Authorization form</h1><p>logged:{log}</p>")
    res.set_cookie("logged", "yes")
    return res


@app.route("/test_logout")
def logout1():
    res = make_response("<p>You are not authorized anymore!</p>")
    res.set_cookie("logged", "", 0)
    return res


@app.route("/total_visits")
def total():
    session.permanent = True
    session["visits"] = session.get("visits", 0) + 1
    return f"<h1>Visits Page</h1><p>Total visits: {session['visits']}"

# with app.test_request_context():
# print(url_for("index"))
