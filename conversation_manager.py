from chatbot import chatbot
from datetime import datetime, timezone
from typing import List, Dict, Any


class ConversationManager:
    """Helper class to manage conversation history and interactions"""
    
    def __init__(self):
        self.history: List[Dict] = []
    
    def send_message(self, user_message: str) -> Dict[str, Any]:
        """
        Send a user message and get chatbot response.
        Automatically manages conversation history.
        
        Args:
            user_message: The user's message
            
        Returns:
            Dict with response_type, content, and optional date/time
        """
        # Get chatbot response
        result = chatbot(self.history, user_message)
        
        # Append user message to history
        self.history.append({
            "role": "user",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": user_message
        })
        
        # Append assistant response to history
        self.history.append({
            "role": "assistant",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": result["content"]
        })
        
        return result
    
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
    print("=" * 70)
    print()
    
    # Create conversation manager
    manager = ConversationManager()
    
    # Turn 1
    print("User: Schedule a team meeting tomorrow at 3pm")
    result = manager.send_message("Schedule a team meeting tomorrow at 3pm")
    print(f"Assistant: {result['content']}")
    print(f"Type: {result['response_type']}")
    if 'date' in result:
        print(f"Date: {result['date']}")
    if 'time' in result:
        print(f"Time: {result['time']}")
    print()
    
    # Turn 2
    print("User: What time is the meeting?")
    result = manager.send_message("What time is the meeting?")
    print(f"Assistant: {result['content']}")
    print(f"Type: {result['response_type']}")
    print()
    
    # Turn 3
    print("User: Can we move it to 4pm instead?")
    result = manager.send_message("Can we move it to 4pm instead?")
    print(f"Assistant: {result['content']}")
    print(f"Type: {result['response_type']}")
    if 'time' in result:
        print(f"New Time: {result['time']}")
    print()
    
    # Turn 4
    print("User: Also add a task to send agenda before the meeting")
    result = manager.send_message("Also add a task to send agenda before the meeting")
    print(f"Assistant: {result['content']}")
    print(f"Type: {result['response_type']}")
    print()
    
    # Show full history
    print("=" * 70)
    print("FULL CONVERSATION HISTORY:")
    print("=" * 70)
    import json
    print(json.dumps(manager.get_history(), indent=2))
