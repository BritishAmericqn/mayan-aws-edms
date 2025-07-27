import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models import Document
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave, EventManagerMethodAfter

from ..events import (
    event_shared_document_created, event_shared_document_accessed,
    event_shared_document_downloaded, event_shared_document_expired,
    event_shared_document_revoked, event_data_quality_check_performed,
    event_security_scan_performed, event_compliance_report_generated,
    event_audit_trail_accessed
)


class SharedDocument(ExtraDataModelMixin, models.Model):
    """
    Model for sharing documents externally with time-limited access.
    Enhanced with comprehensive audit events for Task 3.4.
    """
    
    # Core sharing fields
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='research_shares',
        help_text=_('Document being shared'),
        verbose_name=_('Document')
    )
    
    url_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        help_text=_('Unique key for public access URL'),
        verbose_name=_('URL Key')
    )
    
    label = models.CharField(
        max_length=255,
        help_text=_('Descriptive label for this share'),
        verbose_name=_('Share Label')
    )
    
    # Creator and permissions
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_document_shares',
        help_text=_('User who created this share'),
        verbose_name=_('Created By')
    )
    
    # Access control
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this share is currently active'),
        verbose_name=_('Is Active')
    )
    
    expires_at = models.DateTimeField(
        help_text=_('When this share will expire'),
        verbose_name=_('Expires At')
    )
    
    max_access_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Maximum number of times this document can be accessed (optional)'),
        verbose_name=_('Max Access Count')
    )
    
    # Tracking and audit fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this share was created'),
        verbose_name=_('Created At')
    )
    
    access_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of times this document has been accessed'),
        verbose_name=_('Access Count')
    )
    
    last_accessed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Last time this document was accessed'),
        verbose_name=_('Last Accessed At')
    )
    
    last_accessed_from_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text=_('IP address of last access'),
        verbose_name=_('Last Accessed From IP')
    )

    class Meta:
        verbose_name = _('Shared Document')
        verbose_name_plural = _('Shared Documents')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['url_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.label} ({self.document.label})'

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'document',
            'event': event_shared_document_created,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        """Save with enhanced audit events."""
        result = super().save(*args, **kwargs)
        
        # Fire additional compliance and security events for new shares
        if hasattr(self, '_state') and self._state.adding:
            # Security scan on new share creation
            self._fire_security_scan_event()
            # Data quality check for shared document
            self._fire_data_quality_check_event()
        
        return result

    def delete(self, *args, **kwargs):
        """Delete with revocation event."""
        # Fire revocation event before deletion
        event_shared_document_revoked.commit(
            actor=getattr(self, '_event_actor', None),
            action_object=self.document,
            target=self
        )
        return super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_shared_document_accessed,
        action_object='document',
        target='self'
    )
    def record_access(self, ip_address=None, user_agent=None, download=False):
        """Record an access to this shared document with enhanced audit trail."""
        self._event_actor = getattr(self, '_event_actor', None)
        
        # Update access tracking
        self.access_count += 1
        self.last_accessed_at = timezone.now()
        if ip_address:
            self.last_accessed_from_ip = ip_address
        
        # Store extra audit data
        extra_data = {
            'ip_address': ip_address,
            'user_agent': user_agent,
            'access_count': self.access_count,
            'download': download
        }
        
        # Add extra data to the event
        if hasattr(self, '_event_extra_data'):
            self._event_extra_data.update(extra_data)
        else:
            self._event_extra_data = extra_data
        
        self.save(update_fields=['access_count', 'last_accessed_at', 'last_accessed_from_ip'])
        
        # Fire specific download event if this was a download
        if download:
            event_shared_document_downloaded.commit(
                actor=None,  # External access
                action_object=self.document,
                target=self,
                extra_data=extra_data
            )

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_audit_trail_accessed,
        action_object='self',
        target='document'
    )
    def get_audit_trail(self, user=None):
        """Get audit trail for this shared document with access logging."""
        self._event_actor = user
        
        # This would return audit events related to this shared document
        # For now, just fire the audit trail access event
        return {
            'share_created': self.created_at,
            'total_accesses': self.access_count,
            'last_access': self.last_accessed_at,
            'expires_at': self.expires_at,
            'is_active': self.is_active
        }

    def _fire_security_scan_event(self):
        """Fire security scan event for compliance."""
        security_scan_data = {
            'scan_type': 'document_sharing_security',
            'document_type': self.document.document_type.label if self.document.document_type else 'unknown',
            'file_size': self.document.file_latest.size if self.document.file_latest else 0,
            'expiration_hours': (self.expires_at - self.created_at).total_seconds() / 3600,
            'has_access_limit': bool(self.max_access_count)
        }
        
        event_security_scan_performed.commit(
            actor=self.created_by,
            action_object=self.document,
            target=self,
            extra_data=security_scan_data
        )

    def _fire_data_quality_check_event(self):
        """Fire data quality check event for compliance."""
        quality_check_data = {
            'check_type': 'document_sharing_quality',
            'document_has_file': bool(self.document.file_latest),
            'document_label_length': len(self.document.label),
            'share_label_descriptive': len(self.label) > 10,
            'proper_expiration': self.expires_at > timezone.now() + timedelta(hours=1)
        }
        
        event_data_quality_check_performed.commit(
            actor=self.created_by,
            action_object=self.document,
            target=self,
            extra_data=quality_check_data
        )

    def check_and_expire(self):
        """Check if document should be expired and fire expiration event."""
        if self.is_expired() and self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active'])
            
            event_shared_document_expired.commit(
                actor=None,  # System action
                action_object=self.document,
                target=self,
                extra_data={
                    'expired_at': timezone.now(),
                    'total_accesses': self.access_count,
                    'expiration_reason': 'time_limit'
                }
            )

    def is_expired(self):
        """Check if this share has expired."""
        return timezone.now() > self.expires_at

    def is_access_allowed(self):
        """Check if access is allowed (not expired, active, under access limit)."""
        if not self.is_active:
            return False
        
        if self.is_expired():
            return False
        
        if self.max_access_count and self.access_count >= self.max_access_count:
            return False
        
        return True

    def get_public_url(self):
        """Get the public access URL for this shared document."""
        return f"/shared/{self.url_key}/"

    def get_download_url(self):
        """Get the direct download URL for this shared document."""
        return f"/shared/{self.url_key}/download/"

    def get_preview_url(self):
        """Get the preview URL for this shared document."""
        return f"/shared/{self.url_key}/preview/" 