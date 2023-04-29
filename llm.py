from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import openai
from models import *

load_dotenv()

llm = ChatOpenAI(temperature=0)


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message["content"]


def get_wellness_score(balance_status: BalanceStatus, emotions: list[Emotion]):
    system_message = f"""
    You are a personal financial advisor. You balance emotional intelligence with quantitative analysis to help people make better financial decisions.
    """
    balance_status_str = balance_status.value
    emotions_str = ", ".join(emotion.value for emotion in emotions)
    user_message = f"""
    I need you to rate the user's financial <wellness_score> based on two input factors:
    - <balance_status>: an indication of the financial health of the user
    - <emotions>: one or more emotions the user is currently feeling, separated by commas

    The <balance_status> can be one of the following:
    - <low_expenses>: expenses are a small percentage of the income
    - <moderate_expenses>: expenses are a moderate percentage of the income
    - <high_expenses>: expenses are a large percentage of the income
    - <overshooting_expenses>: expenses are more than the income

    Produce a short reply, with just the computed <wellness_score> and a short <explanation> of the <wellness_score> for the user, \
    as a JSON object with keys: wellness_score, explanation.
    The <wellness_score> can range from 1 to 10 where 1 is poor and 10 is excellent.
    Do your best to determine a <wellness_score> different from null, unless there is input data missing.
    The <explanation> is short text of 50 words maximum that describes the <wellness_score>. It is written in the second person singular \
    as it addresses the user directly. Use a friendly tone and a clear communication style.

    <balance_status>: low_expenses
    <list of emotions>: gratitude
    <wellness_score>: {{ "wellness_score": 10 }}

    <balance_status>: overshooting_expenses
    <list of emotions>: terror, bitterness
    <wellness_score>: {{ "wellness_score": 1 }}     

    <balance_status>: moderate_expenses
    <list of emotions>: nervousness, confusion
    <wellness_score>: {{ "wellness_score": 7 }}    

    <balance_status>: overshooting_expenses
    <list of emotions>: disappointment
    <wellness_score>: {{ "wellness_score": 3 }}      

    <balance_status>: moderate_expenses
    <list of emotions>: acceptance, optimism
    <wellness_score>: {{ "wellness_score": 8 }}      
    
    <balance_status>: high_expenses
    <list of emotions>: frustration, nervousness
    <wellness_score>: {{ "wellness_score": 5 }}    

    <balance_status>: {balance_status_str}
    <list of emotions>: {emotions_str}

    <wellness_score>: 
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': user_message}
    ]
    print(f"User message: {user_message}")
    return get_completion_from_messages(messages, temperature=0)


def get_prompt_for_purchase_decision(user_question):
    system_message_template = f"""
    As "Moeda," an intelligent virtual financial advisor, your mission is to help the user make smart financial decisions \
    that promote financial wellness.
    """
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
