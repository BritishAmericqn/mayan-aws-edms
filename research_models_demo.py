"""
Simplified research models for standalone demo.
Shows the research hierarchy without full Mayan dependencies.
"""

from django.db import models
from django.contrib import admin


class Project(models.Model):
    """Research Project model for demo."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    principal_investigator = models.CharField(max_length=255)
    institution = models.CharField(max_length=255, blank=True)
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    funding_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)
        
    def __str__(self):
        return self.title


class Study(models.Model):
    """Research Study model for demo."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='studies')
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    study_type = models.CharField(max_length=50, blank=True)
    methodology = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'Studies'
        
    def __str__(self):
        return f"{self.title} ({self.project.title})"


class Dataset(models.Model):
    """Research Dataset model for demo."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='datasets')
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    DATA_TYPE_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('image', 'Image'),
        ('other', 'Other'),
    ]
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default='csv')
    size_bytes = models.PositiveIntegerField(default=0)
    
    ANALYSIS_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    analysis_status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, default='pending')
    analysis_results = models.JSONField(null=True, blank=True)
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)
        
    def __str__(self):
        return f"{self.title} ({self.study.title})"


# Admin configuration for demo
class StudyInline(admin.StackedInline):
    model = Study
    extra = 0
    fields = ('title', 'description', 'status', 'study_type')


class DatasetInline(admin.StackedInline):
    model = Dataset
    extra = 0
    fields = ('title', 'description', 'status', 'data_type', 'analysis_status')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'principal_investigator', 'institution', 'status', 'start_date')
    list_filter = ('status', 'institution')
    search_fields = ('title', 'principal_investigator', 'institution')
    date_hierarchy = 'start_date'
    inlines = (StudyInline,)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Research Details', {
            'fields': ('principal_investigator', 'institution', 'status')
        }),
        ('Timeline & Funding', {
            'fields': ('start_date', 'end_date', 'funding_amount')
        }),
    )


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'study_type', 'start_date')
    list_filter = ('status', 'study_type', 'project')
    search_fields = ('title', 'description', 'project__title')
    inlines = (DatasetInline,)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('title', 'study', 'status', 'data_type', 'analysis_status', 'size_bytes')
    list_filter = ('status', 'data_type', 'analysis_status')
    search_fields = ('title', 'description', 'study__title') 