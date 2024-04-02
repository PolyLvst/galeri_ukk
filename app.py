import math
import random
import re
import string
from typing import Union
from bson import ObjectId
from flask import Flask, redirect,render_template,jsonify,request, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
import requests
import hashlib
import secrets
import jwt
import os

load_dotenv(override=True)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")
SALT_HASH = os.environ.get("SALT_HASH")
TOKEN = 'token'

IMAGES_THUMBNAIL_SIZE = (300,300)
image_maxsize = 1 #Mb

# using an access token
StorageURL = os.environ.get("StorageURL")# "http://localhost:5500/"
# Default foto profil untuk user
default_profile_pic = "../static/defaults/default-profile-pic.png"

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
table_saved_collection = db.saved_collection
table_bookmarks = db.bookmarks
table_liked = db.liked
table_comments = db.comments

# JWT Token exp
Expired_Seconds = 60 * 60 * 24 # 24 Hour / 86400 seconds
allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
# Filter extensi file yang diterima
def check_ext(extension:str):
    # Cek dengan ekstensi yg boleh
    return True if extension in allowed_ext else False

# Hemat storage
def limit_image_size(image_path, max_size_mb=1):
    # Check the file size
    if os.path.getsize(image_path) <= max_size_mb * 1024 * 1024:  # Convert MB to bytes
        return True  # File size is within the limit
    # Open the image
    image = Image.open(image_path)
    # Kalkulasi dimensi untuk mecocokkan dengan maximum file size
    new_width = int(image.size[0] * (max_size_mb * 1024 * 1024 / os.path.getsize(image_path)) ** 0.5)
    new_height = int(image.size[1] * (max_size_mb * 1024 * 1024 / os.path.getsize(image_path)) ** 0.5)
    # Resize fotonya
    resized_image = image.resize((new_width, new_height))
    # Save foto
    resized_image.save(image_path)
    return True

# Upload file ke storage atau update
def upload_file_to_storage(file_path_static:str,content:str,token:str):
    # File path static contohnya bisa photos atau profile_pics
    ApiStorage = StorageURL+"api/images/save"
    response = requests.post(
        url=ApiStorage,
        files={"file_give":open(content,"rb")},
        data={"file_path":file_path_static},
        cookies={"token": token}
    )
    if response.status_code != 200:
        print(f"Something went wrong : {response.status_code} | {response.text} | Cookie {token}")
        raise Exception

# Delete file dari storage
def delete_file_from_storage(file_path_repo:str,token:str):
    # File path static contohnya bisa photos atau profile_pics
    ApiStorage = StorageURL+"api/images/delete"
    response = requests.post(
        url=ApiStorage,
        data={"file_path":file_path_repo},
        cookies={"token": token}
    )
    if response.status_code != 200:
        print(f"Something went wrong : {response.status_code} | {response.text} | Cookie {token}")
        raise Exception

# Generate thumbnail
def generate_thumbnail(input_image_path, output_thumbnail_path, thumbnail_size=(300, 300)):
    try:
        # Open the image file
        image = Image.open(input_image_path)
        # Generate the thumbnail
        image.thumbnail(thumbnail_size)
        # Save the thumbnail to the output path
        image.save(output_thumbnail_path)
        print(f"Thumbnail generated and saved to '{output_thumbnail_path}'")
    except Exception as e:
        print("Error generating thumbnail:", e)

# Jika baru pertama kali menjalankan kita harus cek dulu apakah folder sudah lengkap
def check_folders():
    print("Checking folders ... ")
    check = ["./static/temp/photos","./static/temp/profile_pics"]
    for path in check:
        if not os.path.exists(path=path):
            # Buat folder jika tidak ada
            os.makedirs(name=path)
            
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def hash_salt_password(password:str):
    # Hash password
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Salt password agar lebih aman
    salted_password = SALT_HASH+password_hash
    return salted_password

