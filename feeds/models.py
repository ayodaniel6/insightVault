from django.db import models
from django.utils import timezone

class FeedSource(models.Model):
    """
    Represents an external source (RSS, API endpoint, Twitter list, YouTube channel).
    """
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    api_type = models.CharField(max_length=50, choices=[('rss','rss'),('rest','rest'),('youtube','youtube'),('twitter','twitter')])
    endpoint = models.TextField()          # API url or RSS url
    enabled = models.BooleanField(default=True)
    last_fetched = models.DateTimeField(null=True, blank=True)
    config = models.JSONField(default=dict, blank=True)  # auth / params / parsing hints

    def __str__(self):
        return self.name

class FeedItem(models.Model):
    """
    Normalized single feed item.
    """
    source = models.ForeignKey(FeedSource, on_delete=models.CASCADE, related_name='items')
    external_id = models.CharField(max_length=255, db_index=True)  # unique id from source
    title = models.CharField(max_length=400)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)   # full HTML or raw text
    url = models.URLField(max_length=1000, blank=True)
    author = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(default=timezone.now)
    raw = models.JSONField(null=True, blank=True)   # raw payload for debugging
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('source', 'external_id')
        ordering = ['-published_at', '-fetched_at']

    def __str__(self):
        return f"{self.source.slug}:{self.external_id}"
