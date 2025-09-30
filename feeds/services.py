from typing import List, Dict
from django.utils import timezone
from django.db import IntegrityError

from .models import FeedSource, FeedItem
from .fetchers.rss import RSSFetcher
# from .fetchers.rest import RESTFetcher
# from .fetchers.youtube import YouTubeFetcher
# from .fetchers.twitter import TwitterFetcher


def get_fetcher_for_source(source: FeedSource):
    """
    Factory: return the right fetcher class instance for a FeedSource.
    Each fetcher must implement .fetch() -> List[Dict]
    """
    if source.api_type == FeedSource.ApiType.RSS:
        return RSSFetcher(source)
    # elif source.api_type == FeedSource.ApiType.REST:
    #     return RESTFetcher(source)
    # elif source.api_type == FeedSource.ApiType.YOUTUBE:
    #     return YouTubeFetcher(source)
    # elif source.api_type == FeedSource.ApiType.TWITTER:
    #     return TwitterFetcher(source)
    else:
        raise ValueError(f"Unsupported api_type: {source.api_type}")


def fetch_and_save_items(source: FeedSource) -> int:
    """
    Fetch new items from a source and save them into DB.
    Returns number of new items saved.
    """
    fetcher = get_fetcher_for_source(source)
    items: List[Dict] = fetcher.fetch()

    new_count = 0
    for item in items:
        try:
            FeedItem.objects.create(
                source=source,
                external_id=item["external_id"],
                title=item["title"],
                summary=item.get("summary", ""),
                content=item.get("content", ""),
                url=item.get("url", ""),
                author=item.get("author", ""),
                published_at=item.get("published_at"),
                raw=item.get("raw"),
                fetched_at=timezone.now(),
                image_url=item.get("image_url", ""),
                video_url=item.get("video_url", ""),
            )
            new_count += 1
        except IntegrityError:
            # Already exists (unique constraint)
            continue
        except Exception as e:
            # Don’t block other items on unexpected errors
            print(f"Error saving feed item for {source.slug}: {e}")
            continue

    # Update last_fetched
    source.last_fetched = timezone.now()
    source.save(update_fields=["last_fetched"])

    return new_count


def refresh_all_sources() -> int:
    """
    Fetch + save for all enabled sources.
    Returns total new items saved across sources.
    """
    total_new = 0
    for source in FeedSource.objects.filter(enabled=True):
        try:
            total_new += fetch_and_save_items(source)
        except Exception as e:
            print(f"Failed to refresh {source.slug}: {e}")
            continue
    return total_new
