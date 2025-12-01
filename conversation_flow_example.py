from chatbot import chatbot
import json
from datetime import datetime

# Initialize empty conversation history
convo_history = []

print("=" * 70)
print("COMPLETE CONVERSATION FLOW - How to Append to History")
print("=" * 70)
print()

# TURN 1
print("TURN 1:")
print("-" * 70)
user_message_1 = "Schedule a team meeting tomorrow at 3pm"
print(f"User says: '{user_message_1}'")
print()

# Call chatbot
result_1 = chatbot(convo_history, user_message_1)
print(f"Chatbot returns: {json.dumps(result_1, indent=2)}")
print()

# Append user message to history
convo_history.append({
    "role": "user",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "message": user_message_1
})

# Append assistant response to history
# KEY: Use the 'content' field from chatbot output as the message
convo_history.append({
    "role": "assistant",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "message": result_1["content"]  # THIS IS THE KEY!
})

print("Updated conversation history:")
print(json.dumps(convo_history, indent=2))
print()
print()

# TURN 2
print("TURN 2:")
print("-" * 70)
user_message_2 = "What time is the meeting?"
print(f"User says: '{user_message_2}'")
print()

# Call chatbot with updated history
result_2 = chatbot(convo_history, user_message_2)
print(f"Chatbot returns: {json.dumps(result_2, indent=2)}")
print()

# Append to history
convo_history.append({
    "role": "user",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "message": user_message_2
})

convo_history.append({
    "role": "assistant",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "message": result_2["content"]
})

print("Updated conversation history:")
print(json.dumps(convo_history, indent=2))
print()
print()

# TURN 3
print("TURN 3:")
print("-" * 70)
user_message_3 = "Can we move it to 4pm instead?"
print(f"User says: '{user_message_3}'")
print()

# Call chatbot with full history
result_3 = chatbot(convo_history, user_message_3)
print(f"Chatbot returns: {json.dumps(result_3, indent=2)}")
print()

# Append to history
convo_history.append({
    "role": "user",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "message": user_message_3
})

convo_history.append({
    "role": "assistant",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "message": result_3["content"]
})

print("Final conversation history:")
print(json.dumps(convo_history, indent=2))
print()

print("=" * 70)
print("SUMMARY OF THE FLOW:")
print("=" * 70)
print("""
1. User sends message
2. Call: result = chatbot(convo_history, user_message)
3. Append user message to convo_history with role='user'
4. Append result['content'] to convo_history with role='assistant'
5. Repeat for next turn

KEY POINT: 
- Chatbot OUTPUT has: response_type, content, date, time
- Conversation history INPUT needs: role, timestamp, message
- Use result['content'] as the 'message' field for assistant
""")
