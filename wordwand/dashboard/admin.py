from django.contrib import admin
from .models import Course, UserCourse, ScheduledClass, Assignment, DailyActivity


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'total_hours')
    list_filter = ('category',)
    search_fields = ('title',)


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'hours_spent', 'is_completed', 'progress_percent')
    list_filter = ('is_completed', 'course__category')
    search_fields = ('user__username', 'course__title')

    def progress_percent(self, obj):
        return f"{obj.progress_percent}%"


@admin.register(ScheduledClass)
class ScheduledClassAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'instructor', 'scheduled_date', 'scheduled_time')
    list_filter = ('scheduled_date',)
    search_fields = ('user__username', 'course__title', 'instructor')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'course', 'status', 'score', 'max_score')
    list_filter = ('status', 'course__category')
    search_fields = ('title', 'user__username')


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'day_of_week', 'hours', 'week_start')
    list_filter = ('week_start', 'course')
