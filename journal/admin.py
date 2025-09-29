from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'updated_at')
    list_filter = ('author', 'updated_at')
    search_fields = ('title', 'content')
