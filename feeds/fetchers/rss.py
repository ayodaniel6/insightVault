# feeds/fetchers/rss.py
import re
from datetime import datetime, timezone as dt_timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs

import requests
import feedparser

from .base import BaseFetcher


IMG_REGEX = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', flags=re.IGNORECASE)
YOUTUBE_WATCH_RE = re.compile(r"(?:youtube\.com/watch\?.*v=|youtu\.be/)([A-Za-z0-9_-]{6,})")


class RSSFetcher(BaseFetcher):
    """
    RSS/Atom fetcher using requests + feedparser.
    Returns list of normalized dicts with keys:
      external_id, title, summary, content, url, author,
      published_at (datetime or None), image_url, video_url, raw
    """

    def fetch(self) -> List[Dict[str, Any]]:
        headers = {"User-Agent": "InsightVaultBot/1.0 (+https://yourdomain.example)"}
        resp = requests.get(self.endpoint, headers=headers, timeout=15)
        resp.raise_for_status()

        parsed = feedparser.parse(resp.content)

        items: List[Dict[str, Any]] = []
        for entry in parsed.entries:
            external_id = entry.get("id") or entry.get("guid") or entry.get("link")
            title = entry.get("title", "").strip()
            # content prefers full content, fallback to summary
            content = ""
            if entry.get("content"):
                try:
                    content = entry["content"][0].get("value", "") or ""
                except Exception:
                    content = ""
            if not content:
                content = entry.get("summary", "") or ""

            summary = entry.get("summary", "") or ""
            url = entry.get("link", "") or ""
            author = entry.get("author", "") or entry.get("dc_creator", "") or ""

            published_at = self._parse_date(entry)

            # Extract media (image/video) with several fallbacks
            image_url, video_url = self._extract_media(entry, base_url=self.endpoint, content_html=content)

            item = {
                "external_id": external_id,
                "title": title,
                "summary": summary,
                "content": content,
                "url": url,
                "author": author,
                "published_at": published_at,
                "image_url": image_url,
                "video_url": video_url,
                "raw": entry,
            }
            items.append(item)

        return items

    def _parse_date(self, entry) -> Optional[datetime]:
        """
        Convert feedparser date (struct_time) to a timezone-aware datetime in UTC.
        """
        dt_obj = None
        try:
            if getattr(entry, "published_parsed", None):
                t = entry.published_parsed
            elif getattr(entry, "updated_parsed", None):
                t = entry.updated_parsed
            else:
                t = None

            if t:
                dt_obj = datetime(*t[:6], tzinfo=dt_timezone.utc)
        except Exception:
            dt_obj = None
        return dt_obj

    def _extract_media(self, entry, base_url: str = "", content_html: str = "") -> (Optional[str], Optional[str]):
        """
        Try multiple strategies to find a representative image_url and/or video_url.
        Returns (image_url or None, video_url or None)
        """
        image_url = None
        video_url = None

        # 1) 'media_content' (common in many feeds)
        try:
            mc = entry.get("media_content") or entry.get("mediaContents")  # some feeds vary
            if mc:
                # choose first image-like or video-like item
                for m in mc:
                    url = m.get("url") or m.get("value")
                    mtype = (m.get("type") or "").lower()
                    if not url:
                        continue
                    if "image" in mtype and not image_url:
                        image_url = url
                    if ("video" in mtype or "mp4" in url) and not video_url:
                        video_url = url
                    if image_url and video_url:
                        break
        except Exception:
            pass

        # 2) 'media_thumbnail'
        if not image_url:
            try:
                mt = entry.get("media_thumbnail") or entry.get("mediaThumbnails")
                if mt and isinstance(mt, (list, tuple)) and mt:
                    image_url = mt[0].get("url") or mt[0].get("value")
            except Exception:
                pass

        # 3) enclosures / links rel=enclosure
        if not image_url or not video_url:
            links = entry.get("links", []) or entry.get("links", [])
            for link in links:
                rel = (link.get("rel") or "").lower()
                ltype = (link.get("type") or "").lower()
                href = link.get("href") or link.get("url")
                if not href:
                    continue
                if rel == "enclosure":
                    if "image" in ltype and not image_url:
                        image_url = href
                    elif "video" in ltype and not video_url:
                        video_url = href
                    # some feeds provide mp4 with type application/octet-stream etc:
                    elif any(ext in href.lower() for ext in (".mp4", ".webm", ".ogg")):
                        video_url = video_url or href

        # 4) entry.enclosures (some feeds)
        try:
            enclosures = entry.get("enclosures") or []
            for enc in enclosures:
                href = enc.get("href") or enc.get("url")
                etype = (enc.get("type") or "").lower()
                if not href:
                    continue
                if "image" in etype and not image_url:
                    image_url = href
                if ("video" in etype or any(href.lower().endswith(ext) for ext in [".mp4", ".webm", ".ogg"])) and not video_url:
                    video_url = href
        except Exception:
            pass

        # 5) fallback: try to discover first <img> in content_html or summary
        if not image_url and content_html:
            m = IMG_REGEX.search(content_html)
            if m:
                image_url = m.group(1)

        # 6) fallback: check entry.get('image') or entry.get('thumbnail')
        if not image_url:
            image_url = entry.get("image", {}).get("href") if isinstance(entry.get("image"), dict) else entry.get("image")
            image_url = image_url or entry.get("thumbnail")

        # 7) normalize to absolute URLs (join with base)
        if image_url:
            image_url = urljoin(base_url, image_url)
        if video_url:
            video_url = urljoin(base_url, video_url)

        # 8) special handling: detect YouTube links and produce embed URL
        #    if a YouTube watch/short/youtu.be link appears in video_url or url or content_html
        if not video_url:
            # prioritize entry.link then content_html
            candidates = [entry.get("link", ""), content_html or ""]
            for c in candidates:
                m = YOUTUBE_WATCH_RE.search(c)
                if m:
                    vid = m.group(1)
                    video_url = f"https://www.youtube.com/embed/{vid}"
                    break
            # also check if an <iframe> with youtube exists in content_html
            if not video_url and content_html:
                # naive look for "youtube.com/embed/..." in content
                if "youtube.com/embed/" in content_html:
                    vid_match = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]{6,})", content_html)
                    if vid_match:
                        vid = vid_match.group(1)
                        video_url = f"https://www.youtube.com/embed/{vid}"

        # final normalization: None if empty string
        image_url = image_url or None
        video_url = video_url or None

        return image_url, video_url
