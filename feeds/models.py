from django.db import models
from django.utils import timezone
import hashlib

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class FeedSource(models.Model):
    class ApiType(models.TextChoices):
        RSS = "rss", "RSS"
        REST = "rest", "REST"
        YOUTUBE = "youtube", "YouTube"
        TWITTER = "twitter", "Twitter"

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    api_type = models.CharField(max_length=50, choices=ApiType.choices)
    endpoint = models.TextField()  # API URL or RSS URL
    enabled = models.BooleanField(default=True)
    last_fetched = models.DateTimeField(null=True, blank=True)
    # Optional conditional request headers stored here (or in config)
    etag = models.CharField(max_length=255, blank=True, null=True)
    last_modified = models.CharField(max_length=255, blank=True, null=True)
    # config can store auth tokens, fetch params, parsing hints, rate limits, etc.
    config = models.JSONField(default=dict, blank=True)

    # optional fetch hints (in seconds or cron rule in config)
    fetch_interval_seconds = models.IntegerField(null=True, blank=True)
    logo_url = models.URLField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.name

class FeedItem(TimestampedModel):
    source = models.ForeignKey(FeedSource, on_delete=models.CASCADE, related_name="items")
    external_id = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=400)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)   # full HTML or raw text
    url = models.URLField(max_length=1000, blank=True)
    author = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(default=timezone.now)
    image_url = models.URLField(max_length=1000, blank=True)  
    video_url = models.URLField(max_length=1000, blank=True) 
    raw = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # helper for dedupe by content — store hex sha256 of (url || content)
    content_hash = models.CharField(max_length=64, db_index=True, blank=True, null=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "external_id"], name="uniq_source_external"),
        ]
        ordering = ["-published_at", "-fetched_at"]
        indexes = [
            models.Index(fields=["published_at"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["content_hash"]),
        ]

    def __str__(self):
        return f"{self.source.slug}:{self.external_id}"

    def compute_and_set_content_hash(self):
        """
        Compute a stable hash from url + content + title (fallback).
        Call this before saving if you want content-based deduplication.
        """
        base = (self.url or "") + (self.content or "") + (self.title or "")
        h = hashlib.sha256(base.encode("utf-8")).hexdigest()
        self.content_hash = h
        return self.content_hash

    def save(self, *args, **kwargs):
        # if content_hash is empty compute it
        if not self.content_hash:
            try:
                self.compute_and_set_content_hash()
            except Exception:
                # fail-safe: don't block save if hashing fails
                self.content_hash = None
        super().save(*args, **kwargs)
