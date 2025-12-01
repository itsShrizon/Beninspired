# Django Integration Guide

Complete guide for integrating the chatbot and classifier into Django views.

## Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Django Models](#django-models)
- [Views Implementation](#views-implementation)
- [URL Configuration](#url-configuration)
- [Frontend Integration](#frontend-integration)
- [Complete Examples](#complete-examples)

---

## Quick Start

```bash
# 1. Install dependencies
pip install langchain langchain-openai python-dotenv openai

# 2. Add to your Django project
# Copy chatbot.py, classifier.py, and conversation_manager.py to your Django app

# 3. Set environment variable
# Add to your .env file:
OPENAI_API_KEY=your_api_key_here

# 4. Create models and views (see below)
```

---

## Installation

### 1. Install Required Packages

```bash
pip install langchain langchain-openai python-dotenv openai djangorestframework
```

Add to `requirements.txt`:
```
Django>=4.2
djangorestframework>=3.14
langchain>=0.1.0
langchain-openai>=0.0.5
python-dotenv>=1.0.0
openai>=1.0.0
```

### 2. Copy Chatbot Files

Place these files in your Django app directory (e.g., `chat/`):
- `chatbot.py`
- `classifier.py`
- `conversation_manager.py`

### 3. Environment Setup

Create `.env` in your Django project root:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
DEBUG=True
SECRET_KEY=your-secret-key
```

In `settings.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

# Your existing settings...
```

---

## Project Structure

```
myproject/
├── manage.py
├── .env
├── myproject/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── chat/                      # Your Django app
    ├── __init__.py
    ├── models.py              # Conversation models
    ├── views.py               # Chatbot views
    ├── urls.py                # URL routing
    ├── serializers.py         # DRF serializers
    ├── chatbot.py             # Chatbot function
    ├── classifier.py          # Classifier function
    └── conversation_manager.py # Helper class
```

---

## Django Models

Create models to store conversations, events, tasks, and notes.

**`chat/models.py`:**

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Conversation(models.Model):
    """Store conversation sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.session_id} - {self.user.username}"


class Message(models.Model):
    """Store individual messages in conversations"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Store structured data from chatbot response
    response_type = models.CharField(max_length=20, null=True, blank=True)  # event/task/note/response
    metadata = models.JSONField(null=True, blank=True)  # Store date, time, etc.
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class Event(models.Model):
    """Store extracted events"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return self.title


class Task(models.Model):
    """Store extracted tasks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    deadline = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['completed', 'deadline']
    
    def __str__(self):
        return self.description[:50]


class Note(models.Model):
    """Store extracted notes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.content[:50]
```

**Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Views Implementation

### Basic Function-Based View

**`chat/views.py`:**

```python
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

from .models import Conversation, Message, Event, Task, Note
from .chatbot import chatbot
from .classifier import classifier


@login_required
@csrf_exempt
def chat_message(request):
    """Handle incoming chat messages"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            user=request.user,
            session_id=session_id,
            defaults={'session_id': session_id}
        )
        
        # Get conversation history
        history = []
        for msg in conversation.messages.all():
            history.append({
                'role': msg.role,
                'timestamp': msg.timestamp.isoformat(),
                'message': msg.content
            })
        
        # Get chatbot response
        result = chatbot(history, user_message)
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message,
            timestamp=timezone.now()
        )
        
        # Save assistant message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['content'],
            response_type=result['response_type'],
            metadata={
                'date': result.get('date'),
                'time': result.get('time')
            },
            timestamp=timezone.now()
        )
        
        # Extract and save structured data
        _extract_structured_data(request.user, conversation, result)
        
        return JsonResponse({
            'success': True,
            'message': result['content'],
            'response_type': result['response_type'],
            'date': result.get('date'),
            'time': result.get('time'),
            'message_id': assistant_msg.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _extract_structured_data(user, conversation, result):
    """Extract and save events, tasks, and notes"""
    response_type = result['response_type']
    
    if response_type == 'event':
        Event.objects.create(
            user=user,
            conversation=conversation,
            title=result['content'],
            date=result.get('date'),
            time=result.get('time')
        )
    elif response_type == 'task':
        Task.objects.create(
            user=user,
            conversation=conversation,
            description=result['content'],
            deadline=result.get('date')
        )
    elif response_type == 'note':
        Note.objects.create(
            user=user,
            conversation=conversation,
            content=result['content'],
            date=result.get('date')
        )


@login_required
def get_conversation_history(request, session_id):
    """Get full conversation history"""
    try:
        conversation = Conversation.objects.get(
            user=request.user,
            session_id=session_id
        )
        
        messages = []
        for msg in conversation.messages.all():
            messages.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'response_type': msg.response_type,
                'metadata': msg.metadata
            })
        
        return JsonResponse({
            'session_id': session_id,
            'messages': messages
        })
        
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)


@login_required
def get_user_events(request):
    """Get all user events"""
    events = Event.objects.filter(user=request.user).values(
        'id', 'title', 'date', 'time', 'created_at'
    )
    return JsonResponse({'events': list(events)})


@login_required
def get_user_tasks(request):
    """Get all user tasks"""
    tasks = Task.objects.filter(user=request.user).values(
        'id', 'description', 'deadline', 'completed', 'created_at'
    )
    return JsonResponse({'tasks': list(tasks)})


@login_required
def get_user_notes(request):
    """Get all user notes"""
    notes = Note.objects.filter(user=request.user).values(
        'id', 'content', 'date', 'created_at'
    )
    return JsonResponse({'notes': list(notes)})


@login_required
@csrf_exempt
def classify_message(request):
    """Classify a message without generating response"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Classify the message
        result = classifier([], message)
        
        return JsonResponse({
            'response_type': result['response_type'],
            'date': result.get('date'),
            'time': result.get('time')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

---

## Class-Based Views (Django REST Framework)

**`chat/serializers.py`:**

```python
from rest_framework import serializers
from .models import Conversation, Message, Event, Task, Note


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'timestamp', 'response_type', 'metadata']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'session_id', 'created_at', 'updated_at', 'messages']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'date', 'time', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'description', 'deadline', 'completed', 'created_at']


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'content', 'date', 'created_at']
```

**`chat/views.py` (DRF version):**

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Conversation, Message, Event, Task, Note
from .serializers import (
    ConversationSerializer, MessageSerializer,
    EventSerializer, TaskSerializer, NoteSerializer
)
from .chatbot import chatbot
from .classifier import classifier


class ChatViewSet(viewsets.ViewSet):
    """Viewset for chat functionality"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send a message and get chatbot response"""
        user_message = request.data.get('message', '').strip()
        session_id = request.data.get('session_id')
        
        if not user_message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            user=request.user,
            session_id=session_id,
            defaults={'session_id': session_id}
        )
        
        # Build conversation history
        history = []
        for msg in conversation.messages.all():
            history.append({
                'role': msg.role,
                'timestamp': msg.timestamp.isoformat(),
                'message': msg.content
            })
        
        # Get chatbot response
        result = chatbot(history, user_message)
        
        # Save messages
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['content'],
            response_type=result['response_type'],
            metadata={
                'date': result.get('date'),
                'time': result.get('time')
            }
        )
        
        # Extract structured data
        self._extract_data(request.user, conversation, result)
        
        return Response({
            'message': result['content'],
            'response_type': result['response_type'],
            'date': result.get('date'),
            'time': result.get('time'),
            'message_id': assistant_msg.id
        })
    
    @action(detail=False, methods=['post'])
    def classify(self, request):
        """Classify a message without generating response"""
        message = request.data.get('message', '').strip()
        
        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = classifier([], message)
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get conversation history"""
        session_id = request.query_params.get('session_id')
        
        try:
            conversation = Conversation.objects.get(
                user=request.user,
                session_id=session_id
            )
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _extract_data(self, user, conversation, result):
        """Extract and save structured data"""
        response_type = result['response_type']
        
        if response_type == 'event':
            Event.objects.create(
                user=user,
                conversation=conversation,
                title=result['content'],
                date=result.get('date'),
                time=result.get('time')
            )
        elif response_type == 'task':
            Task.objects.create(
                user=user,
                conversation=conversation,
                description=result['content'],
                deadline=result.get('date')
            )
        elif response_type == 'note':
            Note.objects.create(
                user=user,
                conversation=conversation,
                content=result['content'],
                date=result.get('date')
            )


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user events"""
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for user tasks"""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class NoteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user notes"""
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
```

