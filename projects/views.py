from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import modelformset_factory
from django.db.models import Avg
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
from go_fund_auth.models import CustomUser
from .models import Category, Tag, Project, Picture, Comment, Donation, Rating
from .forms import ProjectForm, PictureForm, CommentForm, \
    PictureFormSet as PictureFormset, RatingForm


# Create your views here.
def create_project(request):
    PictureFormSet = modelformset_factory(Picture, form=PictureForm, extra=5, formset=PictureFormset)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        initial = [{'is_main': True if i == 0 else False} for i in range(5)]
        formset = PictureFormSet(request.POST, request.FILES, queryset=Picture.objects.none(), initial=initial)

        if form.is_valid() and formset.is_valid():
            form.user = request.user
            form.save()
            instances = formset.save(commit=False)  # Save each Picture instance without committing to the database
            if instances:  # Check if there are any pictures
                instances[0].is_main = True  # Set is_main for the first picture

            project = form.save()  # Save the project instance to the database

            existing_tags = form.cleaned_data['existing_tags']
            project.tags.set(existing_tags)  # Now you can set the tags

            custom_tags = form.cleaned_data['custom_tags']
            if custom_tags:
                custom_tags_list = [tag.strip() for tag in custom_tags.split(',')]
                for tag_name in custom_tags_list:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    project.tags.add(tag)

            for instance in instances:
                instance.project = project  # Assign the project to the picture
                instance.save()  # Now save the picture instance to the database

            return redirect('projects')
    else:
        form = ProjectForm()
        formset = PictureFormSet(queryset=Picture.objects.none())
    return render(request, 'projects/create_project.html', {'form': form, 'formset': formset})


def project_list(request):
    projects = Project.objects.all()

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

    return render(request, 'projects/projects.html', {'projects': projects, 'rating_range': range(1, 6)})


def project_details(request, id):
    # project = get_object_or_404(Project, pk=id)
    project = Project.objects.annotate(avg_rating=Avg('rating__rating')).get(id=id)
    comment_form = CommentForm()
    rating_form = RatingForm()

    if project.total_target != 0:  # Avoid division by zero
        project.progress = (project.total_raised / project.total_target) * 100
    else:
        project.progress = 0

    # Calculate the average rating
    project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0
    print(project.average_rating)
    # Calculate the half-star threshold
    project.half_star_threshold = round(project.average_rating * 2) / 2

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        # Handle comment submission
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user
            new_comment.project = project

            # Check if the comment is a reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                # If it is, set the parent of the comment
                new_comment.parent_id = int(parent_id)

            new_comment.save()
            comment_form = CommentForm()
            return redirect('project_details', id=id)

        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            user_rating = rating_form.cleaned_data['rating']
            rating, created = Rating.objects.get_or_create(user=request.user, project=project)
            rating.rating = user_rating
            rating.save()
            return redirect('project_details', id=id)

    if request.user.is_authenticated:
        try:
            rating = Rating.objects.filter(user=request.user, project=project).first()
            if rating:
                user_rating = rating.rating
            else:
                user_rating = None
        except Rating.DoesNotExist:
            user_rating = None
    else:
        rating = None
        user_rating = None

    related_projects = Project.objects.filter(category=project.category).exclude(id=project.id)[:3]
    latest_ratings = Rating.objects.filter(project=project).order_by('-id')[:5]

    # comments = project.comment_set.all()
    comments = project.comment_set.filter(parent__isnull=True)

    for related_project in related_projects:
        if related_project.total_target != 0:  # Avoid division by zero
            related_project.progress = (related_project.total_raised / related_project.total_target) * 100
        else:
            related_project.progress = 0

        # Calculate the average rating
        related_project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0

        # Calculate the half-star threshold
        related_project.half_star_threshold = int(related_project.average_rating) + 0.5

    return render(request, 'projects/project_details.html',
                  {'project': project, 'comment_form': comment_form,
                   'comments': comments, 'rating': rating,
                   'rating_range': range(1, 6),
                   'rating_form': rating_form,
                   'user_rating': user_rating,
                   'related_projects': related_projects,
                   'latest_ratings': latest_ratings
                   })


