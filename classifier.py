import os
import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


def classifier(query: str) -> Dict[str, Any]:
    """
    Classifier that only identifies the type of user query without generating responses.
    
    Args:
        convo_history: List of conversation messages with 'role', 'timestamp', 'message'
        query: User's current query
        
    Returns:
        Dict with 'response_type' (response/event/note/task) and optional 'date'/'time'
    """
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    system_prompt = """You are a classification system that categorizes user queries.
Classify the user's request into one of these categories:
- response: General conversation or questions that don't require action
- event: Time-specific activities, appointments, or scheduled items
- note: Information to remember or save for later
- task: Action items, todos, or things that need to be done

Extract dates and times if mentioned.

Format your response as JSON with ONLY classification data (no conversational content):
{
  "type": "response|event|note|task",
  "date": "YYYY-MM-DD (if applicable)",
  "time": "HH:MM (if applicable)"
}

Only include date and time fields if they are explicitly mentioned."""
    
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
            "response_type": result.get("type", "response")
        }
        
        # Add date and time if present
        if "date" in result and result["date"]:
            output["date"] = result["date"]
        if "time" in result and result["time"]:
            output["time"] = result["time"]
            
        return output
    except (json.JSONDecodeError, ValueError, KeyError):
        # Fallback classification
        return {
            "response_type": "response"
        }
