from django import forms
from .models import Note

# --- Shared Styles ---
BASE_INPUT = """
w-full px-4 py-2 rounded-lg border border-gray-200 
focus:outline-none focus:ring-2 focus:ring-indigo-500 
focus:border-indigo-500 transition-all duration-200 ease-in-out
"""

TEXTAREA_INPUT = f"{BASE_INPUT} h-40 resize-none leading-relaxed"

TAG_INPUT = f"{BASE_INPUT} text-sm italic"

CHECKBOX_INPUT = """
h-4 w-4 text-indigo-600 border-gray-300 rounded 
focus:ring-indigo-500 transition-all duration-200
"""

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'tags', 'pinned']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Title ---
        self.fields['title'].widget.attrs.update({
            "class": f"{BASE_INPUT} font-semibold text-gray-800",
            "placeholder": "✏️ Give your note a title..."
        })

        # --- Content ---
        self.fields['content'].widget.attrs.update({
            "class": TEXTAREA_INPUT,
            "placeholder": "💡 Start writing your thoughts here..."
        })

        # --- Tags (optional) ---
        self.fields['tags'].required = False
        self.fields['tags'].widget.attrs.update({
            "class": TAG_INPUT,
            "placeholder": "#tags, separated, by commas"
        })

        # --- Pinned ---
        self.fields['pinned'].required = False
        self.fields['pinned'].widget.attrs.update({
            "class": CHECKBOX_INPUT
        })
