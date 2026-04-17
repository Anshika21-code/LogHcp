from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()

app = FastAPI(title="HCP AI Logger - 5 LLMs Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory form state
form_state: Dict[str, Any] = {
    "hcp_name": "",
    "date": "19-04-2025",
    "time": "19:36",
    "interaction_type": "Meeting",
    "attendees": "",
    "topics_discussed": "",
    "materials_shared": "No materials added",
    "samples_distributed": "No samples added",
    "sentiment": "Neutral",
    "outcomes": "",
    "follow_up_actions": ""
}

class Message(BaseModel):
    message: str
    model_choice: str = "llama-3.3-70b-versatile"   # default model

# ==================== 5 LANGGRAPH TOOLS (Mandatory) ====================

@tool
def log_interaction(details: str) -> str:
    """Log full interaction from natural language."""
    global form_state
    form_state["topics_discussed"] = details
    return "✅ Interaction logged successfully."

@tool
def edit_field(field: str, value: str) -> str:
    """Edit any field in the form."""
    global form_state
    key = field.lower().replace(" ", "_").replace("-", "_")
    if key in form_state:
        form_state[key] = value
        return f"✅ Updated {field} → {value}"
    return f"❌ Field not found."

@tool
def set_hcp_name(name: str) -> str:
    """Set HCP name."""
    global form_state
    form_state["hcp_name"] = name
    return f"✅ HCP set to {name}"

@tool
def set_sentiment(sentiment: str) -> str:
    """Set sentiment: Positive / Neutral / Negative."""
    global form_state
    sent = sentiment.capitalize()
    if sent in ["Positive", "Neutral", "Negative"]:
        form_state["sentiment"] = sent
        return f"✅ Sentiment: {sent}"
    return "❌ Use: Positive, Neutral, Negative"

@tool
def add_followup(action: str) -> str:
    """Add follow-up action."""
    global form_state
    if form_state["follow_up_actions"]:
        form_state["follow_up_actions"] += f"\n- {action}"
    else:
        form_state["follow_up_actions"] = f"- {action}"
    return f"✅ Follow-up added."

tools = [log_interaction, edit_field, set_hcp_name, set_sentiment, add_followup]

# ==================== 5 DIFFERENT LLMs (from Groq) ====================

def get_llm(model_name: str):
    models = {
        "llama-3.3-70b-versatile": "llama-3.3-70b-versatile",   # Strong reasoning
        "llama-3.1-8b-instant": "llama-3.1-8b-instant",         # Fast & cheap
        "gemma2-9b-it": "gemma2-9b-it",                         # Good for structured tasks
        # Add more if Groq has them (you can test in playground)
        "llama-4-scout-17b": "meta-llama/llama-4-scout-17b-16e-instruct",  # if available
        "mixtral": "mixtral-8x7b-32768"                         # fallback if supported
    }
    selected = models.get(model_name, "llama-3.3-70b-versatile")
    
    return ChatGroq(
        model=selected,
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY")
    )

# Default LLM
llm = get_llm("llama-3.3-70b-versatile")
llm_with_tools = llm.bind_tools(tools)

# LangGraph (same as before)
def call_agent(state):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": messages + [response]}

workflow = StateGraph(dict)
workflow.add_node("agent", call_agent)
workflow.add_node("tools", lambda x: x)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    lambda x: "tools" if getattr(x["messages"][-1], "tool_calls", None) else END
)
workflow.add_edge("tools", "agent")

graph = workflow.compile()

# ==================== ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1 style="text-align:center; padding:40px; font-family:Arial;">
        ✅ HCP AI Logger Backend Running<br>
        <small>5 Tools + Multiple LLMs Ready</small>
    </h1>
    """

@app.post("/chat")
async def chat(msg: Message):
    global form_state, llm_with_tools
    
    # Switch model if user sends different choice
    llm = get_llm(msg.model_choice)
    llm_with_tools = llm.bind_tools(tools)
    
    result = graph.invoke({"messages": [HumanMessage(content=msg.message)]})
    ai_reply = result["messages"][-1].content
    
    return {
        "ai_response": f"[Model: {msg.model_choice}] {ai_reply}",
        "form_data": form_state,
        "used_model": msg.model_choice
    }

@app.get("/form-data")
async def get_form():
    return form_state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)