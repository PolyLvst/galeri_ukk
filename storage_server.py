from flask import Flask, redirect,render_template,jsonify,request,send_file, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dotenv import load_dotenv
from PIL import Image
import jwt
import os

load_dotenv(override=True)

SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN = 'token'

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# JWT Token exp
Expired_Seconds = 60 * 60 * 24 # 24 Hour / 86400 seconds
allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
# Filter extensi file yang diterima
def check_ext(extension:str):
    # Cek dengan ekstensi yg boleh
    return True if extension in allowed_ext else False

# Jika baru pertama kali menjalankan kita harus cek dulu apakah folder sudah lengkap
def check_folders():
    print("Checking folders ... ")
    check = ["./static/photos","./static/profile_pics"]
    for path in check:
        if not os.path.exists(path=path):
            # Buat folder jika tidak ada
            os.makedirs(name=path)

@app.post("/api/images/save")
def save_image():
    # Ambil cookie file
    token_receive = request.cookies.get(TOKEN)    
    try:
        # Lihat isi cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['username']
        # Payload terverifikasi
        pass
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        # Tidak ada token atau belum login
        return "Unauthorized",401
    # Jika payload terverifikasi maka kode dibawah akan di execute
    # Cek jika file telah terupload
    if 'file_give' in request.files:
        file = request.files.get('file_give')
        file_path_receive = request.form.get('file_path')

        # Amankan filename dari karakter spesial
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[-1].replace('.','')
        if not check_ext(extension):
            return jsonify({"msg":"Extension not allowed"}),406 # Not acceptable
        unique_format = f"{filename}"
        file_path = f"{file_path_receive}/{unique_format}"
        file_save_path = f"./static/{file_path}"

        # Simpan file ke folder temp
        file.save(file_save_path)

        return {"msg":"Photo uploaded"},200
    else:
        # Foto tidak terupload
        return {"msg":"No image uploaded"},404 # Not found
    
@app.post("/api/images/delete")
def delete_image():
    # Ambil cookie file
    token_receive = request.cookies.get(TOKEN)
    try:
        # Lihat isi cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['username']
        # Payload terverifikasi
        pass
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        # Tidak ada token atau belum login
        return "Unauthorized",401
    # Jika payload terverifikasi maka kode dibawah akan di execute
    file_path = request.form.get("file_path")
    file_location = f"./static/{file_path}"

    if os.path.exists(file_location):
        os.remove(file_location)
        return {"msg":"Item deleted"},200
    else:
        return {"msg":"Not found"},404

if __name__ == "__main__":
    # Cek apakah folder tersedia
    check_folders()
    app.run("0.0.0.0",5500,True)