#!/usr/bin/env python
"""
Standalone Research Platform Demo
Shows our research models in a live Django admin interface.
Run: python quick_demo_standalone.py runserver
"""

import os
import sys
import django
from django.conf import settings
from django.db import models
from django.contrib import admin

# Configure Django for standalone demo
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='demo-key-not-for-production',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            '__main__',  # This module
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        ROOT_URLCONF='__main__',
        STATIC_URL='/static/',
        USE_TZ=True,
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }],
    )

django.setup()

# Define our research models
class Project(models.Model):
    title = models.CharField(max_length=255, help_text="Research project title")
    description = models.TextField(blank=True, help_text="Project description")
    principal_investigator = models.CharField(max_length=255, help_text="Lead researcher")
    institution = models.CharField(max_length=255, blank=True, help_text="Research institution")
    
    STATUS_CHOICES = [
        ('planning', '📋 Planning'),
        ('active', '🔬 Active'),
        ('completed', '✅ Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField(help_text="Project start date")
    end_date = models.DateField(null=True, blank=True, help_text="Project end date")
    funding_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Total funding in USD")
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        
    def __str__(self):
        return f"🎯 {self.title}"

class Study(models.Model):
    title = models.CharField(max_length=255, help_text="Study title")
    description = models.TextField(blank=True, help_text="Study description")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='studies')
    
    STATUS_CHOICES = [
        ('planning', '📋 Planning'),
        ('active', '🔬 Active'),
        ('completed', '✅ Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    study_type = models.CharField(max_length=50, blank=True, help_text="Type of study (experimental, observational, etc.)")
    methodology = models.TextField(blank=True, help_text="Research methodology")
    start_date = models.DateField(help_text="Study start date")
    end_date = models.DateField(null=True, blank=True, help_text="Study end date")
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Studies'
        
    def __str__(self):
        return f"📊 {self.title}"

class Dataset(models.Model):
    title = models.CharField(max_length=255, help_text="Dataset title")
    description = models.TextField(blank=True, help_text="Dataset description")
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='datasets')
    
    STATUS_CHOICES = [
        ('planning', '📋 Planning'),
        ('active', '📈 Active'),
        ('completed', '✅ Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    DATA_TYPE_CHOICES = [
        ('csv', '📄 CSV'),
        ('excel', '📊 Excel'),
        ('json', '🔧 JSON'),
        ('image', '🖼️ Images'),
        ('other', '📁 Other'),
    ]
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default='csv')
    size_bytes = models.PositiveIntegerField(default=0, help_text="Dataset size in bytes")
    
    ANALYSIS_STATUS_CHOICES = [
        ('pending', '⏳ Pending'),
        ('processing', '⚙️ Processing'),
        ('completed', '✅ Completed'),
        ('failed', '❌ Failed'),
    ]
    analysis_status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, default='pending')
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        
    def __str__(self):
        return f"💾 {self.title}"

# Admin configuration
class StudyInline(admin.StackedInline):
    model = Study
    extra = 0
    fields = ['title', 'description', 'status', 'study_type', 'start_date', 'end_date']
    classes = ['collapse']

class DatasetInline(admin.StackedInline):
    model = Dataset
    extra = 0
    fields = ['title', 'description', 'status', 'data_type', 'analysis_status']
    classes = ['collapse']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'principal_investigator', 'institution', 'status', 'start_date', 'study_count']
    list_filter = ['status', 'institution', 'start_date']
    search_fields = ['title', 'principal_investigator', 'institution', 'description']
    date_hierarchy = 'start_date'
    inlines = [StudyInline]
    
    fieldsets = [
        ('🎯 Project Information', {
            'fields': ['title', 'description']
        }),
        ('👨‍🔬 Research Details', {
            'fields': ['principal_investigator', 'institution', 'status']
        }),
        ('💰 Timeline & Funding', {
            'fields': ['start_date', 'end_date', 'funding_amount']
        }),
    ]
    
    def study_count(self, obj):
        return obj.studies.count()
    study_count.short_description = '📊 Studies'

