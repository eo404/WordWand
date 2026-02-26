from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date

from .models import Course, UserCourse, ScheduledClass, Assignment, DailyActivity


@login_required
def dashboard_view(request):
    user = request.user
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # --- Enrolled courses summary ---
    user_courses = UserCourse.objects.filter(user=user).select_related('course')

    # --- Today's / upcoming schedule ---
    schedule = ScheduledClass.objects.filter(
        user=user, scheduled_date__gte=today
    ).select_related('course').order_by('scheduled_date', 'scheduled_time')[:5]

    # --- Assignments ---
    assignments = Assignment.objects.filter(user=user).select_related('course')

    # --- Progress summary ---
    total = user_courses.count()
    completed = user_courses.filter(is_completed=True).count()
    in_progress = total - completed
    completed_pct = round((completed / total * 100)) if total else 0
    in_progress_pct = 100 - completed_pct

    # --- Chart data: hours per day per course (current week) ---
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    activity_qs = DailyActivity.objects.filter(
        user=user, week_start=week_start
    ).select_related('course')

    # Build dict: {course_title: [hours per day]}
    chart_courses = {}
    for entry in activity_qs:
        title = entry.course.title
        if title not in chart_courses:
            chart_courses[title] = [0] * 7
        chart_courses[title][entry.day_of_week] = entry.hours

    context = {
        'user_courses': user_courses,
        'schedule': schedule,
        'assignments': assignments,
        'completed_pct': completed_pct,
        'in_progress_pct': in_progress_pct,
        'days': days,
        'chart_courses': chart_courses,
        'today': today,
    }
    return render(request, 'dashboard/dashboard.html', context)
