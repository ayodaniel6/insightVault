from django.db import models
from django.conf import settings
from django.utils.html import mark_safe
from .utils import format_note_content  # ✅ use same formatter everywhere

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)  # Raw Markdown-like text
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        # Auto-name if title is blank or only spaces
        if not self.title.strip():
            self.title = "Untitled"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def render_html(self):
        """Render safe HTML using the same formatting rules as AJAX."""
        return mark_safe(format_note_content(self.content))
