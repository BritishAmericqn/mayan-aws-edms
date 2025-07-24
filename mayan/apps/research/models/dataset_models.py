from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models import Document
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import (
    EventManagerMethodAfter, EventManagerSave
)

from ..events import (
    event_dataset_created, event_dataset_edited, event_dataset_deleted,
    event_dataset_document_added, event_dataset_document_removed
)
from .study_models import Study


class Dataset(ExtraDataModelMixin, models.Model):
    """
    Research Dataset model for organizing documents within a study.
    Follows the research hierarchy: Project → Study → Dataset → Document
    """
    
    # Relationship to parent study
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='datasets',
        help_text=_('Study this dataset belongs to'),
        verbose_name=_('Study')
    )
    
    # Core dataset information
    title = models.CharField(
        max_length=255,
        help_text=_('Title of the research dataset'),
        verbose_name=_('Title')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Detailed description of the dataset'),
        verbose_name=_('Description')
    )
    
    # Dataset metadata
    data_collector = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Person responsible for data collection'),
        verbose_name=_('Data Collector')
    )
    
    # Dataset type/format
    DATASET_TYPE_CHOICES = [
        ('quantitative', _('Quantitative Data')),
        ('qualitative', _('Qualitative Data')),
        ('mixed_methods', _('Mixed Methods')),
        ('images', _('Images/Visual Data')),
        ('audio', _('Audio Data')),
        ('video', _('Video Data')),
        ('documents', _('Text Documents')),
        ('spreadsheet', _('Spreadsheet/CSV')),
        ('database', _('Database Export')),
        ('other', _('Other')),
    ]
    
    dataset_type = models.CharField(
        max_length=20,
        choices=DATASET_TYPE_CHOICES,
        default='quantitative',
        help_text=_('Type of data in this dataset'),
        verbose_name=_('Dataset Type')
    )
    
    # Data collection timeline
    collection_start_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('When data collection started'),
        verbose_name=_('Collection Start Date')
    )
    
    collection_end_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('When data collection ended'),
        verbose_name=_('Collection End Date')
    )
    
    # Dataset status
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('collecting', _('Collecting Data')),
        ('processing', _('Processing')),
        ('analysis_ready', _('Ready for Analysis')),
        ('analyzed', _('Analyzed')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        help_text=_('Current status of the dataset'),
        verbose_name=_('Status')
    )
    
    # Data quality and processing
    is_anonymized = models.BooleanField(
        default=False,
        help_text=_('Whether the data has been anonymized'),
        verbose_name=_('Anonymized')
    )
    
    is_validated = models.BooleanField(
        default=False,
        help_text=_('Whether the data has been validated'),
        verbose_name=_('Validated')
    )
    
    # Analysis metadata (for demo features)
    analysis_software = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Software used for analysis (e.g., R, Python, SPSS)'),
        verbose_name=_('Analysis Software')
    )
    
    sample_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Number of records/participants in dataset'),
        verbose_name=_('Sample Size')
    )
    
    # Many-to-many relationship with documents
    documents = models.ManyToManyField(
        Document,
        through='DatasetDocument',
        related_name='research_datasets',
        blank=True,
        verbose_name=_('Documents')
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
        ordering = ('study__project__title', 'study__title', 'title')
        verbose_name = _('Dataset')
        verbose_name_plural = _('Datasets')
        unique_together = ['study', 'title']  # Unique within study
        
    def __str__(self):
        return f"{self.study.project.title} - {self.study.title} - {self.title}"
        
    def get_absolute_url(self):
        """Returns the URL for this dataset (for future web interface)"""
        return reverse('research:dataset_detail', kwargs={'pk': self.pk})
        
    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'action_object': 'study',
            'event': event_dataset_created,
            'target': 'self'
        },
        edited={
            'event': event_dataset_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Fire delete event
        self._event_actor = getattr(self, '_event_actor', None)
        
        # Store study reference for event
        study = self.study
        
        result = super().delete(*args, **kwargs)
        
        # Event will be fired by the event system
        return result
        
    @method_event(
        action_object='self',
        event=event_dataset_document_added,
        event_manager_class=EventManagerMethodAfter
    )
    def document_add(self, document, document_role='raw_data', notes='', user=None):
        """Add a document to this dataset with role and metadata"""
        self._event_actor = user
        self._event_target = document
        
        # Create the DatasetDocument relationship
        dataset_doc, created = DatasetDocument.objects.get_or_create(
            dataset=self,
            document=document,
            defaults={
                'document_role': document_role,
                'notes': notes
            }
        )
        return dataset_doc
        
    @method_event(
        action_object='self',
        event=event_dataset_document_removed,
        event_manager_class=EventManagerMethodAfter
    )
    def document_remove(self, document, user=None):
        """Remove a document from this dataset"""
        self._event_actor = user
        self._event_target = document
        
        # Remove the DatasetDocument relationship
        DatasetDocument.objects.filter(
            dataset=self,
            document=document
        ).delete()
        
    @property
    def documents_count(self):
        """Returns the number of documents in this dataset"""
        return self.documents.count()
        
    @property
    def project(self):
        """Returns the project this dataset belongs to"""
        return self.study.project
        
    @property
    def is_ready_for_analysis(self):
        """Returns True if the dataset is ready for analysis"""
        return self.status == 'analysis_ready'
        
    @property
    def has_analysis_files(self):
        """Returns True if the dataset has documents marked as analysis files"""
        return self.datasetdocument_set.filter(document_role='analysis').exists()


class DatasetDocument(models.Model):
    """
    Through model for the many-to-many relationship between Dataset and Document.
    Allows additional metadata about the document's role in the dataset.
    """
    
    # Relationships
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        verbose_name=_('Dataset')
    )
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name=_('Document')
    )
    
    # Document role in the dataset
    DOCUMENT_ROLE_CHOICES = [
        ('raw_data', _('Raw Data')),
        ('processed_data', _('Processed Data')),
        ('analysis', _('Analysis Output')),
        ('visualization', _('Visualization')),
        ('documentation', _('Documentation')),
        ('metadata', _('Metadata')),
        ('protocol', _('Research Protocol')),
        ('consent_form', _('Consent Form')),
        ('other', _('Other')),
    ]
    
    document_role = models.CharField(
        max_length=20,
        choices=DOCUMENT_ROLE_CHOICES,
        default='raw_data',
        help_text=_('Role of this document in the dataset'),
        verbose_name=_('Document Role')
    )
    
    # Additional metadata
    notes = models.TextField(
        blank=True,
        help_text=_('Additional notes about this document in the dataset'),
        verbose_name=_('Notes')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text=_('Display order within the dataset'),
        verbose_name=_('Order')
    )
    
    # Timestamps
    datetime_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Added to Dataset')
    )

    class Meta:
        ordering = ('order', 'datetime_added')
        verbose_name = _('Dataset Document')
        verbose_name_plural = _('Dataset Documents')
        unique_together = ['dataset', 'document']  # Each document can only be in a dataset once
        
    def __str__(self):
        return f"{self.dataset.title} - {self.document.label} ({self.get_document_role_display()})" 