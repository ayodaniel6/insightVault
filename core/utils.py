import markdown2
from django.utils.safestring import mark_safe

def format_note_content(content: str) -> str:
    """Convert markdown-like note content into safe HTML."""
    if not content:
        return ""

    # Enable safe_mode to strip raw HTML (prevents XSS)
    extras = [
        "fenced-code-blocks",   # ``` code ```
        "tables",               # Markdown tables
        "strike",               # ~~strikethrough~~
        "underline",            # __underline__
        "cuddled-lists",        # compact lists
        "footnotes",            # footnotes support
    ]
    html = markdown2.markdown(content, extras=extras, safe_mode="escape")

    # Optional: wrap output in Tailwind-friendly typography
    html = f"<div class='prose prose-indigo max-w-none'>{html}</div>"

    return mark_safe(html)
