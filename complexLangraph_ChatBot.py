## so the graph would be like,, Start -- classifier -- router-- logical -- therapist -- end.

from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_community.chat_models import ChatOpenAI
from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict
load_dotenv()

print("fuck moni")

llm = ChatOpenAI(
    model_name="gpt-4o-mini",  # specify GPT-4o-mini
    temperature=0.7,            # optional: controls creativity
)

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional(therapist) or logical response"
    )

class State(TypedDict):
    messages:Annotated[list, add_messages]
    message_type: str | None
    

    
def classify_message(state: State):
    lastmessage = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)
    
    result = classifier_llm.invoke([
        
        {
            "role": "system",
            "content": """ Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            """
        }
    ])
    

def router(state: State):
    pass

def therapist_agent(state: State):
    pass

def logical_agent(state: State):
    pass