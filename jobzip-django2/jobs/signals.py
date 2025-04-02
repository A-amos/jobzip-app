from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import JobEnrollment, JobReview, EmployeeReview, Comment, Report, Job, Bookmark
from django.utils import timezone

@receiver(post_save, sender=JobEnrollment)
def create_enrollment_notification(sender, instance, created, **kwargs):
    if created:
        from .models import Notification
        # Notify employer
        Notification.objects.create(
            user=instance.job.employer,
            notification_type='listing',
            message=f'{instance.employee.username} has enrolled in your job: {instance.job.title}'
        )

@receiver(post_save, sender=JobReview)
def create_review_notification(sender, instance, created, **kwargs):
    if created:
        from .models import Notification
        # Notify employer
        Notification.objects.create(
            user=instance.job.employer,
            notification_type='review',
            message=f'{instance.employee.username} has reviewed your job: {instance.job.title}'
        )

@receiver(post_save, sender=EmployeeReview)
def create_employee_review_notification(sender, instance, created, **kwargs):
    if created:
        from .models import Notification
        # Notify employee
        Notification.objects.create(
            user=instance.employee,
            notification_type='general',
            message=f'{instance.employer.username} has reviewed your work on: {instance.job.title}'
        )

@receiver(post_save, sender=Report)
def create_report_notification(sender, instance, created, **kwargs):
    if created:
        from .models import Notification
        # Notify reported user
        Notification.objects.create(
            user=instance.reported_user,
            notification_type='general',
            message='You have been reported. Our team will review the case.'
        )

@receiver(m2m_changed, sender=Comment.likes.through)
def create_like_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from .models import Notification, User
        user = User.objects.get(pk=list(pk_set)[0])
        if instance.user != user:  # Don't notify if user likes their own comment
            Notification.objects.create(
                user=instance.user,
                notification_type='general',
                message=f'{user.username} liked your comment'
            )

@receiver(post_save, sender=Job)
def check_job_status(sender, instance, **kwargs):
    from .models import Notification, Bookmark
    if instance.deadline < timezone.now() or JobEnrollment.objects.filter(job=instance, status='accepted').count() >= instance.employees_required:
        # Update job status
        if instance.status == 'open':
            instance.status = 'closed'
            instance.save()
            
        # Notify bookmarked users
        bookmarks = Bookmark.objects.filter(job=instance)
        for bookmark in bookmarks:
            Notification.objects.create(
                user=bookmark.user,
                notification_type='bookmark',
                message=f'A job you bookmarked ({instance.title}) is no longer available'
            )
            bookmark.delete()
