from django.db import models
from django.db import models
from django.conf import settings


class TTSRequest(models.Model):
    """
    Stores each text-to-speech processing request.
    Connected to the authenticated user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tts_requests"
    )

    # Uploaded file
    uploaded_file = models.FileField(
        upload_to="tts_uploads/",
        null=True,
        blank=True
    )

    # Extracted and cleaned text
    extracted_text = models.TextField()

    # Generated audio file
    audio_file = models.FileField(
        upload_to="tts_audio/",
        null=True,
        blank=True
    )

    # Hard words detected (stored as JSON)
    hard_words = models.JSONField(default=list, blank=True)

    # Syllable breakdown
    syllables = models.JSONField(default=dict, blank=True)

    # Metadata
    file_type = models.CharField(max_length=10, blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # seconds

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TTS Request by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
