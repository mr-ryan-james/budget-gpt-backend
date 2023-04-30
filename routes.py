from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from llm import *
from pydantic import ValidationError
from models import *
import json
from database import *
from opendata import get_open_data_source

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
    db = request.app.db
    user = fetch_user(db, name)
    return user


@router.get("/recommendations", response_model=FinancialRecommendations)
def get_recommendations(request: Request, name: str) -> FinancialRecommendations:
    db = request.app.db
    user = fetch_user(db, name)
    response = request.app.llm.get_financial_recommendations(user)
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
    db = request.app.db
    user = fetch_user(db, name)
    return list(request.app.db.get_wellness_history(str(user.id)))


@router.get("/emotions_history", response_model=list[EmotionsHistoryEntry])
def get_emotions_history(request: Request, name: str) -> list[EmotionsHistoryEntry]:
    db = request.app.db
    user = fetch_user(db, name)
    return list(db.get_emotions_history(str(user.id)))


@router.get("/flow_units", response_model=list[FlowUnit])
def get_expenses(request: Request, name: str) -> list[FlowUnit]:
    db = request.app.db
    user = fetch_user(db, name)
    return user.flow_units()


@router.get("/about_me", response_model=AboutMe)
def get_about_me(request: Request, name: str) -> AboutMe:
    db = request.app.db
    llm = request.app.llm
    user = fetch_user(db, name)
    emotions_history = list(map(
        lambda x: EmotionsHistoryEntry(
            date=x["date"], emotions=x["emotions"], user_id=x["user_id"]),
        list(db.get_emotions_history(str(user.id)))
    ))
    wellness_history = list(map(
        lambda x: WellnessHistoryEntry(
            date=x["date"], wellness_score=x["wellness_score"], user_id=x["user_id"]),
        list(db.get_wellness_history(str(user.id)))
    ))
    response = llm.get_about_me(emotions_history, wellness_history)
    print("Response:")
    print(response)
    print("")

    try:
        json_payload = json.loads(response)
        about_me = AboutMe.parse_obj(json_payload)
        return about_me
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Couldn't parse response: {response}")


@router.get("/did_you_know", response_model=DidYouKnow)
def get_did_you_know(request: Request, name: str) -> DidYouKnow:
    db = request.app.db
    llm = request.app.llm
    user = fetch_user(db, name)
    wellness_score_explanation = db.get_last_wellness_score_explanation(
        str(user.id))
    if wellness_score_explanation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Explanation not found".format(name=name))
    open_data_source = get_open_data_source()
    response = llm.get_did_you_know(
        wellness_score_explanation, open_data_source)
    print("Response:")
    print(response)
    print("")

    try:
        json_payload = json.loads(response)
        did_you_know = DidYouKnow.parse_obj(json_payload)
        return did_you_know
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Couldn't parse response: {response}".format(response))


@router.post("/emotions", response_model=WellnessUpdate)
def process_emotions(request: Request, name: str, emotions: list[Emotion] = Body(...)) -> WellnessUpdate:
    db = request.app.db
    llm = request.app.llm
    user = fetch_user(db, name)

    # Add emotions to history
    emotions_history_entry = EmotionsHistoryEntry(
        date=now(), emotions=emotions, user_id=str(user.id))
    db.insert_emotions_history_entry(emotions_history_entry.dict())

    response = llm.get_wellness_score(user.balance_status(), emotions)
    print("Response:")
    print(response)
    print("")

    try:
        json_payload = json.loads(response)
        previous_wellness_score = user.wellness_score
        wellness_update = WellnessUpdate.parse_obj(json_payload)
        if wellness_update.wellness_score is not None:
            print(
                f"Wellness score updated from {previous_wellness_score} to {user.wellness_score} for {user.name}")

            # Add wellness score to history
            wellness_history_entry = WellnessHistoryEntry(
                date=now(), wellness_score=wellness_update.wellness_score, explanation=wellness_update.explanation, user_id=str(user.id))
            db.insert_wellness_history_entry(wellness_history_entry.dict())

            # Update user with new wellness score, if needed
            if previous_wellness_score != wellness_update.wellness_score:
                db.update_user(user.id, wellness_update.wellness_score)

        return wellness_update
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Couldn't parse response: {response}")


@router.post("/purchase_decision", response_model=PurchaseDecision)
def purchase_decision(request: Request, name: str, purchase_intent: PurchaseIntent = Body(...)):
    user = fetch_user(request.app.db, name)

    response = request.app.llm.get_purchase_decision(
        user, purchase_intent.user_question)
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
