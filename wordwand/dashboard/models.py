from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('digital_marketing', 'Digital Marketing'),
        ('ui_ux', 'UI/UX Design'),
        ('sales', 'Sales & BD'),
        ('development', 'Development'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    total_hours = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class UserCourse(models.Model):
    """Tracks a user's enrolment and progress in a course."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolments')
    hours_spent = models.FloatField(default=0)
    is_completed = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"

    @property
    def progress_percent(self):
        if self.course.total_hours == 0:
            return 0
        return min(int((self.hours_spent / self.course.total_hours) * 100), 100)


class ScheduledClass(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.CharField(max_length=100)
    scheduled_time = models.TimeField()
    scheduled_date = models.DateField()

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']

    def __str__(self):
        return f"{self.course.title} @ {self.scheduled_time} on {self.scheduled_date}"


class Assignment(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    total_tasks = models.PositiveIntegerField(default=12)
    completed_tasks = models.PositiveIntegerField(default=0)
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-updated_at']

    def __str__(self):
        return f"{self.title} — {self.user.username}"


class DailyActivity(models.Model):
    """Hours spent per course per day of the week for chart display."""
    DAY_CHOICES = [
        (0, 'Mon'), (1, 'Tue'), (2, 'Wed'),
        (3, 'Thu'), (4, 'Fri'), (5, 'Sat'), (6, 'Sun'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activity')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    hours = models.FloatField(default=0)
    week_start = models.DateField()

    class Meta:
        unique_together = ('user', 'course', 'day_of_week', 'week_start')

    def __str__(self):
        return f"{self.user.username} | {self.course.title} | {self.get_day_of_week_display()}: {self.hours}h"