# Jika database tidak ada user superadmin
def check_superadmin():
    superadmin = table_users.find_one({"is_superadmin":True})
    if not superadmin:
        pw = generate_password(length=31)
        salted_password = hash_salt_password(pw)
        doc = {
            "username":"helios-ruler",
            "password":salted_password,
            "bio": "I'am the ruler of the world",
            "profile_pic": default_profile_pic,
            "gender": "N/A",
            "is_superadmin": True,
        }
        table_users.insert_one(doc)
        print(f"# ------------------ #")
        print(f"# Generated superadmin")
        print(f"# User : helios-ruler")
        print(f"# Password : {pw}")

def get_pagination_count(items_per_page=20,page=1,total_items=1):
    # total_items = table_photos.count_documents({"username":username})  # Total number of items in the collection
    # total_items = table_photos.count_documents({})  # Total number of items in the collection
    total_pages = math.ceil(total_items / items_per_page)

    skip = (page - 1) * items_per_page

    # Calculate end page, previous page, and next page
    end_page = total_pages
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return skip,prev_page,next_page,end_page

def search_images_query(query:str=''):
    regex_pattern = re.compile(query, re.IGNORECASE)
    results = list(table_photos.find({'$or': [
        {'title': {'$regex': regex_pattern}},
        {'kategori': {'$regex': regex_pattern}},
        {'deskripsi': {'$regex': regex_pattern}},
        {'username': {'$regex': regex_pattern}}
    ]}).sort("_id",-1))
    return results

def count_like_images(posts:Union[list,dict],username:str):
    user_data = table_users.find_one({"username":username})
    user_choose_collection = user_data.get('choose_collection','My Collection')
    collection = table_saved_collection.find_one({"username":username,"collection_name":user_choose_collection})
    collection_id = str(collection.get('_id'))
    if isinstance(posts,list):
        idx = 0
        for post in posts:
            post_id = str(post['_id'])
            posts[idx]['count_like'] = table_liked.count_documents({'post_id':post_id})
            posts[idx]['like_by_me'] = bool(table_liked.find_one({'post_id':post_id,'username':username}))

            bookmark_by_me = table_bookmarks.find_one({'post_id':post_id,'username':username,'collection_id':collection_id})
            posts[idx]['bookmark_by_me'] = bool(bookmark_by_me)
            idx+=1
    else:
        post_id = str(posts.get('_id'))
        posts['like_by_me'] = bool(table_liked.find_one({'post_id':post_id,'username':username}))
        posts['bookmark_by_me'] = bool(table_bookmarks.find_one({'post_id':post_id,'username':username,'collection_id':collection_id}))
        posts['count_like'] = table_liked.count_documents({'post_id':post_id})

    return posts

def images_social(posts:Union[list,dict],username:str):
    user_data = table_users.find_one({"username":username})
    user_choose_collection = user_data.get('choose_collection','My Collection')
    collection = table_saved_collection.find_one({"username":username,"collection_name":user_choose_collection})
    collection_id = str(collection.get('_id'))
    if isinstance(posts,list):
        idx = 0
        for post in posts:
            post_id = str(post['_id'])
            posts[idx]['like_by_me'] = bool(table_liked.find_one({'post_id':post_id,'username':username}))
            posts[idx]['bookmark_by_me'] = bool(table_bookmarks.find_one({'post_id':post_id,'username':username,'collection_id':collection_id}))
            idx+=1
    else:
        post_id = str(posts.get('_id'))
        posts['like_by_me'] = bool(table_liked.find_one({'post_id':post_id,'username':username}))
        posts['bookmark_by_me'] = bool(table_bookmarks.find_one({'post_id':post_id,'username':username,'collection_id':collection_id}))
    return posts

def mask_long_string(original_string:str,max_length:int=17):
    # 12345678901234567
    # My Collection From Last Year -> My Collection Fro...
    if len(original_string) > max_length:
        # Trim the original string to the maximum length and add "..."
        trimmed_string = original_string[:max_length - 3] + "..."
        return trimmed_string
    else:
        return original_string

# -------------- ENDPOINT -------------- #

