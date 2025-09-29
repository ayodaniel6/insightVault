from django import forms
from .models import Note

INPUT_CLASSES = """
w-full px-4 py-2 rounded-xl border border-gray-300 
focus:outline-none focus:ring-2 focus:ring-indigo-500 
shadow-sm transition-all duration-200 ease-in-out
focus:scale-[1.01]
"""

CHECKBOX_CLASSES = """
h-4 w-4 text-indigo-600 border-gray-300 rounded 
focus:ring-indigo-500
"""

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'tags', 'pinned']  # Added new fields

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)

        # Title field
        self.fields['title'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Give your note a title...'
        })

        # Content field (textarea)
        self.fields['content'].widget.attrs.update({
            'class': f"{INPUT_CLASSES} h-48 resize-none",
            'placeholder': 'Start typing your thoughts, ideas, or plans here...'
        })

        # Tags field (optional)
        self.fields['tags'].required = False
        self.fields['tags'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Comma-separated tags (optional)'
        })

        # Pinned checkbox
        self.fields['pinned'].required = False
        self.fields['pinned'].widget.attrs.update({
            'class': CHECKBOX_CLASSES
        })
