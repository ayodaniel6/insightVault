from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Note
from .forms import NoteForm
from .utils import format_note_content


@login_required
def journal_home(request):
    """
    Show all notes for the logged-in user.
    Handles note creation + editing via AJAX.
    """
    notes = Note.objects.filter(author=request.user).order_by('-pinned', '-updated_at')

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        note_id = request.POST.get('note_id')

        if note_id:
            note = get_object_or_404(Note, id=note_id, author=request.user)
            form = NoteForm(request.POST, instance=note)
        else:
            form = NoteForm(request.POST)

        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user

            # handle pinned + tags
            tags = request.POST.get('tags', '').strip()
            note.tags = tags
            pinned_val = request.POST.get('pinned')
            note.pinned = bool(pinned_val and str(pinned_val).lower() in ['true', '1', 'on', 'yes'])

            # fallback title
            if not note.title or not note.title.strip():
                note.title = "Untitled"

            note.save()

            tags_list = [t.strip() for t in note.tags.split(',') if t.strip()] if note.tags else []

            return JsonResponse({
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'rendered_content': format_note_content(note.content),
                'tags_list': tags_list,
                'pinned': note.pinned,
                'updated_at': note.updated_at.strftime("%b %d, %Y %H:%M")
            }, status=200)

        return JsonResponse({'errors': form.errors}, status=400)

    return render(request, 'journal/journal.html', {
        'notes': notes,
        'form': NoteForm()
    })


@login_required
def delete_note(request, pk):
    """
    Delete a note with a normal POST request.
    Page reloads after deletion.
    """
    note = get_object_or_404(Note, pk=pk, author=request.user)
    if request.method == "POST":
        note.delete()
    return redirect("journal:journal_home")


@login_required
def toggle_pin(request, pk):
    """
    Toggle pin/unpin via AJAX (no page reload).
    """
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        note = get_object_or_404(Note, pk=pk, author=request.user)
        note.pinned = not note.pinned
        note.save()

        tags_list = [t.strip() for t in note.tags.split(',') if t.strip()] if note.tags else []

        return JsonResponse({
            'success': True,
            'note': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'rendered_content': format_note_content(note.content),
                'tags_list': tags_list,
                'pinned': note.pinned,
                'updated_at': note.updated_at.strftime("%b %d, %Y %H:%M")
            }
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
