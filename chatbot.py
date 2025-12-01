import os
import json
from typing import List, Dict, Any
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


def chatbot(convo_history: List[Dict], query: str) -> Dict[str, Any]:
    """
    Chatbot that classifies user queries and returns structured responses.
    
    Args:
        convo_history: List of conversation messages with 'role', 'timestamp', 'message'
        query: User's current query
        
    Returns:
        Dict with 'response_type' (response/event/note/task), 'content', and optional 'date'/'time'
    """
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    system_prompt = """You are a helpful assistant that helps users manage their day.
Classify the user's request and respond accordingly:
- response: General conversation or questions
- event: Time-specific activities or appointments (include DATE and TIME)
- note: Information to remember or save (include DATE and TIME if mentioned)
- task: Action items or todos (include DATE and TIME if deadline mentioned)

Format your response as JSON:
{
  "type": "response|event|note|task",
  "content": "your response",
  "date": "YYYY-MM-DD (if applicable)",
  "time": "HH:MM (if applicable)"
}

Only include date and time fields if they are mentioned or relevant."""
    
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
        
        output = {
            "response_type": result.get("type", "response"),
            "content": result.get("content", response.content)
        }
        
        # Add date and time if present
        if "date" in result and result["date"]:
            output["date"] = result["date"]
        if "time" in result and result["time"]:
            output["time"] = result["time"]
            
        return output
    except (json.JSONDecodeError, ValueError, KeyError):
        # Fallback if JSON parsing fails
        return {
            "response_type": "response",
            "content": response.content
        }


class Chat:
    """
    Simple conversation manager - handles conversation history automatically.
    
    Usage:
        chat = Chat()
        response = chat.send("Schedule meeting tomorrow at 3pm")
        print(response["content"])
    """
    
    def __init__(self):
        """Initialize with empty conversation history"""
        self.history: List[Dict] = []
    
    def send(self, message: str) -> Dict[str, Any]:
        """
        Send a message and get response. Automatically manages history.
        
        Args:
            message: User's message
            
        Returns:
            Dict with response_type, content, date, time
        """
        # Get chatbot response
        result = chatbot(self.history, message)
        
        # Append user message to history
        self.history.append({
            "role": "user",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message
        })
        
        # Append assistant response to history
        self.history.append({
            "role": "assistant",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": result["content"]
        })
        
        return result
    
    def get_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.history
    
    def clear(self):
        """Clear conversation history"""
        self.history = []
    
    def __call__(self, message: str) -> Dict[str, Any]:
        """Allow using chat instance as a function"""
        return self.send(message)
