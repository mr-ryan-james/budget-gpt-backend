from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from llm import llm, get_prompt_for_purchase_decision
from pydantic import ValidationError
from models import *
import json


router = APIRouter()


@router.get("/")
def greeting():
    return {"message": "Hello world!"}


# endpoint for a purchase decision with query param user_question
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
