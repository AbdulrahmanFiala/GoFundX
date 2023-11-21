from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.forms import SetPasswordForm
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.core.mail import EmailMessage

from .decorators import user_not_authenticated
from .tokens import account_activation_token, password_reset_token

from .forms import CustomUserCreationForm, CustomUserChangeForm, ForgotPasswordForm

from django.db.models import Avg
from projects.models import Project, Category, Rating, Donation


def home(request):
    projects = Project.objects.all()
    categories = Category.objects.all()

    for project in projects:
        if project.total_target != 0:  # Avoid division by zero
            project.progress = (project.total_raised / project.total_target) * 100
        else:
            project.progress = 0

        # Calculate the average rating
        project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0

        # Calculate the half-star threshold
        project.half_star_threshold = int(project.average_rating) + 0.5

    latest_projects = projects.order_by('-created_at')[:5]
    featured_projects = projects.filter(is_featured=True)

    for project in latest_projects:
        if project.total_target != 0:  # Avoid division by zero
            project.progress = (project.total_raised / project.total_target) * 100
        else:
            project.progress = 0

        # Calculate the average rating
        project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0

        # Calculate the half-star threshold
        project.half_star_threshold = int(project.average_rating) + 0.5

    for project in featured_projects:
        if project.total_target != 0:  # Avoid division by zero
            project.progress = (project.total_raised / project.total_target) * 100
        else:
            project.progress = 0

        # Calculate the average rating
        project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0

        # Calculate the half-star threshold
        project.half_star_threshold = int(project.average_rating) + 0.5

    # Order projects by average rating and select the top five
    top_rated_projects = sorted(projects, key=lambda x: x.average_rating, reverse=True)[:5]

    return render(request, 'index.html',
                  {'projects': projects, 'categories': categories, 'latest_projects': latest_projects,
                   'featured_projects': featured_projects, 'top_rated_projects': top_rated_projects,
                   'rating_range': range(1, 6)})


@user_not_authenticated
def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Hello {user.email}! You have been logged in")

            return redirect('home')
        else:
            User = get_user_model()
            try:
                existing_user = User.objects.get(email=email)
                if not existing_user.is_active:
                    return render(request, 'login.html', {'error': 'Your account is not active. Please activate it.'})
            except User.DoesNotExist:
                return render(request, 'login.html', {'error': 'Invalid email or password.'})
            return render(request, 'login.html', {'error': 'Invalid email or password.'})

    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


@user_not_authenticated
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            if activateEmail(request, user, form.cleaned_data.get('email')):
                return redirect('account_activation_sent')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        time_difference = timezone.now() - user.activation_sent_date
        if time_difference > timedelta(hours=24):
            return render(request, 'account_activation/activation_expired.html')

        user.is_active = True
        user.save()

        return redirect('account_activation_complete')

    return render(request, 'account_activation/activation_link_invalid.html')


def reset_password(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and password_reset_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('login')
            else:
                messages.error(request, 'There was an error resetting your password.')
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset/reset_password_form.html', {'form': form})

    return render(request, 'password_reset/reset_password_link_invalid.html')


def change_password(request, user, email):
    mail_subject = "Change your GoFundX account password."
    message = render_to_string("password_reset/reset_password_email.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': password_reset_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[email])

    if not email.send():
        messages.error(request, f'Problem sending email to {email}, check if you typed it correctly.')
        return False
    return True


def activateEmail(request, user, to_email):
    mail_subject = "Activate your GoFundX account."
    message = render_to_string("account_activation/template_activate_account.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    # activation_link = f"http://{get_current_site(request).domain}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_activation_token.make_token(user)}"  # Construct the activation link
    # print("Activation Link:", activation_link)

    email = EmailMessage(mail_subject, message, to=[to_email])

    if not email.send():
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
        return False
    return True


def account_activation_complete(request):
    return render(request, 'account_activation/account_activation_complete.html')


def account_activation_sent(request):
    return render(request, 'account_activation/account_activation_sent.html')


def password_reset_sent(request):
    return render(request, 'password_reset/password_reset_sent.html')


def forgot_password(request):
    User = get_user_model()
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:

                if change_password(request, user, form.cleaned_data.get('email')):
                    return redirect('password_reset_sent')
                return redirect('home')
            else:
                messages.error(request, "Email address not found.")
    else:
        form = ForgotPasswordForm()

    return render(request, 'password_reset/forgot_password.html', {'form': form})


@login_required
def profile(request):
    projects = Project.objects.filter(user=request.user)
    donations = Donation.objects.filter(user=request.user)

    for project in projects:
        if project.total_target != 0:  # Avoid division by zero
            project.progress = (project.total_raised / project.total_target) * 100
        else:
            project.progress = 0

        # Calculate the average rating
        project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0
        print(project.average_rating)
        # Calculate the half-star threshold
        project.half_star_threshold = round(project.average_rating * 2) / 2

    return render(request, 'profile.html', {'user': request.user, 'projects': projects,
                                            'donations': donations, 'rating_range': range(1, 6)})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(request, username=request.user.email, password=password)

        if user is not None:
            request.user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')
        else:
            error = "Incorrect Password"
            return render(request, 'confirm_delete.html', {'error': error})

    return render(request, 'confirm_delete.html')
