import sqlite3
import math
import time
import re
from flask import url_for

class FDataBase:
    def __init__(self,db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        sql = """SELECT * from MAINMENU"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Error reading from db")
        return []

    def addPost(self,title,text,url):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res["count"] > 0:
                print("Article already exists")
                return False

            base = url_for('static', filename="images_html")
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL,?,?,?,?)", (title,text,url,tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error of adding article in DB {e}")
            return False
        return True

    def get_post(self,alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE url LIKE '{alias}'")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Error of getting article from BD {e}")
        return False,False

    def get_posts_announce(self):
        sql = """SELECT id,text,title,url FROM posts  ORDER BY time DESC"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Error reading from db")
        return []

    def add_user(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?,NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False
        return True

    def get_user(self,user_id):
        try:
            self.__cur.execute(f"SELECT * FROM  users WHERE id = {user_id}")
            res = self.__cur.fetchone()
            if not res:
                print("User not found")
                return False
            return res
        except sqlite3.Error as e:
            print("Error reading from db" + str(e))

        return False

    def get_user_by_email(self,email):
        try:
            self.__cur.execute(f"SELECT * FROM  users WHERE email = '{email}'")
            res = self.__cur.fetchone()
            if not res:
                print("User not found")
                return False
            return res
        except sqlite3.Error as e:
            print(f"Error reading from db {e}")

        return False

    def update_user_avatar(self,avatar,user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users set avatar = ? WHERE id = ?", (binary,user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error of reading from DB: {e}")
            return False
        return True

