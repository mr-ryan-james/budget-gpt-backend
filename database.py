from pymongo import MongoClient
from dotenv import load_dotenv
from models import Persona
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

    def reset_user(self, collection, name):
        self.users_collection.delete_one({"name": name})
        try:
            user = Persona(name.lower())
            self.users_collection.insert_one(user.default_value)
        except ValueError:
            return

    def get_user(self, name):
        return self.users_collection.find_one({"name": name.lower().title()})


if __name__ == "__main__":
    db = Database()
    for user in Persona:
        db.reset_user(user.value)
    db.close()
