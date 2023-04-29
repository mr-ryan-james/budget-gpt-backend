from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from llm import llm, get_prompt_for_purchase_decision
from pydantic import ValidationError
from models import *
import json
from database import *


router = APIRouter()


@router.get("/")
def greeting():
    return {"message": "Hello world!"}


@router.get("/user", response_model=User)
def get_user(request: Request, name: str):
    user = request.app.db.get_user(name)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User with name {name} not found".format(name=name))
    return user


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
