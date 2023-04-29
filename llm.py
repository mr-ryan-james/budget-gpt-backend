from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

load_dotenv()

llm = ChatOpenAI(temperature=0)
system_message_template = f"""
As "Moeda," an intelligent virtual financial advisor, your mission is to help the user make smart financial decisions \
that promote financial wellness.
"""


def get_prompt_for_purchase_decision(user_question):
    user_message_template = f"""
    Given the following financial information about the user:
    ```
    - average monthly income: $4,000
    - average monthly expense on food: $500
    - average montly expense on rent: $1,500
    - average monthly expense on transportation: $300
    - average monthly expense on healthcare: $400
    - average monthly expense on other categories: $200
    ```

    and the following financial goals:
    ```
    - 2 yearly holidays worth $2,000 each
    - 4 yearly welness or sport outings for $800 each
    ```

    What would you recommend the user to do, given the following question?
    - should the user go ahead with their purchase intent? (true or false)
    - explanation of the decision in 100 words at most (string)

    Provide your answer exclusively in JSON format with the following keys: 
    decision, explanation

    Question: `{user_question}`

    Answer:
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        system_message_template)
    user_message_prompt = HumanMessagePromptTemplate.from_template(
        user_message_template)
    chatPrompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, user_message_prompt])
    return chatPrompt.format_prompt(user_question=user_question)
