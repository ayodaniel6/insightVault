from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter
def split_tags(value):
    """
    Splits a comma-separated string into a list of trimmed tags.
    Usage: {{ note.tags|split_tags }}
    """
    if not value:
        return []
    return [tag.strip() for tag in value.split(',') if tag.strip()]


@register.filter(name="render_markdown")
def render_markdown(value):
    """
    Converts Markdown text to HTML, supporting headings, bold, code blocks, and tables.
    Usage: {{ note.content|render_markdown|safe }}
    """
    if not value:
        return ""
    
    html = markdown.markdown(
        value,
        extensions=[
            "fenced_code",
            "tables",
            "nl2br",
            "sane_lists",
            "toc",            # Table of contents for headings
            "attr_list"       # Allow extra HTML attributes in markdown
        ]
    )
    return mark_safe(html)
