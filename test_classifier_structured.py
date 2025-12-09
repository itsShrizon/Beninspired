"""
Test file for classifier.py - Tests the structured response format
All datetime fields should be in ISO-8601 UTC format (e.g., "2025-12-03T05:00:00Z")
"""
import pytest
import re
from classifier import classifier, get_current_datetime_utc


# Regex pattern for ISO-8601 UTC format
ISO_8601_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'


def is_valid_iso8601_utc(datetime_str: str) -> bool:
    """Check if datetime string is valid ISO-8601 UTC format"""
    return bool(re.match(ISO_8601_PATTERN, datetime_str))


class TestEventClassification:
    """Test event classification and structure"""
    
    def test_event_doctor_appointment(self):
        """Test doctor appointment classification"""
        result = classifier("Doctor appointment at City Hospital on December 5th at 2:30pm")
        
        assert result["response_type"] == "event"
        assert "title" in result
        assert "description" in result
        assert "location_address" in result
        assert "event_datetime" in result
        assert "reminders" in result
        
        # Check datetime format
        assert is_valid_iso8601_utc(result["event_datetime"]), f"Invalid datetime: {result['event_datetime']}"
    
    def test_event_meeting(self):
        """Test meeting classification"""
        result = classifier("Schedule team meeting tomorrow at 3pm in Conference Room B")
        
        assert result["response_type"] == "event"
        assert is_valid_iso8601_utc(result["event_datetime"])
    
    def test_event_structure_matches_api(self):
        """Test event structure matches POST /actions/events/ format"""
        result = classifier("Annual checkup at 123 Main Street on December 25th at 10am")
        
        assert result["response_type"] == "event"
        
        # Required fields for events
        expected_keys = {"response_type", "title", "description", "location_address", "event_datetime", "reminders"}
        assert set(result.keys()) == expected_keys
        
        # Type checks
        assert isinstance(result["title"], str)
        assert isinstance(result["description"], str)
        assert isinstance(result["location_address"], str)
        assert isinstance(result["reminders"], list)
        
        # Reminders structure
        for reminder in result["reminders"]:
            assert "time_before" in reminder
            assert "types" in reminder
            assert isinstance(reminder["time_before"], int)
            assert isinstance(reminder["types"], list)


class TestTaskClassification:
    """Test task classification and structure"""
    
    def test_task_with_deadline(self):
        """Test task with deadline"""
        result = classifier("Finish project report by Friday at 5pm")
        
        assert result["response_type"] == "task"
        assert "title" in result
        assert "description" in result
        assert "start_time" in result
        assert "end_time" in result
        assert "tags" in result
        assert "reminders" in result
        
        # Check datetime formats
        assert is_valid_iso8601_utc(result["start_time"])
        assert is_valid_iso8601_utc(result["end_time"])
    
    def test_task_urgent_work(self):
        """Test urgent work task"""
        result = classifier("Urgently prepare the final report for submission by December 2nd at 11:20pm")
        
        assert result["response_type"] == "task"
        assert isinstance(result["tags"], list)
    
    def test_task_structure_matches_api(self):
        """Test task structure matches POST /actions/tasks/ format"""
        result = classifier("Submit report by tomorrow noon")
        
        assert result["response_type"] == "task"
        
        # Required fields for tasks
        expected_keys = {"response_type", "title", "description", "start_time", "end_time", "tags", "reminders"}
        assert set(result.keys()) == expected_keys
        
        # Type checks
        assert isinstance(result["title"], str)
        assert isinstance(result["description"], str)
        assert isinstance(result["tags"], list)
        assert isinstance(result["reminders"], list)
        
        # Datetime checks
        assert is_valid_iso8601_utc(result["start_time"])
        assert is_valid_iso8601_utc(result["end_time"])


