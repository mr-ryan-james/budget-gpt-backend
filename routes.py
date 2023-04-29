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
                            detail=f"Couldn't parse content: {response}")


@router.post("/emotions", response_model=WellnessUpdate)
def process_emotions(request: Request, name: str, emotions: list[Emotion] = Body(...)) -> WellnessUpdate:
    user = fetch_user(request.app.db, name)

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
                            detail=f"Couldn't parse content: {response}")


@router.post("/purchase_decision", response_model=PurchaseDecision)
def purchase_decision(request: Request, purchase_intent: PurchaseIntent = Body(...)):
    prompt = get_prompt_for_purchase_decision(purchase_intent.user_question)
    print("Prompt:")
    print(prompt)
    print("")

    response = llm(prompt.to_messages())
    print("Response:")
    print(response)
    print("")

    # Cleanup response
    content = response.content.replace("\n", "")
    content = content.replace("\"true\"", "true")
    content = content.replace("\"false\"", "false")
    content = content.replace("\"True\"", "true")
    content = content.replace("\"False\"", "false")
    print("Content:")
    print(content)
    print("")

    try:
        json_payload = json.loads(content)
        decision = PurchaseDecision.parse_obj(json_payload)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Couldn't parse content: {content}".format(content))

    return decision
