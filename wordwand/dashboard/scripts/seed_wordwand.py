from django.contrib.auth.models import User
from dashboard.models import Course, UserCourse, ScheduledClass, Assignment, DailyActivity
from datetime import date, time, timedelta
import random

# ── Change to your login username ────────────────────────────
USERNAME = 'mr_eo'
# ─────────────────────────────────────────────────────────────

user = User.objects.get(username=USERNAME)
today = date.today()
week_start = today - timedelta(days=today.weekday())

# Clear existing data
DailyActivity.objects.filter(user=user).delete()
Assignment.objects.filter(user=user).delete()
ScheduledClass.objects.filter(user=user).delete()
UserCourse.objects.filter(user=user).delete()
Course.objects.all().delete()
print("Cleared existing data.")

# ── COURSES — WordWand's actual learning modules ─────────────
# Each course = one learning area inside the platform
# Categories: development | ui_ux | digital_marketing | sales | other

courses_data = [
    (
        "Phonics & Letter Sounds",
        "other",
        20,
        "Learn letter sounds, phoneme matching, and sound-to-letter "
        "relationships through the Sound Match game. Covers all 26 letters "
        "across 4 difficulty levels."
    ),
    (
        "Spelling & Word Building",
        "other",
        25,
        "Build words by arranging scrambled letters using the Word Builder game. "
        "Practise correct spelling patterns and letter order at adaptive difficulty."
    ),
    (
        "Sight Words & Reading Fluency",
        "other",
        20,
        "Memorise and recognise high-frequency sight words through the Sight Word "
        "Tap game. Builds reading fluency and instant word recognition."
    ),
    (
        "Syllables & Word Structure",
        "other",
        15,
        "Learn to break words into syllables using the Syllable Breaker game. "
        "Covers single, double and multi-syllabic words across difficulty levels."
    ),
    (
        "Listening & Audio Reading",
        "other",
        20,
        "Develop listening comprehension through the Listen & Type game and "
        "Story Builder. Text-to-speech reads every word aloud — children "
        "hear and then type what they hear."
    ),
]

courses = []
for title, category, hours, desc in courses_data:
    c = Course.objects.create(
        title=title, category=category,
        total_hours=hours, description=desc
    )
    courses.append(c)
    print(f"  Created: {title}")

phonics = courses[0]   # Phonics & Letter Sounds
spelling = courses[1]   # Spelling & Word Building
sight_words = courses[2]   # Sight Words & Reading Fluency
syllables = courses[3]   # Syllables & Word Structure
listening = courses[4]   # Listening & Audio Reading

# ── ENROLMENTS — child's progress across all modules ─────────
# hours_spent reflects realistic play time for a child aged 5-10
for course, hours_spent, is_completed in [
    (phonics,     18, True),    # Completed — first module learned
    (spelling,    16, False),   # In progress — active game
    (sight_words, 12, False),   # In progress
    (syllables,    8, False),   # Just started
    (listening,   20, True),    # Completed — strong audio learner
]:
    uc = UserCourse.objects.create(
        user=user, course=course,
        hours_spent=hours_spent, is_completed=is_completed
    )
    print(
        f"  Enrolled: {course.title} — {uc.progress_percent}% {'✓' if is_completed else ''}")

# ── SCHEDULED CLASSES — upcoming game sessions / lessons ─────
for course, instructor, days_ahead, t in [
    (spelling,    "Ms. Priya Menon",   1, "10:00"),
    (sight_words, "Mr. Arjun Nair",    2, "11:00"),
    (phonics,     "Ms. Priya Menon",   4, "10:00"),
    (syllables,   "Mr. Arjun Nair",    5, "14:00"),
    (listening,   "Ms. Sarah Kurien",  7, "09:00"),
    (spelling,    "Ms. Priya Menon",   9, "10:00"),
]:
    h, m = map(int, t.split(":"))
    ScheduledClass.objects.create(
        user=user, course=course, instructor=instructor,
        scheduled_date=today + timedelta(days=days_ahead),
        scheduled_time=time(h, m)
    )
print("  Scheduled classes created.")

