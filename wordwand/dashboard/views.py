from collections import defaultdict
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from .models import DailyActivity


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

    # --- HEATMAP DATA (Last 365 days) ---
    activities = (
        DailyActivity.objects
        .filter(user=user)
        .values('week_start', 'day_of_week')
        .annotate(total_hours=Sum('hours'))
    )

    # Convert weekly stored format → real date
    activity_map = defaultdict(float)

    for entry in activities:
        actual_date = entry['week_start'] + \
            timedelta(days=entry['day_of_week'])
        activity_map[actual_date] += float(entry['total_hours'])

    # Build full 365 day grid
    heatmap_data = []
    current_date = one_year_ago
    max_hours = 0

    while current_date <= today:
        hours = activity_map.get(current_date, 0)
        heatmap_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "hours": round(hours, 2)
        })
        max_hours = max(max_hours, hours)
        current_date += timedelta(days=1)

    context = {
        "heatmap_data": heatmap_data,
        "max_hours": max_hours if max_hours > 0 else 1,
        "time_greeting": time_greeting,
    }

    return render(request, "dashboard/dashboard.html", context)