---

## URL Configuration

**`chat/urls.py`:**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# For DRF
router = DefaultRouter()
router.register(r'chat', views.ChatViewSet, basename='chat')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'notes', views.NoteViewSet, basename='note')

urlpatterns = [
    # DRF URLs
    path('api/', include(router.urls)),
    
    # Function-based view URLs (alternative)
    # path('chat/', views.chat_message, name='chat_message'),
    # path('chat/history/<str:session_id>/', views.get_conversation_history, name='conversation_history'),
    # path('events/', views.get_user_events, name='user_events'),
    # path('tasks/', views.get_user_tasks, name='user_tasks'),
    # path('notes/', views.get_user_notes, name='user_notes'),
    # path('classify/', views.classify_message, name='classify_message'),
]
```

**`myproject/urls.py`:**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
]
```

---

## Frontend Integration

### JavaScript/AJAX Example

```javascript
// Send message to chatbot
async function sendMessage(message, sessionId) {
    const response = await fetch('/api/chat/send_message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            message: message,
            session_id: sessionId
        })
    });
    
    const data = await response.json();
    return data;
}

// Usage
const result = await sendMessage('Schedule meeting tomorrow at 3pm', 'session-123');
console.log(result.message);  // Display chatbot response
console.log(result.response_type);  // 'event', 'task', 'note', or 'response'
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function ChatComponent() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [sessionId] = useState('session-' + Date.now());
    
    const sendMessage = async () => {
        if (!input.trim()) return;
        
        // Add user message to UI
        setMessages([...messages, { role: 'user', content: input }]);
        
        try {
            const response = await fetch('/api/chat/send_message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    message: input,
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            // Add assistant message to UI
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.message,
                type: data.response_type,
                date: data.date,
                time: data.time
            }]);
            
            setInput('');
        } catch (error) {
            console.error('Error:', error);
        }
    };
    
    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <p>{msg.content}</p>
                        {msg.type === 'event' && msg.date && (
                            <span className="badge">📅 {msg.date} {msg.time}</span>
                        )}
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type a message..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}
```