@app.get("/")
def home():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    items_per_page_home = 20

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=items_per_page_home, type=int) # Number of items per page
    query = request.args.get('query', '')
    collection = request.args.get('collection', '')
    args_nav = "%26" # &

    if query != '':
        # Untuk tombol navigasi bawah
        args_nav = f'{args_nav}query={query}'
        results = search_images_query(query=query)
        total_items = len(results)  # Total number of items in the collection
        
        skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)
        # Batasi sesuai items per page
        skip = (page - 1) * per_page
        limit = skip + per_page
        photos = results[skip:limit]
    elif collection != '':
        # Untuk tombol navigasi bawah
        args_nav = f'{args_nav}collection={collection}'
        bookmarks_list = list(table_bookmarks.find({"collection_id":collection}).sort("_id",-1))
        total_items = len(bookmarks_list)
        skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)
        # Batasi sesuai items per page
        skip = (page - 1) * per_page
        limit = skip + per_page
        bookmarks_list = bookmarks_list[skip:limit]
        post_ids = [ObjectId(bookmark['post_id']) for bookmark in bookmarks_list]
        photos = list(table_photos.find({"_id": {"$in": post_ids}}).sort("_id",-1))
    else:
        args_nav = ""
        total_items = table_photos.count_documents({})
        skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)

        # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
        photos = list(table_photos.find({}).sort("_id",-1).skip(skip=skip).limit(limit=per_page))        
    photos = images_social(posts=photos,username=username)
    idx = 0
    for doc in photos:
        photos[idx]["_id"] = str(doc["_id"])
        idx += 1
    return render_template('index.html',
                           images=photos,
                           current_username=username,
                           is_superadmin=is_superadmin,
                           curr_page=page,
                           prev_page=prev_page,
                           next_page=next_page,
                           end_page=end_page,
                           args_nav=args_nav,
                           query=query)

@app.get("/detail/<post_id>")
def get_detail_page(post_id=None):
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    from_page = request.args.get("from_page","/")
    if not post_id or len(post_id) < 24:
        return redirect(url_for('home'))
    photo = table_photos.find_one({"_id":ObjectId(post_id)})
    if not photo:
        return redirect(url_for('home'))
    comments = table_comments.find({"post_id":post_id}).sort("_id",-1)
    photo = count_like_images(photo,username)
    poster_user = table_users.find_one({"username":photo.get('username')})
    return render_template("comment.html",
                           photo=photo,
                           poster_user=poster_user,
                           current_username=username,
                           is_superadmin=is_superadmin,
                           comments=comments,
                           from_page=from_page)

@app.post("/api/comment/create")
def create_comment():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    post_id_receive = request.form.get("post_id_give")
    comment_receive = request.form.get("comment_give")
    commenter = table_users.find_one({"username":username})
    
    doc = {
        "username":username,
        "post_id":post_id_receive,
        "comment":comment_receive,
        "profile_pic":commenter.get("profile_pic"),
        "date":datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }

    table_comments.insert_one(doc)
    return jsonify({"msg":"Comment added","status":"created"})

@app.delete("/api/comment/delete")
def delete_comment():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    comment_id_receive = request.form.get("comment_id_give")
    # Ambil data dari database
    result = table_comments.find_one({"_id":ObjectId(comment_id_receive)})
    if not result:
        return jsonify({"msg":"Comment not found"}),404 # Not found
    if is_superadmin:
        # Jika superadmin maka bolehkan
        pass
    # Jika owner foto tersebut berbeda maka tidak akan di hapus
    elif result.get("username") != username:
        return jsonify({"msg":"Comment owner is different"}),403 # Forbidden

    # Delete dari mongodb
    table_comments.delete_one({"_id":ObjectId(comment_id_receive)})
    return jsonify({"msg":"Item deleted","status":"deleted"})

@app.get("/api/bookmarks")
def bookmarks():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    bookmarks_collection_amount = 3
    bookmarks_preview_amount = 4
    # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
    bookmarks = list(table_bookmarks.find({"username":username},{"_id":False, "bookmarks": {"$slice": bookmarks_preview_amount}}).sort("_id",-1).limit(limit=bookmarks_collection_amount))
    return jsonify({"data":bookmarks})
    # return render_template('bookmarks.html')

