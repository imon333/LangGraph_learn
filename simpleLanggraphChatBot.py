## so the graph would be like,, Start -- classifier -- router-- logical -- therapist -- end.

from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_community.chat_models import ChatOpenAI
from typing_extensions import NotRequired, TypedDict
load_dotenv()

print("fuck moni")

llm = ChatOpenAI(
    model_name="gpt-4o-mini",  # specify GPT-4o-mini
    temperature=0.7,            # optional: controls creativity
)


class State(TypedDict):
    messages:Annotated[list, add_messages]


