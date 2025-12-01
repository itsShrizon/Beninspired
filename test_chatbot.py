import pytest
import os
from chatbot import chatbot


class TestEventResponses:
    """Test event classification and structured output - Real API calls"""
    
    def test_event_meeting_tomorrow_afternoon(self):
        result = chatbot([], "Schedule a team meeting tomorrow at 3pm")
        assert result["response_type"] == "event"
        assert "date" in result
        assert "time" in result
    
    def test_event_doctor_appointment(self):
        result = chatbot([], "I have a doctor's appointment next Monday at 2:30pm")
        assert result["response_type"] == "event"
        assert "date" in result or "time" in result
    
    def test_event_birthday_party(self):
        result = chatbot([], "Sarah's birthday party is on December 15th")
        assert result["response_type"] == "event"
        assert "date" in result
    
    def test_event_conference_multiday(self):
        result = chatbot([], "I'm attending a tech conference from Nov 28 to Dec 2")
        assert result["response_type"] == "event"
    
    def test_event_lunch_meeting(self):
        result = chatbot([], "Lunch meeting with the client today at noon")
        assert result["response_type"] == "event"
        assert "time" in result or "date" in result
    
    def test_event_dentist_checkup(self):
        result = chatbot([], "Book dentist for a checkup on Friday morning")
        assert result["response_type"] in ["event", "task"]
    
    def test_event_wedding_anniversary(self):
        result = chatbot([], "Our wedding anniversary is June 20, 2026")
        assert result["response_type"] in ["event", "note", "response"]
        # Date may or may not be extracted for informational statements
    
    def test_event_zoom_call(self):
        result = chatbot([], "Zoom call with the team at 4:30pm tomorrow")
        assert result["response_type"] == "event"
    
    def test_event_gym_class(self):
        result = chatbot([], "Yoga class every Tuesday and Thursday at 6pm")
        assert result["response_type"] == "event"
    
    def test_event_concert_tickets(self):
        result = chatbot([], "Concert on New Year's Eve at 9pm")
        assert result["response_type"] == "event"


class TestTaskResponses:
    """Test task classification and structured output - Real API calls"""
    
    def test_task_submit_report_deadline(self):
        result = chatbot([], "I need to submit the quarterly report by end of day Friday")
        assert result["response_type"] == "task"
    
    def test_task_grocery_shopping(self):
        result = chatbot([], "Buy milk, eggs, bread, and coffee beans")
        assert result["response_type"] == "task"
    
    def test_task_call_someone_urgent(self):
        result = chatbot([], "Urgent: call the accountant about tax documents")
        assert result["response_type"] == "task"
    
    def test_task_fix_bug(self):
        result = chatbot([], "Need to debug the login authentication issue before Monday")
        assert result["response_type"] == "task"
    
    def test_task_send_email(self):
        result = chatbot([], "Send follow-up email to Alex about the proposal")
        assert result["response_type"] == "task"
    
    def test_task_pay_bill(self):
        result = chatbot([], "Pay the internet bill by November 30th")
        assert result["response_type"] == "task"
        assert "date" in result
    
    def test_task_prepare_presentation(self):
        result = chatbot([], "Prepare slides for the investor pitch next week")
        assert result["response_type"] == "task"
    
    def test_task_workout_routine(self):
        result = chatbot([], "Do 30 minutes of cardio and strength training")
        assert result["response_type"] == "task"
    
    def test_task_clean_house(self):
        result = chatbot([], "Clean the apartment this weekend")
        assert result["response_type"] == "task"
    
    def test_task_book_flight(self):
        result = chatbot([], "Book flight tickets to Tokyo for Christmas vacation")
        assert result["response_type"] == "task"


