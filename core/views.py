from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Enrollment, QuizResult, Profile, Assessment, Progress
from .forms import ProfileForm
from .forms import CustomUserCreationForm
from .models import Profile
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Avg, Max, Count

User = get_user_model()


from datetime import datetime

from core.models import Course

def home(request):
    courses = Course.objects.all()[:6]  # show top 6 courses
    return render(request, "home.html", {"courses": courses})

def about(request):
    return render(request, 'about.html')

def courses(request):
    return render(request, 'courses.html')
# Courses
def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses/course_list.html", {"courses": courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if already enrolled
    enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    # Handle enrollment on POST
    if request.method == "POST" and not enrolled:
        Enrollment.objects.create(user=request.user, course=course)
        return redirect("dashboard")

    # Get quizzes for this course
    quizzes = course.quiz_set.all()  # assuming Quiz model has FK to Course

    # Get progress if enrolled
    progress = None
    if enrolled:
        progress = course.progress_set.filter(user=request.user).first()

    return render(request, "course_detail.html", {
        "course": course,
        "enrolled": enrolled,
        "quizzes": quizzes,
        "progress": progress,
    })


def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        messages.success(request, f"You have successfully enrolled in {course.title}!")
        return redirect("dashboard")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")
        return redirect("course_detail", course_id=course.id)





def take_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = Assessment.objects.filter(course=course)

    if request.method == "POST":
        if not questions.exists():
            return render(request, "quiz_result.html", {
                "course": course,
                "result": None,
                "error": "No questions available for this quiz."
            })

        score = 0
        total = questions.count()

        for q in questions:
            selected = request.POST.get(f"q{q.id}")
            if selected and selected.strip().upper() == q.answer.strip().upper():
                score += 1

        result, created = QuizResult.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                "score": score,
                "total": total,
                "passed": (score >= total/2),
                "taken_at": timezone.now(),
            }
        )

        return render(request, "quiz_result.html", {
            "course": course,
            "result": result
        })

    # ✅ GET request shows quiz
    return render(request, "take_quiz.html", {
        "course": course,
        "questions": questions
    })




def quiz_result(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    result = QuizResult.objects.filter(user=request.user, course=course).last()
    return render(request, "quiz_result.html", {"course": course, "result": result})



def my_results(request):
    course_id = request.GET.get("course")
    results = QuizResult.objects.filter(user=request.user).order_by("-taken_at")

    if course_id:
        results = results.filter(course_id=course_id)

    courses = Course.objects.all()

    # Summary stats
    summary = results.aggregate(
        total_attempts=Count("id"),
        average_score=Avg("score"),
        highest_score=Max("score"),
    )

    return render(request, "my_results.html", {
        "results": results,
        "courses": courses,
        "selected_course": course_id,
        "summary": summary,
    })


# Dashboard & My Courses
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, "my_courses.html", {"enrollments": enrollments})


# Auth




# Profile
@login_required

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile.html", {"profile": profile, "form": form})

@login_required
def dashboard(request):
    # Get all enrollments for the logged-in user
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")

    # Get all quiz results for the logged-in user
    results = QuizResult.objects.filter(user=request.user).select_related("course")

    # Map course_id → latest quiz result
    course_results = {}
    for r in results.order_by("-taken_at"):
        if r.course.id not in course_results:
            course_results[r.course.id] = r

    # Map course_id → progress completion percentage
    progress_data = {}
    for enrollment in enrollments:
        progress = Progress.objects.filter(enrollment=enrollment).first()
        completion = progress.completion_percentage() if progress else 0
        progress_data[enrollment.course.id] = {"completion": round(completion, 2)}

    context = {
        "enrollments": enrollments,
        "results": results,
        "course_results": course_results,
        "progress_data": progress_data,
    }
    return render(request, "dashboard.html", context)



def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "🎉 Account created successfully! Please log in.")
            return redirect("login")
        else:
            messages.error(request, "❌ Signup failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"✅ Welcome back, {user.username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "❌ Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "👋 You have been logged out successfully.")
    return redirect("login")


@login_required
def view_progress(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    progress = Progress.objects.filter(enrollment=enrollment).first()

    if not progress:
        completion = 0
    else:
        completion = progress.completion_percentage()

    context = {
        "enrollment": enrollment,
        "progress": progress,
        "completion": round(completion, 2),
    }
    return render(request, "progress.html", context)

@login_required
def upload_resume(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST" and "resume" in request.FILES:
        profile.resume = request.FILES["resume"]
        profile.save()
        messages.success(request, "Your resume has been uploaded successfully!")
        return redirect("profile")

    return render(request, "upload_resume.html", {"profile": profile})

@login_required
def submit_quiz(request, course_id):
    if request.method == "POST":
        score = int(request.POST.get("score", 0))
        total = int(request.POST.get("total", 0))
        passed = score >= (total * 0.6)  # 60% pass threshold

        QuizResult.objects.create(
            user=request.user,
            course_id=course_id,
            score=score,
            total=total,
            passed=passed,
        )

        if passed:
            messages.success(request, "🎉 Congratulations! You passed the quiz.")
        else:
            messages.error(request, "❌ Better luck next time. Keep practicing!")

        return redirect("dashboard")


@login_required
def update_profile(request):
    # Get or create the profile for the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile_edit.html", {"form": form, "profile": profile})