@app.post("/api/collection/create")
def create_collection():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    collection_name_receive = request.form.get('collection_name_give','')
    also_choose_new_collection = request.form.get('choose_created_collection','true')
    if collection_name_receive == '':
        return jsonify({"msg":"Missing field","status":"not found"}),404 # Not found
    collection_exist = table_saved_collection.find_one({"username":username,"collection_name":collection_name_receive})
    if collection_exist:
        return jsonify({"msg":"Collection already existed","status":"conflict"}),409 # Conflict
    doc = {
        "username":username,
        "collection_name":collection_name_receive,
        "date":datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    if also_choose_new_collection == "true":
        update_collection_choose = {
            "choose_collection":collection_name_receive
        }
        table_users.update_one({"username":username},{"$set":update_collection_choose})
    table_saved_collection.insert_one(doc)
    return jsonify({"msg":"Collection saved","status":"created"})

@app.put("/api/collection/select")
def update_collection_choose():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    collection_id_receive = request.form.get('collection_id_give','')
    if collection_id_receive == '':
        return jsonify({"msg":"Missing field","status":"not found"}),404 # Not found
    collection_exist = table_saved_collection.find_one({"username":username,"_id":ObjectId(collection_id_receive)})
    if not collection_exist:
        return jsonify({"msg":"Collection not found","status":"not found"}),404 # Not found
    update_collection_choose = {
        "choose_collection":collection_exist.get("collection_name")
    }
    table_users.update_one({"username":username},{"$set":update_collection_choose})
    return jsonify({"msg":"Collection choosed","status":"updated"})

@app.delete("/api/collection/delete")
def delete_collection():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    collection_id_receive = request.form.get('collection_id_give','')
    if collection_id_receive == '':
        return jsonify({"msg":"Missing field","status":"not found"}),404 # Not found
    collection_exist = table_saved_collection.find_one({"username":username,"_id":ObjectId(collection_id_receive)})
    if not collection_exist:
        return jsonify({"msg":"Collection not found","status":"not found"}),404 # Not found
    # Delete bookmarks with collection_id
    table_bookmarks.delete_many({"username":username,"collection_id":str(collection_exist.get('_id'))})
    table_saved_collection.delete_one({"username":username,"collection_name":collection_exist.get('collection_name')})
    return jsonify({"msg":"Collection deleted","status":"deleted"})

@app.post("/api/bookmark")
def update_bookmark():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    post_id = request.form.get('post_id_give','')
    # Cari user
    user = table_users.find_one({'username':username})
    # Cari koleksi id di user choose collection
    collection_id = table_saved_collection.find_one({"username":username,"collection_name":user.get("choose_collection")})
    # Cari bookmark dengan koleksi tsb
    bookmark = table_bookmarks.find_one_and_delete({"username":username,"post_id":post_id,"collection_id":str(collection_id.get("_id"))})
    image = table_photos.find_one({"_id":ObjectId(post_id)})
    if bookmark:
        return jsonify({"msg":"Bookmark deleted","status":"deleted"})
    if not collection_id:
        return jsonify({"msg":"Collection not found","status":"not found"}),404
    if not image:
        return jsonify({"msg":"Post not found","status":"not found"}),404
    doc = {
        "image":image.get('image'),
        "image_thumbnail":image.get('image_thumbnail'),
        "post_id":post_id,
        "username":username,
        "collection_id":str(collection_id.get("_id")),
        "date":datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    table_bookmarks.insert_one(doc)
    return jsonify({"msg":"Bookmarked","status":"created"})

@app.post("/api/like")
def update_like():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    post_id = request.form.get('post_id_give','')

    liked = table_liked.find_one_and_delete({"username":username,"post_id":post_id})
    if liked:
        return jsonify({"msg":"Like deleted","status":"deleted"})
    
    doc = {
        "post_id":post_id,
        "username":username,
        "date":datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    table_liked.insert_one(doc)
    return jsonify({"msg":"Liked","status":"created"})

@app.get("/bookmarks")
def bookmarks_page():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['username']
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    items_per_page = 4

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=items_per_page, type=int) # Number of items per page

    total_items = table_saved_collection.count_documents({"username":username})
    skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)
    bookmarks_preview_amount = 4
    # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
    collection_saved = list(table_saved_collection.find({"username":username}).sort("_id",-1).skip(skip).limit(limit=per_page))
    user_choose_collection = table_users.find_one({"username":username})
    for collection in collection_saved:
        bookmarks_list = list(table_bookmarks.find({"collection_id":str(collection['_id']),"username":username}).sort("_id",-1).limit(limit=bookmarks_preview_amount))
        if not bookmarks_list:
            print(collection['collection_name']," # --- Not found")
            # Maka koleksi masih baru atau kosong
            continue
        previews = []
        for bookmark in bookmarks_list:
            previews.append({
                "image_thumbnail": bookmark.get('image_thumbnail'),
                "image": bookmark.get('image'),
            })
        collection['previews'] = previews
    idx = 0
    for doc in collection_saved:
        collection_saved[idx]["_id"] = str(doc["_id"])
        idx += 1    
    return render_template('bookmarks.html',
                        collections =collection_saved,
                        curr_page = page,
                        end_page = end_page,
                        prev_page = prev_page,
                        next_page = next_page,
                        current_username=username,
                        user_choose_collection=user_choose_collection.get('choose_collection'))

@app.get("/api/search")
def search():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    query = request.args.get('query', '')
    items_per_page = 20

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=items_per_page, type=int) # Number of items per page
    args_nav = "%26" # &
    # Untuk tombol navigasi bawah
    args_nav = f'{args_nav}query={query}'

    results = search_images_query(query=query)
    
    total_items = len(results)  # Total number of items in the collection
    total_pages = math.ceil(total_items / per_page)

    # Calculate end page, previous page, and next page
    end_page = total_pages
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None
    # Batasi sesuai items per page
    results = results[:per_page]
    results = images_social(posts=results,username=username)
    idx = 0
    for doc in results:
        results[idx]["_id"] = str(doc["_id"])
        idx += 1
    return jsonify({"results":results,
                    "is_superadmin":is_superadmin,
                    "username":username,
                    "curr_page":page,
                    "prev_page":prev_page,
                    "next_page":next_page,
                    "end_page":end_page,
                    "args_nav":args_nav})

