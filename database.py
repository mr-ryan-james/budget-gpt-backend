from pymongo import MongoClient
from dotenv import load_dotenv
from models import *
import os

load_dotenv()


class Database:
    def __init__(self):
        db_password = os.getenv("DB_PASSWORD")
        self.client = MongoClient("mongodb+srv://admin:" + db_password +
                                  "@cluster0.wgf9exk.mongodb.net/?retryWrites=true&w=majority")
        self.users_collection = self.client["moeda"]["users"]

    def close(self):
        self.client.close()

    def reset_user(self, name):
        self.users_collection.delete_one({"name": name})
        user = Persona(name)
        self.users_collection.insert_one(user.default_value)

    def get_user(self, name):
        formatted_name = name.lower().title()
        db_user = self.users_collection.find_one({"name": formatted_name})
        return User.parse_obj(db_user)

    def update_user(self, wellness_update):
        return self.users_collection.update_one({"_id": user.id}, {"$set": wellness_update})


if __name__ == "__main__":
    db = Database()
    for user in Persona:
        db.reset_user(user.value)
    db.close()
