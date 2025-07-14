# 🌍 Tour Management Platform Backend

This is the Django REST API backend for the multi-organizer tour management platform.

## 🧱 Features

- JWT Authentication + Google OAuth
- Role-based permissions: Admin, Organizer, Tourist
- Tour event creation and participation
- Media sharing, cost tracking, and region logging
- Ready to be consumed by React, Flutter, or React Native apps

## 🚀 Quickstart

```bash
git clone https://github.com/yourusername/tour-management-backend.git
cd tour-management-backend

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp ..env .env

# Apply migrations and run server
python manage.py migrate
python manage.py runserver
```

## 🧩 Tech Stack

- Django + DRF
- PostgreSQL
- JWT (`djoser`, `simplejwt`)
- Cloudinary (media)
- Google Auth (`social-auth-app-django`)
