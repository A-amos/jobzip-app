from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Job, CompanyPicture, JobEnrollment, JobReview,
    EmployeeReview, Bookmark, Notification, Report, Comment
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'location', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'profile_picture', 'location', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'profile_picture', 'location', 'bio')}),
    )

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'employer', 'status', 'deadline')
    list_filter = ('status', 'company', 'location')
    search_fields = ('title', 'company', 'description')

@admin.register(CompanyPicture)
class CompanyPictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at')

@admin.register(JobEnrollment)
class JobEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('job', 'employee', 'status', 'enrolled_at')
    list_filter = ('status',)

@admin.register(JobReview)
class JobReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'employee', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(EmployeeReview)
class EmployeeReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'employee', 'employer', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'created_at')
    list_filter = ('created_at',)