class TestNoteResponses:
    """Test note classification and structured output - Real API calls"""
    
    def test_note_wifi_password(self):
        result = chatbot([], "The WiFi password for the office is SecurePass2025!")
        assert result["response_type"] == "note"
    
    def test_note_phone_number(self):
        result = chatbot([], "Lisa's new phone number is 555-123-4567")
        assert result["response_type"] == "note"
    
    def test_note_birthday_date(self):
        result = chatbot([], "Mark's birthday is on March 8th")
        assert result["response_type"] == "note"
        assert "date" in result
    
    def test_note_favorite_restaurant(self):
        result = chatbot([], "My favorite Italian restaurant is Antonio's on 5th Avenue")
        assert result["response_type"] == "note"
    
    def test_note_book_recommendation(self):
        result = chatbot([], "Recommended book: Deep Work by Cal Newport")
        assert result["response_type"] == "note"
    
    def test_note_recipe_ingredients(self):
        result = chatbot([], "Grandma's cake recipe: 2 cups flour, 1 cup sugar, 3 eggs, butter")
        assert result["response_type"] == "note"
    
    def test_note_quote_inspiration(self):
        result = chatbot([], "Save this quote: 'Success is not final, failure is not fatal'")
        assert result["response_type"] == "note"
    
    def test_note_parking_location(self):
        result = chatbot([], "Parked in lot C, section 4, spot 27")
        assert result["response_type"] == "note"
    
    def test_note_project_idea(self):
        result = chatbot([], "Idea: Build a mobile app for tracking daily habits")
        assert result["response_type"] == "note"
    
    def test_note_license_plate(self):
        result = chatbot([], "Client's car license plate is XYZ-1234")
        assert result["response_type"] == "note"


class TestGeneralResponses:
    """Test general conversation responses - Real API calls"""
    
    def test_response_greeting(self):
        result = chatbot([], "Hello, how are you?")
        assert result["response_type"] == "response"
        assert "content" in result
    
    def test_response_help_question(self):
        result = chatbot([], "What can you help me with?")
        assert result["response_type"] == "response"
    
    def test_response_thanks(self):
        result = chatbot([], "Thank you so much!")
        assert result["response_type"] == "response"
    
    def test_response_weather_question(self):
        result = chatbot([], "Do you know what the weather is like today?")
        assert result["response_type"] == "response"
    
    def test_response_explain_concept(self):
        result = chatbot([], "Can you explain what machine learning is?")
        assert result["response_type"] == "response"
    
    def test_response_joke_request(self):
        result = chatbot([], "Tell me a funny joke")
        assert result["response_type"] == "response"
    
    def test_response_goodbye(self):
        result = chatbot([], "Goodbye, see you later!")
        assert result["response_type"] == "response"
    
    def test_response_random_chat(self):
        result = chatbot([], "I'm feeling good today")
        assert result["response_type"] == "response"
    
    def test_response_capability_question(self):
        result = chatbot([], "Are you able to set reminders?")
        assert result["response_type"] == "response"
    
    def test_response_clarification_needed(self):
        result = chatbot([], "Something something tomorrow")
        assert result["response_type"] == "response"


class TestConversationHistory:
    """Test conversation history handling - Real API calls"""
    
    def test_with_simple_history(self):
        history = [
            {"role": "user", "timestamp": "2025-11-22T10:00:00Z", "message": "Hi there"},
            {"role": "assistant", "timestamp": "2025-11-22T10:00:05Z", "message": "Hello! How can I help?"}
        ]
        result = chatbot(history, "Schedule a meeting for 2pm today")
        assert result["response_type"] == "event"
    
    def test_context_from_history(self):
        history = [
            {"role": "user", "timestamp": "2025-11-22T10:00:00Z", "message": "I need to organize my week"},
            {"role": "assistant", "timestamp": "2025-11-22T10:00:05Z", "message": "I can help with that!"}
        ]
        result = chatbot(history, "Add a dentist appointment on Friday at 3pm")
        assert result["response_type"] == "event"
    
    def test_follow_up_task(self):
        history = [
            {"role": "user", "timestamp": "2025-11-22T09:00:00Z", "message": "I'm working on a big project"},
            {"role": "assistant", "timestamp": "2025-11-22T09:00:05Z", "message": "Great! Let me know if you need help organizing tasks"}
        ]
        result = chatbot(history, "Add finishing the design mockups to my list")
        assert result["response_type"] == "task"


