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
# JWT Token exp
Expired_Seconds = 60 * 60 * 24 # 24 Hour / 86400 seconds
allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
def not_allowed_file(filename:str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext

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

# Endpoint ambil path images
@app.get("/images/")
def get_images():
    curr,conn = connect_db()
    sql = "SELECT * FROM photos"
    curr.execute(sql)
    data = curr.fetchall()
    curr.close()
    conn.close()
    response = [{"id":i[0],
                 "foto_path":i[1],
                 "user_id":i[2]} for i in data] 
    return response

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
        "exp": datetime.utcnow() + timedelta (seconds=Expired_Seconds),
    }

if __name__ == "__main__":
    app.run("0.0.0.0",5000,True)