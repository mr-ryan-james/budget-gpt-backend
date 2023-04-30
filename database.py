from pymongo import MongoClient
from dotenv import load_dotenv
from models import *
import os
import random
from datetime import datetime, timedelta

load_dotenv()


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def random_past_date():
    return (datetime.now() - timedelta(days=random.randint(1, 20))).strftime('%Y-%m-%d %H:%M:%S')


class Database:
    def __init__(self):
        db_password = os.getenv("DB_PASSWORD")
        self.client = MongoClient("mongodb+srv://admin:" + db_password +
                                  "@cluster0.wgf9exk.mongodb.net/?retryWrites=true&w=majority")
        self.users_collection = self.client["moeda"]["users"]
        self.emotions_history = self.client["moeda"]["emotions_history"]
        self.wellness_history = self.client["moeda"]["wellness_history"]

    def close(self):
        self.client.close()

    def reset(self):
        self.users_collection.drop()
        self.emotions_history.drop()
        self.wellness_history.drop()

    def initialize_with_sample_data(self):
        for persona in Persona:
            self.create_persona(persona.value)
            num_entries = random.randint(1, 20)
            for i in range(num_entries):
                user = self.get_user(persona.value)
                emotion_history_entry = EmotionsHistoryEntry(
                    date=random_past_date(),
                    emotions=Emotion.random_emotion_list(persona),
                    user_id=str(user.id)
                )
                self.insert_emotions_history_entry(
                    emotion_history_entry.dict())
                wellness_history_entry = WellnessHistoryEntry(
                    date=random_past_date(),
                    wellness_score=random.uniform(
                        *persona.wellness_sample_range),
                    user_id=str(user.id)
                )
                self.insert_wellness_history_entry(
                    wellness_history_entry.dict())

    def create_persona(self, name):
        self.users_collection.delete_one({"name": name})
        user = Persona(name)
        return self.users_collection.insert_one(user.default_value)

    def get_user(self, name):
        formatted_name = name.lower().title()
        db_user = self.users_collection.find_one({"name": formatted_name})
        return User.parse_obj(db_user)

    def get_wellness_history(self, user_id):
        return self.wellness_history.find({"user_id": user_id}).sort("date", -1)

    def get_emotions_history(self, user_id):
        return self.emotions_history.find({"user_id": user_id}).sort("date", -1)

    def update_user(self, id, wellness_score):
        return self.users_collection.update_one({"_id": id}, {"$set": {"wellness_score": wellness_score}})

    def insert_emotions_history_entry(self, emotion_history_entry):
        return self.emotions_history.insert_one(emotion_history_entry)

    def insert_wellness_history_entry(self, wellness_history_entry):
        return self.wellness_history.insert_one(wellness_history_entry)

    def get_last_wellness_score_explanation(self, user_id):
        records = list(self.wellness_history.find(
            {"user_id": user_id}).sort("date", -1).limit(1))
        if records.count == 0:
            return None
        return records[0]["explanation"]


if __name__ == "__main__":
    db = Database()
    db.reset()
    db.initialize_with_sample_data()
    db.close()
