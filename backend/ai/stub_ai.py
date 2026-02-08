"""
Stub AI response generator for the chatbot feature.
This module provides mock AI responses for development and testing.
"""

import random
import time
from typing import Dict, Any, Optional
from datetime import datetime


class StubAIResponder:
    """
    A stub AI responder that generates mock responses for testing and development.
    This will be replaced with a real AI service in production.
    """

    def __init__(self):
        """
        Initialize the stub AI responder with predefined response patterns.
        """
        self.response_templates = [
            "I understand you're asking about '{query}'. Based on our conversation, I'd suggest considering various perspectives on this topic.",
            "Thanks for sharing '{query}' with me. This is an interesting point that relates to broader themes in your work.",
            "Regarding '{query}', I think it's important to consider the context and potential implications of different approaches.",
            "I've noted your message about '{query}'. This connects to other items we've discussed previously.",
            "That's a thoughtful question about '{query}'. From what I understand, there are several factors to consider here.",
            "Based on your input regarding '{query}', I can provide some insights that might be helpful.",
            "I recognize '{query}' as an important topic in your workflow. Let me share some observations.",
            "Your point about '{query}' is well-taken. How does this relate to your other objectives?",
            "Interesting perspective on '{query}'. Have you considered alternative viewpoints?",
            "Thanks for bringing up '{query}'. I can see how this connects to your broader goals."
        ]

        # More specific responses for common queries
        self.todo_specific_responses = {
            "task": [
                "I see you mentioned tasks. Managing tasks effectively often involves prioritization and regular review.",
                "Tasks are fundamental to productivity. Consider grouping related tasks together for efficiency.",
                "I understand you're thinking about tasks. What's the most important one right now?",
                "Regarding tasks, it's helpful to break larger items into smaller, manageable pieces."
            ],
            "todo": [
                "Todos are great for organizing your work. Consider reviewing your list regularly.",
                "I see you're focused on todos. How can I help you prioritize these items?",
                "Todos help maintain focus on important activities. What's the priority level of this item?",
                "Organizing todos effectively can improve your productivity significantly."
            ],
            "complete": [
                "Completing tasks gives a sense of accomplishment and moves you toward your goals.",
                "I see you're interested in completing items. What's blocking progress right now?",
                "Completion is an important milestone. How can we help you achieve this?",
                "Finishing tasks is rewarding and helps maintain momentum on your projects."
            ],
            "schedule": [
                "Scheduling helps ensure important tasks receive adequate attention.",
                "I understand scheduling is important to you. How can I help optimize your schedule?",
                "Time management through scheduling can significantly improve productivity.",
                "Consider the dependencies between scheduled items to avoid conflicts."
            ]
        }

    def generate_response(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a mock AI response based on the user's message.

        Args:
            user_message: The message from the user
            context: Optional context information about the conversation

        Returns:
            str: A generated response string
        """
        # Simulate AI processing time
        time.sleep(random.uniform(0.5, 1.5))

        user_message_lower = user_message.lower()

        # Check for specific keywords that trigger tailored responses
        for keyword, responses in self.todo_specific_responses.items():
            if keyword in user_message_lower:
                return random.choice(responses)

        # Use a general template if no specific keyword matched
        template = random.choice(self.response_templates)
        response = template.format(query=user_message[:50] + "..." if len(user_message) > 50 else user_message)

        # Add a personalized ending based on time of day
        hour = datetime.now().hour
        if 5 <= hour < 12:
            response += " Good morning! Hope this helps."
        elif 12 <= hour < 17:
            response += " Good afternoon! Let me know if you'd like more details."
        elif 17 <= hour < 21:
            response += " Good evening! Feel free to ask more questions."
        else:
            response += " Thanks for reaching out. Looking forward to continuing our discussion."

        return response

    def generate_response_async(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Asynchronously generate a mock AI response (simulated for this stub implementation).

        Args:
            user_message: The message from the user
            context: Optional context information about the conversation

        Returns:
            str: A generated response string
        """
        # In a real implementation, this would be truly async
        # For the stub, we just use the regular method
        return self.generate_response(user_message, context)

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the AI model (stub implementation).

        Returns:
            Dict[str, Any]: Information about the stub AI model
        """
        return {
            "model_name": "stub-ai-v1",
            "version": "1.0.0",
            "provider": "Mock AI Provider",
            "capabilities": ["text_generation", "context_awareness"],
            "is_production_ready": False,
            "estimated_response_time": "0.5-1.5 seconds"
        }


# Global instance for easy access
stub_ai = StubAIResponder()


def get_ai_response(user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to get an AI response using the stub responder.

    Args:
        user_message: The message from the user
        context: Optional context information about the conversation

    Returns:
        str: A generated response string
    """
    return stub_ai.generate_response(user_message, context)


def get_stub_ai_instance() -> StubAIResponder:
    """
    Get the global instance of the stub AI responder.

    Returns:
        StubAIResponder: The global stub AI responder instance
    """
    return stub_ai