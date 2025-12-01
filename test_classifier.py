from classifier import classifier

# Example 1: Simple greeting (should be 'response')
print("=" * 60)
print("Query: 'Hello, how are you?'")
result = classifier([], "Hello, how are you?")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()

# Example 2: Schedule an event
print("=" * 60)
print("Query: 'Schedule a team meeting tomorrow at 3pm'")
result = classifier([], "Schedule a team meeting tomorrow at 3pm")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()

# Example 3: Create a task
print("=" * 60)
print("Query: 'Buy groceries - milk, eggs, bread'")
result = classifier([], "Buy groceries - milk, eggs, bread")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()

# Example 4: Save a note
print("=" * 60)
print("Query: 'WiFi password is SecurePass123'")
result = classifier([], "WiFi password is SecurePass123")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()

# Example 5: Task with deadline
print("=" * 60)
print("Query: 'Submit report by Friday 5pm'")
result = classifier([], "Submit report by Friday 5pm")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()

# Example 6: Question (response type)
print("=" * 60)
print("Query: 'What is the weather today?'")
result = classifier([], "What is the weather today?")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()

# Example 7: Event with specific date and time
print("=" * 60)
print("Query: 'Doctor appointment on December 5th at 2:30pm'")
result = classifier([], "Doctor appointment on December 5th at 2:30pm")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()

# Example 8: Note with date
print("=" * 60)
print("Query: 'Sarah's birthday is March 15th'")
result = classifier([], "Sarah's birthday is March 15th")
print(f"Classification: {result['response_type']}")
print(f"Full result: {result}")
print()
