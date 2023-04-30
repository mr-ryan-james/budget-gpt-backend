from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from llm import *
from pydantic import ValidationError
from models import *
import json
from database import *


router = APIRouter()


@router.get("/")
def greeting():
    return {"message": "Hello world!"}


def fetch_user(db: Database, name: str) -> User:
    user = db.get_user(name)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User with name {name} not found".format(name=name))
    return user


@router.get("/user", response_model=User)
def get_user(request: Request, name: str) -> User:
    user = fetch_user(request.app.db, name)
    return user


@router.get("/recommendations", response_model=FinancialRecommendations)
def get_recommendations(request: Request, name: str) -> FinancialRecommendations:
    user = fetch_user(request.app.db, name)
    response = get_financial_recommendations(user)
    print("Response:")
    print(response)
    print("")

    try:
        json_payload = json.loads(response)
        recommendations = FinancialRecommendations.parse_obj(json_payload)
        return recommendations
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Couldn't parse response: {response}")


@router.get("/wellness_history", response_model=list[WellnessHistoryEntry])
def get_wellness_history(request: Request, name: str) -> list[WellnessHistoryEntry]:
    user = fetch_user(request.app.db, name)
    return list(request.app.db.get_wellness_history(str(user.id)))


@router.get("/emotions_history", response_model=list[EmotionsHistoryEntry])
def get_emotions_history(request: Request, name: str) -> list[EmotionsHistoryEntry]:
    user = fetch_user(request.app.db, name)
    return list(request.app.db.get_emotions_history(str(user.id)))


@router.get("/expenses", response_model=list[Expense])
def get_expenses(request: Request, name: str) -> list[Expense]:
    user = fetch_user(request.app.db, name)
    return user.expenses()


@router.post("/emotions", response_model=WellnessUpdate)
def process_emotions(request: Request, name: str, emotions: list[Emotion] = Body(...)) -> WellnessUpdate:
    user = fetch_user(request.app.db, name)

    # Add emotions to history
    emotions_history_entry = EmotionsHistoryEntry(
        date=now(), emotions=emotions, user_id=str(user.id))
    request.app.db.insert_emotions_history_entry(emotions_history_entry.dict())

    response = get_wellness_score(user.balance_status(), emotions)
    print("Response:")
    print(response)
    print("")

    try:
        json_payload = json.loads(response)
        previous_wellness_score = user.wellness_score
        wellness_update = WellnessUpdate.parse_obj(json_payload)
        if wellness_update.wellness_score is not None and wellness_update.wellness_score != user.wellness_score:
            print(
                f"Wellness score updated from {previous_wellness_score} to {user.wellness_score} for {user.name}")

            # Add wellness score to history
            wellness_history_entry = WellnessHistoryEntry(
                date=now(), wellness_score=wellness_update.wellness_score, user_id=str(user.id))
            request.app.db.insert_wellness_history_entry(
                emotions_history_entry.dict())

            # Update user with new wellness score
            update_result = request.app.db.update_user(
                user.id, wellness_update.wellness_score)
            if update_result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with name {name} not found"
                )
        else:
            print(f"Wellness score unchanged for {user.name}")
        return wellness_update
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Couldn't parse response: {response}")


@router.post("/purchase_decision", response_model=PurchaseDecision)
def purchase_decision(request: Request, name: str, purchase_intent: PurchaseIntent = Body(...)):
    user = fetch_user(request.app.db, name)

    response = get_purchase_decision(user, purchase_intent.user_question)
    print("Response:")
    print(response)
    print("")

    try:
        json_payload = json.loads(response)
        decision = PurchaseDecision.parse_obj(json_payload)
        return decision
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Couldn't parse response: {response}".format(response))
