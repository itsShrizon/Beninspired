"""
SIMPLE USAGE EXAMPLES - Just import chatbot.py
"""

from chatbot import Chat

# ==========================================
# EXAMPLE 1: Simple Usage (Recommended)
# ==========================================
print("=" * 60)
print("EXAMPLE 1: Simple Usage")
print("=" * 60)

chat = Chat()

# Just send messages - history is automatic!
response = chat.send("Schedule a team meeting tomorrow at 3pm")
print(f"Bot: {response['content']}")
print(f"Type: {response['response_type']}")
if 'time' in response:
    print(f"Time: {response['time']}")
print()

# Next message - history is remembered
response = chat.send("What time is the meeting?")
print(f"Bot: {response['content']}")
print()

# Another message
response = chat.send("Can we move it to 4pm?")
print(f"Bot: {response['content']}")
print()


# ==========================================
# EXAMPLE 2: Even Simpler - Use as Function
# ==========================================
print("=" * 60)
print("EXAMPLE 2: Use as Function")
print("=" * 60)

chat = Chat()

# You can call the chat object directly!
result = chat("Buy milk, eggs, and bread")
print(f"Bot: {result['content']}")
print(f"Type: {result['response_type']}")
print()

result = chat("Also add coffee")
print(f"Bot: {result['content']}")
print()


# ==========================================
# EXAMPLE 3: Multiple Conversations
# ==========================================
print("=" * 60)
print("EXAMPLE 3: Multiple Conversations")
print("=" * 60)

chat1 = Chat()
chat2 = Chat()

# Conversation 1
result = chat1.send("Schedule dentist for Monday")
print(f"Chat 1: {result['content']}")

# Conversation 2 (separate, won't know about dentist)
result = chat2.send("What's on my calendar?")
print(f"Chat 2: {result['content']}")
print()


# ==========================================
# EXAMPLE 4: Access History
# ==========================================
print("=" * 60)
print("EXAMPLE 4: Access History")
print("=" * 60)

chat = Chat()
chat.send("Hello")
chat.send("Schedule meeting tomorrow")
chat.send("Thanks!")

print("Full conversation history:")
for msg in chat.get_history():
    print(f"  {msg['role']}: {msg['message']}")
print()


# ==========================================
# EXAMPLE 5: Clear History
# ==========================================
print("=" * 60)
print("EXAMPLE 5: Clear History")
print("=" * 60)

chat = Chat()
chat.send("Schedule meeting")
print(f"Messages: {len(chat.get_history())}")  # 2 messages

chat.clear()
print(f"After clear: {len(chat.get_history())}")  # 0 messages

chat.send("Buy groceries")
print(f"New conversation: {len(chat.get_history())}")  # 2 messages
print()


# ==========================================
# EXAMPLE 6: Extract Structured Data
# ==========================================
print("=" * 60)
print("EXAMPLE 6: Extract Structured Data")
print("=" * 60)

chat = Chat()

# Events
result = chat.send("Doctor appointment next Friday at 2pm")
if result['response_type'] == 'event':
    print(f"📅 Event: {result['content']}")
    print(f"   Date: {result.get('date', 'Not specified')}")
    print(f"   Time: {result.get('time', 'Not specified')}")

# Tasks
result = chat.send("Buy birthday gift by Wednesday")
if result['response_type'] == 'task':
    print(f"✓ Task: {result['content']}")
    if 'date' in result:
        print(f"   Deadline: {result['date']}")

# Notes
result = chat.send("WiFi password is SecurePass123")
if result['response_type'] == 'note':
    print(f"📝 Note: {result['content']}")
print()


# ==========================================
# EXAMPLE 7: For Django/Flask (Simple)
# ==========================================
print("=" * 60)
print("EXAMPLE 7: Web Framework Integration")
print("=" * 60)

# Store chat per session
sessions = {}

def handle_message(session_id, message):
    # Get or create chat for this session
    if session_id not in sessions:
        sessions[session_id] = Chat()
    
    chat = sessions[session_id]
    result = chat.send(message)
    
    return result

# Simulate requests
result = handle_message("user123", "Schedule meeting tomorrow")
print(f"Response: {result['content']}")

result = handle_message("user123", "What time?")
print(f"Response: {result['content']}")
print()

print("=" * 60)
print("THAT'S IT! Super simple to use!")
print("=" * 60)
