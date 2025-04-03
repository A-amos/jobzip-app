from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='jobs/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('listings/', views.listings, name='listings'),
    path('job/post/', views.post_job, name='post_job'),
    path('job/<int:job_id>/close/', views.close_job, name='close_job'),
    path('job/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('job/reviews/', views.job_reviews, name='job_reviews'),
    path('job/current/', views.current_jobs, name='current_jobs'),
    path('jobs/update_progress/<int:enrollment_id>/', views.update_progress, name='update_progress'),
    path('jobs/quit_job/<int:job_id>/', views.quit_job, name='quit_job'),
    path('job/progress/<int:enrollment_id>/', views.update_job_progress, name='update_job_progress'),
    path('job/bookmarks/', views.bookmarks, name='bookmarks'),
    path('job/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/apply/', views.apply_for_job, name='apply_for_job'),
    path('job/<int:job_id>/quit/', views.quit_job, name='quit_job'),
    path('jobs/<int:job_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/cover-letter/', views.view_cover_letter, name='view_cover_letter'),
    path('report/', views.report, name='report'),
    path('progress-tracker/', views.progress_tracker, name='progress_tracker'),
    path('comment/<int:review_id>/add/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', views.toggle_like, name='toggle_like'),
    path('comment/<int:comment_id>/dislike/', views.toggle_dislike, name='toggle_dislike'),
]
