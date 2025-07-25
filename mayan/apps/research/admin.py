from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import messages
import json

from mayan.apps.documents.admin import DocumentAdmin
from .models import Project, Study, Dataset, DatasetDocument

# Add search fields to DocumentAdmin for autocomplete
if not hasattr(DocumentAdmin, 'search_fields') or not DocumentAdmin.search_fields:
    DocumentAdmin.search_fields = ('label', 'description')


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
    fields = ('title', 'description', 'status', 'dataset_type')
    readonly_fields = ('datetime_created', 'datetime_modified')


class DatasetDocumentInline(admin.TabularInline):
    model = DatasetDocument
    extra = 1
    fields = ('document', 'document_role', 'order', 'notes')
    autocomplete_fields = ('document',)
    verbose_name = "Associated Document"
    verbose_name_plural = "📂 Dataset Documents (Associate Existing Documents)"
    
    def get_help_text(self):
        return (
            "To add documents to this dataset:\n"
            "1. First upload documents via 'Documents' → 'Add Document'\n"
            "2. Then select those documents here to associate them with this dataset"
        )
    
    class Meta:
        help_text = "Associate existing Mayan documents with this dataset"


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
            'fields': ('status', 'study_type')
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
        'title', 'study', 'status', 'dataset_type', 
        'document_count', 'analysis_status_display', 'datetime_created'
    )
    list_filter = ('status', 'dataset_type', 'study__project')
    search_fields = ('title', 'description', 'study__title', 'study__project__title')
    date_hierarchy = 'datetime_created'
    readonly_fields = ('datetime_created', 'datetime_modified', 'document_count', 'live_analysis_display')
    autocomplete_fields = ('study',)
    
    # Safe admin actions for analysis
    actions = ['run_enhanced_analysis', 'test_analysis_system', 'mark_as_analyzed']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description', 'study'),
            'description': 'Basic dataset information and research context.'
        }),
        (_('Dataset Details'), {
            'fields': ('status', 'dataset_type', 'data_collector', 'sample_size')
        }),
        (_('Data Collection'), {
            'fields': ('collection_start_date', 'collection_end_date'),
            'classes': ('collapse',)
        }),
        (_('Data Quality'), {
            'fields': ('is_anonymized', 'is_validated'),
            'classes': ('collapse',)
        }),
        (_('Analysis'), {
            'fields': ('analysis_software', 'live_analysis_display'),
            'classes': ('collapse',),
            'description': 'Enhanced Task 2.2 analysis results appear here after running analysis.'
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
    
    def analysis_status_display(self, obj):
        """Enhanced analysis status display"""
        if obj.status == 'analysis_ready':
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Ready for Enhanced Analysis</span>'
            )
        elif obj.status == 'analyzed':
            return format_html(
                '<span style="color: blue; font-weight: bold;">📊 Analysis Complete - Use "Run Enhanced Analysis" to see details</span>'
            )
        elif obj.status == 'processing':
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚙️ Processing</span>'
            )
        else:
            return format_html(
                '<span style="color: gray;">⏳ {}</span>', 
                obj.get_status_display()
            )
    analysis_status_display.short_description = _('Analysis Status')
    
    def live_analysis_display(self, obj):
        """Display REAL analysis results from actual CSV data"""
        # Try to run real analysis on the fly
        try:
            from .analysis.real_analyzer import RealCSVAnalyzer
            
            # Get documents linked to this dataset
            dataset_documents = obj.documents.filter(
                datasetdocument__document_role='raw_data'
            )
            
            if dataset_documents.exists():
                doc = dataset_documents.first()
                analyzer = RealCSVAnalyzer()
                results = analyzer.analyze_document(doc)
                
                if results.get('status') != 'error':
                    return self._display_real_analysis_results(results)
                else:
                    return format_html(
                        '<div style="color: #dc3545; padding: 15px; border: 1px solid #dc3545; border-radius: 5px;">'
                        '<h4>❌ Analysis Error</h4>'
                        '<p><strong>Error:</strong> {message}</p>'
                        '<p><strong>Suggestion:</strong> {suggestion}</p>'
                        '</div>',
                        message=results.get('message', 'Unknown error'),
                        suggestion=results.get('suggestion', 'Try again')
                    )
            
            # If no documents, show helpful message
            return format_html(
                '<div style="color: #856404; padding: 15px; border: 1px solid #ffc107; border-radius: 5px; background: #fff3cd;">'
                '<h4>⚠️ Analysis Not Available</h4>'
                '<p>No CSV files found for analysis. To see real data insights:</p>'
                '<ol>'
                '<li>Associate CSV files with this dataset</li>'
                '<li>Run the "🚀 Run Enhanced Analysis" action</li>'
                '<li>Return here to see real analysis results</li>'
                '</ol>'
                '</div>'
            )
            
        except Exception as e:
            return format_html(
                '<div style="color: orange; padding: 10px; border: 1px solid #ffc107; border-radius: 5px;">'
                '⚠️ Unable to generate live analysis preview: {}<br/>'
                'Use "🚀 Run Enhanced Analysis" action from the dataset list for full results.'
                '</div>',
                str(e)
            )
    
    live_analysis_display.short_description = _('Live Analysis Results')
    live_analysis_display.allow_tags = True
    
    def run_enhanced_analysis(self, request, queryset):
        """Run REAL analysis on selected datasets - analyzes your actual CSV files"""
        success_count = 0
        
        for dataset in queryset:
            try:
                # Import the REAL analyzer (no more fake demo data)
                from .analysis.real_analyzer import RealCSVAnalyzer
                
                # Get documents linked to this dataset  
                dataset_documents = dataset.documents.filter(
                    datasetdocument__document_role='raw_data'
                )
                
                if not dataset_documents.exists():
                    self.message_user(
                        request,
                        f'⚠️ Dataset "{dataset.title}" has no documents with "raw_data" role. Please associate CSV files first.',
                        messages.WARNING
                    )
                    continue
                
                # Get the first document and analyze it with REAL analyzer
                doc = dataset_documents.first()
                analyzer = RealCSVAnalyzer()
                results = analyzer.analyze_document(doc)
                
                if results.get('status') == 'error':
                    self.message_user(
                        request,
                        f'❌ Analysis failed for "{dataset.title}": {results["message"]}. {results["suggestion"]}',
                        messages.ERROR
                    )
                    continue
                
                # Mark dataset as analyzed (results displayed on-demand)
                dataset.status = 'analyzed'
                dataset.save()
                
                success_count += 1
                
                # Extract REAL metrics for user feedback
                summary = results["dataset_summary"]
                quality = results["data_quality"]
                
                # Log success with REAL data
                self.message_user(
                    request,
                    f'✅ REAL analysis completed for "{dataset.title}": '
                    f'{summary["total_rows"]} rows × {summary["total_columns"]} columns, '
                    f'{quality["score"]}% complete ({quality["status"]} quality). '
                    f'Edit the dataset to see actual data insights!',
                    messages.SUCCESS
                )
                
            except Exception as e:
                self.message_user(
                    request,
                    f'❌ Analysis failed for "{dataset.title}": {str(e)}',
                    messages.ERROR
                )
        
        if success_count > 0:
            self.message_user(
                request,
                f'🎉 Enhanced Task 2.2 analysis completed for {success_count} dataset(s)! '
                f'Click on any dataset title to edit and see the beautiful live analysis results!',
                messages.SUCCESS
            )
    
    run_enhanced_analysis.short_description = _('🔬 Run REAL Data Analysis (No More Fake Values)')
    
    def test_analysis_system(self, request, queryset):
        """Test the enhanced analysis system"""
        try:
            from .analysis.analyzers import StatisticalAnalyzer
            from .analysis.quality_indicators import DataQualityIndicator
            import io
            
            # Test data
            test_data = """temperature,humidity,quality_score,measurement_id
22.5,68.2,85,1
23.1,67.8,92,2
21.9,69.1,78,3
24.2,66.5,95,4
20.8,71.3,88,5"""
            
            # Run test analysis
            analyzer = StatisticalAnalyzer()
            file_obj = io.StringIO(test_data)
            results = analyzer.analyze_dataset(file_obj, 'csv')
            
            # Show results
            self.message_user(
                request,
                f'✅ Enhanced Analysis System Test PASSED! '
                f'Quality Grade: {results["demo_highlights"]["key_metrics"]["data_quality_grade"]}, '
                f'Features: Color-coded quality indicators, Professional charts, Demo polish, '
                f'Statistical analysis with visual polish. Live results available!',
                messages.SUCCESS
            )
            
        except Exception as e:
            self.message_user(
                request,
                f'❌ Analysis system test failed: {str(e)}',
                messages.ERROR
            )
    
    test_analysis_system.short_description = _('🧪 Test Enhanced Analysis System')
    
    def mark_as_analyzed(self, request, queryset):
        """Mark datasets as analyzed (for demo purposes)"""
        count = queryset.update(status='analyzed')
        self.message_user(
            request,
            f'📊 Marked {count} dataset(s) as analyzed. '
            f'Edit any dataset to see live enhanced analysis results with Task 2.2 features!',
            messages.SUCCESS
        )
    
    mark_as_analyzed.short_description = _('📊 Mark as Analyzed (Demo)')

    def _display_real_analysis_results(self, results):
        """Display real analysis results in a simple, readable format"""
        from django.utils.html import format_html, format_html_join
        from django.utils.safestring import mark_safe
        
        try:
            if results.get('status') == 'error':
                return format_html(
                    '<div style="padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;">'
                    '<strong>❌ Analysis Error:</strong> {}<br>'
                    '<strong>Suggestion:</strong> {}'
                    '</div>',
                    results.get('message', 'Unknown error'),
                    results.get('suggestion', 'Try again')
                )
            
            summary = results.get('dataset_summary', {})
            quality = results.get('data_quality', {})
            preview = results.get('data_preview', {})
            insights = results.get('insights', [])
            
            # Quality indicator
            quality_score = quality.get('score', 0)
            if quality_score >= 90:
                quality_badge = mark_safe('<span style="background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 3px;">✅ Excellent</span>')
            elif quality_score >= 70:
                quality_badge = mark_safe('<span style="background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 3px;">⚠️ Good</span>')
            else:
                quality_badge = mark_safe('<span style="background: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 3px;">❌ Poor</span>')
            
            # Build proper data preview table
            preview_html = ""
            if preview.get('headers') and preview.get('sample_rows'):
                headers = preview['headers'][:5]  # First 5 columns
                rows = preview['sample_rows'][:3]  # First 3 rows
                
                # Build table headers matching dark theme
                header_cells = ""
                for header in headers:
                    header_cells += f'<th style="padding: 8px; border: 1px solid #417690; background: #417690; color: white; font-weight: bold;">{header}</th>'
                
                # Build table rows matching dark theme
                table_rows = ""
                for row in rows:
                    table_rows += '<tr>'
                    for i, cell in enumerate(row[:5]):  # First 5 cells
                        cell_value = str(cell)[:30] if len(str(cell)) > 30 else str(cell)  # Truncate long values
                        table_rows += f'<td style="padding: 8px; border: 1px solid #417690; background: #3a3f58; color: #fff;">{cell_value}</td>'
                    table_rows += '</tr>'
                
                preview_html = mark_safe(f'''
                <table style="border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 12px; background: #3a3f58;">
                    <thead>
                        <tr>{header_cells}</tr>
                    </thead>
                    <tbody style="background: #3a3f58;">
                        {table_rows}
                    </tbody>
                </table>
                <p style="font-style: italic; color: #ccc; font-size: 11px;">{preview.get("showing", "")}</p>
                ''')
            else:
                preview_html = mark_safe('<p style="color: #ccc; font-style: italic;">No data preview available for this dataset.</p>')
            
            # Build insights list matching dark theme
            insights_html = ""
            if insights:
                insight_items = ""
                for insight in insights[:5]:  # First 5 insights
                    insight_items += f'<li style="margin: 4px 0; color: #fff;">{insight}</li>'
                insights_html = mark_safe(f'<ul style="margin: 10px 0; padding-left: 25px; color: #fff;">{insight_items}</ul>')
            else:
                insights_html = mark_safe('<p style="color: #ccc; font-style: italic;">No insights available for this dataset.</p>')
            
            # Match the dark admin theme background
            return format_html(
                '''
                <div style="background: #2f3349; padding: 20px; border: 1px solid #417690; border-radius: 5px; color: #fff;">
                    <h4 style="color: #79aec8; margin-top: 0; border-bottom: 2px solid #417690; padding-bottom: 10px;">🔬 Real Data Analysis Results</h4>
                    
                    <p style="color: #fff;"><strong>📊 Dataset Summary:</strong></p>
                    <ul style="color: #fff;">
                        <li><strong>Size:</strong> {} rows × {} columns</li>
                        <li><strong>Data Types:</strong> {} numeric, {} text columns</li>
                        <li><strong>Quality:</strong> {}% ({})</li>
                        <li><strong>Completeness:</strong> {} missing cells out of {}</li>
                    </ul>
                    
                    <p style="color: #fff;"><strong>👁️ Data Preview:</strong></p>
                    {}
                    
                    <p style="color: #fff;"><strong>💡 Key Insights:</strong></p>
                    {}
                    
                    <p style="font-size: 11px; color: #ccc; margin-top: 15px; border-top: 1px solid #417690; padding-top: 10px;">
                        <strong>Source:</strong> {} ({})
                    </p>
                </div>
                ''',
                summary.get('total_rows', 0),
                summary.get('total_columns', 0), 
                summary.get('numeric_columns', 0),
                summary.get('text_columns', 0),
                quality_score,
                quality.get('status', 'unknown'),
                quality.get('missing_cells', 0),
                quality.get('total_cells', 0),
                preview_html,
                insights_html,
                results.get('document_name', 'Unknown'),
                results.get('file_name', 'Unknown')
            )
            
        except Exception as e:
            return format_html(
                '<div style="padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;">'
                '<strong>❌ Display Error:</strong> Could not format analysis results: {}'
                '</div>',
                str(e)
            )


@admin.register(DatasetDocument)
class DatasetDocumentAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'document', 'document_role', 'order', 'datetime_added')
    list_filter = ('document_role', 'dataset__study__project')
    search_fields = ('dataset__title', 'document__label')
    date_hierarchy = 'datetime_added'
    readonly_fields = ('datetime_added',)
    autocomplete_fields = ('dataset', 'document')
    
    fieldsets = (
        (_('Relationship'), {
            'fields': ('dataset', 'document')
        }),
        (_('Details'), {
            'fields': ('document_role', 'order', 'notes')
        }),
        (_('Metadata'), {
            'fields': ('datetime_added',)
        }),
    ) 