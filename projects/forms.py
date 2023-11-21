from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from PIL import Image
from datetime import datetime

from .models import Category, Tag, Project, Picture, Comment, Donation, Rating


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
        exclude = ['created_at', 'updated_at']


class PictureFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            # is_main will be True for the first form, False for the rest.
            is_main = i == 0
            form.fields['is_main'].initial = is_main

    def clean(self):
        super().clean()

        # Check that at least one image has been uploaded
        if any(self.errors):
            return
        if not any(cleaned_data.get('image') for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('At least one image must be uploaded.')


class PictureForm(forms.ModelForm):
    # Add style to the picture fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    is_main = forms.BooleanField(
        initial=False, required=False, widget=forms.HiddenInput())

    class Meta:
        model = Picture
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'project']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            img = Image.open(image)
            width, height = img.size

            # Set the minimum width based on whether the image is the main picture
            min_width = 1920 if self.cleaned_data.get('is_main') else 500

            if width < min_width:
                raise ValidationError(
                    f'The image is too small, it should be at least {min_width}px wide.')

            return image


class ProjectForm(forms.ModelForm):
    # Add style to the project creation form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.name != 'existing_tags':
                visible.field.widget.attrs['class'] = 'form-control'

        self.fields['title'].widget.attrs['placeholder'] = 'Project Title'
        self.fields['details'].widget.attrs['placeholder'] = 'Write the details of the project'
        self.fields['total_target'].widget.attrs['placeholder'] = 'e.g. 5000'
        self.fields['custom_tags'].widget.attrs['placeholder'] = 'e.g. Help Palestinians, Help children'

    start_time = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}))
    end_time = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    existing_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    custom_tags = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'tags',
                   'total_raised', 'avg_rating', 'reports_num', 'is_featured', 'user', 'reported_by']

    def clean(self):
        cleaned_data = super().clean()

        is_main = cleaned_data.get('is_main')
        pictures = cleaned_data.get('pictures')

        # If the main picture is required, make sure that there is at least one picture submitted
        if is_main and not pictures:
            raise ValidationError('The main picture is required.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # ... handle tags ...
        if commit:
            instance.user = self.user
            instance.save()

        return instance


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        self.fields['content'].widget.attrs['placeholder'] = 'Your comment here'
        self.fields['content'].widget.attrs['rows'] = '4'

    class Meta:
        model = Comment
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'user', 'project', 'reports_num', 'reported', 'reported_by', 'parent']
        labels = {
            "content": ""
        }


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = '__all__'
        exclude = ['created_at', 'updated_at']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        exclude = ['created_at', 'updated_at']


class RatingForm(forms.Form):
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={'type': 'range', 'min': 1, 'max': 5, 'step': 1})
    )