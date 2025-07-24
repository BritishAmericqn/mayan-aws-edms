from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from ..events import (
    event_project_created, event_project_edited, event_project_deleted
)


class Project(ExtraDataModelMixin, models.Model):
    """
    Research Project model for organizing studies and datasets.
    Follows the research hierarchy: Project → Study → Dataset → Document
    """
    
    # Core project information
    title = models.CharField(
        max_length=255,
        help_text=_('Title of the research project'),
        verbose_name=_('Title')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Detailed description of the research project'),
        verbose_name=_('Description')
    )
    
    # Research metadata
    principal_investigator = models.CharField(
        max_length=255,
        help_text=_('Name of the principal investigator'),
        verbose_name=_('Principal Investigator')
    )
    
    institution = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Research institution or organization'),
        verbose_name=_('Institution')
    )
    
    # Project timeline
    start_date = models.DateField(
        help_text=_('Project start date'),
        verbose_name=_('Start Date')
    )
    
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Project end date (optional)'),
        verbose_name=_('End Date')
    )
    
    # Project status
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('active', _('Active')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        help_text=_('Current status of the project'),
        verbose_name=_('Status')
    )
    
    # Funding information (for demo purposes)
    funding_source = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Source of project funding'),
        verbose_name=_('Funding Source')
    )
    
    funding_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Total funding amount'),
        verbose_name=_('Funding Amount')
    )
    
    # Timestamps (following Mayan pattern)
    datetime_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created')
    )
    
    datetime_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Modified')
    )

    class Meta:
        ordering = ('title',)
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        """Returns the URL for this project (for future web interface)"""
        return reverse('research:project_detail', kwargs={'pk': self.pk})
        
    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_project_created,
            'target': 'self'
        },
        edited={
            'event': event_project_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Fire delete event
        self._event_actor = getattr(self, '_event_actor', None)
        
        # Store project info before deletion
        project_title = self.title
        
        result = super().delete(*args, **kwargs)
        
        # Event will be fired by the event system
        return result
        
    @property
    def studies_count(self):
        """Returns the number of studies in this project"""
        return self.studies.count()
        
    @property
    def datasets_count(self):
        """Returns the total number of datasets across all studies"""
        return sum(study.datasets.count() for study in self.studies.all())
        
    @property
    def is_active(self):
        """Returns True if the project is currently active"""
        return self.status == 'active' 