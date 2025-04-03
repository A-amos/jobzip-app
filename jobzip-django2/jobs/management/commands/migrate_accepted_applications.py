from django.core.management.base import BaseCommand
from jobs.models import JobApplication, JobEnrollment

class Command(BaseCommand):
    help = 'Migrates accepted job applications to JobEnrollment records'

    def handle(self, *args, **options):
        accepted_applications = JobApplication.objects.filter(status='accepted')
        count = 0
        
        for application in accepted_applications:
            # Check if enrollment already exists
            enrollment_exists = JobEnrollment.objects.filter(
                job=application.job,
                employee=application.applicant
            ).exists()
            
            if not enrollment_exists:
                JobEnrollment.objects.create(
                    job=application.job,
                    employee=application.applicant,
                    status='accepted',
                    progress=0,
                    enrolled_at=application.applied_at
                )
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully migrated {count} accepted applications to JobEnrollment records'
            )
        )
