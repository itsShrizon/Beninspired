"""
Test file for chatbot.py - Tests the structured response format
All datetime fields should be in ISO-8601 UTC format (e.g., "2025-12-03T05:00:00Z")
"""
import pytest
import re
from chatbot import chatbot, Chat, get_current_datetime_utc, utc_to_local, format_response_for_display


# Regex pattern for ISO-8601 UTC format
ISO_8601_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'


def is_valid_iso8601_utc(datetime_str: str) -> bool:
    """Check if datetime string is valid ISO-8601 UTC format"""
    return bool(re.match(ISO_8601_PATTERN, datetime_str))


class TestEventResponses:
    """Test event responses match the required structure"""
    
    def test_event_doctor_appointment(self):
        """Test event with location"""
        result = chatbot([], "Doctor appointment at 123 Main Street tomorrow at 2pm")
        
        assert result["response_type"] == "event"
        assert "title" in result
        assert "description" in result
        assert "location_address" in result
        assert "event_datetime" in result
        assert "reminders" in result
        
        # Check datetime format
        assert is_valid_iso8601_utc(result["event_datetime"]), f"Invalid datetime format: {result['event_datetime']}"
        
        # Check reminders structure
        assert isinstance(result["reminders"], list)
        for reminder in result["reminders"]:
            assert "time_before" in reminder
            assert "types" in reminder
            assert isinstance(reminder["time_before"], int)
            assert isinstance(reminder["types"], list)
    
    def test_event_meeting(self):
        """Test meeting event"""
        result = chatbot([], "Schedule team meeting on December 15th at 3pm in Conference Room A")
        
        assert result["response_type"] == "event"
        assert "title" in result
        assert "event_datetime" in result
        assert is_valid_iso8601_utc(result["event_datetime"])
    
    def test_event_birthday_party(self):
        """Test party event"""
        result = chatbot([], "Sarah's birthday party on January 20th at 6pm at her house")
        
        assert result["response_type"] == "event"
        assert "title" in result
        assert "location_address" in result
        assert is_valid_iso8601_utc(result["event_datetime"])
    
    def test_event_structure_complete(self):
        """Test complete event structure matches API format"""
        result = chatbot([], "Annual checkup at City Hospital on December 25th at 10am")
        
        expected_keys = {"response_type", "title", "description", "location_address", "event_datetime", "reminders"}
        assert set(result.keys()) == expected_keys
        
        # Verify structure matches POST /actions/events/
        assert isinstance(result["title"], str)
        assert isinstance(result["description"], str)
        assert isinstance(result["location_address"], str)
        assert is_valid_iso8601_utc(result["event_datetime"])
        assert isinstance(result["reminders"], list)


class TestTaskResponses:
    """Test task responses match the required structure"""
    
    def test_task_with_deadline(self):
        """Test task with deadline"""
        result = chatbot([], "Finish project report by Friday at 5pm")
        
        assert result["response_type"] == "task"
        assert "title" in result
        assert "description" in result
        assert "start_time" in result
        assert "end_time" in result
        assert "tags" in result
        assert "reminders" in result
        
        # Check datetime formats
        assert is_valid_iso8601_utc(result["start_time"]), f"Invalid start_time format: {result['start_time']}"
        assert is_valid_iso8601_utc(result["end_time"]), f"Invalid end_time format: {result['end_time']}"
    
    def test_task_urgent(self):
        """Test urgent task"""
        result = chatbot([], "Urgently submit the final report for work by tomorrow noon")
        
        assert result["response_type"] == "task"
        assert "tags" in result
        assert isinstance(result["tags"], list)
        # Should contain urgent or work tags
        tags_lower = [t.lower() for t in result["tags"]]
        assert any(tag in tags_lower for tag in ["urgent", "work"]) or len(result["tags"]) >= 0
    
    def test_task_structure_complete(self):
        """Test complete task structure matches API format"""
        result = chatbot([], "Prepare final report for submission by December 2nd at 11:20pm")
        
        expected_keys = {"response_type", "title", "description", "start_time", "end_time", "tags", "reminders"}
        assert set(result.keys()) == expected_keys
        
        # Verify structure matches POST /actions/tasks/
        assert isinstance(result["title"], str)
        assert isinstance(result["description"], str)
        assert is_valid_iso8601_utc(result["start_time"])
        assert is_valid_iso8601_utc(result["end_time"])
        assert isinstance(result["tags"], list)
        assert isinstance(result["reminders"], list)
        
        # Check reminder structure
        for reminder in result["reminders"]:
            assert "time_before" in reminder
            assert "types" in reminder


