from django import forms
from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.models import Document
from mayan.apps.forms import form_fields, form_widgets

from .models import Dataset, Project, Study, DatasetDocument


class ProjectForm(forms.ModelForm):
    """
    Professional form for creating and editing research projects.
    Enhanced for Task 2.4 with better UX and validation.
    """
    
    class Meta:
        model = Project
        fields = (
            'title', 'description', 'principal_investigator', 'institution',
            'start_date', 'end_date', 'status', 'funding_source', 'funding_amount'
        )
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': _('Detailed description of the research project, objectives, and expected outcomes...')
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Climate Change Impact Assessment')
            }),
            'principal_investigator': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Dr. Jane Smith')
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., University of California, Berkeley')
            }),
            'funding_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., National Science Foundation')
            }),
            'funding_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., 500000')
            }),
            'status': forms.Select(attrs={
                'class': 'form-control select2'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Enhanced field configuration for demo
        self.fields['title'].help_text = _(
            'Clear, descriptive title that will appear in reports and presentations'
        )
        self.fields['description'].help_text = _(
            'Comprehensive description including objectives, methodology, and expected impact'
        )
        self.fields['principal_investigator'].help_text = _(
            'Lead researcher responsible for the project'
        )
        self.fields['start_date'].help_text = _(
            'Project start date for timeline planning'
        )
        self.fields['funding_amount'].help_text = _(
            'Total project funding in dollars (optional)'
        )
        
        # Make certain fields required for better data quality
        self.fields['principal_investigator'].required = True
        self.fields['start_date'].required = True

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate date range
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(
                _('End date must be after start date.')
            )
        
        return cleaned_data


class StudyForm(forms.ModelForm):
    """
    Professional form for creating and editing studies within projects.
    Enhanced for Task 2.4 with project context and better validation.
    """
    
    class Meta:
        model = Study
        fields = (
            'title', 'description', 'study_type',
            'start_date', 'end_date', 'status', 'lead_researcher'
        )
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Study objectives, methods, and scope...')
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Urban Heat Island Analysis')
            }),
            'lead_researcher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Dr. Alex Johnson')
            }),
            'study_type': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control select2'
            })
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Enhanced help text for demo
        self.fields['title'].help_text = _(
            'Specific study name within the research project'
        )
        self.fields['study_type'].help_text = _(
            'Type of research study being conducted'
        )
        
        # Set project context if provided
        if project:
            self.project = project
            # Auto-populate lead researcher from project if not set
            if not self.instance.pk and not self.instance.lead_researcher:
                self.fields['lead_researcher'].initial = project.principal_investigator

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set project if provided during initialization
        if hasattr(self, 'project') and self.project:
            instance.project = self.project
            
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate date range
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(
                _('Study end date must be after start date.')
            )
        
        return cleaned_data


class DatasetForm(forms.ModelForm):
    """
    Professional form for creating and editing datasets within studies.
    Enhanced for Task 2.4 with document selection and advanced features.
    """
    
    # Document selection field using Mayan patterns
    documents = forms.ModelMultipleChoiceField(
        queryset=Document.objects.none(),
        required=False,
        widget=form_widgets.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-minimum-input-length': 2
        }),
        help_text=_('Select documents to associate with this dataset')
    )
    
    class Meta:
        model = Dataset
        fields = (
            'title', 'description', 'dataset_type', 'data_collector',
            'collection_start_date', 'collection_end_date', 'status',
            'is_anonymized', 'is_validated', 'analysis_software', 'sample_size'
        )
        widgets = {
            'collection_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'collection_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Dataset description, content, and methodology...')
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Temperature Sensor Data 2024')
            }),
            'data_collector': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Research Assistant Name')
            }),
            'analysis_software': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Python, R, SPSS')
            }),
            'sample_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., 1000')
            }),
            'dataset_type': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'is_anonymized': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_validated': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('study', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configure document queryset with proper permissions
        if user:
            # In a real implementation, this would respect ACL permissions
            self.fields['documents'].queryset = Document.valid.all()[:100]  # Limit for performance
        else:
            self.fields['documents'].queryset = Document.valid.all()[:50]
        
        # Enhanced help text for demo
        self.fields['title'].help_text = _(
            'Descriptive name for the dataset within the study'
        )
        self.fields['dataset_type'].help_text = _(
            'Type of data contained in this dataset'
        )
        self.fields['sample_size'].help_text = _(
            'Number of records, participants, or data points'
        )
        self.fields['is_anonymized'].help_text = _(
            'Check if personal identifiers have been removed'
        )
        self.fields['is_validated'].help_text = _(
            'Check if data quality has been verified'
        )
        
        # Set study context if provided
        if study:
            self.study = study
        
        # Pre-populate existing document relationships
        if self.instance and self.instance.pk:
            self.fields['documents'].initial = self.instance.documents.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set study if provided during initialization
        if hasattr(self, 'study') and self.study:
            instance.study = self.study
            
        if commit:
            instance.save()
            
            # Handle document relationships through DatasetDocument
            if 'documents' in self.cleaned_data:
                # Clear existing relationships
                DatasetDocument.objects.filter(dataset=instance).delete()
                
                # Create new relationships
                for document in self.cleaned_data['documents']:
                    DatasetDocument.objects.create(
                        dataset=instance,
                        document=document,
                        document_role='raw_data'  # Default role
                    )
        
        return instance

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('collection_start_date')
        end_date = cleaned_data.get('collection_end_date')
        
        # Validate collection date range
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(
                _('Collection end date must be after start date.')
            )
        
        # Validate sample size
        sample_size = cleaned_data.get('sample_size')
        if sample_size is not None and sample_size < 0:
            raise forms.ValidationError(
                _('Sample size must be a positive number.')
            )
        
        return cleaned_data


class DatasetDocumentForm(forms.ModelForm):
    """
    Form for managing document-dataset relationships with roles.
    Enhanced for Task 2.4 with better role management.
    """
    
    class Meta:
        model = DatasetDocument
        fields = ('document', 'document_role', 'notes', 'order')
        widgets = {
            'document': form_widgets.Select(attrs={
                'class': 'form-control select2'
            }),
            'document_role': form_widgets.Select(attrs={
                'class': 'form-control select2'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': _('Optional notes about this document in the dataset...')
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        dataset = kwargs.pop('dataset', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configure document queryset
        if user:
            self.fields['document'].queryset = Document.valid.all()
        else:
            self.fields['document'].queryset = Document.valid.all()[:100]
        
        # Set dataset context
        if dataset:
            self.dataset = dataset
        
        # Enhanced help text
        self.fields['document_role'].help_text = _(
            'Role of this document within the dataset'
        )
        self.fields['order'].help_text = _(
            'Display order (lower numbers appear first)'
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set dataset if provided
        if hasattr(self, 'dataset') and self.dataset:
            instance.dataset = self.dataset
            
        if commit:
            instance.save()
        return instance 