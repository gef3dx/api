from enum import Enum
from typing import Any, Dict, Optional

from jinja2 import Template


class MessageTemplateType(str, Enum):
    """Message template types."""

    WELCOME = "welcome"
    NOTIFICATION = "notification"
    ALERT = "alert"
    REMINDER = "reminder"
    CONFIRMATION = "confirmation"


class MessageTemplate:
    """Message template system using Jinja2."""

    # Default templates
    DEFAULT_TEMPLATES = {
        MessageTemplateType.WELCOME: {
            "subject": "Welcome to our platform!",
            "content": "Hello {{ user_name }}!\n\nWelcome to our platform. We're excited to have you on board.\n\nBest regards,\nThe Team",
        },
        MessageTemplateType.NOTIFICATION: {
            "subject": "{{ notification_title }}",
            "content": "{{ notification_message }}",
        },
        MessageTemplateType.ALERT: {
            "subject": "Alert: {{ alert_title }}",
            "content": "Attention required: {{ alert_message }}\n\nPlease take action as soon as possible.",
        },
        MessageTemplateType.REMINDER: {
            "subject": "Reminder: {{ reminder_title }}",
            "content": "This is a reminder about: {{ reminder_message }}\n\nDue date: {{ due_date }}",
        },
        MessageTemplateType.CONFIRMATION: {
            "subject": "Confirmation: {{ action }}",
            "content": "Your {{ action }} has been confirmed.\n\nDetails:\n{{ details }}",
        },
    }

    def __init__(self):
        """Initialize the template system."""
        self.templates = self.DEFAULT_TEMPLATES.copy()

    def add_template(
        self, template_type: MessageTemplateType, subject: str, content: str
    ) -> None:
        """
        Add a new template or update an existing one.

        Args:
            template_type: The template type
            subject: The subject template string
            content: The content template string
        """
        self.templates[template_type] = {"subject": subject, "content": content}

    def render(
        self,
        template_type: MessageTemplateType,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Render a template with the provided context.

        Args:
            template_type: The template type to render
            context: Context variables for the template

        Returns:
            Dict with rendered subject and content

        Raises:
            ValueError: If template type is not found
        """
        if template_type not in self.templates:
            raise ValueError(f"Template type '{template_type}' not found")

        if context is None:
            context = {}

        template_data = self.templates[template_type]

        # Render subject and content
        subject_template = Template(template_data["subject"])
        content_template = Template(template_data["content"])

        return {
            "subject": subject_template.render(context),
            "content": content_template.render(context),
        }

    def get_template_types(self) -> list:
        """
        Get all available template types.

        Returns:
            List of available template types
        """
        return list(self.templates.keys())


# Global template instance
message_template = MessageTemplate()