@app.get("/blog")
def blog():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    items_per_page_blog = 4

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=items_per_page_blog, type=int) # Number of items per page

    total_items = table_photos.count_documents({})
    skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)

    # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
    photos = list(table_photos.find({}).sort("_id",-1).skip(skip=skip).limit(limit=per_page))
    photos = images_social(posts=photos,username=username)
    idx = 0
    for doc in photos:
        photos[idx]["_id"] = str(doc["_id"])
        idx += 1
    return render_template('blog.html',
                           images=photos,
                           current_username=username,
                           is_superadmin=is_superadmin,
                           curr_page=page,
                           prev_page=prev_page,
                           next_page=next_page,
                           end_page=end_page)

@app.get("/user/<user_name>")
def user_gallery(user_name):
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    items_per_page_blog = 12

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=items_per_page_blog, type=int) # Number of items per page

    total_items = table_photos.count_documents({"username":user_name})
    skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)

    # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
    photos = list(table_photos.find({"username":user_name}).sort("_id",-1).skip(skip=skip).limit(limit=per_page))
    photos = images_social(posts=photos,username=user_name)
    user_name = table_users.find_one({"username":user_name})
    idx = 0
    for doc in photos:
        photos[idx]["_id"] = str(doc["_id"])
        idx += 1
    return render_template('galleryUser.html',
                           images=photos,
                           current_username=username,
                           user_name=user_name,
                           is_superadmin=is_superadmin,
                           curr_page=page,
                           prev_page=prev_page,
                           next_page=next_page,
                           end_page=end_page)

