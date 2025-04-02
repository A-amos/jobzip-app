# JobZip

JobZip is a local job finder application built with Django that connects employers and employees. Find your next opportunity or hire talented individuals in your area.

## Features

- Job market feed with filtering options
- Job listings management for employers
- Job bookmarking system
- Job review system
- Current jobs tracking
- User profiles for both employers and employees
- Notification system
- Reporting system

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MySQL database in .env file

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.
