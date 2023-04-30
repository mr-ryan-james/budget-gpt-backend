from dotenv import load_dotenv
import os
import openai
from models import *

load_dotenv()


class LLM:
    def __init__(self):
        self.llm = openai.ChatCompletion
        self.system_message = f"""
        You are a personal financial advisor. You balance emotional intelligence with quantitative analysis to help people make better financial decisions.
        """
        self.tone_message = "The explanation is written in the second person singular and it addresses the user directly. Use a friendly tone and a clear communication style."

    def get_completion(self, user_message, model="gpt-3.5-turbo", temperature=0):
        messages = [
            {'role': 'system', 'content': self.system_message},
            {'role': 'user', 'content': user_message}
        ]
        response = self.llm.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message["content"]

    def get_wellness_score(self, balance_status: BalanceStatus, emotions: list[Emotion]):
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
        The <explanation> is short text of 50 words maximum that describes the <wellness_score>. 
        {self.tone_message}

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
        print(f"User message: {user_message}")
        return self.get_completion(user_message, temperature=0)

    def get_financial_recommendations(self, user):
        user_message = f"""
        I need you to give one recommendation for each of the following categories of advice: 
        1 - <spending_and_saving>: optimizing spending and saving
        2 - <money_feelings>: developing a healthy relationship to money
        3 - <opportunities>: finding new opportunities to make more money  

        Gi
        {user.data_points_prompt()}

        Return the recommendation and category in JSON format with keys spending_and_saving, money_feelings, and opportunities. 
        Each recommendation should be max 140 characters long. 
        {self.tone_message}
        """
        print(f"User message: {user_message}")
        return self.get_completion(user_message, temperature=0)

    def get_purchase_decision(self, user, user_question):
        user_message = f"""
        {user.data_points_prompt()}

        What would you recommend the user to do, given the following question?
        - should the user go ahead with their purchase intent? (true or false)
        - explanation of the decision in 50 words at most (string)

        Provide your answer exclusively in JSON format with the following keys: 
        decision, explanation
        {self.tone_message}

        Question: `{user_question}`

        Answer:
        """
        print(f"User message: {user_message}")
        return self.get_completion(user_message, temperature=0)
