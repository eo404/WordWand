from django.contrib import admin
from .models import TTSRequest


@admin.register(TTSRequest)
class TTSRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_type', 'processing_time', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('user__username', 'extracted_text')
    readonly_fields = ('created_at', 'processing_time')