@app.get("/my-gallery")
def gallery_page():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['username']
        is_superadmin = payload['is_superadmin']
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    items_per_page_home = 4

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=items_per_page_home, type=int) # Number of items per page

    total_items = table_photos.count_documents({"username":username})
    skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)

    # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
    photos = list(table_photos.find({"username":username}).sort("_id",-1).skip(skip=skip).limit(limit=per_page))
    photos = images_social(posts=photos,username=username)
    idx = 0
    for doc in photos:
        photos[idx]["_id"] = str(doc["_id"])
        idx += 1
    return render_template('gallery.html',
                           images=photos,
                           current_username=username,
                           is_superadmin=is_superadmin,
                           curr_page=page,
                           prev_page=prev_page,
                           next_page=next_page,
                           end_page=end_page)

@app.get("/about")
def about_page():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        is_superadmin = payload["is_superadmin"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    return render_template("about.html",current_username=username)

# Get info dari token tentang user
@app.get("/api/me")
def get_info_me():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['username']
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    # Exclude password
    user = table_users.find_one({"username":username},{"password":False})
    user["_id"] = str(user["_id"])
    return jsonify({"data":user})
    
# Endpoint ambil path images
@app.get("/api/images") # Optional args skip and limit, contoh : /api/images?skip=0&limit=10
def get_images():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['username']
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    items_per_page = 4

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=items_per_page, type=int) # Number of items per page

    total_items = table_photos.count_documents({})
    skip,prev_page,next_page,end_page = get_pagination_count(items_per_page=per_page,page=page,total_items=total_items)

    # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
    photos = list(table_photos.find({}).sort("_id",-1).skip(skip=skip).limit(limit=per_page))
    photos = images_social(posts=photos,username=username)
    idx = 0
    for doc in photos:
        photos[idx]["_id"] = str(doc["_id"])
        idx += 1
    return jsonify({
        "data":photos,
        'end_page': end_page,
        'prev_page': prev_page,
        'next_page': next_page})

# Endpoint ambil path images by me
@app.get("/api/images/me") # Optional args skip and limit, contoh : /api/images?skip=0&limit=10
def get_images_me():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        # Payload terverifikasi
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    skip = int(request.args.get("skip",default=0))
    limit = int(request.args.get("limit",default=20))
    # Sort dari id terbaru (-1) jika (1) maka dari yang terdahulu
    photos = list(table_photos.find({"username":username}).sort("_id",-1).skip(skip=skip).limit(limit=limit))
    idx = 0
    for doc in photos:
        photos[idx]["_id"] = str(doc["_id"])
        idx += 1
    return jsonify({"data":photos})

