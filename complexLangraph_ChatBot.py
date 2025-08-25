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
        },
        {
            "role":"user",
            "content": lastmessage.content
        }
        
    ])
    return {"message_type": result.message_type}
    

def router(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {next: "therapist"}
    
    return {next: "logical"}

def therapist_agent(state: State):
    lastmessage = state["messages"][-1]
    
    message = [
        {
            "role": "system",
            "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""
        },
        {
            "role": "user",
            "content": lastmessage.content
        }
    ]
    reply = llm.invoke(message)
    return {"messages":[{"role":"assistant", "content": reply.content}]}

def logical_agent(state: State):
    lastmessage = state["messages"][-1]
    
    message = [
        {
            "role": "system",
            "content": """You are a purely logical assistant. Focus only on facts and information.
                        Provide clear, concise answers based on logic and evidence.
                        Do not address emotions or provide emotional support.
                        Be direct and straightforward in your responses."""
        },
        {
            "role": "user",
            "content": lastmessage.content
        }
    ]
    reply = llm.invoke(message)
    return {"messages":[{"role":"assistant", "content": reply.content}]}