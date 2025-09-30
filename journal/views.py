from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Note, Tag
from .forms import NoteForm
from django.utils.text import Truncator

# ----------------------------
# Helpers
# ----------------------------
def _note_to_dict(note):
    """Serialize a note to JSON-friendly dict."""
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "rendered_content": note.rendered_html(), 
        "tags_list": [tag.name for tag in note.tags.all()],
        "pinned": note.pinned,
        "updated_at": note.updated_at.strftime("%b %d, %Y %H:%M"),
    }


def _handle_tags(note, tags_str):
    """Sync tags with ManyToMany field."""
    tags = []
    for name in tags_str.split(","):
        name = name.strip()
        if name:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
    note.tags.set(tags)


# ----------------------------
# Views
# ----------------------------

@login_required
def journal_home(request):
    """
    Render the journal main page with user's notes.
    AJAX requests for note CRUD should go to dedicated endpoints.
    """
    notes = Note.objects.filter(author=request.user).select_related("author").prefetch_related("tags")

    for note in notes:
        note.preview = Truncator(note.content).chars(200)  

    return render(request, "journal/journal.html", {
        "notes": notes,
        "form": NoteForm()
    })


@login_required
@require_POST
def save_note(request):
    """
    Create or update a note (AJAX only).
    """
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"error": "Invalid request"}, status=400)

    note_id = request.POST.get("note_id")

    # Determine whether we're updating or creating
    if note_id:
        note = get_object_or_404(Note, id=note_id, author=request.user)
        form = NoteForm(request.POST, instance=note)
    else:
        note = None
        form = NoteForm(request.POST)

    if form.is_valid():
        note = form.save(commit=False)
        note.author = request.user
        note.save()

        # Handle tags safely
        tags_str = request.POST.get("tags", "").strip()
        _handle_tags(note, tags_str)

        return JsonResponse({
            "success": True,
            "note": _note_to_dict(note),
            "message": "Note updated" if note_id else "Note created"
        })

    return JsonResponse({
        "success": False,
        "errors": form.errors,
        "message": "Validation failed"
    }, status=400)


@login_required
def get_note(request, pk):
    """
    Fetch a single note (AJAX only).
    Used to prefill the edit form modal.
    """
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"error": "Invalid request"}, status=400)

    note = get_object_or_404(Note, pk=pk, author=request.user)
    return JsonResponse({"success": True, "note": _note_to_dict(note)})



@login_required
@require_POST
def delete_note(request, pk):
    """
    Delete a note (AJAX or normal POST).
    """
    note = get_object_or_404(Note, pk=pk, author=request.user)
    note.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})
    return redirect("journal:journal_home")


@login_required
@require_POST
def toggle_pin(request, pk):
    """
    Toggle pin/unpin for a note (AJAX only).
    """
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"error": "Invalid request"}, status=400)

    note = get_object_or_404(Note, pk=pk, author=request.user)
    note.pinned = not note.pinned
    note.save()

    return JsonResponse({"success": True, "note": _note_to_dict(note)})
