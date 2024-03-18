from flask import Flask,render_template,jsonify,request
from datetime import datetime, timedelta
import mysql.connector
from PIL import Image
import secrets
import jwt
import os

app = Flask(__name__)
SECRET_KEY = '860df52f8a4dea4e3e362b1532c09067a2ce2cace93f8b0343699f3888856299'
TOKEN = 'token'
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "galeri_ukk"
}
def connect_db():
    try:
        conn = mysql.connector.connect(**db_config)
    except Exception as e:
        print(f"{e} \n --- Error --- ")
        exit()
    cursor = conn.cursor()
    return cursor,conn
@app.get("/")
def home():
    return render_template("index.html")

@app.post("/images/create")
def create_images():
    pass

@app.get("/login")
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.post("/sign_in")
def sign_in():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    is_correct_username = secrets.compare_digest(nama, username_receive)
    is_correct_password = secrets.compare_digest(password, password_receive)
    if not is_correct_username or not is_correct_password:
        return jsonify({
            "result":"fail", "msg":"Cannot find user with that username and password combination",
        })
    payload={
        "id":username_receive,
        "exp": datetime.utcnow() + timedelta (seconds=Expired__Seconds),
    }

if __name__ == "__main__":
    app.run("0.0.0.0",5000,True)