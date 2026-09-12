"""
URL configuration for learner_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views   # 👈 this line must be here
from core import views   # your app views



urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('core.urls')),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    path("signup/", views.signup_view, name="signup"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),
    path("courses/<int:course_id>/enroll/", views.enroll_course, name="enroll_course"),
    path("courses/<int:course_id>/quiz/", views.take_quiz, name="take_quiz"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("profile/", views.profile_view, name="profile"),
    path("my-results/", views.my_results, name="my_results"),
    path("accounts/", include("django.contrib.auth.urls")),
    

    # 👇 Add this for homepage
    path("", views.home, name="home"),
]




