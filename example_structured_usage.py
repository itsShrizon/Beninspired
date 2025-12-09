"""
Example usage of the updated chatbot and classifier.
Shows structured responses matching the API format with ISO-8601 UTC timestamps.
"""
import json
from chatbot import chatbot, Chat, format_response_for_display
from classifier import classifier

print("=" * 80)
print("STRUCTURED RESPONSE EXAMPLES")
print("All datetimes are in ISO-8601 UTC format (e.g., 2025-12-03T05:00:00Z)")
print("=" * 80)
print()

# ============================================================================
# EXAMPLE 1: Event Response (matches POST /actions/events/)
# ============================================================================
print("EXAMPLE 1: Event Response")
print("-" * 80)

result = chatbot([], "Doctor appointment at 123 Main Street tomorrow at 2pm")
print("Query: 'Doctor appointment at 123 Main Street tomorrow at 2pm'")
print()
print("Response (ready for POST /actions/events/):")
print(json.dumps(result, indent=2))
print()

# Show with local timezone conversion
print("With local timezone (Asia/Dhaka):")
display_result = format_response_for_display(result, "Asia/Dhaka")
if "event_datetime_local" in display_result:
    print(f"  UTC: {display_result['event_datetime']}")
    print(f"  Local: {display_result['event_datetime_local']}")
print()
print()

# ============================================================================
# EXAMPLE 2: Task Response (matches POST /actions/tasks/)
# ============================================================================
print("EXAMPLE 2: Task Response")
print("-" * 80)

result = chatbot([], "Finish project report by Friday 5pm, it's urgent for work")
print("Query: 'Finish project report by Friday 5pm, it's urgent for work'")
print()
print("Response (ready for POST /actions/tasks/):")
print(json.dumps(result, indent=2))
print()

# Show with local timezone conversion
display_result = format_response_for_display(result, "Asia/Dhaka")
if "start_time_local" in display_result:
    print("With local timezone (Asia/Dhaka):")
    print(f"  Start (UTC): {display_result['start_time']}")
    print(f"  Start (Local): {display_result['start_time_local']}")
    print(f"  End (UTC): {display_result['end_time']}")
    print(f"  End (Local): {display_result['end_time_local']}")
print()
print()

# ============================================================================
# EXAMPLE 3: Note Response
# ============================================================================
print("EXAMPLE 3: Note Response")
print("-" * 80)

result = chatbot([], "WiFi password is SecurePass123")
print("Query: 'WiFi password is SecurePass123'")
print()
print("Response:")
print(json.dumps(result, indent=2))
print()
print()

# ============================================================================
# EXAMPLE 4: General Response
# ============================================================================
print("EXAMPLE 4: General Response")
print("-" * 80)

result = chatbot([], "Hello, how are you?")
print("Query: 'Hello, how are you?'")
print()
print("Response:")
print(json.dumps(result, indent=2))
print()
print()

# ============================================================================
# EXAMPLE 5: Using Classifier (Classification Only)
# ============================================================================
print("EXAMPLE 5: Using Classifier")
print("-" * 80)

result = classifier("Annual checkup at City Hospital on December 25th at 10am")
print("Query: 'Annual checkup at City Hospital on December 25th at 10am'")
print()
print("Classification (ready for POST /actions/events/):")
print(json.dumps(result, indent=2))
print()
print()

# ============================================================================
# EXAMPLE 6: Using Chat Class with Timezone
# ============================================================================
print("EXAMPLE 6: Using Chat Class with Timezone")
print("-" * 80)

chat = Chat(local_tz="Asia/Dhaka")

print("Message 1: 'Schedule team meeting tomorrow at 3pm'")
result = chat.send_and_display("Schedule team meeting tomorrow at 3pm")
print("Response:")
print(json.dumps(result, indent=2))
print()

print("Message 2: 'Add a task to prepare the agenda before the meeting'")
result = chat.send_and_display("Add a task to prepare the agenda before the meeting")
print("Response:")
print(json.dumps(result, indent=2))
print()
print()

# ============================================================================
# API FORMAT REFERENCE
# ============================================================================
print("=" * 80)
print("API FORMAT REFERENCE")
print("=" * 80)
print("""
POST /actions/events/
{
  "title": "Doctor Appointment",
  "description": "Annual checkup",
  "location_address": "123 Main Street",
  "event_datetime": "2025-12-02T23:20:00Z",
  "reminders": [
    {"time_before": 10, "types": ["notification"]},
    {"time_before": 12, "types": ["notification", "call"]}
  ]
}

POST /actions/tasks/
{
  "title": "Finish Project Report",
  "description": "Prepare the final report for submission",
  "start_time": "2025-12-02T23:20:00Z",
  "end_time": "2025-12-02T23:20:00Z",
  "tags": ["work", "urgent"],
  "reminders": [
    {"time_before": 120, "types": ["notification"]},
    {"time_before": 30, "types": ["notification", "call"]}
  ]
}

NOTES:
- All datetime fields are in ISO-8601 UTC format (YYYY-MM-DDTHH:MM:SSZ)
- time_before in reminders is in minutes
- Use format_response_for_display() to convert to local timezone for UI
""")
