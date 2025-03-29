# python -m pip install "pymongo[srv]"
import os
import time

import bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# os.environ["http_proxy"] = "http://127.0.0.1:10808"
# os.environ["https_proxy"] = "http://127.0.0.1:10808"
uri = "mongodb+srv://vswork666:VuSnbgmkrs4jamVt@cluster0.naywsqs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client: MongoClient = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    db = client.web
    db.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    # col = db.users
    users_ref = db.users

    # 使用bcrypt加密密码
    password_hash = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt())

    # 创建用户文档
    users_ref.insert_one({
        'username': "liu1",
        'email': "liu1@qq.com",
        'password_hash': password_hash,
        'role': "user",
        'trial_count': 10,
        'trial_seconds': 60,
        'created_at': time.time()
    })

except Exception as e:
    print(e)
