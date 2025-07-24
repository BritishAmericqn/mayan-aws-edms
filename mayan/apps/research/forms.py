from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Dataset, Project, Study


class ProjectForm(forms.ModelForm):
    """Form for creating and editing research projects."""
    
    class Meta:
        fields = (
            'title', 'description', 'principal_investigator', 'institution',
            'start_date', 'end_date', 'status', 'funding_source', 'funding_amount'
        )
        model = Project
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful placeholders and help text
        self.fields['title'].widget.attrs.update({
            'placeholder': _('e.g., Climate Change Impact Assessment')
        })
        self.fields['principal_investigator'].widget.attrs.update({
            'placeholder': _('e.g., Dr. Jane Smith')
        })
        self.fields['institution'].widget.attrs.update({
            'placeholder': _('e.g., University of California, Berkeley')
        })
        self.fields['funding_source'].widget.attrs.update({
            'placeholder': _('e.g., National Science Foundation')
        })


class StudyForm(forms.ModelForm):
    """Form for creating and editing studies within projects."""
    
    class Meta:
        fields = (
            'title', 'description', 'study_type', 'start_date', 'end_date', 'status'
        )
        model = Study
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Add helpful placeholders
        self.fields['title'].widget.attrs.update({
            'placeholder': _('e.g., Urban Heat Island Analysis')
        })
        
        # If this is a new study, set project context
        if project and not self.instance.pk:
            self.instance.project = project

    def save(self, commit=True):
        study = super().save(commit=False)
        
        # Ensure project is set (for new studies)
        if hasattr(self.instance, 'project') and self.instance.project:
            study.project = self.instance.project
            
        if commit:
            study.save()
        return study


class DatasetForm(forms.ModelForm):
    """Form for creating and editing datasets within studies."""
    
    class Meta:
        fields = (
            'name', 'description', 'data_type', 'analysis_status'
        )
        model = Dataset
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('study', None)
        super().__init__(*args, **kwargs)
        
        # Add helpful placeholders
        self.fields['name'].widget.attrs.update({
            'placeholder': _('e.g., Temperature Sensor Data 2024')
        })
        
        # If this is a new dataset, set study context
        if study and not self.instance.pk:
            self.instance.study = study

    def save(self, commit=True):
        dataset = super().save(commit=False)
        
        # Ensure study is set (for new datasets)
        if hasattr(self.instance, 'study') and self.instance.study:
            dataset.study = self.instance.study
            
        if commit:
            dataset.save()
        return dataset 