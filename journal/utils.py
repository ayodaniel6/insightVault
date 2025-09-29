import re
from django.utils.html import escape
from django.utils.safestring import mark_safe

def format_note_content(content):
    """Formats note content with simple markdown-like syntax."""
    if not content:
        return ""

    # Escape HTML for safety
    content = escape(content)

    # Headings
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)

    # Bold and italic
    content = re.sub(r'\*(.+?)\*', r'<strong>\1</strong>', content)
    content = re.sub(r'_(.+?)_', r'<em>\1</em>', content)

    # Lists
    def list_replacer(match):
        items = match.group(0).strip().split("\n")
        items = [f"<li>{re.sub(r'^- ', '', item)}</li>" for item in items if item.strip()]
        return "<ul>" + "".join(items) + "</ul>"

    content = re.sub(r'(^- .+(?:\n- .+)*)', list_replacer, content, flags=re.MULTILINE)

    # Line breaks for everything else
    content = content.replace("\n", "<br>")

    return mark_safe(content)