class TestNoteClassification:
    """Test note classification and structure"""
    
    def test_note_password(self):
        """Test password note"""
        result = classifier("WiFi password is SecurePass123")
        
        assert result["response_type"] == "note"
        assert "title" in result
        assert "content" in result
    
    def test_note_phone_number(self):
        """Test phone number note"""
        result = classifier("Sarah's phone number is 555-1234")
        
        assert result["response_type"] == "note"
    
    def test_note_structure(self):
        """Test note structure"""
        result = classifier("Remember: meeting room code is 4567")
        
        assert result["response_type"] == "note"
        
        expected_keys = {"response_type", "title", "content"}
        assert set(result.keys()) == expected_keys
        
        assert isinstance(result["title"], str)
        assert isinstance(result["content"], str)


class TestResponseClassification:
    """Test general response classification"""
    
    def test_greeting(self):
        """Test greeting is classified as response"""
        result = classifier("Hello, how are you?")
        
        assert result["response_type"] == "response"
        assert set(result.keys()) == {"response_type"}
    
    def test_question(self):
        """Test question is classified as response"""
        result = classifier("What is the weather today?")
        
        assert result["response_type"] == "response"
    
    def test_thanks(self):
        """Test thanks is classified as response"""
        result = classifier("Thank you for your help!")
        
        assert result["response_type"] == "response"


class TestDatetimeFormats:
    """Test ISO-8601 UTC datetime format compliance"""
    
    def test_current_datetime_format(self):
        """Test get_current_datetime_utc function"""
        dt = get_current_datetime_utc()
        assert is_valid_iso8601_utc(dt)
    
    def test_event_datetime_format(self):
        """Test event datetime is ISO-8601 UTC"""
        result = classifier("Meeting on December 15th 2025 at 3pm")
        
        if result["response_type"] == "event":
            assert is_valid_iso8601_utc(result["event_datetime"])
            assert result["event_datetime"].endswith("Z")
    
    def test_task_datetime_format(self):
        """Test task datetimes are ISO-8601 UTC"""
        result = classifier("Complete task by December 20th at 5pm")
        
        if result["response_type"] == "task":
            assert is_valid_iso8601_utc(result["start_time"])
            assert is_valid_iso8601_utc(result["end_time"])
            assert result["start_time"].endswith("Z")
            assert result["end_time"].endswith("Z")


class TestRemindersStructure:
    """Test reminders structure in classifications"""
    
    def test_event_reminders_structure(self):
        """Test event reminders match expected format"""
        result = classifier("Important meeting tomorrow at 9am")
        
        if result["response_type"] == "event":
            reminders = result["reminders"]
            assert isinstance(reminders, list)
            assert len(reminders) > 0
            
            for reminder in reminders:
                assert "time_before" in reminder
                assert "types" in reminder
                assert isinstance(reminder["time_before"], int)
                assert isinstance(reminder["types"], list)
    
    def test_task_reminders_structure(self):
        """Test task reminders match expected format"""
        result = classifier("Finish report by end of day")
        
        if result["response_type"] == "task":
            reminders = result["reminders"]
            assert isinstance(reminders, list)
            
            for reminder in reminders:
                assert "time_before" in reminder
                assert "types" in reminder


class TestWithConversationHistory:
    """Test classifier with conversation history"""
    
    def test_with_history(self):
        """Test classifier with conversation history"""
        history = [
            {"role": "user", "message": "I have a meeting tomorrow"},
            {"role": "assistant", "message": "Got it, a meeting tomorrow"}
        ]
        
        result = classifier("Can we move it to 4pm?", convo_history=history)
        
        # Should recognize this is about an event
        assert result["response_type"] in ["event", "task", "response"]
    
    def test_without_history(self):
        """Test classifier without history (default empty)"""
        result = classifier("Schedule dentist appointment next Monday at 2pm")
        
        assert result["response_type"] == "event"
        assert is_valid_iso8601_utc(result["event_datetime"])


class TestTagsExtraction:
    """Test tags extraction for tasks"""
    
    def test_work_tags(self):
        """Test work-related tags"""
        result = classifier("Submit work report for the project by Friday")
        
        if result["response_type"] == "task":
            assert isinstance(result["tags"], list)
    
    def test_urgent_tags(self):
        """Test urgent tags"""
        result = classifier("Urgently call the client about the deal")
        
        if result["response_type"] == "task":
            assert isinstance(result["tags"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
