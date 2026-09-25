from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import Course, Enrollment, QuizResult, Profile, Assessment, Progress, Quiz
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

@login_required
def course_list(request):
    courses = Course.objects.all()

    enrolled_course_ids = set(
        Enrollment.objects.filter(
            user=request.user
        ).values_list("course_id", flat=True)
    )

    return render(request, "courses.html", {
        "courses": courses,
        "enrolled_course_ids": enrolled_course_ids,
    })


# Courses
def course_list(request):
    courses = Course.objects.all()

    return render(request, "courses.html", {"courses": courses})



@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Find the current user's enrollment for this course
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    enrolled = enrollment is not None

    # Handle enrollment
    if request.method == "POST" and not enrolled:
        enrollment = Enrollment.objects.create(
            user=request.user,
            course=course
        )
        return redirect("dashboard")

    # Get quizzes for this course
    quizzes = course.quiz_set.all()

    # Get progress through the enrollment
    progress = None
    if enrollment:
        progress = Progress.objects.filter(
            enrollment=enrollment
        ).first()

    return render(request, "course_detail.html", {
        "course": course,
        "enrolled": enrolled,
        "quizzes": quizzes,
        "progress": progress,
    })






@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        # Create progress record for the new enrollment
        Progress.objects.get_or_create(
            user=request.user,
            enrollment=enrollment,
            defaults={
                "completed_units": 0,
                "total_units": 0,
            }
        )

        messages.success(
            request,
            f"You have successfully enrolled in {course.title}!"
        )
    else:
        messages.info(
            request,
            f"You are already enrolled in {course.title}."
        )

    # Go back to the course details page
    return redirect("course_detail", course_id=course.id)








@login_required
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

        # Check answers
        for question in questions:
            selected_answer = request.POST.get(f"q{question.id}")

            if selected_answer:
                if selected_answer.strip().upper() == question.answer.strip().upper():
                    score += 1

        # Calculate percentage
        percentage = (score / total) * 100 if total > 0 else 0

        # Create or update result
        result, created = QuizResult.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                "score": score,
                "total": total,
                "passed": percentage >= 60,
                "taken_at": timezone.now(),
            }
        )

        # Show result page
        return render(request, "quiz_result.html", {
            "course": course,
            "result": result,
            "percentage": percentage,
        })

    # GET request → show questions
    return render(request, "take_quiz.html", {
        "course": course,
        "questions": questions,
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
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related("course")

    results = QuizResult.objects.filter(
        user=request.user
    ).select_related("course").order_by("-taken_at")

    for enrollment in enrollments:
        progress = Progress.objects.filter(
            enrollment=enrollment
        ).first()

        if progress:
            enrollment.completion = round(
                progress.completion_percentage(), 2
            )
        else:
            enrollment.completion = 0

    course_results = {}

    for result in results:
        if result.course_id not in course_results:
            course_results[result.course_id] = result

    context = {
        "enrollments": enrollments,
        "results": results,
        "course_results": course_results.values(),
    }

    return render(request, "dashboard.html", context)




def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Ensure Profile is linked correctly
            Profile.objects.get_or_create(user=user)
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


@login_required
def quiz_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    questions = Assessment.objects.filter(course=course)

    return render(request, "take_quiz.html", {
        "course": course,
        "questions": questions,
    })
