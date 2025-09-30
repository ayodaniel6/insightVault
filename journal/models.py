from django.db import models
from django.conf import settings
from django.utils import timezone
from core.utils import format_note_content   

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)  # Raw markdown text
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="notes")
    pinned = models.BooleanField(default=False)
    feed_item = models.ForeignKey(
        "feeds.FeedItem",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="notes"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-pinned", "-updated_at"]

    def save(self, *args, **kwargs):
        if not self.title or not self.title.strip():
            self.title = "Untitled"
        super().save(*args, **kwargs)

    def rendered_html(self):
        """Return safe, formatted HTML using markdown parser."""
        return format_note_content(self.content)   

    def __str__(self):
        return self.title
