from collections import defaultdict
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from .models import DailyActivity, UserCourse, ScheduledClass, Assignment


@login_required
def dashboard_view(request):
    user = request.user
    today = date.today()
    one_year_ago = today - timedelta(days=364)

    # Greeting
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        time_greeting = 'morning'
    elif 12 <= current_hour < 17:
        time_greeting = 'afternoon'
    elif 17 <= current_hour < 21:
        time_greeting = 'evening'
    else:
        time_greeting = 'night'

    # Heatmap (last 365 days)
    activities = (
        DailyActivity.objects
        .filter(user=user)
        .values('week_start', 'day_of_week')
        .annotate(total_hours=Sum('hours'))
    )
    activity_map = defaultdict(float)
    for entry in activities:
        actual_date = entry['week_start'] + timedelta(days=entry['day_of_week'])
        activity_map[actual_date] += float(entry['total_hours'])

    heatmap_data = []
    current_date = one_year_ago
    max_hours = 0
    while current_date <= today:
        hours = activity_map.get(current_date, 0)
        heatmap_data.append({"date": current_date.strftime("%Y-%m-%d"), "hours": round(hours, 2)})
        max_hours = max(max_hours, hours)
        current_date += timedelta(days=1)

    # Weekly bar chart — chart_courses = { "Title": [mon..sun] }
    week_start = today - timedelta(days=today.weekday())
    weekly_qs = (
        DailyActivity.objects
        .filter(user=user, week_start=week_start)
        .values('course__title', 'day_of_week')
        .annotate(total=Sum('hours'))
    )
    chart_courses = defaultdict(lambda: [0.0] * 7)
    for row in weekly_qs:
        chart_courses[row['course__title']][row['day_of_week']] += float(row['total'])

    # Donut chart
    user_courses = UserCourse.objects.filter(user=user).select_related('course')
    total_courses = user_courses.count()
    completed_count = user_courses.filter(is_completed=True).count()
    in_progress_count = user_courses.filter(is_completed=False).count()

    completed_pct = int((completed_count / total_courses) * 100) if total_courses > 0 else 0
    in_progress_pct = int((in_progress_count / total_courses) * 100) if total_courses > 0 else 0

    # Scheduled classes
    scheduled_classes = (
        ScheduledClass.objects
        .filter(user=user, scheduled_date__gte=today)
        .select_related('course')
        .order_by('scheduled_date', 'scheduled_time')[:5]
    )

    # Assignments
    assignments = (
        Assignment.objects
        .filter(user=user)
        .select_related('course')
        .order_by('status', '-updated_at')
    )

    context = {
        "time_greeting": time_greeting,
        "heatmap_data": heatmap_data,
        "max_hours": max_hours if max_hours > 0 else 1,
        "chart_courses": dict(chart_courses),
        "days": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        "completed_pct": completed_pct,
        "in_progress_pct": in_progress_pct,
        "user_courses": user_courses,
        "total_courses": total_courses,
        "completed_count": completed_count,
        "in_progress_count": in_progress_count,
        "total_hours_spent": round(sum(uc.hours_spent for uc in user_courses), 1),
        "scheduled_classes": scheduled_classes,
        "assignments": assignments,
    }

    return render(request, "dashboard/dashboard.html", context)