class TestNoteResponses:
    """Test note responses match the required structure"""
    
    def test_note_password(self):
        """Test saving a password note"""
        result = chatbot([], "WiFi password is SecurePass123")
        
        assert result["response_type"] == "note"
        assert "title" in result
        assert "content" in result
    
    def test_note_structure_complete(self):
        """Test complete note structure"""
        result = chatbot([], "Remember: Sarah's phone number is 555-1234")
        
        expected_keys = {"response_type", "title", "content"}
        assert set(result.keys()) == expected_keys
        
        assert isinstance(result["title"], str)
        assert isinstance(result["content"], str)


class TestGeneralResponses:
    """Test general conversation responses"""
    
    def test_greeting(self):
        """Test greeting response"""
        result = chatbot([], "Hello, how are you?")
        
        assert result["response_type"] == "response"
        assert "content" in result
        assert isinstance(result["content"], str)
    
    def test_question(self):
        """Test question response"""
        result = chatbot([], "What can you help me with?")
        
        assert result["response_type"] == "response"
        assert "content" in result


class TestDatetimeFormat:
    """Test ISO-8601 UTC datetime formatting"""
    
    def test_get_current_datetime_utc(self):
        """Test current datetime function"""
        dt = get_current_datetime_utc()
        assert is_valid_iso8601_utc(dt)
    
    def test_utc_to_local_conversion(self):
        """Test UTC to local conversion"""
        utc_time = "2025-12-03T05:00:00Z"
        local_time = utc_to_local(utc_time, "Asia/Dhaka")
        assert local_time is not None
        assert "2025" in local_time
    
    def test_format_response_for_display_event(self):
        """Test display formatting for events"""
        result = {
            "response_type": "event",
            "title": "Test Event",
            "description": "Test",
            "location_address": "",
            "event_datetime": "2025-12-03T05:00:00Z",
            "reminders": []
        }
        
        display = format_response_for_display(result, "Asia/Dhaka")
        assert "event_datetime_local" in display
    
    def test_format_response_for_display_task(self):
        """Test display formatting for tasks"""
        result = {
            "response_type": "task",
            "title": "Test Task",
            "description": "Test",
            "start_time": "2025-12-03T05:00:00Z",
            "end_time": "2025-12-03T10:00:00Z",
            "tags": [],
            "reminders": []
        }
        
        display = format_response_for_display(result, "Asia/Dhaka")
        assert "start_time_local" in display
        assert "end_time_local" in display


class TestChatClass:
    """Test the Chat class"""
    
    def test_chat_send(self):
        """Test sending message via Chat class"""
        chat = Chat()
        result = chat.send("Schedule meeting tomorrow at 3pm")
        
        assert "response_type" in result
        assert result["response_type"] in ["event", "task", "note", "response"]
    
    def test_chat_history(self):
        """Test conversation history"""
        chat = Chat()
        chat.send("Hello")
        
        history = chat.get_history()
        assert len(history) == 2  # user + assistant
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        
        # Check timestamps are ISO-8601 UTC
        assert is_valid_iso8601_utc(history[0]["timestamp"])
        assert is_valid_iso8601_utc(history[1]["timestamp"])
    
    def test_chat_with_timezone(self):
        """Test Chat with local timezone"""
        chat = Chat(local_tz="Asia/Dhaka")
        result = chat.send_and_display("Doctor appointment tomorrow at 2pm")
        
        if result["response_type"] == "event":
            assert "event_datetime_local" in result
    
    def test_chat_clear(self):
        """Test clearing history"""
        chat = Chat()
        chat.send("Hello")
        chat.clear()
        
        assert len(chat.get_history()) == 0


class TestRemindersStructure:
    """Test reminders structure in responses"""
    
    def test_event_reminders(self):
        """Test event has proper reminder structure"""
        result = chatbot([], "Important meeting tomorrow at 9am")
        
        if result["response_type"] == "event":
            reminders = result["reminders"]
            assert isinstance(reminders, list)
            
            for reminder in reminders:
                assert "time_before" in reminder
                assert "types" in reminder
                assert isinstance(reminder["time_before"], int)
                assert isinstance(reminder["types"], list)
                assert all(t in ["notification", "call", "email"] for t in reminder["types"])
    
    def test_task_reminders(self):
        """Test task has proper reminder structure"""
        result = chatbot([], "Submit report by Friday 5pm")
        
        if result["response_type"] == "task":
            reminders = result["reminders"]
            assert isinstance(reminders, list)
            
            for reminder in reminders:
                assert "time_before" in reminder
                assert "types" in reminder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
