
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),

    # Authentication
    path("signup/", views.signup_view, name="signup"),

    # Courses
    path("courses/", views.course_list, name="course_list"),
    path(
        "courses/<int:course_id>/",
        views.course_detail,
        name="course_detail",
    ),
    path(
        "courses/<int:course_id>/enroll/",
        views.enroll_course,
        name="enroll_course",
    ),

    # Quiz
    path(
        "courses/<int:course_id>/quiz/",
        views.take_quiz,
        name="take_quiz",
    ),

    # Quiz list
    path(
        "courses/<int:course_id>/quizzes/",
        views.quiz_list,
        name="quiz_list",
    ),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("my-courses/", views.my_courses, name="my_courses"),

    # Profile
    path("profile/", views.profile_view, name="profile"),
    path(
        "progress/<int:enrollment_id>/",
        views.view_progress,
        name="view_progress",
    ),
    path(
        "upload_resume/",
        views.upload_resume,
        name="upload_resume",
    ),

    # Results
    path(
        "my-results/",
        views.my_results,
        name="my_results",
    ),
]
