from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from mayan.apps.documents.models import Document
from .models import SharedDocument


class ShareDocumentForm(forms.ModelForm):
    """Main form for creating document shares with comprehensive options"""
    
    EXPIRATION_CHOICES = [
        (1, _('1 hour')),
        (24, _('1 day')),
        (168, _('1 week')),
        (720, _('1 month')),
        (0, _('Never expires')),
    ]
    
    expiration_hours = forms.ChoiceField(
        choices=EXPIRATION_CHOICES,
        initial=24,
        label=_('Link expires in'),
        help_text=_('How long the sharing link will remain valid')
    )
    
    max_access_count = forms.IntegerField(
        initial=10,
        min_value=1,
        max_value=1000,
        label=_('Maximum downloads'),
        help_text=_('Maximum number of times this document can be downloaded')
    )
    
    class Meta:
        model = SharedDocument
        fields = ['document', 'label', 'expiration_hours', 'max_access_count']
        widgets = {
            'document': forms.Select(attrs={'class': 'form-select'}),
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter a description for this share...')
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filter documents the user can access
        if user:
            # In a real implementation, filter by user permissions
            self.fields['document'].queryset = Document.objects.all()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set created_by
        if self.user:
            instance.created_by = self.user
        
        # Calculate expiration based on selected hours
        expiration_hours = int(self.cleaned_data['expiration_hours'])
        if expiration_hours > 0:
            instance.expires_at = timezone.now() + timedelta(hours=expiration_hours)
        else:
            # Never expires - set to far future
            instance.expires_at = timezone.now() + timedelta(days=3650)  # 10 years
        
        if commit:
            instance.save()
        return instance


class QuickShareForm(forms.Form):
    """Simplified form for quick sharing via modal"""
    
    document_id = forms.IntegerField(widget=forms.HiddenInput())
    expiration_hours = forms.ChoiceField(
        choices=ShareDocumentForm.EXPIRATION_CHOICES,
        initial=24,
        label=_('Expires in'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    max_access_count = forms.IntegerField(
        initial=5,
        min_value=1,
        max_value=100,
        label=_('Max downloads'),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, document=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.document = document
        self.user = user
        
        if document:
            self.fields['document_id'].initial = document.id
    
    def create_share(self):
        """Create a SharedDocument from form data"""
        if not self.is_valid():
            return None
        
        # Auto-generate label
        label = f"Quick share of {self.document.label}" if self.document else "Quick share"
        
        # Calculate expiration
        expiration_hours = int(self.cleaned_data['expiration_hours'])
        if expiration_hours > 0:
            expires_at = timezone.now() + timedelta(hours=expiration_hours)
        else:
            expires_at = timezone.now() + timedelta(days=3650)
        
        # Create shared document
        shared_doc = SharedDocument.objects.create(
            document=self.document,
            label=label,
            created_by=self.user,
            expires_at=expires_at,
            max_access_count=self.cleaned_data['max_access_count']
        )
        
        return shared_doc 