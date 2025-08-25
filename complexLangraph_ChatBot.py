import os
from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI  
from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict

load_dotenv()

# Fix the model name and add structured output method
llm = ChatOpenAI(
    model="gpt-4o",  # Use gpt-4o for structured output support
    temperature=0.7, 
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional(therapist) or logical response"
    )

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

def classify_message(state: State):
    last_message = state["messages"][-1]
    
    # Fix: Specify method for older models
    classifier_llm = llm.with_structured_output(MessageClassifier, method="function_calling")
    
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            """
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    
    print(f"Classified as: {result.message_type}")  # Debug print
    return {"message_type": result.message_type}

# Fix: Router should return string directly, not dict
def router(state: State):
    message_type = state.get("message_type", "logical")
    print(f"Routing to: {message_type}")  # Debug print
    
    if message_type == "emotional":
        return "therapist"  # Return string directly
    return "logical"  # Return string directly

def therapist_agent(state: State):
    last_message = state["messages"][-1]
    
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
            "content": last_message.content
        }
    ]
    
    reply = llm.invoke(message)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def logical_agent(state: State):
    last_message = state["messages"][-1]
    
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
            "content": last_message.content
        }
    ]
    
    reply = llm.invoke(message)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

# Build the graph
graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)

graph_builder.add_edge(START, "classifier")

# Fix: Use router function directly and correct mapping
graph_builder.add_conditional_edges(
    "classifier",  # Start from classifier, not router
    router,        # Use router function directly
    {
        "therapist": "therapist",  # Map return value to node name
        "logical": "logical"       # Map return value to node name
    }
)

graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END) 

graph = graph_builder.compile()

def run_chatbot():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input.lower() == "exit":
            print("Bye")
            break

        # Add user message to state
        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        # Process through graph
        try:
            state = graph.invoke(state)
            
            # Get the last assistant message
            if state.get("messages") and len(state["messages"]) > 0:
                last_message = state["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"Assistant: {last_message.content}")
                else:
                    print(f"Assistant: {last_message['content']}")
        
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    run_chatbot()