---

## Complete Examples

### Example 1: Simple Chat Page

**`chat/templates/chat.html`:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
    <style>
        .chat-box { max-width: 600px; margin: 50px auto; }
        .messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; text-align: right; }
        .assistant { background: #f5f5f5; }
        .badge { font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="chat-box">
        <div id="messages" class="messages"></div>
        <input type="text" id="input" placeholder="Type a message..." style="width: 80%">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <script>
        const sessionId = 'session-' + Date.now();
        
        async function sendMessage() {
            const input = document.getElementById('input');
            const message = input.value.trim();
            if (!message) return;
            
            // Display user message
            addMessage('user', message);
            input.value = '';
            
            // Send to backend
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            // Display assistant message
            addMessage('assistant', data.message, data.response_type, data.date, data.time);
        }
        
        function addMessage(role, content, type, date, time) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            let html = `<p>${content}</p>`;
            if (type === 'event' && date) {
                html += `<span class="badge">📅 ${date} ${time || ''}</span>`;
            } else if (type === 'task') {
                html += `<span class="badge">✓ Task added</span>`;
            } else if (type === 'note') {
                html += `<span class="badge">📝 Note saved</span>`;
            }
            
            messageDiv.innerHTML = html;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        document.getElementById('input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
```

---

## Testing

### Test with curl:

```bash
# Send message
curl -X POST http://localhost:8000/api/chat/send_message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{"message": "Schedule meeting tomorrow at 3pm", "session_id": "test-123"}'

# Get history
curl http://localhost:8000/api/chat/history/?session_id=test-123 \
  -H "Authorization: Token your-auth-token"

# Get events
curl http://localhost:8000/api/events/ \
  -H "Authorization: Token your-auth-token"
```

---

## Best Practices

1. **Use session IDs**: Generate unique session IDs for each conversation
2. **Limit history**: Only load recent messages (last 20-30) to avoid token limits
3. **Cache conversations**: Use Django cache for active conversations
4. **Background tasks**: Use Celery for heavy processing if needed
5. **Error handling**: Always handle API errors gracefully
6. **Rate limiting**: Implement rate limiting to prevent abuse
7. **Monitor costs**: Track OpenAI API usage

---

## Troubleshooting

**Issue: "No module named 'langchain'"**
- Solution: Install dependencies: `pip install -r requirements.txt`

**Issue: OpenAI API errors**
- Solution: Check your API key in `.env` file
- Solution: Ensure you have credits in your OpenAI account

**Issue: Slow responses**
- Solution: Use `gpt-3.5-turbo` instead of `gpt-4` for faster responses
- Solution: Implement caching for common queries

**Issue: Context too long**
- Solution: Limit conversation history to last N messages
- Solution: Implement message summarization

---

## Next Steps

1. Add user authentication
2. Implement WebSocket for real-time chat
3. Add file upload capabilities
4. Create admin dashboard for monitoring
5. Implement conversation search
6. Add multi-language support
7. Create mobile app integration

---

## Support

For issues or questions:
- Check the examples in `examples.txt`
- Review `USAGE_GUIDE.txt`
- Test with `conversation_manager.py`
