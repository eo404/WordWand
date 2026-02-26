from django.db import models
from django.conf import settings


class Course(models.Model):
    """Represents a learning course (e.g., Alphabets, Numbers, Phonics)"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Individual lesson inside a course (e.g., Letter A, Letter B)"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    """Connects authenticated users to courses"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    """Tracks user progress per lesson"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress_records")
    completed = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    attempts = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class LessonAttempt(models.Model):
    """Stores individual attempts for analytics"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_attempts")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attempts")
    score = models.FloatField()
    time_taken = models.FloatField(help_text="Time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} attempt on {self.lesson.title}"