# ── ASSIGNMENTS — named after actual WordWand game activities ─
for course, title, total, done, score, status in [

    # Phonics assignments
    (phonics,     "Sound Match — Level 1 Complete",       10, 10, 95, "completed"),
    (phonics,     "Sound Match — Level 2 Complete",       10, 10, 88, "completed"),
    (phonics,     "Sound Match — Level 3 Challenge",      10,  6,  0, "in_progress"),

    # Spelling assignments
    (spelling,    "Word Builder — 3-Letter Words",        10, 10, 90, "completed"),
    (spelling,    "Word Builder — 4-Letter Words",        10,  7,  0, "in_progress"),
    (spelling,    "Word Builder — 5-Letter Words",        10,  0,  0, "not_started"),

    # Sight words assignments
    (sight_words, "Sight Word Tap — Basic 20 Words",      10, 10, 85, "completed"),
    (sight_words, "Sight Word Tap — Intermediate Words",  10,  5,  0, "in_progress"),
    (sight_words, "Letter Fix — b/d Confusion Practice",  8,   0,  0, "not_started"),

    # Syllables assignments
    (syllables,   "Syllable Breaker — 2-Syllable Words",  8,   3,  0, "in_progress"),
    (syllables,   "Syllable Breaker — 3-Syllable Words",  8,   0,  0, "not_started"),

    # Listening assignments
    (listening,   "Listen & Type — Short Words",          10, 10, 92, "completed"),
    (listening,   "Story Builder — Level 1 Stories",      6,   6, 89, "completed"),
    (listening,   "Story Builder — Level 2 Stories",      6,   2,  0, "in_progress"),
]:
    Assignment.objects.create(
        user=user, course=course, title=title,
        total_tasks=total, completed_tasks=done,
        score=score, max_score=100, status=status
    )
print("  Assignments created.")

# ── THIS WEEK'S ACTIVITY — drives the bar chart ───────────────
# Hours per day reflect a child's daily game session time
# [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
this_week = {
    phonics:     [0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5],
    spelling:    [1.0, 0.5, 1.0, 0.5, 1.0, 0.5, 0.0],
    sight_words: [0.5, 1.0, 0.5, 1.0, 0.5, 0.5, 0.0],
    syllables:   [0.5, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0],
    listening:   [0.5, 0.5, 1.0, 0.5, 0.5, 1.0, 0.5],
}

for course, day_hours in this_week.items():
    for day_idx, hours in enumerate(day_hours):
        if hours > 0:
            DailyActivity.objects.get_or_create(
                user=user, course=course,
                day_of_week=day_idx, week_start=week_start,
                defaults={'hours': hours}
            )
print("  This week activity seeded.")

# ── PAST 8 WEEKS — fills the heatmap ─────────────────────────
random.seed(42)
base_pattern = {
    phonics:     [0.5, 1.0, 0.5, 1.0, 0.5, 1.0, 0.0],
    spelling:    [1.0, 0.5, 1.0, 0.5, 1.0, 0.5, 0.0],
    sight_words: [0.5, 1.0, 0.5, 1.0, 0.5, 0.5, 0.0],
    syllables:   [0.5, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0],
    listening:   [0.5, 0.5, 1.0, 0.5, 1.0, 1.0, 0.5],
}

for weeks_ago in range(1, 9):
    ws = week_start - timedelta(weeks=weeks_ago)
    for course, pattern in base_pattern.items():
        for day_idx, base_h in enumerate(pattern):
            h = round(base_h * random.uniform(0.6, 1.3), 2)
            if h > 0:
                DailyActivity.objects.get_or_create(
                    user=user, course=course,
                    day_of_week=day_idx, week_start=ws,
                    defaults={'hours': h}
                )
print("  Past 8 weeks activity seeded.")

# ── SUMMARY ───────────────────────────────────────────────────
print("\n" + "=" * 52)
print("  WORDWAND DASHBOARD SEED COMPLETE")
print("=" * 52)
print(f"  Courses:       {Course.objects.count()}")
print(f"  Enrolments:    {UserCourse.objects.filter(user=user).count()}")
print(f"  Scheduled:     {ScheduledClass.objects.filter(user=user).count()}")
print(f"  Assignments:   {Assignment.objects.filter(user=user).count()}")
print(f"  Activity rows: {DailyActivity.objects.filter(user=user).count()}")
c = UserCourse.objects.filter(user=user, is_completed=True).count()
t = UserCourse.objects.filter(user=user).count()
print(f"  Completed:     {c}/{t} modules")
print(f"\n  Refresh /dashboard/ to see the data!")