class TestAmbiguousScenarios:
    """Test ambiguous and edge case scenarios - Real API calls"""
    
    def test_ambiguous_time_reference(self):
        result = chatbot([], "Let's meet sometime next week")
        assert result["response_type"] in ["event", "response"]
    
    def test_vague_task(self):
        result = chatbot([], "I should probably work on that thing")
        assert result["response_type"] in ["task", "response"]
    
    def test_mixed_intent(self):
        result = chatbot([], "Remind me Sarah's birthday is March 5th and I need to buy a gift")
        assert result["response_type"] in ["event", "note", "task"]
    
    def test_question_with_date(self):
        result = chatbot([], "What day is December 25th?")
        assert result["response_type"] == "response"
    
    def test_statement_about_past(self):
        result = chatbot([], "I went to the doctor yesterday")
        assert result["response_type"] in ["note", "response"]
    
    def test_conditional_task(self):
        result = chatbot([], "If it rains tomorrow, remind me to bring an umbrella")
        assert result["response_type"] in ["task", "note"]
    
    def test_multiple_dates_one_query(self):
        result = chatbot([], "Meeting on Monday, report due Wednesday, and presentation Friday")
        assert result["response_type"] in ["event", "task"]
    
    def test_special_characters_password(self):
        result = chatbot([], "Password is T3$t@2025!#")
        assert result["response_type"] == "note"
    
    def test_very_casual_language(self):
        result = chatbot([], "yo grab some pizza later?")
        assert result["response_type"] in ["event", "response", "task"]
    
    def test_numbered_list_input(self):
        result = chatbot([], "1. Call dentist 2. Buy groceries 3. Finish report")
        assert result["response_type"] == "task"


class TestDateTimeVariations:
    """Test various date and time format interpretations - Real API calls"""
    
    def test_relative_date_tomorrow(self):
        result = chatbot([], "Meeting tomorrow at 10am")
        assert result["response_type"] == "event"
        assert "date" in result or "time" in result
    
    def test_relative_date_next_week(self):
        result = chatbot([], "Doctor appointment next Tuesday")
        assert result["response_type"] == "event"
    
    def test_twelve_hour_format(self):
        result = chatbot([], "Conference call at 3:30 PM")
        assert result["response_type"] == "event"
        assert "time" in result
    
    def test_specific_date_format(self):
        result = chatbot([], "Deadline is November 30, 2025")
        assert result["response_type"] in ["event", "task"]
    
    def test_time_range(self):
        result = chatbot([], "Meeting from 2pm to 4pm tomorrow")
        assert result["response_type"] == "event"


class TestComplexRealWorldScenarios:
    """Test complex unpredictable real-world scenarios - Real API calls"""
    
    def test_nested_task_with_multiple_steps(self):
        result = chatbot([], "Prepare for the presentation: research competitors, create slides, practice delivery, all by Thursday")
        assert result["response_type"] == "task"
    
    def test_event_with_location_and_people(self):
        result = chatbot([], "Team lunch with Sarah and Mike at the downtown bistro on Friday noon")
        assert result["response_type"] == "event"
    
    def test_conditional_reminder(self):
        result = chatbot([], "If the package arrives, remember to check the contents and sign the receipt")
        assert result["response_type"] in ["task", "note"]
    
    def test_recurring_complex_schedule(self):
        result = chatbot([], "Gym every Monday, Wednesday, and Friday at 7am starting next week")
        assert result["response_type"] == "event"
    
    def test_contact_info_with_multiple_fields(self):
        result = chatbot([], "New client: Jennifer Adams, email jen.adams@company.com, phone 555-9876, based in Seattle")
        assert result["response_type"] == "note"
    
    def test_travel_itinerary(self):
        result = chatbot([], "Flight to Boston on Dec 10 at 6am, return on Dec 15 at 8pm")
        assert result["response_type"] in ["event", "note", "response"]
    
    def test_deadline_with_consequences(self):
        result = chatbot([], "Must submit tax documents by April 15 or face penalties")
        assert result["response_type"] == "task"
    
    def test_shopping_list_with_quantities(self):
        result = chatbot([], "Buy 2 dozen eggs, 5 pounds of flour, 3 bottles of olive oil, and fresh herbs")
        assert result["response_type"] == "task"
    
    def test_event_cancellation_mention(self):
        result = chatbot([], "Cancel the 3pm meeting and reschedule for next Monday at 10am")
        assert result["response_type"] in ["event", "task"]
    
    def test_brainstorming_session_note(self):
        result = chatbot([], "Project ideas from today's brainstorm: AI chatbot, expense tracker app, recipe organizer")
        assert result["response_type"] == "note"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