def update_project(request, id):
    project = get_object_or_404(Project, pk=id)
    PictureFormSet = modelformset_factory(Picture, form=PictureForm, extra=5, formset=PictureFormset)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        formset = PictureFormSet(request.POST, request.FILES, queryset=Picture.objects.filter(project=project))
        if form.is_valid() and formset.is_valid():
            project = form.save(commit=False)  # Don't save the Project instance yet
            project.user = request.user  # Assign the user to the project
            project.save()  # Now save the Project instance to the database
            instances = formset.save(commit=False)
            for instance in instances:
                instance.project = project
                instance.save()
            return redirect('project_details', id=id)
    else:
        form = ProjectForm(instance=project)
        formset = PictureFormSet(queryset=Picture.objects.filter(project=project))
    return render(request, 'projects/update_project.html', {'form': form, 'formset': formset})


def delete_project(request, id):
    project = get_object_or_404(Project, pk=id)
    if project.total_raised >= (project.total_target * Decimal('0.25')):
        return render(request, 'projects/delete_project.html', context={'project': project,'error': 'Cannot delete project as it has already raised 25% of its target.'})

    if request.method == 'POST':
        # Clear all messages
        storage = messages.get_messages(request)
        storage.used = True

        # Check if total_raised is equal to or more than 25% of total_target
        if project.total_raised >= (project.total_target * Decimal('0.25')):
            return redirect(reverse('project_details', args=[id]), context={'error': 'Cannot delete project as it has already raised 25% of its target.'})
        else:
            project.delete()
            return redirect(reverse('projects'))

    return render(request, 'projects/delete_project.html', {'project': project})


def donate(request, id):
    if request.method == 'POST':
        project = Project.objects.get(id=id)
        try:
            user = CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            user = None

        amount = request.POST['flexDefault']
        if amount == "":
            amount = request.POST['flexRadioDefault']

        # Convert the amount to decimal
        amount = Decimal(amount)

        # Calculate the remaining amount of the total target
        remaining_amount = project.total_target - project.total_raised

        # Check if the donation amount is valid
        if amount <= 0 or amount > remaining_amount:
            # If not, return an error message
            return render(request, 'projects/donate.html', {'error': 'Invalid donation amount.'})

        donation = Donation(amount=amount, user=user, project=project)
        donation.save()

        # Add the donation amount to the total raised
        project.total_raised += amount
        project.save()

        return redirect('project_details', id=project.id)
    return render(request, 'projects/donate.html')


def search_results(request):
    query = request.GET.get('search')
    search_type = request.GET.get('searchType')

    if search_type == 'names':
        results = Project.objects.filter(title__icontains=query)
    else:
        results = Project.objects.filter(tags__name__icontains=query)

    for project in results:
        if project.total_target != 0:  # Avoid division by zero
            project.progress = (project.total_raised / project.total_target) * 100
        else:
            project.progress = 0

        # Calculate the average rating
        project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0

        # Calculate the half-star threshold
        project.half_star_threshold = int(project.average_rating) + 0.5

    return render(request, 'projects/search_results.html', {'results': results, 'rating_range': range(1, 6)})


def category_projects(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    projects = Project.objects.filter(category=category)

    for project in projects:
        if project.total_target != 0:  # Avoid division by zero
            project.progress = (project.total_raised / project.total_target) * 100
        else:
            project.progress = 0

        # Calculate the average rating
        project.average_rating = Rating.objects.filter(project=project).aggregate(Avg('rating'))['rating__avg'] or 0

        # Calculate the half-star threshold
        project.half_star_threshold = int(project.average_rating) + 0.5

    return render(request, 'projects/category_projects.html', {'category': category, 'projects': projects, 'rating_range': range(1, 6)})


def report_project(request, id):
    if request.user.is_authenticated:
        project = Project.objects.get(id=id)
        if request.user not in project.reported_by.all():
            project.reported_by.add(request.user)
            project.reports_num += 1
            project.save()
    return redirect('project_details', id=id)


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user:
        comment.delete()
    return redirect('project_details', id=comment.project.id)


def report_comment(request, comment_id):
    if request.user.is_authenticated:
        comment = Comment.objects.get(id=comment_id)
        if request.user not in comment.reported_by.all():
            comment.reported_by.add(request.user)
            comment.reports_num += 1
            comment.save()
    return redirect('project_details', id=comment.project.id)


def custom_404(request, exception=None):
    return render(request, 'error/404.html', status=404)


def custom_500(request):
    return render(request, 'error/500.html', status=500)


def trigger_server_error(request):
    # Simulate a server error
    raise Exception("This is a simulated server error")
    return HttpResponse("This won't be reached")
