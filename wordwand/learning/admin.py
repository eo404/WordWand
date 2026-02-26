from django.contrib import admin
from .models import Course, Lesson, Enrollment, LessonProgress, LessonAttempt


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    list_filter = ('course',)
    search_fields = ('user__username', 'course__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'score', 'attempts', 'last_accessed')
    list_filter = ('completed', 'lesson__course')
    search_fields = ('user__username', 'lesson__title')


@admin.register(LessonAttempt)
class LessonAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'score', 'time_taken', 'created_at')
    list_filter = ('lesson__course',)
    search_fields = ('user__username', 'lesson__title')
    readonly_fields = ('created_at',)
