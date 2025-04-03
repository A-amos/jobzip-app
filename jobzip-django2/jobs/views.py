from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job, JobReview, JobEnrollment, Bookmark, Report, Comment, User, JobApplication, Notification, EmployerProfile, EmployeeProfile
from .forms import UserRegistrationForm, CustomAuthenticationForm, JobPostForm, JobApplicationForm
from django.urls import reverse

def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = form.cleaned_data['user_type']
                user.save()
                
                # Create corresponding profile
                if user.user_type == 'employer':
                    company_name = request.POST.get('company_name')
                    if not company_name:
                        raise ValueError("Company name is required for employer accounts")
                    EmployerProfile.objects.create(user=user, company_name=company_name)
                else:
                    EmployeeProfile.objects.create(user=user)
                    
                login(request, user)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Account created successfully! Redirecting...',
                        'redirect_url': reverse('home')
                    })
                else:
                    messages.success(request, 'Account created successfully!')
                    return redirect('home')
            except ValueError as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'company_name': [str(e)]}
                    })
                else:
                    messages.error(request, str(e))
                    return render(request, 'jobs/signup.html', {'form': form})
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': ['An error occurred while creating your account. Please try again.']}
                    })
                else:
                    messages.error(request, 'An error occurred while creating your account. Please try again.')
                    return render(request, 'jobs/signup.html', {'form': form})
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                # Add form field errors
                for field, error_list in form.errors.items():
                    errors[field] = error_list
                # Add non-field errors
                if form.non_field_errors():
                    errors['__all__'] = form.non_field_errors()
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
            else:
                return render(request, 'jobs/signup.html', {'form': form})
    else:
        form = UserRegistrationForm()
        
    return render(request, 'jobs/signup.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.exclude(pk=user.pk).filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already exists'})
        
        user.email = email
        if password:
            user.set_password(password)
        user.save()
        
        if hasattr(user, 'employerprofile'):
            company_name = request.POST.get('company_name')
            user.employerprofile.company_name = company_name
            user.employerprofile.save()
        elif hasattr(user, 'employeeprofile'):
            location = request.POST.get('location')
            user.employeeprofile.location = location
            user.employeeprofile.save()
        
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
    
    is_employer = hasattr(request.user, 'employerprofile')
    context = {
        'is_employer': is_employer,
        'employer_profile': getattr(request.user, 'employerprofile', None),
        'employee_profile': getattr(request.user, 'employeeprofile', None),
    }
    return render(request, 'jobs/profile.html', context)

@login_required
def home(request):
    """Home view showing relevant content based on user type"""
    if request.user.user_type == 'employee':
        recent_applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')[:5]
        bookmarked_jobs = Job.objects.filter(bookmark__user=request.user).order_by('-created_at')[:5]
        recommended_jobs = Job.objects.filter(status='open').exclude(bookmark__user=request.user).order_by('-created_at')[:5]
        
        return render(request, 'jobs/employee_home.html', {
            'recent_applications': recent_applications,
            'bookmarked_jobs': bookmarked_jobs,
            'recommended_jobs': recommended_jobs
        })
    else:
        # Employer view
        active_jobs = Job.objects.filter(employer=request.user, status='open').order_by('-created_at')
        recent_applications = JobApplication.objects.filter(job__employer=request.user).order_by('-applied_at')[:10]
        
        return render(request, 'jobs/employer_home.html', {
            'active_jobs': active_jobs,
            'recent_applications': recent_applications
        })

@login_required
def listings(request):
    if request.user.user_type == 'employer':
        # Show employer their own job postings
        return render(request, 'jobs/employer_listings.html', {
            'jobs': Job.objects.filter(employer=request.user).order_by('-created_at'),
            'form': JobPostForm()
        })
    elif request.user.user_type == 'employee':
        # Show employee all open jobs
        jobs = Job.objects.filter(status='open').order_by('-created_at')
        bookmarks = Bookmark.objects.filter(user=request.user).values_list('job_id', flat=True)
        for job in jobs:
            job.is_bookmarked = job.id in bookmarks
        return render(request, 'jobs/listings.html', {'jobs': jobs})
    return redirect('home')

