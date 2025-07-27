#!/usr/bin/env python3
"""
Restore Demo Data Script for Mayan EDMS Research Platform
Uploads test CSV files and creates proper research hierarchies.
"""

import os
import sys
import django
from datetime import date, timedelta
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.development.base')
django.setup()

# Now import Django models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.research.models import Project, Study, Dataset, DatasetDocument

def clear_existing_demo_data():
    """Clear existing broken demo data"""
    print("🧹 Clearing existing demo data...")
    
    # Clear in reverse dependency order
    DatasetDocument.objects.all().delete()
    Dataset.objects.all().delete()
    Study.objects.all().delete()
    Project.objects.all().delete()
    
    # Clear documents that might have broken file references
    Document.objects.filter(label__icontains='climate').delete()
    Document.objects.filter(label__icontains='demo').delete()
    Document.objects.filter(label__icontains='test').delete()
    
    print("✅ Existing demo data cleared")

def get_or_create_document_type():
    """Get or create a document type for CSV files"""
    doc_type, created = DocumentType.objects.get_or_create(
        label='Research Data',
        defaults={'description': 'CSV files for research analysis'}
    )
    return doc_type

def upload_csv_file(file_path, label, doc_type):
    """Upload a CSV file to Mayan and return the Document"""
    print(f"📄 Uploading {label}...")
    
    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Create uploaded file object
    uploaded_file = SimpleUploadedFile(
        name=os.path.basename(file_path),
        content=file_content,
        content_type='text/csv'
    )
    
    # Create document
    document = Document(
        label=label,
        document_type=doc_type
    )
    document.save()
    
    # Upload the file
    document.file_new(
        file_object=uploaded_file,
        user=User.objects.filter(is_superuser=True).first()
    )
    
    print(f"✅ Uploaded {label} (ID: {document.id})")
    return document

