from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

load_dotenv()

llm = ChatOpenAI(temperature=0)

category_prompt = PromptTemplate(
    input_variables=["category"],
    template="How can I control expenses for \"{category}\" as a expense category?"
)
chain = LLMChain(llm=llm, prompt=category_prompt)


def debug_str(self, inputs):
    return self.template.format(
        **{k: v for k, v in zip(self.input_variables, inputs)})


PromptTemplate.debug_str = debug_str