# Endpoint tambah foto
@app.post("/api/images/create")
def create_images():
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
        return redirect(url_for('home'))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    # Cek jika file telah terupload
    if 'file_give' in request.files:
        file = request.files['file_give']
        title_receive = request.form.get("title_give","")
        deskripsi_receive = request.form.get("deskripsi_give","")
        kategori_receive = request.form.get("kategori_give","")

        # Amankan filename dari karakter spesial
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[-1].replace('.','')
        if not check_ext(extension):
            return jsonify({"msg":"Extension not allowed"}),406 # Not acceptable
        unique_format = f"{username}-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.{extension}"
        file_path = f"photos/{unique_format}"
        file_save_path = f"./static/temp/{file_path}"

        # Simpan file ke folder temp
        file.save(file_save_path)
        limit_image_size(file_save_path,image_maxsize)

        # Thumbnail
        thumbnail_unique_format = f"thumbnail_{unique_format}"
        thumbnail_path = f"photos/{thumbnail_unique_format}"
        file_save_path_thumbnail = f"./static/temp/{thumbnail_path}"
        generate_thumbnail(input_image_path=file_save_path,output_thumbnail_path=file_save_path_thumbnail,thumbnail_size=IMAGES_THUMBNAIL_SIZE)
        
        # Upload ke storage
        upload_file_to_storage(file_path_static="photos",content=file_save_path,token=token_receive)

        # Upload ke storage
        upload_file_to_storage(file_path_static="photos",content=file_save_path_thumbnail,token=token_receive)

        # Delete temp file
        os.remove(file_save_path)
        os.remove(file_save_path_thumbnail)
        doc = {
            "username": username,
            "image": StorageURL+"static/"+file_path,
            "image_repo": file_path,
            "image_thumbnail": StorageURL+"static/"+thumbnail_path,
            "image_thumbnail_repo": thumbnail_path,
            "title": title_receive,
            "deskripsi": deskripsi_receive,
            "kategori": kategori_receive,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        # Masukkan url ke database
        table_photos.insert_one(doc)
        return {"msg":"Photo uploaded"}
    else:
        # Foto tidak terupload
        return {"msg":"No image uploaded"},404 # Not found

# Endpoint delete foto
@app.delete("/api/images/delete")
def delete_images():
    # Ambil cookie file
    token_receive = request.cookies.get(TOKEN)
    try:
        # Lihat isi cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['username']
        is_superadmin = payload['is_superadmin']
        # Payload terverifikasi
        pass
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        # Tidak ada token atau belum login
        return redirect(url_for('home'))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    image_id = request.form.get("image_id_give")
    # Ambil data dari database
    result = table_photos.find_one({"_id":ObjectId(image_id)})
    if not result:
        return jsonify({"msg":"Image not found"}),404 # Not found
    if is_superadmin:
        # Jika superadmin maka bolehkan
        pass
    # Jika owner foto tersebut berbeda maka tidak akan di hapus
    elif result.get("username") != username:
        return jsonify({"msg":"Image owner is different"}),403 # Forbidden
    
    # Cek apakah thumbnail tersedia
    current_data_image_thumb = result.get("image_thumbnail_repo")
    if current_data_image_thumb:
        # Delete dari storage
        delete_file_from_storage(current_data_image_thumb,token=token_receive)
    # Delete dari storage
    delete_file_from_storage(result.get("image_repo"),token=token_receive)
    # Delete dari mongodb
    table_photos.delete_one({"_id":ObjectId(image_id)})
    table_bookmarks.delete_many({"post_id":image_id})
    table_liked.delete_many({"post_id":image_id})
    table_comments.delete_many({"post_id":image_id})
    return jsonify({"msg":"Image deleted"})

# Endpoint update foto profil, about, bio
@app.put("/api/me")
def update_user_me():
    # Ambil cookie
    token_receive = request.cookies.get(TOKEN)
    try:
        # Buka konten cookie
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload["username"]
        pass
    except jwt.ExpiredSignatureError:
        # Sesinya sudah lewat dari 24 Jam
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        # Tidak ada token
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    # Jika payload terverifikasi maka kode dibawah akan di execute
    bio_receive = request.form.get('bio_give','')
    gender_receive = request.form.get('gender_give','')
    doc = {}
    # Cek jika file telah terupload
    if 'file_give' in request.files:
        file = request.files['file_give']
        
        # Amankan filename dari karakter spesial
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[-1].replace('.','')
        
        if not check_ext(extension):
            return jsonify({"msg":"Extension not allowed"}),406 # Not acceptable
        
        # Get current user profile pic
        current_data = table_users.find_one({"username":username},{"_id":False})
        current_data_profile_pic = current_data.get("profile_pic_repo")
        
        unique_format = f"{username}-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.{extension}"
        file_path = f"profile_pics/mini_{unique_format}"
        file_save_path = f"./static/temp/{file_path}"
        # Simpan file ke folder temp
        file.save(file_save_path)

        limit_image_size(image_path=file_save_path,max_size_mb=0.2)
        
        # Cek apakah user pernah mengupload file ke storage
        if current_data_profile_pic:
            # Delete dari storage
            delete_file_from_storage(file_path_repo=current_data_profile_pic,token=token_receive)
        # Jika tidak ada current profile pic di db maka user masih menggunakan profile pict default dari static folder
        # Upload ke storage
        upload_file_to_storage(file_path_static="profile_pics",content=file_save_path,token=token_receive)

        # Delete temp file
        os.remove(file_save_path)
        doc["profile_pic"] = StorageURL+"static/"+file_path
        doc["profile_pic_repo"] =file_path
        # Append profile pic ke doc untuk diupdate di database
        update_comment_pp = {
            "profile_pic": StorageURL+"static/"+file_path
        }
        table_comments.update_many({"username":username},{"$set":update_comment_pp})

    if bio_receive != '':
        doc["bio"] = bio_receive
    if gender_receive != '':
        doc["gender"] = gender_receive
    # Masukkan url ke database
    # $set adalah cara mongodb mengupdate suatu document dalam table
    table_users.update_one(filter={"username":username},update={"$set":doc})
    return {"msg":"Photo uploaded. Items updated"}

# Login page
@app.get("/login")
def login_fn():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

# Login page
@app.get("/daftar")
def daftar_fn():
    return render_template("daftar.html")

@app.get("/forgotpw")
def forgotpw_fn():
    return render_template("lupapw.html")

# Endpoint registrasi
@app.post('/api/sign_up')
def sign_up():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    # Cek apakah username telah dipakai
    user_from_db = table_users.find_one({"username":username_receive})
    if user_from_db:
        return jsonify({"msg":"username telah dipakai"}),409 # Conflict
    salted_password = hash_salt_password(password_receive)
    doc = {
        "username": username_receive,
        "password": salted_password,
        "bio": "Hello this is my bio",
        "profile_pic": default_profile_pic,
        "gender": "N/A",
        "is_superadmin": False,
        "choose_collection": "My Collection",
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    doc_default_collection = {
        "collection_name":"My Collection",
        "username":username_receive,
        "date":datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    # Masukkan ke database
    table_users.insert_one(doc)
    table_saved_collection.insert_one(doc_default_collection)
    return jsonify({'result':'success'})

# Sign in untuk mendapat token JWT
@app.post("/api/sign_in")
def sign_in():
    username_receive = request.form.get('username_give','')
    password_receive = request.form.get('password_give','')
    # Mencari user dengan username tsb
    user_from_db = table_users.find_one({"username":username_receive})
    salted_password = hash_salt_password(password_receive)
    if username_receive == '' or password_receive == '':
        # Compare digest digunakan untuk mencegah timing attack
        secrets.compare_digest(salted_password,salted_password)
        # Login salah
        return jsonify({
            "result":"fail", "msg":"Cannot find user with that username and password combination",
        }),404 # Not found
    if not user_from_db:
        # Compare digest digunakan untuk mencegah timing attack
        secrets.compare_digest(salted_password,salted_password)
        # Login salah
        return jsonify({
            "result":"fail", "msg":"Cannot find user with that username and password combination",
        }),404 # Not found
    # Compare digest digunakan untuk mencegah timing attack
    is_correct_username = secrets.compare_digest(user_from_db.get("username"), username_receive)
    is_correct_password = secrets.compare_digest(user_from_db.get("password"), salted_password)
    if not is_correct_username or not is_correct_password:
        # Login salah
        return jsonify({
            "result":"fail", "msg":"Cannot find user with that username and password combination",
        }),404 # Not found
    # Buat isi token
    payload={
        "username":username_receive,
        "is_superadmin":user_from_db.get('is_superadmin'),
        "exp": datetime.utcnow() + timedelta (seconds=Expired_Seconds),
    }
    # Buat token lalu encode
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"result": "success","token": token})

@app.post('/api/check_username')
def check_username():
    username_receive = request.form.get('username_give')
    
    # Check if username is already taken
    user_from_db = table_users.find_one({"username": username_receive})
    if user_from_db:
        return jsonify({'available': False}), 200  # Username is not available
    
    return jsonify({'available': True}), 200  # Username is available

@app.post('/api/forgotpw')
def forgot_password():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')

    user_from_db = table_users.find_one({"username":username_receive})
    salted_password = hash_salt_password(password_receive)

    doc={
        "password": salted_password
    }
    table_users.update_one(filter={"username":username_receive},update={"$set":doc})
    return jsonify({"msg":"Password changed"})

if __name__ == "__main__":
    check_superadmin()
    # Cek apakah folder tersedia
    check_folders()
    # app.run("localhost",5000,True)
    app.run("0.0.0.0",5000,True)