from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Project, Study, Dataset, DatasetDocument


class StudyInline(admin.StackedInline):
    model = Study
    extra = 0
    classes = ('collapse-open',)
    fields = ('title', 'description', 'status', 'start_date', 'end_date')
    readonly_fields = ('datetime_created', 'datetime_modified')


class DatasetInline(admin.StackedInline):
    model = Dataset
    extra = 0
    classes = ('collapse-open',)
    fields = ('title', 'description', 'status', 'data_type')
    readonly_fields = ('datetime_created', 'datetime_modified')


class DatasetDocumentInline(admin.TabularInline):
    model = DatasetDocument
    extra = 1
    fields = ('document', 'role', 'order')
    autocomplete_fields = ('document',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'principal_investigator', 'institution', 
        'status', 'start_date', 'studies_count', 'datetime_created'
    )
    list_filter = ('status', 'institution', 'start_date')
    search_fields = ('title', 'principal_investigator', 'institution', 'description')
    date_hierarchy = 'start_date'
    readonly_fields = ('datetime_created', 'datetime_modified', 'studies_count', 'datasets_count')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description')
        }),
        (_('Research Details'), {
            'fields': ('principal_investigator', 'institution', 'status')
        }),
        (_('Timeline'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Funding'), {
            'fields': ('funding_source', 'funding_amount'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('studies_count', 'datasets_count'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('datetime_created', 'datetime_modified'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = (StudyInline,)
    
    def studies_count(self, obj):
        return obj.studies.count()
    studies_count.short_description = _('Studies')
    
    def datasets_count(self, obj):
        return sum(study.datasets.count() for study in obj.studies.all())
    datasets_count.short_description = _('Datasets')


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'project', 'status', 'start_date', 
        'datasets_count', 'datetime_created'
    )
    list_filter = ('status', 'project', 'start_date')
    search_fields = ('title', 'description', 'project__title')
    date_hierarchy = 'start_date'
    readonly_fields = ('datetime_created', 'datetime_modified', 'datasets_count')
    autocomplete_fields = ('project',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description', 'project')
        }),
        (_('Study Details'), {
            'fields': ('status', 'study_type', 'methodology')
        }),
        (_('Timeline'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Statistics'), {
            'fields': ('datasets_count',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('datetime_created', 'datetime_modified'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = (DatasetInline,)
    
    def datasets_count(self, obj):
        return obj.datasets.count()
    datasets_count.short_description = _('Datasets')


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'study', 'status', 'data_type', 
        'document_count', 'datetime_created'
    )
    list_filter = ('status', 'data_type', 'study__project')
    search_fields = ('title', 'description', 'study__title', 'study__project__title')
    date_hierarchy = 'datetime_created'
    readonly_fields = ('datetime_created', 'datetime_modified', 'document_count')
    autocomplete_fields = ('study',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description', 'study')
        }),
        (_('Dataset Details'), {
            'fields': ('status', 'data_type', 'format', 'size_bytes')
        }),
        (_('Analysis'), {
            'fields': ('analysis_status', 'analysis_results'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('document_count',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('datetime_created', 'datetime_modified'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = (DatasetDocumentInline,)
    
    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = _('Documents')


@admin.register(DatasetDocument)
class DatasetDocumentAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'document', 'role', 'order', 'datetime_added')
    list_filter = ('role', 'dataset__study__project')
    search_fields = ('dataset__title', 'document__label')
    date_hierarchy = 'datetime_added'
    readonly_fields = ('datetime_added',)
    autocomplete_fields = ('dataset', 'document')
    
    fieldsets = (
        (_('Relationship'), {
            'fields': ('dataset', 'document')
        }),
        (_('Details'), {
            'fields': ('role', 'order', 'notes')
        }),
        (_('Metadata'), {
            'fields': ('datetime_added',)
        }),
    ) 