# 🎓 Learner Portal

## Overview

The **Learner Portal** is a Django-based web application with a Bootstrap frontend.  
It provides a centralized platform for students to browse courses, enroll, take quizzes, and track progress.  
The portal also includes an admin dashboard for managing courses, enrollments, and performance analytics.

---

## Features

✅ Responsive course catalog with search & filter  
✅ Course detail pages (duration, category, description)  
✅ Progress tracking with styled progress bars  
✅ Quiz results and performance analytics  
✅ Admin dashboard for course & user management  
✅ Dark theme with gold-accented UI styling  
✅ Featured course section for highlighting important programs  

---

## Tech Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5  
- **Backend**: Django (Python)  
- **Database**: SQLite (default) / PostgreSQL / MySQL  
- **Other Tools**: Git, GitHub, VS Code  

---

## How It Works

1. User registers and logs in  
2. User browses available courses  
3. Enrolls in a course and tracks progress  
4. Takes quizzes and receives instant results  
5. Progress and performance are stored in the database  
6. Admins manage courses, users, and generate reports  

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/navya-379/learner-portal.git
cd learner-portal

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Start the server
python manage.py runserver
