from flask import Flask
from config import Configuration
import sqlite3
import os
from flask_login import LoginManager
from admin.admin import admin

app = Flask(__name__)
app.config.from_object(Configuration)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))
app.register_blueprint(admin,url_prefix="/admin")

login_manager = LoginManager(app)
login_manager.login_view = "login" # атрибуту логин менеджера присваивается функция-обработчик, которая вызывается когда пользователь посещает закрытую страницу и будет переадресован когда ее посещает
login_manager.login_message = "Please, log in to view closed pages"
login_manager.login_message_category = "success"