from django.db import models
from django.conf import settings


class TTSRequest(models.Model):
    """Stores each text-to-speech processing request."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tts_requests"
    )
    uploaded_file = models.FileField(upload_to="tts_uploads/", null=True, blank=True)
    extracted_text = models.TextField()
    audio_file = models.FileField(upload_to="tts_audio/", null=True, blank=True)
    hard_words = models.JSONField(default=list, blank=True)
    syllables = models.JSONField(default=dict, blank=True)
    file_type = models.CharField(max_length=10, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"TTS by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
