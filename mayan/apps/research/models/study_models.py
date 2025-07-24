from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from ..events import (
    event_study_created, event_study_edited, event_study_deleted
)
from .project_models import Project


class Study(ExtraDataModelMixin, models.Model):
    """
    Research Study model for organizing datasets within a project.
    Follows the research hierarchy: Project → Study → Dataset → Document
    """
    
    # Relationship to parent project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='studies',
        help_text=_('Project this study belongs to'),
        verbose_name=_('Project')
    )
    
    # Core study information
    title = models.CharField(
        max_length=255,
        help_text=_('Title of the research study'),
        verbose_name=_('Title')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Detailed description of the research study'),
        verbose_name=_('Description')
    )
    
    # Study metadata
    lead_researcher = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Lead researcher for this study'),
        verbose_name=_('Lead Researcher')
    )
    
    # Study type/methodology
    STUDY_TYPE_CHOICES = [
        ('observational', _('Observational')),
        ('experimental', _('Experimental')),
        ('survey', _('Survey')),
        ('case_study', _('Case Study')),
        ('longitudinal', _('Longitudinal')),
        ('cross_sectional', _('Cross-sectional')),
        ('meta_analysis', _('Meta-analysis')),
        ('other', _('Other')),
    ]
    
    study_type = models.CharField(
        max_length=20,
        choices=STUDY_TYPE_CHOICES,
        default='observational',
        help_text=_('Type of research study'),
        verbose_name=_('Study Type')
    )
    
    # Study timeline
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Study start date'),
        verbose_name=_('Start Date')
    )
    
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Study end date'),
        verbose_name=_('End Date')
    )
    
    # Study status
    STATUS_CHOICES = [
        ('design', _('Design Phase')),
        ('data_collection', _('Data Collection')),
        ('analysis', _('Analysis')),
        ('completed', _('Completed')),
        ('on_hold', _('On Hold')),
        ('cancelled', _('Cancelled')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='design',
        help_text=_('Current status of the study'),
        verbose_name=_('Status')
    )
    
    # Participant information (for demo purposes)
    target_sample_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Target number of participants/samples'),
        verbose_name=_('Target Sample Size')
    )
    
    current_sample_size = models.PositiveIntegerField(
        default=0,
        help_text=_('Current number of participants/samples'),
        verbose_name=_('Current Sample Size')
    )
    
    # Research ethics
    ethics_approval_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Ethics committee approval number'),
        verbose_name=_('Ethics Approval Number')
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
        ordering = ('project__title', 'title')
        verbose_name = _('Study')
        verbose_name_plural = _('Studies')
        unique_together = ['project', 'title']  # Unique within project
        
    def __str__(self):
        return f"{self.project.title} - {self.title}"
        
    def get_absolute_url(self):
        """Returns the URL for this study (for future web interface)"""
        return reverse('research:study_detail', kwargs={'pk': self.pk})
        
    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'project',
            'event': event_study_created,
            'target': 'self'
        },
        edited={
            'event': event_study_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Fire delete event
        self._event_actor = getattr(self, '_event_actor', None)
        
        # Store project reference for event
        project = self.project
        
        result = super().delete(*args, **kwargs)
        
        # Event will be fired by the event system
        return result
        
    @property
    def datasets_count(self):
        """Returns the number of datasets in this study"""
        return self.datasets.count()
        
    @property
    def completion_percentage(self):
        """Returns the completion percentage based on sample size"""
        if self.target_sample_size and self.target_sample_size > 0:
            percentage = (self.current_sample_size / self.target_sample_size) * 100
            return min(percentage, 100)  # Cap at 100%
        return 0
        
    @property
    def is_data_collection_active(self):
        """Returns True if the study is in data collection phase"""
        return self.status == 'data_collection' 