@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'study_type', 'start_date', 'dataset_count']
    list_filter = ['status', 'study_type', 'project__status']
    search_fields = ['title', 'description', 'project__title']
    inlines = [DatasetInline]
    
    def dataset_count(self, obj):
        return obj.datasets.count()
    dataset_count.short_description = '💾 Datasets'

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['title', 'study', 'status', 'data_type', 'analysis_status', 'readable_size']
    list_filter = ['status', 'data_type', 'analysis_status', 'study__status']
    search_fields = ['title', 'description', 'study__title']
    
    def readable_size(self, obj):
        if obj.size_bytes < 1024:
            return f"{obj.size_bytes} bytes"
        elif obj.size_bytes < 1024*1024:
            return f"{obj.size_bytes/1024:.1f} KB"
        else:
            return f"{obj.size_bytes/(1024*1024):.1f} MB"
    readable_size.short_description = '📏 Size'

# URL configuration
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <html><head><title>Research Platform Demo</title></head>
    <body style='font-family: Arial; padding: 40px; background: #f8f9fa;'>
        <h1>🎯 Research Platform Demo</h1>
        <p>Welcome to the Mayan EDMS Research Platform demonstration!</p>
        <h2>🎪 Demo Features:</h2>
        <ul>
            <li><strong>Research Hierarchy:</strong> Project → Study → Dataset</li>
            <li><strong>Professional Admin:</strong> Enterprise-grade interface</li>
            <li><strong>Data Management:</strong> Comprehensive research organization</li>
        </ul>
        <p><a href='/admin/' style='background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>
            🚀 Open Admin Interface
        </a></p>
        <hr>
        <p><em>This demo showcases the research platform foundation built for Mayan EDMS.</em></p>
    </body></html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]

# Create demo data
def create_demo_data():
    from django.contrib.auth.models import User
    
    # Create superuser
    if not User.objects.filter(username='demo').exists():
        User.objects.create_superuser('demo', 'demo@example.com', 'demo123')
    
    # Create demo projects
    if not Project.objects.exists():
        # Climate Change Project
        climate_project = Project.objects.create(
            title="Climate Change Impact Assessment",
            description="Comprehensive study of climate change impacts on urban environments and infrastructure resilience.",
            principal_investigator="Dr. Sarah Chen",
            institution="University of Environmental Sciences",
            status="active",
            start_date="2024-01-15",
            funding_amount=2500000.00
        )
        
        urban_study = Study.objects.create(
            title="Urban Heat Island Analysis",
            description="Analysis of urban heat island effects using satellite data and ground sensors.",
            project=climate_project,
            status="active",
            study_type="observational",
            methodology="Remote sensing + statistical modeling",
            start_date="2024-01-20"
        )
        
        Dataset.objects.create(
            title="Temperature Station Data 2024",
            description="Hourly temperature readings from 150 weather stations across 5 metropolitan areas.",
            study=urban_study,
            status="active",
            data_type="csv",
            size_bytes=52428800,
            analysis_status="completed"
        )
        
        # Healthcare Project
        healthcare_project = Project.objects.create(
            title="Healthcare Data Analytics Platform",
            description="ML models for predictive healthcare analytics using large-scale patient data.",
            principal_investigator="Dr. Michael Rodriguez",
            institution="Medical Research Institute",
            status="active",
            start_date="2024-02-01",
            funding_amount=1800000.00
        )
        
        outcome_study = Study.objects.create(
            title="Patient Outcome Prediction",
            description="ML models to predict patient outcomes based on historical medical records.",
            project=healthcare_project,
            status="active",
            study_type="computational",
            methodology="Machine learning + statistical analysis",
            start_date="2024-02-15"
        )
        
        Dataset.objects.create(
            title="Patient Medical Records Dataset",
            description="Anonymized patient records spanning 5 years with diagnoses and outcomes.",
            study=outcome_study,
            status="active",
            data_type="csv",
            size_bytes=1073741824,
            analysis_status="completed"
        )

if __name__ == '__main__':
    from django.core.management.base import BaseCommand
    from django.db import connection
    
    # Create tables
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Project)
        schema_editor.create_model(Study)
        schema_editor.create_model(Dataset)
    
    # Create demo data
    create_demo_data()
    
    # Set admin site header
    admin.site.site_header = "🎯 Research Platform Demo"
    admin.site.site_title = "Research Admin"
    admin.site.index_title = "Welcome to Research Platform Administration"
    
    # Run management command
    from django.core.management import execute_from_command_line
    if len(sys.argv) == 1:
        sys.argv.append('runserver')
        sys.argv.append('8000')
    execute_from_command_line(sys.argv) 