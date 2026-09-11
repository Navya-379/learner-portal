from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("signup/", views.signup, name="signup"),

    # Courses
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),
    path("courses/<int:course_id>/enroll/", views.enroll_course, name="enroll_course"),
    path("courses/<int:course_id>/quiz/", views.take_quiz, name="take_quiz"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("profile/", views.profile_view, name="profile"),
    path("progress/<int:enrollment_id>/", views.view_progress, name="view_progress"),
    path("upload_resume/", views.upload_resume, name="upload_resume"),


]
