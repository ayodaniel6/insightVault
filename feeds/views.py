from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages

from .models import FeedSource, FeedItem
from .services import fetch_and_save_items


def feed_list(request):
    """
    Show all feed items (from DB).
    Optionally filter by source (?source=slug).
    """
    source_slug = request.GET.get("source")
    if source_slug:
        source = get_object_or_404(FeedSource, slug=source_slug, enabled=True)
        items = FeedItem.objects.filter(source=source, is_active=True)
    else:
        items = FeedItem.objects.filter(is_active=True)

    items = items.select_related("source")[:50]  # limit for now

    context = {
        "sources": FeedSource.objects.filter(enabled=True),
        "items": items,
        "active_source": source_slug,
    }
    return render(request, "feeds/feed_list.html", context)


def feed_detail(request, pk):
    """
    Show a single feed item in detail.
    """
    item = get_object_or_404(FeedItem, pk=pk, is_active=True)
    return render(request, "feeds/feed_detail.html", {"item": item})



def refresh_source(request, slug):
    """
    Manually refresh a single source (fetch new items).
    Redirect back to feed list.
    """
    source = get_object_or_404(FeedSource, slug=slug, enabled=True)
    new_count = fetch_and_save_items(source)
    messages.success(request, f"Fetched {new_count} new items from {source.name}")
    return redirect("feeds:feed_list")


def refresh_all(request):
    """
    Refresh all sources manually.
    """
    total_new = 0
    for src in FeedSource.objects.filter(enabled=True):
        total_new += fetch_and_save_items(src)

    messages.success(request, f"Fetched {total_new} new items from all sources")
    return redirect("feeds:feed_list")
