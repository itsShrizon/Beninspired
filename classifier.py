import os
import json
from typing import List, Dict, Any
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


def get_current_datetime_utc() -> str:
    """Get current datetime in ISO-8601 UTC format"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classifier(query: str, convo_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Classifier that identifies the type of user query and extracts structured data.
    
    Args:
        query: User's current query
        convo_history: Optional list of conversation messages
        
    Returns:
        For events: {response_type, title, description, location_address, event_datetime, reminders}
        For tasks: {response_type, title, description, start_time, end_time, tags, reminders}
        For notes: {response_type, title, content}
        For response: {response_type}
        
    All datetime fields are in ISO-8601 UTC format (e.g., "2025-12-03T05:00:00Z")
    """
    if convo_history is None:
        convo_history = []
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    
    system_prompt = f"""You are a classification system that categorizes user queries and extracts structured data.
Current date: {current_date}
Current time: {current_time}

Classify and extract data based on the type:

For EVENTS (appointments, meetings, scheduled activities):
{{
  "type": "event",
  "title": "Short title of the event",
  "description": "Detailed description",
  "location_address": "Address or location (empty string if not mentioned)",
  "event_datetime": "YYYY-MM-DDTHH:MM:SSZ (UTC format)",
  "reminders": [
    {{"time_before": 30, "types": ["notification"]}}
  ]
}}

For TASKS (action items, todos):
{{
  "type": "task",
  "title": "Short title of the task",
  "description": "Detailed description of what needs to be done",
  "start_time": "YYYY-MM-DDTHH:MM:SSZ (UTC format)",
  "end_time": "YYYY-MM-DDTHH:MM:SSZ (deadline, UTC format)",
  "tags": ["tag1", "tag2"],
  "reminders": [
    {{"time_before": 60, "types": ["notification"]}}
  ]
}}

For NOTES (information to remember):
{{
  "type": "note",
  "title": "Short title of the note",
  "content": "The information to save"
}}

For GENERAL/RESPONSE (questions, greetings):
{{
  "type": "response"
}}

IMPORTANT:
- All datetime must be in ISO-8601 UTC format (e.g., "2025-12-03T05:00:00Z")
- time_before in reminders is in minutes
- Extract relevant tags for tasks
- Do NOT include conversational content - only classification data"""
    
    messages = [SystemMessage(content=system_prompt)]
    
    # Add conversation history
    for msg in convo_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["message"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["message"]))
    
    # Add current query
    messages.append(HumanMessage(content=query))
    
    # Get response
    response = llm.invoke(messages)
    
    # Parse JSON response
    try:
        result = json.loads(response.content.strip())
        
        # Handle if result is a list (take first item)
        if isinstance(result, list):
            result = result[0] if result else {}
        
        # Ensure result is a dict
        if not isinstance(result, dict):
            raise ValueError("Invalid response format")
        
        response_type = result.get("type", "response")
        
        if response_type == "event":
            return {
                "response_type": "event",
                "title": result.get("title", ""),
                "description": result.get("description", ""),
                "location_address": result.get("location_address", ""),
                "event_datetime": result.get("event_datetime", get_current_datetime_utc()),
                "reminders": result.get("reminders", [{"time_before": 30, "types": ["notification"]}])
            }
        
        elif response_type == "task":
            return {
                "response_type": "task",
                "title": result.get("title", ""),
                "description": result.get("description", ""),
                "start_time": result.get("start_time", get_current_datetime_utc()),
                "end_time": result.get("end_time", get_current_datetime_utc()),
                "tags": result.get("tags", []),
                "reminders": result.get("reminders", [{"time_before": 60, "types": ["notification"]}])
            }
        
        elif response_type == "note":
            return {
                "response_type": "note",
                "title": result.get("title", ""),
                "content": result.get("content", "")
            }
        
        else:  # response
            return {
                "response_type": "response"
            }
            
    except (json.JSONDecodeError, ValueError, KeyError):
        # Fallback classification
        return {
            "response_type": "response"
        }
