from typing import Union
from flask import Flask, redirect,render_template,jsonify,request,send_file, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from github import Github
from github import Auth
from PIL import Image
import hashlib
import secrets
import jwt
import os

load_dotenv(override=True)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")
SALT_HASH = os.environ.get("SALT_HASH")
GH_USER = os.environ.get("GH_USER")
GH_PW = os.environ.get("GH_PW")
GH_TOKEN = os.environ.get("GH_TOKEN")
TOKEN = 'token'

# using an access token
StorageRepo = "ambatron-dev/storage-ukk"
StorageURL = "https://ambatron-dev.github.io/storage-ukk/"

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['PROFILE'] = './static/profile_pics'
# app.config['PHOTOS'] = './static/photos'

# MongoDB
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
# Collection
table_users = db.users
table_photos = db.photos

# JWT Token exp
Expired_Seconds = 60 * 60 * 24 # 24 Hour / 86400 seconds
allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
# Filter file yang diterima
def not_allowed_file(filename:str):
    # Mencari titik terakhir pada filename lalu ambil index terakhirnya dan cek dengan ekstensi yg boleh
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext

# Login ke github dengan token yang didapat dari github settings developer
def login_github():
    auth = Auth.Token(token=GH_TOKEN)
    return Github(auth=auth)

# Upload file ke github atau update
def upload_file_or_update(path:str,message:str,content:Union[str,bytes],update=False,branch:str="main"):
    g = login_github()
    repo = g.get_repo(StorageRepo)
    if update:
        contents = repo.get_contents(path)
        repo.update_file(path=contents.path, message=message, content=content, sha=contents.sha, branch=branch)
    else:
        repo.create_file(path=path,message=message,content=content,branch=branch)
    g.close()

# Jika baru pertama kali menjalankan kita harus cek dulu apakah folder sudah lengkap
def check_folders():
    print("Checking folders ... ")
    check = ["./static/temp/photos","./static/temp/profile_pics"]
    for path in check:
        if not os.path.exists(path=path):
            # Buat folder jika tidak ada
            os.makedirs(name=path)

# -------------- ENDPOINT -------------- #

@app.get("/")
def home():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))

# Endpoint ambil path images
@app.get("/api/images") # Optional args skip and limit, contoh : /api/images?skip=0&limit=10
def get_images():
    skip = int(request.args.get("skip",default=0))
    limit = int(request.args.get("limit",default=20))
    photos = list(table_photos.find({},{'_id':False}).skip(skip=skip).limit(limit=limit))
    return jsonify({"data":photos})

@app.post("/api/images/create")
def create_images():
    # Ambil cookie file
    token_receive = request.cookies.get(TOKEN)
    try:
        # Lihat isi cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['id']
        # Cek jika file telah terupload
        if 'file_give' in request.files:
            file = request.files['file_give']
            # Amankan filename dari karakter spesial
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            unique_format = f"{username}-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.{extension}"
            file_path = f"photos/{unique_format}"
            file_save_path = f"./static/temp/{file_path}"
            # Cek apakah folder tersedia
            check_folders()
            # Simpan file ke folder temp
            file.save(file_save_path)
            
            # Open file sebagai binary
            with open(file_save_path, "rb") as image:
                f = image.read()
                image_data = bytearray(f)
                # Upload ke github storage
                upload_file_or_update(file_path,f"By {username}",bytes(image_data))
            # Delete temp file
            os.remove(file_save_path)
            doc = {
                "username": username,
                "image": StorageURL+file_path,
            }
            # Masukkan url ke database
            table_photos.insert_one(doc)
            return {"msg":"Photo uploaded"}
        else:
            # Foto tidak terupload
            return {"msg":"No image uploaded"}
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        # Tidak ada token atau belum login
        return redirect(url_for('home'))

# Login page
@app.get("/login")
def login_fn():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.post('/api/sign_up')
def sign_up():
    # Default foto profil untuk user
    default_profile_pic = StorageURL+"profile_pics/default.png"
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    bio_receive = request.form.get('bio_give')
    # Cek apakah username telah dipakai
    user_from_db = table_users.find_one({"username":username_receive})
    if user_from_db:
        return jsonify({"msg":"username telah dipakai"})
    # Hash password
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # Salt password agar lebih aman
    salted_password = SALT_HASH+password_hash
    doc = {
        "username": username_receive,
        "password": salted_password,
        "bio": bio_receive,
        "profile_pic": default_profile_pic,
    }
    # Masukkan ke database
    table_users.insert_one(doc)
    return jsonify({'result':'success'})

# Sign in untuk mendapat token JWT
@app.post("/api/sign_in")
def sign_in():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    # Mencari user dengan username tsb
    user_from_db = table_users.find_one({"username":username_receive})
    # Mengubah string ke bentuk hash
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # Menambah salt pada awal hash
    salted_password = SALT_HASH+password_hash
    # Compare digest digunakan untuk mencegah timing attack
    is_correct_username = secrets.compare_digest(user_from_db.get("username"), username_receive)
    is_correct_password = secrets.compare_digest(user_from_db.get("password"), salted_password)
    if not is_correct_username or not is_correct_password:
        # Login salah
        return jsonify({
            "result":"fail", "msg":"Cannot find user with that username and password combination",
        })
    # Buat isi token
    payload={
        "id":username_receive,
        "exp": datetime.now() + timedelta (seconds=Expired_Seconds),
    }
    # Buat token lalu encode
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"result": "success","token": token})

if __name__ == "__main__":
    app.run("0.0.0.0",5000,True)