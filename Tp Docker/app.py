from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017/")
db = client.testdb
collections = db.users

@app.route("/")
def hello():
    return f"Connexion MongoDB OK. Collections : {collections}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)