def create_demo_research_data():
    """Create comprehensive demo research data with uploaded CSV files"""
    print("🔬 Creating demo research hierarchy...")
    
    doc_type = get_or_create_document_type()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ No admin user found. Please create a superuser first.")
        return
    
    # Create Project 1: Climate Change Research
    climate_project = Project.objects.create(
        title="Climate Change Research 2024",
        description="Comprehensive analysis of climate data using advanced statistical methods",
        principal_investigator="Dr. Sarah Johnson",
        start_date=date(2024, 1, 15),
        status="active",
        funding_source="National Science Foundation",
        budget_amount=500000
    )
    print(f"✅ Created project: {climate_project.title}")
    
    # Upload climate CSV file
    climate_doc = upload_csv_file(
        'test_data/climate_research/sensor_data_sample.csv',
        'Climate Research - Sensor Data 2024',
        doc_type
    )
    
    # Create Study 1: Urban Heat Island Analysis
    heat_study = Study.objects.create(
        project=climate_project,
        title="Urban Heat Island Analysis",
        description="Analyzing temperature variations in urban vs rural areas",
        study_type="observational",
        start_date=date(2024, 2, 1),
        target_sample_size=100,
        current_sample_size=75,
        status="in_progress"
    )
    print(f"✅ Created study: {heat_study.title}")
    
    # Create Dataset 1: Temperature Sensor Data
    temp_dataset = Dataset.objects.create(
        study=heat_study,
        title="Temperature Sensor Data Q1 2024",
        description="Hourly temperature readings from 50 urban and rural sensors",
        dataset_type="quantitative_data",
        collection_method="automated_sensors",
        sample_size=12960,
        collection_period_start=date(2024, 1, 1),
        collection_period_end=date(2024, 3, 31),
        status="analyzed",
        quality_score=92.5
    )
    print(f"✅ Created dataset: {temp_dataset.title}")
    
    # Link document to dataset
    DatasetDocument.objects.create(
        dataset=temp_dataset,
        document=climate_doc,
        role="primary",
        upload_date=date.today(),
        file_format="csv",
        description="Primary sensor data file with validated temperature readings"
    )
    print(f"✅ Linked {climate_doc.label} to {temp_dataset.title}")
    
    # Create Project 2: Demographics Research
    demo_project = Project.objects.create(
        title="Population Demographics Study 2024",
        description="Analysis of demographic trends and population changes",
        principal_investigator="Dr. Maria Rodriguez",
        start_date=date(2024, 3, 1),
        status="active",
        funding_source="Department of Health",
        budget_amount=250000
    )
    print(f"✅ Created project: {demo_project.title}")
    
    # Upload demographics CSV file
    demo_doc = upload_csv_file(
        'test_data/demographics/population_study.csv',
        'Demographics - Population Analysis 2024',
        doc_type
    )
    
    # Create Study 2: Population Trends Analysis
    pop_study = Study.objects.create(
        project=demo_project,
        title="Population Trends Analysis",
        description="Examining demographic shifts over the past decade",
        study_type="longitudinal",
        start_date=date(2024, 3, 15),
        target_sample_size=5000,
        current_sample_size=3200,
        status="collecting_data"
    )
    print(f"✅ Created study: {pop_study.title}")
    
    # Create Dataset 2: Population Survey Data
    pop_dataset = Dataset.objects.create(
        study=pop_study,
        title="Population Survey Data 2024",
        description="Comprehensive demographic survey responses",
        dataset_type="mixed_methods",
        collection_method="survey",
        sample_size=3200,
        collection_period_start=date(2024, 3, 15),
        collection_period_end=date(2024, 6, 30),
        status="ready_for_analysis",
        quality_score=87.3
    )
    print(f"✅ Created dataset: {pop_dataset.title}")
    
    # Link document to dataset
    DatasetDocument.objects.create(
        dataset=pop_dataset,
        document=demo_doc,
        role="primary",
        upload_date=date.today(),
        file_format="csv",
        description="Primary survey response data with demographic variables"
    )
    print(f"✅ Linked {demo_doc.label} to {pop_dataset.title}")
    
    # Create additional datasets with CSV files for variety
    
    # Water Quality Dataset
    water_doc = upload_csv_file(
        'test_data/water_quality/multi_station_analysis.csv',
        'Water Quality - Multi-Station Analysis',
        doc_type
    )
    
    water_dataset = Dataset.objects.create(
        study=heat_study,  # Link to existing study for demo purposes
        title="Water Quality Monitoring Q1",
        description="Multi-station water quality measurements",
        dataset_type="quantitative_data",
        collection_method="field_sampling",
        sample_size=2400,
        collection_period_start=date(2024, 1, 1),
        collection_period_end=date(2024, 3, 31),
        status="analyzed",
        quality_score=89.7
    )
    
    DatasetDocument.objects.create(
        dataset=water_dataset,
        document=water_doc,
        role="primary",
        upload_date=date.today(),
        file_format="csv",
        description="Water quality measurements from 8 monitoring stations"
    )
    print(f"✅ Created and linked water quality dataset")
    
    # Lab Measurements Dataset
    lab_doc = upload_csv_file(
        'test_data/lab_measurements/precision_experiment.csv',
        'Lab Measurements - Precision Experiment',
        doc_type
    )
    
    lab_dataset = Dataset.objects.create(
        study=pop_study,  # Link to existing study
        title="Laboratory Precision Measurements",
        description="High-precision laboratory measurement validation",
        dataset_type="quantitative_data",
        collection_method="laboratory",
        sample_size=150,
        collection_period_start=date(2024, 2, 1),
        collection_period_end=date(2024, 2, 28),
        status="published",
        quality_score=95.8
    )
    
    DatasetDocument.objects.create(
        dataset=lab_dataset,
        document=lab_doc,
        role="primary",
        upload_date=date.today(),
        file_format="csv",
        description="Precision measurement data with calibrated instruments"
    )
    print(f"✅ Created and linked lab measurements dataset")
    
    print("\n🎉 Demo data restoration complete!")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"Projects: {Project.objects.count()}")
    print(f"Studies: {Study.objects.count()}")
    print(f"Datasets: {Dataset.objects.count()}")
    print(f"Documents: {Document.objects.count()}")
    print(f"Dataset-Document links: {DatasetDocument.objects.count()}")

def verify_file_access():
    """Verify that all uploaded files are accessible"""
    print("\n🔍 Verifying file access...")
    
    working_files = 0
    total_files = 0
    
    for doc in Document.objects.all():
        total_files += 1
        try:
            if hasattr(doc, 'file_latest') and doc.file_latest:
                with doc.file_latest.open() as f:
                    content = f.read(100)  # Read first 100 bytes
                    if content:
                        print(f"✅ {doc.label}: File accessible ({len(content)} bytes)")
                        working_files += 1
                    else:
                        print(f"❌ {doc.label}: File empty")
            else:
                print(f"❌ {doc.label}: No file_latest")
        except Exception as e:
            print(f"❌ {doc.label}: Access error - {str(e)[:50]}")
    
    print(f"\n📈 File Status: {working_files}/{total_files} files accessible")
    return working_files == total_files

if __name__ == "__main__":
    print("🚀 Starting demo data restoration...")
    
    try:
        clear_existing_demo_data()
        create_demo_research_data()
        
        if verify_file_access():
            print("\n🎉 SUCCESS! All demo data restored with working file access!")
        else:
            print("\n⚠️  Demo data created but some files may have access issues")
            
    except Exception as e:
        print(f"\n❌ Error during restoration: {e}")
        import traceback
        traceback.print_exc() 