import os
from pymongo import MongoClient
uri = os.environ.get('MONGO_URI')
client = MongoClient(uri)
print("connected")
db = client.panic