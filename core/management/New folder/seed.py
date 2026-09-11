from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Course, Assessment

class Command(BaseCommand):
    help = "Seed database with sample courses and assessments"

    def handle(self, *args, **kwargs):
        # Create a test user
        user, created = User.objects.get_or_create(username="testuser")
        if created:
            user.set_password("password123")
            user.save()

        # Create a sample course
        course, _ = Course.objects.get_or_create(
            title="Python Basics",
            duration="4 weeks",
            category="Programming"
        )

        # Create sample assessments
        Assessment.objects.get_or_create(
            course=course,
            question="What is the output of print(2+3)?",
            option1="5",
            option2="23",
            option3="Error",
            option4="None",
            answer="5"
        )

        Assessment.objects.get_or_create(
            course=course,
            question="Which keyword is used to define a function in Python?",
            option1="func",
            option2="def",
            option3="function",
            option4="lambda",
            answer="def"
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
