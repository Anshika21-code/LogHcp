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

app = FastAPI(title="HCP AI Logger")

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

# ==================== 5 LANGGRAPH TOOLS ====================

@tool
def log_interaction(details: str) -> str:
    """Log full interaction details from natural language."""
    global form_state
    form_state["topics_discussed"] = details
    return "✅ Interaction successfully logged and form updated."

@tool
def edit_field(field: str, value: str) -> str:
    """Update any specific field in the form."""
    global form_state
    key = field.lower().replace(" ", "_").replace("-", "_")
    if key in form_state:
        form_state[key] = value
        return f"✅ Updated '{field}' to: {value}"
    return f"❌ Field '{field}' not found."

@tool
def set_hcp_name(name: str) -> str:
    """Set the HCP name."""
    global form_state
    form_state["hcp_name"] = name
    return f"✅ HCP Name set to: {name}"

@tool
def set_sentiment(sentiment: str) -> str:
    """Set sentiment - Positive, Neutral, or Negative."""
    global form_state
    sent = sentiment.capitalize()
    if sent in ["Positive", "Neutral", "Negative"]:
        form_state["sentiment"] = sent
        return f"✅ Sentiment set to: {sent}"
    return "❌ Please use: Positive, Neutral, or Negative"

@tool
def add_followup(action: str) -> str:
    """Add a follow-up action."""
    global form_state
    if form_state.get("follow_up_actions"):
        form_state["follow_up_actions"] += f"\n- {action}"
    else:
        form_state["follow_up_actions"] = f"- {action}"
    return f"✅ Follow-up action added: {action}"

tools = [log_interaction, edit_field, set_hcp_name, set_sentiment, add_followup]

# LLM Setup
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("❌ GROQ_API_KEY not found in .env file! Please add it.")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=groq_api_key
)

llm_with_tools = llm.bind_tools(tools)

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
    lambda x: "tools" if getattr(x.get("messages", [{}])[-1], "tool_calls", None) else END
)
workflow.add_edge("tools", "agent")

graph = workflow.compile()

# ==================== ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>HCP AI Logger</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>✅ HCP AI Logger Backend is Running!</h1>
            <p>Backend is live on http://127.0.0.1:8000</p>
            <p><strong>Available Endpoints:</strong></p>
            <ul style="display: inline-block; text-align: left;">
                <li><strong>GET /</strong> → This page</li>
                <li><strong>POST /chat</strong> → Send message to AI</li>
                <li><strong>GET /form-data</strong> → Get current form data</li>
            </ul>
            <p>Now start the React frontend and test it.</p>
        </body>
    </html>
    """

@app.post("/chat")
async def chat(msg: Message):
    global form_state
    try:
        result = graph.invoke({"messages": [HumanMessage(content=msg.message)]})
        ai_reply = result["messages"][-1].content
        
        return {
            "ai_response": ai_reply,
            "form_data": form_state
        }
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/form-data")
async def get_form():
    return form_state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)