"""
Conversation Manager - Helper class to manage chatbot interactions.
All timestamps are in ISO-8601 UTC format.
"""
import json
from chatbot import chatbot, get_current_datetime_utc, format_response_for_display
from typing import List, Dict, Any


class ConversationManager:
    """Helper class to manage conversation history and interactions"""
    
    def __init__(self, local_tz: str = None):
        self.history: List[Dict] = []
        self.local_tz = local_tz
    
    def send_message(self, user_message: str) -> Dict[str, Any]:
        """
        Send a user message and get chatbot response.
        Automatically manages conversation history.
        
        Args:
            user_message: The user's message
            
        Returns:
            Structured response (event/task/note/response format)
        """
        # Get chatbot response
        result = chatbot(self.history, user_message)
        
        # Append user message to history
        self.history.append({
            "role": "user",
            "timestamp": get_current_datetime_utc(),
            "message": user_message
        })
        
        # Append assistant response to history
        content = result.get("content") or result.get("title") or result.get("description", "")
        self.history.append({
            "role": "assistant",
            "timestamp": get_current_datetime_utc(),
            "message": content
        })
        
        return result
    
    def send_message_for_display(self, user_message: str) -> Dict[str, Any]:
        """
        Send message and get response with local timezone conversion.
        
        Returns:
            Response with additional _local fields for datetime
        """
        result = self.send_message(user_message)
        return format_response_for_display(result, self.local_tz)
    
    def get_history(self) -> List[Dict]:
        """Get the full conversation history"""
        return self.history
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
    
    def get_last_exchange(self) -> Dict:
        """Get the last user-assistant exchange"""
        if len(self.history) >= 2:
            return {
                "user": self.history[-2],
                "assistant": self.history[-1]
            }
        return {}


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("CONVERSATION MANAGER EXAMPLE")
    print("All datetimes in ISO-8601 UTC format (e.g., 2025-12-03T05:00:00Z)")
    print("=" * 70)
    print()
    
    # Create conversation manager with timezone
    manager = ConversationManager(local_tz="Asia/Dhaka")
    
    # Turn 1: Event
    print("User: Schedule a team meeting tomorrow at 3pm in Conference Room A")
    result = manager.send_message_for_display("Schedule a team meeting tomorrow at 3pm in Conference Room A")
    print(f"Response Type: {result['response_type']}")
    print(f"Full Response:")
    print(json.dumps(result, indent=2))
    print()
    
    # Turn 2: Task
    print("User: Add a task to prepare the meeting agenda by tonight")
    result = manager.send_message_for_display("Add a task to prepare the meeting agenda by tonight")
    print(f"Response Type: {result['response_type']}")
    print(f"Full Response:")
    print(json.dumps(result, indent=2))
    print()
    
    # Turn 3: Note
    print("User: Remember the meeting room code is 4567")
    result = manager.send_message_for_display("Remember the meeting room code is 4567")
    print(f"Response Type: {result['response_type']}")
    print(f"Full Response:")
    print(json.dumps(result, indent=2))
    print()
    
    # Turn 4: General response
    print("User: Thanks for your help!")
    result = manager.send_message_for_display("Thanks for your help!")
    print(f"Response Type: {result['response_type']}")
    print(f"Full Response:")
    print(json.dumps(result, indent=2))
    print()
    
    # Show full history
    print("=" * 70)
    print("FULL CONVERSATION HISTORY:")
    print("=" * 70)
    print(json.dumps(manager.get_history(), indent=2))
