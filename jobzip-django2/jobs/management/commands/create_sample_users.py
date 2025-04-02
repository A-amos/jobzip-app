from django.core.management.base import BaseCommand
from jobs.models import User

class Command(BaseCommand):
    help = 'Creates sample users for testing'

    def handle(self, *args, **kwargs):
        # Create an employer
        employer = User.objects.create_user(
            username='employer1',
            email='employer1@example.com',
            password='jobzip2024',
            user_type='employer'
        )
        employer.first_name = 'John'
        employer.last_name = 'Smith'
        employer.save()

        # Create an employee
        employee = User.objects.create_user(
            username='employee1',
            email='employee1@example.com',
            password='jobzip2024',
            user_type='employee'
        )
        employee.first_name = 'Jane'
        employee.last_name = 'Doe'
        employee.save()

        # Create a superuser
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='jobzip2024admin',
            user_type='employer'
        )
        admin.save()

        self.stdout.write(self.style.SUCCESS('Successfully created sample users'))
