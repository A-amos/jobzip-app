from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import User, Job, JobApplication

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'pattern': '^[a-zA-Z]{3,20}$',
            'title': 'Username must be 3-20 characters long and can only contain letters'
        }),
        validators=[
            RegexValidator(
                regex='^[a-zA-Z]{3,20}$',
                message='Username must be 3-20 characters long and can only contain letters',
                code='invalid_username'
            )
        ]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'minlength': '8'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username does not exist')
        return username

class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('employer', 'I want to hire'),
        ('employee', 'I want to find work'),
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'pattern': '^[a-zA-Z]{3,20}$',
            'title': 'Username must be 3-20 characters long and can only contain letters'
        }),
        validators=[
            RegexValidator(
                regex='^[a-zA-Z]{3,20}$',
                message='Username must be 3-20 characters long and can only contain letters',
                code='invalid_username'
            )
        ]
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'required': 'required'
        }),
        validators=[EmailValidator(message='Enter a valid email address')]
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'minlength': '8',
            'title': 'Password must be at least 8 characters long and include uppercase, lowercase, numbers and special characters'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'minlength': '8'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'user_type':
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)
        except forms.ValidationError as error:
            raise forms.ValidationError(error)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        
        return cleaned_data

class JobPostForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'duration', 'company', 'salary', 'employees_required', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the job responsibilities, requirements, and benefits...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., San Francisco, CA or Remote'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3 months, 1 year, Full-time'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your company name'}),
            'salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $50,000/year or $25/hour'}),
            'employees_required': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Number of positions'}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write a brief cover letter explaining why you\'re a great fit for this position...'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            })
        }
