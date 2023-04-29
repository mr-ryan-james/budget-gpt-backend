from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
CONNECTION_STRING = "mongodb+srv://admin:" + \
    db_password + "@cluster0.wgf9exk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)


def get_users_collection():
    return client["moeda"]["users"]


def close_db():
    client.close()


if __name__ == "__main__":
    collection = get_users_collection()
    print(f"{collection.count_documents({})} documents")
    close_db()