@login_required
def apply_job(request):
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')
        
        try:
            job = Job.objects.get(id=job_id, status='open')
            
            # Check if user already applied
            if JobApplication.objects.filter(job=job, applicant=request.user).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'You have already applied for this position'
                })
            
            # Create application
            application = JobApplication.objects.create(
                job=job,
                applicant=request.user,
                cover_letter=cover_letter,
                resume=resume
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Application submitted successfully'
            })
            
        except Job.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Job not found or no longer accepting applications'
            })
            
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def toggle_bookmark(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            job=job
        )
        
        if not created:
            bookmark.delete()
            message = 'Job removed from bookmarks'
        else:
            message = 'Job added to bookmarks'
            
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Job.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Job not found'
        })

@login_required
def post_job(request):
    """View for posting a new job"""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Only employers can post jobs'}, status=403)
        
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.status = 'open'
            job.save()
            return redirect('listings')
    return redirect('listings')

@login_required
def job_reviews(request):
    reviews = JobReview.objects.select_related('job', 'employee').prefetch_related('comments').order_by('-created_at')
    filter_type = request.GET.get('filter')
    
    if filter_type == 'your_location' and request.user.location:
        reviews = reviews.filter(job__location=request.user.location)
    elif filter_type == 'other_location':
        location = request.GET.get('location')
        if location:
            reviews = reviews.filter(job__location=location)
    elif filter_type == 'company':
        company = request.GET.get('company')
        if company:
            reviews = reviews.filter(job__company=company)
            
    return render(request, 'jobs/reviews.html', {'reviews': reviews})

@login_required
def current_jobs(request):
    """View for showing user's current jobs"""
    if request.user.user_type != 'employee':
        return redirect('home')
        
    enrollments = JobEnrollment.objects.filter(
        employee=request.user,
        status__in=['accepted', 'in_progress', 'completed']
    ).select_related('job').order_by('-enrolled_at')
    
    return render(request, 'jobs/current_jobs.html', {'enrollments': enrollments})

@login_required
def bookmarks(request):
    # Get bookmarked jobs for the current user
    bookmarked_jobs = Job.objects.filter(
        bookmark__user=request.user,
        status='open'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(bookmarked_jobs, 6)  # 6 jobs per page
    page = request.GET.get('page')
    bookmarked_jobs = paginator.get_page(page)
    
    context = {
        'bookmarked_jobs': bookmarked_jobs,
    }
    return render(request, 'jobs/bookmarks.html', context)

@login_required
def report(request):
    if request.method == 'POST':
        reported_user_id = request.POST.get('reported_user')
        reason = request.POST.get('reason')
        
        if reported_user_id and reason:
            reported_user = get_object_or_404(User, id=reported_user_id)
            if reported_user != request.user:
                Report.objects.create(
                    reporter=request.user,
                    reported_user=reported_user,
                    reason=reason
                )
                messages.success(request, 'Your report has been submitted and will be reviewed by our team.')
            else:
                messages.error(request, 'You cannot report yourself.')
        
        return redirect('report')
    
    users = User.objects.exclude(id=request.user.id)
    user_reports = Report.objects.filter(reporter=request.user).select_related('reported_user').order_by('-created_at')
    
    return render(request, 'jobs/report.html', {
        'users': users,
        'user_reports': user_reports
    })

@login_required
def apply_for_job(request, job_id):
    """Handle job application submission"""
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.job = job
                application.applicant = request.user
                application.save()
                
                # Create notification for employer
                Notification.objects.create(
                    user=job.employer,
                    notification_type='application',
                    message=f'{request.user.username} has applied for {job.title}',
                    related_job=job
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Your application has been submitted successfully!'
                })
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'message': 'You have already applied for this job.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please check your form inputs.'
            })
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply.html', {
        'form': form,
        'job': job
    })

@login_required
def my_applications(request):
    """View for showing user's job applications"""
    applications = JobEnrollment.objects.filter(employee=request.user).order_by('-enrolled_at')
    context = {
        'applications': applications,
        'total_count': applications.count(),
        'pending_count': applications.filter(status='pending').count(),
        'accepted_count': applications.filter(status='accepted').count(),
    }
    return render(request, 'jobs/my_applications.html', context)

@login_required
@require_POST
def update_application_status(request, application_id):
    """Update status of a job application"""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    application = get_object_or_404(JobApplication, id=application_id)
    if application.job.employer != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        status = data.get('status')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if status not in ['accepted', 'rejected', 'pending']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    application.status = status
    application.save()
    
    # Create JobEnrollment when application is accepted
    if status == 'accepted':
        JobEnrollment.objects.create(
            job=application.job,
            employee=application.applicant,
            status='accepted',
            progress=0
        )
    
    # Create notification for applicant
    Notification.objects.create(
        user=application.applicant,
        notification_type='application_status',
        message=f'Your application for {application.job.title} has been {status}',
        related_job=application.job
    )
    
    return JsonResponse({'success': True})

