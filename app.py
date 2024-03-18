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

if __name__ == "__main__":
    app.run("0.0.0.0",5000,True)