from chatbot import chatbot

# Example 1: Simple greeting
print("=" * 60)
print("Example 1: Greeting")
result = chatbot([], "Hello, how are you?")
print(f"Type: {result['response_type']}")
print(f"Response: {result['content']}")
print()

# Example 2: Schedule an event
print("=" * 60)
print("Example 2: Schedule Event")
result = chatbot([], "Schedule a team meeting tomorrow at 3pm")
print(f"Type: {result['response_type']}")
print(f"Response: {result['content']}")
if 'date' in result:
    print(f"Date: {result['date']}")
if 'time' in result:
    print(f"Time: {result['time']}")
print()

# Example 3: Create a task
print("=" * 60)
print("Example 3: Create Task")
result = chatbot([], "Buy groceries - milk, eggs, bread")
print(f"Type: {result['response_type']}")
print(f"Response: {result['content']}")
if 'date' in result:
    print(f"Date: {result['date']}")
print()

# Example 4: Save a note
print("=" * 60)
print("Example 4: Save Note")
result = chatbot([], "WiFi password is SecurePass123")
print(f"Type: {result['response_type']}")
print(f"Response: {result['content']}")
print()

# Example 5: With conversation history
print("=" * 60)
print("Example 5: With Conversation History")
history = [
    {"role": "user", "timestamp": "2025-11-22T10:00:00Z", "message": "Hi"},
    {"role": "assistant", "timestamp": "2025-11-22T10:00:05Z", "message": "Hello! How can I help you today?"}
]
result = chatbot(history, "Can you help me schedule a doctor appointment?")
print(f"Type: {result['response_type']}")
print(f"Response: {result['content']}")
print()
