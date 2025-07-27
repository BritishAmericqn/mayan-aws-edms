from django import forms
from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.models import Document
from mayan.apps.forms import form_fields, form_widgets

from .models import Dataset, Project, Study, DatasetDocument
from .reports.models import ReportTemplate


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

# Tasks 3.2-3.3: Enhanced sharing permissions - MOVED TO permissions.py
# Import permissions instead of defining them here
from .permissions import (
    permission_shared_document_create,
    permission_shared_document_view, 
    permission_shared_document_edit,
    permission_shared_document_delete,
    permission_compliance_dashboard_view,
    permission_compliance_report_create,
    permission_audit_trail_access,
    permission_report_create,
    permission_report_view,
    permission_report_download,
    permission_report_delete
)

# Task 3.6: PDF Report Generation Forms
class ReportRequestForm(forms.Form):
    """
    Form for requesting PDF report generation.
    Task 3.6: Professional report request interface.
    """
    
    REPORT_TYPE_CHOICES = [
        ('compliance', _('Compliance Report - Security and audit analysis')),
        ('research_summary', _('Research Summary - Project overview and statistics')),
        ('audit_trail', _('Audit Trail - Detailed event history')),
        ('security_analysis', _('Security Analysis - Access and sharing metrics')),
    ]
    
    TIME_RANGE_CHOICES = [
        ('7', _('Last 7 days')),
        ('30', _('Last 30 days')),
        ('90', _('Last 90 days')),
        ('365', _('Last year')),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Report Type'),
        help_text=_('Select the type of report to generate')
    )
    
    title = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Auto-generated if empty')}),
        label=_('Report Title'),
        help_text=_('Custom title for the report (optional)')
    )
    
    time_range_days = forms.ChoiceField(
        choices=TIME_RANGE_CHOICES,
        initial='30',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Time Range'),
        help_text=_('Period to include in the report')
    )
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Specific Project'),
        help_text=_('Include only this project (for research summaries)')
    )
    
    include_charts = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Include Charts'),
        help_text=_('Add visual charts and graphs to the report')
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # If a specific project is provided, filter and set default
        if self.project:
            self.fields['project'].initial = self.project
            self.fields['project'].widget.attrs['disabled'] = True
        
        # Filter projects by user permissions if needed
        if self.user and hasattr(self.user, 'accessible_projects'):
            self.fields['project'].queryset = self.user.accessible_projects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get('report_type')
        project = cleaned_data.get('project')
        
        # Validate project requirement for research summaries
        if report_type == 'research_summary' and not project:
            raise forms.ValidationError(_('A project must be selected for research summary reports.'))
        
        return cleaned_data
    
    def get_parameters(self):
        """Get parameters dict for report generation."""
        params = {
            'time_range_days': int(self.cleaned_data['time_range_days']),
            'include_charts': self.cleaned_data['include_charts'],
        }
        
        if self.cleaned_data.get('project'):
            params['project_id'] = self.cleaned_data['project'].id
        
        return params


class ReportTemplateForm(forms.ModelForm):
    """
    Form for creating reusable report templates.
    Task 3.6: Template management for repeated report generation.
    """
    
    class Meta:
        model = ReportTemplate
        fields = ['name', 'report_type', 'description', 'default_parameters', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'default_parameters': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['default_parameters'].help_text = _('JSON format: {"time_range_days": 30, "project_id": 1}')
    
    def save(self, commit=True):
        template = super().save(commit=False)
        if self.user:
            template.created_by = self.user
        if commit:
            template.save()
        return template 