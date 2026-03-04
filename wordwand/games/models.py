from django.db import models
from django.contrib.auth.models import User


# ═══════════════════════════════════════════════
# GAME 1 — Sound–Letter Match
# ═══════════════════════════════════════════════

class Phoneme(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Single Letters'),
        (2, 'Consonant Blends'),
        (3, 'Digraphs'),
        (4, 'Vowel Teams'),
    ]
    sound_file = models.FileField(upload_to='phonemes/audio/')
    phoneme_text = models.CharField(max_length=10)
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES, default=1)

    def __str__(self):
        return f"{self.phoneme_text} (Level {self.difficulty_level})"


class PhonemeOption(models.Model):
    phoneme = models.ForeignKey(
        Phoneme, on_delete=models.CASCADE, related_name='options')
    letter_option = models.CharField(max_length=5)
    is_correct = models.BooleanField(default=False)


class PhonemeAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='phoneme_attempts')
    phoneme = models.ForeignKey(Phoneme, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(
        PhonemeOption, on_delete=models.SET_NULL, null=True)
    is_correct = models.BooleanField()
    response_time = models.FloatField(help_text='seconds')
    attempted_at = models.DateTimeField(auto_now_add=True)


# ═══════════════════════════════════════════════
# GAME 2 — Word Builder (Drag & Drop)
# ═══════════════════════════════════════════════

class Word(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Basic (3 letters)'),
        (2, 'Medium (4–5 letters)'),
        (3, 'Advanced (digraphs/blends)'),
        (4, 'Expert (long words)'),
    ]
    word_text = models.CharField(max_length=50)
    image_path = models.ImageField(
        upload_to='words/images/', blank=True, null=True)
    audio_file = models.FileField(
        upload_to='words/audio/', blank=True, null=True)
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES, default=1)

    def __str__(self):
        return f"{self.word_text} (Level {self.difficulty_level})"


class WordLetter(models.Model):
    word = models.ForeignKey(
        Word, on_delete=models.CASCADE, related_name='letters')
    letter = models.CharField(max_length=3)   # supports digraphs: 'sh', 'ch'
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']


class WordBuildAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='word_build_attempts')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    submitted_order = models.JSONField()
    is_correct = models.BooleanField()
    response_time = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)


# ═══════════════════════════════════════════════
# GAME 3 — Sight Word Speed Tap
# ═══════════════════════════════════════════════

class SightWord(models.Model):
    word = models.CharField(max_length=30, unique=True)
    level = models.PositiveIntegerField(default=1)
    frequency_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.word} (L{self.level})"


class UserSightWordProgress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sight_word_progress')
    word = models.ForeignKey(SightWord, on_delete=models.CASCADE)
    attempts = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'word')

    @property
    def accuracy(self):
        return round((self.correct / self.attempts) * 100, 1) if self.attempts else 0


class SightWordAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sight_word_attempts')
    word = models.ForeignKey(SightWord, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    response_time = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)


# ═══════════════════════════════════════════════
# GAME 4 — Confusing Letter Fix (b/d/p/q)
# ═══════════════════════════════════════════════

class ConfusionSet(models.Model):
    letter_a = models.CharField(max_length=3)
    letter_b = models.CharField(max_length=3)
    sound_a = models.FileField(
        upload_to='confusion/audio/', blank=True, null=True)
    sound_b = models.FileField(
        upload_to='confusion/audio/', blank=True, null=True)

    def __str__(self):
        return f"{self.letter_a} vs {self.letter_b}"


class ConfusionAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='confusion_attempts')
    confusion_set = models.ForeignKey(ConfusionSet, on_delete=models.CASCADE)
    shown_letter = models.CharField(max_length=3)
    selected = models.CharField(max_length=3)
    is_correct = models.BooleanField()
    response_time = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)


# ═══════════════════════════════════════════════
# GAME 5 — Syllable Breaker
# ═══════════════════════════════════════════════

class SyllableWord(models.Model):
    DIFFICULTY_CHOICES = [
        (1, '2 syllables'),
        (2, '3 syllables'),
        (3, '4+ syllables'),
    ]
    word = models.CharField(max_length=50)
    syllable_structure = models.JSONField()          # e.g. ["ba","na","na"]
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES, default=1)
    audio_file = models.FileField(
        upload_to='syllables/audio/', blank=True, null=True)

    def __str__(self):
        return f"{self.word} → {self.syllable_structure}"


class SyllableAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='syllable_attempts')
    syllable_word = models.ForeignKey(SyllableWord, on_delete=models.CASCADE)
    submitted_splits = models.JSONField()
    is_correct = models.BooleanField()
    response_time = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)


# ═══════════════════════════════════════════════
# GAME 6 — Listening & Type
# ═══════════════════════════════════════════════

