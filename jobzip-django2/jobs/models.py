from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('employer', 'Employer'),
        ('employee', 'Employee'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='employee')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

class Job(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    company = models.CharField(max_length=200)
    salary = models.CharField(max_length=100, help_text="e.g., $50,000/year or $25/hour", null=True, blank=True)
    employees_required = models.IntegerField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    company_pictures = models.ManyToManyField('CompanyPicture')

    def __str__(self):
        return f"{self.title} at {self.company}"

class CompanyPicture(models.Model):
    image = models.ImageField(upload_to='company_pics/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class JobEnrollment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('quit', 'Quit')
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # Progress percentage (0-100)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def update_progress(self, new_progress):
        self.progress = min(max(0, new_progress), 100)  # Ensure progress is between 0-100
        if self.progress == 100:
            self.status = 'completed'
            self.completed_at = timezone.now()
        elif self.progress > 0:
            self.status = 'in_progress'
        self.save()

    def __str__(self):
        return f"{self.employee.username}'s enrollment in {self.job.title}"

class JobReview(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class EmployeeReview(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_reviews')
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField()
    remarks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('listing', 'Listing'),
        ('bookmark', 'Bookmark'),
        ('review', 'Review'),
        ('current_job', 'Current Job'),
        ('general', 'General'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    ban_duration = models.IntegerField(null=True, blank=True)  # Duration in days

class Comment(models.Model):
    review = models.ForeignKey(JobReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments')
    dislikes = models.ManyToManyField(User, related_name='disliked_comments')
    created_at = models.DateTimeField(auto_now_add=True)

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.username}'s application for {self.job.title}"

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.user.username})"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.location})"
