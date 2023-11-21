from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

from go_fund_auth.models import CustomUser


def get_upload_to(instance, filename):
    # Get the current date
    current_date = timezone.now().strftime('%Y-%m-%d')
    # Return the upload path
    return f'uploads/{current_date}_{instance.project.id}_{filename}'


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(unique=True, max_length=255)
    details = models.TextField()
    total_target = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(50),
            MaxValueValidator(250000)
        ]
    )
    total_raised = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )
    start_time = models.DateField()
    end_time = models.DateField()
    reports_num = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    reported_by = models.ManyToManyField(CustomUser, related_name="reported_projects")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__gte=date.today()),
                name='start_time_check'
            ),
            models.CheckConstraint(
                check=models.Q(end_time__gte=models.F('start_time')),
                name='end_time_check'
            )
        ]


class Picture(models.Model):
    image = models.ImageField(upload_to=get_upload_to)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='pictures')


class Comment(models.Model):
    content = models.TextField()
    reports_num = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reported = models.BooleanField(default=False)
    reported_by = models.ManyToManyField(CustomUser, related_name="reported_comments")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')


class Donation(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Rating(models.Model):
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, default=1)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