class ListenWord(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Short CVC words'),
        (2, 'Blends & digraphs'),
        (3, 'Multi-syllable'),
    ]
    word_text = models.CharField(max_length=50)
    audio_file = models.FileField(upload_to='listen/audio/')
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES, default=1)

    def __str__(self):
        return self.word_text


class ListenAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='listen_attempts')
    listen_word = models.ForeignKey(ListenWord, on_delete=models.CASCADE)
    typed_answer = models.CharField(max_length=60)
    is_correct = models.BooleanField()
    wrong_positions = models.JSONField(default=list, blank=True)  # e.g. [2, 4]
    response_time = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)


# ═══════════════════════════════════════════════
# GAME 7 — Story Builder
# ═══════════════════════════════════════════════

class Story(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Simple sentences'),
        (2, 'Short paragraphs'),
        (3, 'Fill-in-the-blank'),
    ]
    title = models.CharField(max_length=100)
    content = models.TextField()
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES, default=1)
    hard_words = models.TextField(blank=True, help_text='Comma-separated')
    fill_blanks = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title

    def get_hard_words(self):
        return [w.strip() for w in self.hard_words.split(',') if w.strip()]


class StoryAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='story_attempts')
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    fill_answers = models.JSONField(default=dict, blank=True)
    time_spent = models.FloatField(default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)


# ═══════════════════════════════════════════════
# GLOBAL — Adaptive Difficulty + Progress Tracking
# ═══════════════════════════════════════════════

GAME_TYPES = [
    ('sound_match',   'Sound–Letter Match'),
    ('word_builder',  'Word Builder'),
    ('sight_word',    'Sight Word Speed Tap'),
    ('confusion',     'Confusing Letter Fix'),
    ('syllable',      'Syllable Breaker'),
    ('listen_type',   'Listening & Type'),
    ('story_builder', 'Story Builder'),
]

ERROR_TYPES = [
    ('bd_confusion',          'b/d Confusion'),
    ('pq_confusion',          'p/q Confusion'),
    ('vowel_substitution',    'Vowel Substitution'),
    ('blending_failure',      'Blending Failure'),
    ('syllable_segmentation', 'Syllable Segmentation Error'),
    ('sight_word_miss',       'Sight Word Miss'),
    ('phoneme_miss',          'Phoneme Miss'),
]


class UserProgress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='game_progress')
    game_type = models.CharField(max_length=30, choices=GAME_TYPES)
    level = models.PositiveIntegerField(default=1)
    accuracy = models.FloatField(default=0.0)
    average_time = models.FloatField(default=0.0)
    sessions_at_level = models.PositiveIntegerField(default=0)
    last_played = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game_type')

    def __str__(self):
        return f"{self.user.username} | {self.game_type} | L{self.level} | {self.accuracy:.1f}%"

    def update_after_session(self, session_accuracy: float, session_avg_time: float):
        """
        Adaptive difficulty:
          accuracy > 85% for 3 consecutive sessions → level up
          accuracy < 60% → level down immediately
        """
        self.accuracy = round(0.70 * self.accuracy +
                              0.30 * session_accuracy,  2)
        self.average_time = round(
            0.70 * self.average_time + 0.30 * session_avg_time,  2)

        if session_accuracy > 85:
            self.sessions_at_level += 1
            if self.sessions_at_level >= 3:
                self.level = min(self.level + 1, 4)
                self.sessions_at_level = 0
        elif session_accuracy < 60:
            self.level = max(self.level - 1, 1)
            self.sessions_at_level = 0
        else:
            self.sessions_at_level = 0

        self.save()


class UserErrorPattern(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='error_patterns')
    error_type = models.CharField(max_length=40, choices=ERROR_TYPES)
    frequency = models.PositiveIntegerField(default=0)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'error_type')
        ordering = ['-frequency']

    def __str__(self):
        return f"{self.user.username} | {self.error_type} ×{self.frequency}"

    @classmethod
    def log(cls, user, error_type: str):
        obj, _ = cls.objects.get_or_create(user=user, error_type=error_type)
        obj.frequency += 1
        obj.save()

    @classmethod
    def recommend_game(cls, user) -> str:
        """Return the game_type targeting the user's most frequent error."""
        top = cls.objects.filter(user=user).order_by('-frequency').first()
        if not top:
            return 'sound_match'
        mapping = {
            'bd_confusion':          'confusion',
            'pq_confusion':          'confusion',
            'vowel_substitution':    'sound_match',
            'blending_failure':      'word_builder',
            'syllable_segmentation': 'syllable',
            'sight_word_miss':       'sight_word',
            'phoneme_miss':          'sound_match',
        }
        return mapping.get(top.error_type, 'sound_match')
