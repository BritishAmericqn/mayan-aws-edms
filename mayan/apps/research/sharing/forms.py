from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from mayan.apps.documents.models import Document
from mayan.apps.forms import form_fields, form_widgets

from .models import SharedDocument


class ShareDocumentForm(forms.ModelForm):
    """
    Professional form for creating secure document shares.
    Task 3.2: Sharing Forms & Views with demo-optimized UX.
    """
    
    # Expiration options for demo (1hr, 1day, 1week)
    EXPIRATION_CHOICES = (
        (1, _('1 Hour')),
        (24, _('1 Day')),
        (168, _('1 Week')),
        (720, _('1 Month')),  # For extended demo scenarios
    )
    
    expiration_hours = forms.ChoiceField(
        choices=EXPIRATION_CHOICES,
        initial=24,  # Default to 1 day
        widget=forms.Select(attrs={
            'class': 'form-control select2'
        }),
        label=_('Expires In'),
        help_text=_('How long the sharing link will remain active')
    )
    
    class Meta:
        model = SharedDocument
        fields = ('label', 'expiration_hours')
        widgets = {
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Shared for Review - Dr. Smith')
            })
        }

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Enhanced help text for demo
        self.fields['label'].help_text = _(
            'Descriptive label to identify this share (visible in audit logs)'
        )
        
        # Auto-populate label if document is provided
        if self.document and not self.initial.get('label'):
            self.fields['label'].initial = f'Shared: {self.document.label}'

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate document is provided
        if not self.document:
            raise forms.ValidationError(_('Document is required for sharing'))
        
        # Validate user permissions (would be more complex in production)
        if not self.user:
            raise forms.ValidationError(_('User is required for sharing'))
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set required fields
        instance.document = self.document
        instance.created_by = self.user
        
        # Calculate expiration time
        expiration_hours = int(self.cleaned_data['expiration_hours'])
        instance.expires_at = timezone.now() + timedelta(hours=expiration_hours)
        
        if commit:
            instance.save()
            
        return instance


class QuickShareForm(forms.Form):
    """
    Quick sharing form for modal popup - minimal fields for fast demo.
    Task 3.2: Modal integration with copy-to-clipboard functionality.
    """
    
    QUICK_EXPIRATION_CHOICES = (
        (1, _('1 Hour - Urgent')),
        (24, _('1 Day - Standard')),
        (168, _('1 Week - Extended')),
    )
    
    expiration_hours = forms.ChoiceField(
        choices=QUICK_EXPIRATION_CHOICES,
        initial=24,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Share Duration')
    )
    
    send_notification = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Log Access (Compliance)'),
        help_text=_('Track when the shared document is accessed')
    )

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def create_share(self):
        """Create the shared document and return URL info."""
        if not self.is_valid():
            return None
            
        # Create SharedDocument
        expiration_hours = int(self.cleaned_data['expiration_hours'])
        expires_at = timezone.now() + timedelta(hours=expiration_hours)
        
        shared_doc = SharedDocument.objects.create(
            document=self.document,
            created_by=self.user,
            label=f'Quick Share: {self.document.label}',
            expires_at=expires_at
        )
        
        # Generate URL using the generator
        from .generators import PreSignedURLGenerator
        generator = PreSignedURLGenerator()
        
        url_info = generator.generate_url(
            document=self.document,
            expiration_hours=expiration_hours,
            shared_document=shared_doc
        )
        
        return {
            'shared_document': shared_doc,
            'url_info': url_info,
            'demo_ready': True,
            'compliance_tracking': self.cleaned_data['send_notification']
        } 