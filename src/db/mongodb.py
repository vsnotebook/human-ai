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
db = client.voice_workshop
