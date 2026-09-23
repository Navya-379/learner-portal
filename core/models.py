from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return self.username

class Course(models.Model):
    title = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)   # e.g. "8 weeks"
    category = models.CharField(max_length=50)   # e.g. "Fullstack", "AI/ML"
    description = models.TextField(blank=True)

    # New fields for homepage integration
    short_description = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="course_images/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        # Always return a string, even if fields are empty
        title = self.title if self.title else "Untitled"
        category = self.category if self.category else "Uncategorized"
        return f"{title} ({category})"
  


# Enrollment model
class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


# Profile model
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)   # ✅ add this
    education = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Quiz Result model
class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    passed = models.BooleanField(default=False)
    taken_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.score}/{self.total})"

class Quiz(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


# Assessment model
class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assessments")
    text = models.CharField(max_length=255)   # Question text
    option_a = models.CharField(max_length=100, default="N/A")
    option_b = models.CharField(max_length=100, default="N/A")
    option_c = models.CharField(max_length=100, default="N/A")
    option_d = models.CharField(max_length=100, default="N/A")
    answer = models.CharField(max_length=1, default="A")

    def __str__(self):
        # Safe string representation
        course_title = getattr(self.course, "title", "Unknown Course")
        question_text = self.text if self.text else "No Question"
        return f"{course_title} - {question_text[:30]}"

# Progress model
class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # new direct link
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    completed_units = models.PositiveIntegerField(default=0)
    total_units = models.PositiveIntegerField(default=0)

    def completion_percentage(self):
        return (self.completed_units / self.total_units) * 100 if self.total_units else 0

    def __str__(self):
        user = getattr(self.user, "username", "Unknown User")
        course = getattr(self.enrollment.course, "title", "Unknown Course")
        return f"{user} - {course} ({self.completion_percentage():.2f}%)"
