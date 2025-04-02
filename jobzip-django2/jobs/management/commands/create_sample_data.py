from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from jobs.models import Job, JobEnrollment, JobReview, EmployeeReview, JobApplication
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        
        # Clear existing data
        JobApplication.objects.all().delete()
        JobEnrollment.objects.all().delete()
        JobReview.objects.all().delete()
        EmployeeReview.objects.all().delete()
        Job.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()  # Keep superuser

        self.stdout.write('Creating sample data...')

        # Create sample employers
        employers = []
        employer_data = [
            {'username': 'tech_corp', 'company': 'Tech Corp'},
            {'username': 'creative_studio', 'company': 'Creative Studio'},
            {'username': 'food_service', 'company': 'Food Service Inc'},
        ]
        
        for data in employer_data:
            employer = User.objects.create_user(
                username=data['username'],
                email=f"{data['username']}@example.com",
                password='testpass123',
                user_type='employer',
                location='New York, NY'
            )
            employers.append({'user': employer, 'company': data['company']})
            self.stdout.write(f'Created employer: {employer.username}')

        # Create sample employees
        employees = []
        employee_names = ['john_doe', 'jane_smith', 'bob_wilson', 'alice_brown']
        
        for name in employee_names:
            employee = User.objects.create_user(
                username=name,
                email=f"{name}@example.com",
                password='testpass123',
                user_type='employee',
                location='Los Angeles, CA',
                bio=f"I am {name.replace('_', ' ').title()}, looking for exciting opportunities!"
            )
            employees.append(employee)
            self.stdout.write(f'Created employee: {employee.username}')

        # Create sample jobs
        jobs = []
        job_titles = [
            'Senior Software Engineer',
            'UI/UX Designer',
            'Project Manager',
            'Data Analyst',
            'Marketing Specialist',
            'Chef',
            'Sales Representative',
            'Content Writer'
        ]

        for i in range(len(job_titles)):
            employer = random.choice(employers)
            deadline = timezone.now() + timedelta(days=random.randint(7, 30))
            
            job = Job.objects.create(
                employer=employer['user'],
                title=job_titles[i],
                description=f"We are looking for an experienced {job_titles[i]} to join our team.",
                location='Remote' if random.random() > 0.5 else 'On-site',
                duration='Full-time' if random.random() > 0.3 else 'Part-time',
                company=employer['company'],
                salary=f"${random.randint(50, 150)}k/year",
                employees_required=random.randint(1, 3),
                deadline=deadline,
                status='open'
            )
            jobs.append(job)
            self.stdout.write(f'Created job: {job.title}')

        # Create job applications
        statuses = ['pending', 'accepted', 'rejected']
        for job in jobs[:5]:  # Create applications for first 5 jobs
            for employee in random.sample(employees, k=random.randint(1, 3)):
                JobApplication.objects.create(
                    job=job,
                    applicant=employee,
                    status=random.choice(statuses),
                    cover_letter=f"I am very interested in the {job.title} position."
                )
                self.stdout.write(f'Created application: {employee.username} -> {job.title}')

        # Create job enrollments
        for job in random.sample(jobs, k=3):  # Enroll in 3 random jobs
            for employee in random.sample(employees, k=2):
                status = random.choice(['pending', 'in_progress', 'completed'])
                JobEnrollment.objects.create(
                    job=job,
                    employee=employee,
                    status=status
                )
                self.stdout.write(f'Created enrollment: {employee.username} -> {job.title}')

        # Create reviews
        for job in jobs:
            if random.random() > 0.5:  # 50% chance of having reviews
                for employee in random.sample(employees, k=random.randint(1, 2)):
                    # Job review
                    JobReview.objects.create(
                        job=job,
                        employee=employee,
                        rating=random.randint(3, 5),
                        comment=f"Great experience working on {job.title}!"
                    )
                    
                    # Employee review
                    EmployeeReview.objects.create(
                        job=job,
                        employee=employee,
                        employer=job.employer,
                        rating=random.randint(3, 5),
                        remarks=f"Great work by {employee.username}!"
                    )
                    self.stdout.write(f'Created reviews for: {job.title} <-> {employee.username}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
