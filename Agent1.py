from typing import  TypedDict
from langgraph.graph import StateGraph

# part follow--

class AgentState(TypedDict): 
    message: str
    
    
def greeting_node(state: AgentState) -> AgentState:
    state['message'] = "Hello " + state['message']+ ",how can I assist you today?"
    return state   

graph = StateGraph(AgentState)

graph.add_node("greeting", greeting_node)
graph.set_entry_point("greeting")
graph.set_finish_point("greeting")

app = graph.compile()

#from IPython.display import Image, display 
#display(Image(app.get_graph().draw_mermaid_png()))

output = app.invoke({"message": "imon"})

output['message']  

# exercise 

class AgentState(TypedDict): 
    message: str
    complement: str
    
    
def greeting_node(state: AgentState) -> AgentState:
    state['message'] += "Hello " + state['message'] + state['complement']

    
    return state   

graph = StateGraph(AgentState)

graph.add_node("greeting", greeting_node)
graph.set_entry_point("greeting")
graph.set_finish_point("greeting")

app = graph.compile()



output = app.invoke({"message": "imon", "complement": ", you are the best"})

output['message']  
