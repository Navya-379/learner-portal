from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Course, Enrollment, QuizResult, Progress, Profile, Assessment, Quiz

# Inline models for CustomUser
class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    readonly_fields = ("course", "enrolled_at")

class QuizResultInline(admin.TabularInline):
    model = QuizResult
    extra = 0
    readonly_fields = ("course", "score", "total", "passed", "taken_at")

class ProgressInline(admin.TabularInline):
    model = Progress
    extra = 0
    readonly_fields = ("completed_units", "total_units")

# CustomUser admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    
    list_display = ("username", "email", "role", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email")
    ordering = ("username",)

admin.site.register(Quiz)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "duration", "category")
    search_fields = ("title", "category")
    list_filter = ("category",)


# Enrollment admin
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at")
    list_filter = ("course", "enrolled_at")
    search_fields = ("user__username", "course__title")
    ordering = ("-enrolled_at",)

# QuizResult admin
@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "score", "total", "passed", "taken_at")
    list_filter = ("course", "passed", "taken_at")
    search_fields = ("user__username", "course__title")
    ordering = ("-taken_at",)

# Profile admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("get_username", "education", "skills", "portfolio_url")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "User"

# Assessment admin
@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("course", "text", "answer")
    search_fields = ("text", "course__title")
    list_filter = ("course",)

# Progress admin
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "completed_units", "total_units", "completion_percentage_display")
    list_filter = ("enrollment__course",)
    search_fields = ("enrollment__user__username", "enrollment__course__title")
    ordering = ("enrollment__course",)

    def completion_percentage_display(self, obj):
        return f"{obj.completion_percentage():.2f}%"
    completion_percentage_display.short_description = "Completion"
