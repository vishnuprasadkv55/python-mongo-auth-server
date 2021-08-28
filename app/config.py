from pymongo import MongoClient
uri = "mongodb://mongo_location:RrkeBMxZHt1cOFYm@cluster0-shard-00-00.1f6b4.mongodb.net:27017,cluster0-shard-00-01.1f6b4.mongodb.net:27017,cluster0-shard-00-02.1f6b4.mongodb.net:27017/panic?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-dsv22b-shard-0&authSource=admin&retryWrites=true&w=majority"
client = MongoClient(uri)
print("connected")
db = client.panic