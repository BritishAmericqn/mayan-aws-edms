import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from mayan.apps.documents.models import Document
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave, EventManagerMethodAfter

from ..events import (
    event_shared_document_created, event_shared_document_accessed,
    event_shared_document_expired, event_shared_document_deleted
)

User = get_user_model()


class SharedDocumentManager(models.Manager):
    def create_shared_document(self, document, created_by, expiration_hours=24, label=None):
        """
        Create a new shared document with automatic expiration.
        """
        expiration_time = timezone.now() + timedelta(hours=expiration_hours)
        
        return self.create(
            document=document,
            created_by=created_by,
            expires_at=expiration_time,
            label=label or f"Shared: {document.label}"
        )
    
    def get_valid_shares(self):
        """
        Get all non-expired shared documents.
        """
        return self.filter(expires_at__gt=timezone.now())
    
    def cleanup_expired(self):
        """
        Remove expired shared documents.
        """
        expired_shares = self.filter(expires_at__lte=timezone.now())
        count = expired_shares.count()
        expired_shares.delete()
        return count


class SharedDocument(ExtraDataModelMixin, models.Model):
    """
    Model to track documents shared externally via pre-signed URLs.
    Integrates with Mayan's permission and event systems.
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='shared_instances',
        verbose_name=_('Document'),
        help_text=_('The document being shared externally')
    )
    
    # Unique identifier for the share (used in URLs)
    url_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name=_('URL Key'),
        help_text=_('Unique identifier for this shared document')
    )
    
    # Sharing metadata
    label = models.CharField(
        max_length=255,
        verbose_name=_('Share Label'),
        help_text=_('Descriptive label for this share')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_shared_documents',
        verbose_name=_('Created By'),
        help_text=_('User who created this share')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        help_text=_('When this share was created')
    )
    
    expires_at = models.DateTimeField(
        verbose_name=_('Expires At'),
        help_text=_('When this share will expire and become inaccessible')
    )
    
    # Access tracking for compliance
    access_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Access Count'),
        help_text=_('Number of times this share has been accessed')
    )
    
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Accessed At'),
        help_text=_('When this share was last accessed')
    )
    
    last_accessed_from_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Last Access IP'),
        help_text=_('IP address of last access for security tracking')
    )
    
    # Demo and configuration options
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
        help_text=_('Whether this share is currently active')
    )
    
    max_access_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Max Access Count'),
        help_text=_('Maximum number of times this share can be accessed (optional)')
    )
    
    objects = SharedDocumentManager()

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Shared Document')
        verbose_name_plural = _('Shared Documents')
        indexes = [
            models.Index(fields=['url_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['document', 'is_active']),
        ]

    def __str__(self):
        return f"{self.label} (expires: {self.expires_at})"

    @method_event(
        event_manager_class=EventManagerSave,
        created={'event': event_shared_document_created, 'target': 'self'}
    )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_shared_document_deleted,
        target='self'
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def get_absolute_url(self):
        """
        Get the URL for accessing this shared document.
        """
        return reverse('research:shared_document_access', kwargs={'url_key': self.url_key})

    def is_expired(self):
        """
        Check if this share has expired.
        """
        return timezone.now() > self.expires_at

    def is_access_allowed(self):
        """
        Check if access is still allowed (not expired, under access limit).
        """
        if not self.is_active or self.is_expired():
            return False
            
        if self.max_access_count and self.access_count >= self.max_access_count:
            return False
            
        return True

    def record_access(self, ip_address=None):
        """
        Record an access to this shared document for compliance tracking.
        """
        if not self.is_access_allowed():
            return False
            
        self.access_count += 1
        self.last_accessed_at = timezone.now()
        
        if ip_address:
            self.last_accessed_from_ip = ip_address
            
        self.save(update_fields=['access_count', 'last_accessed_at', 'last_accessed_from_ip'])
        
        # Fire access event for audit trail
        event_shared_document_accessed.commit(
            actor=None,  # External access
            action_object=self.document,
            target=self
        )
        
        return True

    def get_expiration_status(self):
        """
        Get human-readable expiration status for demo.
        """
        if self.is_expired():
            return {'status': 'expired', 'class': 'danger', 'text': _('Expired')}
        
        time_left = self.expires_at - timezone.now()
        
        if time_left.total_seconds() < 3600:  # Less than 1 hour
            return {'status': 'expiring', 'class': 'warning', 'text': _('Expiring Soon')}
        elif time_left.days < 1:  # Less than 1 day
            return {'status': 'active', 'class': 'info', 'text': _('Expires Today')}
        else:
            return {'status': 'active', 'class': 'success', 'text': _('Active')}

    def get_demo_info(self):
        """
        Get demo-friendly information for presentation.
        """
        return {
            'share_key': str(self.url_key)[:8] + '...',
            'document_name': self.document.label,
            'created_by': self.created_by.get_full_name() or self.created_by.username,
            'access_count': self.access_count,
            'expiration_status': self.get_expiration_status(),
            'time_until_expiry': self.expires_at - timezone.now(),
        } 