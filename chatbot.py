import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


def get_current_datetime_utc() -> str:
    """Get current datetime in ISO-8601 UTC format"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_to_local(utc_datetime_str: str, local_tz: str = None) -> str:
    """
    Convert UTC datetime string to local timezone.
    
    Args:
        utc_datetime_str: ISO-8601 UTC datetime string (e.g., "2025-12-03T05:00:00Z")
        local_tz: Local timezone name (e.g., "Asia/Dhaka"). If None, uses system timezone.
        
    Returns:
        Formatted local datetime string
    """
    try:
        # Parse UTC datetime
        if utc_datetime_str.endswith('Z'):
            utc_datetime_str = utc_datetime_str[:-1] + '+00:00'
        utc_dt = datetime.fromisoformat(utc_datetime_str)
        
        # Convert to local timezone
        if local_tz:
            local_timezone = ZoneInfo(local_tz)
        else:
            local_timezone = datetime.now().astimezone().tzinfo
        
        local_dt = utc_dt.astimezone(local_timezone)
        return local_dt.strftime("%Y-%m-%d %H:%M %Z")
    except Exception:
        return utc_datetime_str


def local_to_utc(date_str: str, time_str: str = None, local_tz: str = None) -> str:
    """
    Convert local date/time to UTC ISO-8601 format.
    
    Args:
        date_str: Date string (e.g., "2025-12-03", "tomorrow", "next Monday")
        time_str: Time string (e.g., "15:00", "3pm")
        local_tz: Local timezone name. If None, uses system timezone.
        
    Returns:
        ISO-8601 UTC datetime string (e.g., "2025-12-03T05:00:00Z")
    """
    try:
        # Get local timezone
        if local_tz:
            local_timezone = ZoneInfo(local_tz)
        else:
            local_timezone = datetime.now().astimezone().tzinfo
        
        # Parse date
        if date_str:
            local_dt = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            local_dt = datetime.now()
        
        # Add time if provided
        if time_str:
            time_parts = datetime.strptime(time_str, "%H:%M")
            local_dt = local_dt.replace(hour=time_parts.hour, minute=time_parts.minute, second=0)
        else:
            local_dt = local_dt.replace(hour=0, minute=0, second=0)
        
        # Make timezone aware and convert to UTC
        local_dt = local_dt.replace(tzinfo=local_timezone)
        utc_dt = local_dt.astimezone(timezone.utc)
        
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        # Fallback: return current time in UTC
        return get_current_datetime_utc()


def chatbot(convo_history: List[Dict], query: str) -> Dict[str, Any]:
    """
    Chatbot that classifies user queries and returns structured responses.
    
    Args:
        convo_history: List of conversation messages with 'role', 'timestamp', 'message'
        query: User's current query
        
    Returns:
        For events: {response_type, title, description, location_address, event_datetime, reminders}
        For tasks: {response_type, title, description, start_time, end_time, tags, reminders}
        For notes: {response_type, title, content}
        For response: {response_type, content}
        
    All datetime fields are in ISO-8601 UTC format (e.g., "2025-12-03T05:00:00Z")
    """
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    
    system_prompt = f"""You are a helpful assistant that helps users manage their day.
Current date: {current_date}
Current time: {current_time}

Classify the user's request and respond with structured JSON:

For EVENTS (appointments, meetings, scheduled activities):
{{
  "type": "event",
  "title": "Short title of the event",
  "description": "Detailed description",
  "location_address": "Address or location (if mentioned, otherwise empty string)",
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
  "start_time": "YYYY-MM-DDTHH:MM:SSZ (when to start, UTC format)",
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

For GENERAL RESPONSE (questions, greetings, etc.):
{{
  "type": "response",
  "content": "Your helpful response"
}}

IMPORTANT:
- All datetime must be in ISO-8601 UTC format (e.g., "2025-12-03T05:00:00Z")
- Convert mentioned times to UTC (assume user is in local timezone)
- time_before in reminders is in minutes
- Include appropriate reminders based on urgency
- Extract tags from context for tasks
- Always include location_address for events (empty string if not mentioned)"""
    
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
                "response_type": "response",
                "content": result.get("content", response.content)
            }
            
    except (json.JSONDecodeError, ValueError, KeyError):
        # Fallback if JSON parsing fails
        return {
            "response_type": "response",
            "content": response.content
        }


def format_response_for_display(result: Dict[str, Any], local_tz: str = None) -> Dict[str, Any]:
    """
    Convert UTC times in response to local timezone for display.
    
    Args:
        result: Chatbot response dict
        local_tz: Local timezone name (e.g., "Asia/Dhaka")
        
    Returns:
        Same response with datetime fields converted to local time
    """
    display_result = result.copy()
    
    if result["response_type"] == "event":
        display_result["event_datetime_local"] = utc_to_local(result["event_datetime"], local_tz)
    
    elif result["response_type"] == "task":
        display_result["start_time_local"] = utc_to_local(result["start_time"], local_tz)
        display_result["end_time_local"] = utc_to_local(result["end_time"], local_tz)
    
    return display_result


class Chat:
    """
    Simple conversation manager - handles conversation history automatically.
    
    Usage:
        chat = Chat()
        response = chat.send("Schedule meeting tomorrow at 3pm")
        print(response)
    """
    
    def __init__(self, local_tz: str = None):
        """Initialize with empty conversation history"""
        self.history: List[Dict] = []
        self.local_tz = local_tz
    
    def send(self, message: str) -> Dict[str, Any]:
        """
        Send a message and get response. Automatically manages history.
        
        Args:
            message: User's message
            
        Returns:
            Structured response based on type (event/task/note/response)
        """
        # Get chatbot response
        result = chatbot(self.history, message)
        
        # Append user message to history
        self.history.append({
            "role": "user",
            "timestamp": get_current_datetime_utc(),
            "message": message
        })
        
        # Append assistant response to history
        content = result.get("content") or result.get("title") or result.get("description", "")
        self.history.append({
            "role": "assistant",
            "timestamp": get_current_datetime_utc(),
            "message": content
        })
        
        return result
    
    def send_and_display(self, message: str) -> Dict[str, Any]:
        """
        Send a message and get response with local timezone conversion.
        
        Returns:
            Response with additional _local fields for datetime
        """
        result = self.send(message)
        return format_response_for_display(result, self.local_tz)
    
    def get_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.history
    
    def clear(self):
        """Clear conversation history"""
        self.history = []
    
    def __call__(self, message: str) -> Dict[str, Any]:
        """Allow using chat instance as a function"""
        return self.send(message)