@login_required
@require_POST
def close_job(request, job_id):
    """Close a job posting"""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    job.status = 'closed'
    job.save()
    
    return JsonResponse({'success': True})

@login_required
def view_cover_letter(request, application_id):
    """View cover letter for a job application"""
    application = get_object_or_404(JobApplication, id=application_id)
    
    if request.user != application.job.employer and request.user != application.applicant:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({'cover_letter': application.cover_letter or ''})

@login_required
@require_POST
def update_progress(request, enrollment_id):
    """Update the progress of a job enrollment"""
    try:
        data = json.loads(request.body)
        progress = data.get('progress')
        
        if not isinstance(progress, int) or progress < 0 or progress > 100:
            return JsonResponse({
                'success': False,
                'error': 'Invalid progress value. Must be between 0 and 100.'
            })
            
        enrollment = get_object_or_404(JobEnrollment, id=enrollment_id)
        
        # Only allow employer of the job to update progress
        if request.user != enrollment.job.employer:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied. Only the employer can update progress.'
            })
            
        enrollment.update_progress(progress)
        
        # Create notification for employee
        Notification.objects.create(
            user=enrollment.employee,
            notification_type='current_job',
            message=f'Your progress on {enrollment.job.title} has been updated to {progress}%'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Progress updated successfully'
        })
        
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        })
    except JobEnrollment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Job enrollment not found'
        })

@login_required
@require_POST
def quit_job(request, job_id):
    """View for quitting a job"""
    try:
        enrollment = get_object_or_404(JobEnrollment, job_id=job_id, employee=request.user)
        enrollment.status = 'quit'
        enrollment.quit_at = timezone.now()
        enrollment.save()
        
        # Create notification for employer
        Notification.objects.create(
            user=enrollment.job.employer,
            notification_type='current_job',
            message=f'{request.user.username} has quit the job: {enrollment.job.title}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Job quit successfully'
        })
        
    except JobEnrollment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Job enrollment not found'
        })

@login_required
@require_POST
def add_comment(request, review_id):
    review = get_object_or_404(JobReview, id=review_id)
    content = request.POST.get('content')
    
    if content:
        Comment.objects.create(
            review=review,
            user=request.user,
            content=content
        )
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Comment content is required'})

@login_required
@require_POST
def toggle_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
    
    return JsonResponse({'success': True})

@login_required
@require_POST
def toggle_dislike(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)
    
    return JsonResponse({'success': True})

@login_required
def job_applications(request, job_id):
    # Only employers can view applications
    if request.user.user_type != 'employer':
        messages.error(request, 'Only employers can view job applications')
        return redirect('home')
        
    # Get the job and verify ownership
    job = get_object_or_404(Job, id=job_id)
    if job.employer != request.user:
        messages.error(request, 'You can only view applications for your own jobs')
        return redirect('listings')
        
    # Get all applications for this job
    applications = JobApplication.objects.filter(job=job).order_by('-applied_at')
    
    return render(request, 'jobs/job_applications.html', {
        'job': job,
        'applications': applications
    })

@login_required
@require_POST
def update_job_progress(request, enrollment_id):
    """Update the progress status of a job enrollment"""
    if request.user.user_type != 'employee':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    enrollment = get_object_or_404(JobEnrollment, id=enrollment_id, employee=request.user)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in ['pending', 'in_progress', 'completed']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        enrollment.status = new_status
        enrollment.save()
        
        # Create notification for employer
        Notification.objects.create(
            user=enrollment.job.employer,
            notification_type='job_progress',
            message=f'{request.user.username} has updated their progress on {enrollment.job.title} to {new_status}',
            related_job=enrollment.job
        )
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def progress_tracker(request):
    """View for employers to track employee progress"""
    if request.user.user_type != 'employer':
        return redirect('home')
        
    jobs = Job.objects.filter(employer=request.user).prefetch_related(
        'jobenrollment_set',
        'jobenrollment_set__employee'
    ).order_by('-created_at')
    
    # Add enrollments to each job
    for job in jobs:
        job.enrollments = job.jobenrollment_set.all().order_by('-enrolled_at')
    
    return render(request, 'jobs/progress_tracker.html', {'jobs': jobs})
