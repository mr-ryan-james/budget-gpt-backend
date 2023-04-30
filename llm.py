from dotenv import load_dotenv
import os
import openai
from models import *


class LLM:
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.llm = openai.ChatCompletion
        self.system_message = "You are a personal financial advisor. You balance emotional intelligence with quantitative analysis to help people make better financial decisions."
        self.query_tone_message = "The explanation is written in the second person singular and it addresses the user directly. Use a friendly tone and a clear communication style."
        self.market_situation_prompt = f"""
The current US economic conditions is as follows:
US economic growth slowed to 1.1 per cent in the first quarter of this year, the Commerce Department said on Thursday, as the possibility of a mild recession increases. \
The figure came in below economists' expectations of 2 per cent growth, while core personal consumption expenditure for the first quarter rose by 4.9 per cent, \
versus economists' projections of 4.7 per cent growth. Economic activity has been easing as the US central bank has rapidly raised the benchmark lending rate to \
tackle stubborn inflation, while the full fallout from recent financial sector unrest — following the failures of three midsized lenders last month — has yet to be seen.        
"""

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
{self.query_tone_message}

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

{user.data_points_prompt()}

{self.market_situation_prompt}

Base your recommendations primarily on the user data points but incorporate the current economic conditions. Use simple language that \
a non-technical person would understand. Use diverse language so that it doesn't sound repetitive.

Return the recommendation and category in JSON format with keys spending_and_saving, money_feelings, and opportunities. 
Each recommendation should be max 80 words long. 
{self.query_tone_message}
        """
        print(f"User message: {user_message}")
        return self.get_completion(user_message, temperature=0.9)

    def get_purchase_decision(self, user, user_question):
        user_message = f"""
{user.data_points_prompt()}

What would you recommend the user to do, given the following question?
- should the user go ahead with their purchase intent? (true or false)
- explanation of the decision in 50 words at most (string)

Provide your answer exclusively in JSON format with the following keys: 
decision, explanation
{self.query_tone_message}

Question: `{user_question}`

Answer:
        """
        print(f"User message: {user_message}")
        return self.get_completion(user_message, temperature=0)

    def get_about_me(self, emotions_history, wellness_score_history):
        emotions_history_str = "\n".join(
            f"{entry.date}: {', '.join(emotion.value for emotion in entry.emotions)}" for entry in emotions_history)
        wellness_score_history_str = "\n".join(
            f"{entry.date}: {entry.wellness_score}" for entry in wellness_score_history)

        user_message = f"""
Write a short summary of the evolution of the user's emotions and wellness score over the past 6 months.

This is the record of the user's emotions with dates:
{emotions_history_str}

This is the record of the wellness score with dates, sorted from more recent to older. \
The <wellness_score> can range from 1 to 10 where 1 is poor and 10 is excellent:
{wellness_score_history_str}

Provide your answer exclusively in JSON format with the following key: description
The description should be max 80 words long. Focus more on the latest emotions and wellness score.
{self.query_tone_message}
        """
        print(f"User message: {user_message}")
        return self.get_completion(user_message, temperature=0)

    def get_did_you_know(self, wellness_score_explanation, open_data_source):
        user_message = f"""
Given the following data about Americans:
- {format(open_data_source.distress, '.2f')}% feel significant financial stress
- {format(open_data_source.control, '.2f')}% feel like finances control their lives
- {format(open_data_source.frugality, '.2f')}% are frugal
- {format(open_data_source.skills, '.2f')}% consider themselves financially skilled
- {format(open_data_source.confident_in_savings, '.2f')}% are not confident that their savings will last

Given the following most recent explanation about the <wellness_score> of the user:
`{wellness_score_explanation}`

Provide a relatioship of the current emotional state of the user to the provided data about Americans.
{self.query_tone_message}
Start with 'did you know' and complete the sentence. The description should be max 80 words long.
"""
        print(f"User message: {user_message}")
        description = self.get_completion(user_message, temperature=0)
        return f"{{ \"description\": \"{description}\", \"source\": \"{open_data_source.source}\"}}"
