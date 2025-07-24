#!/usr/bin/env python
"""
🔬 Mayan EDMS Research Platform - Backend Verification Suite
Comprehensive testing of all research platform components.

Usage:
    # Via Docker (Recommended)
    docker-compose -f docker-compose.research-platform.yml exec app python /app/verify_research_backend.py

    # Local development
    python verify_research_backend.py
"""

import os
import sys
import django
from pathlib import Path

# Configure Django environment for Mayan EDMS
# Add the mayan directory to Python path
mayan_path = Path(__file__).parent / 'mayan'
if str(mayan_path) not in sys.path:
    sys.path.insert(0, str(mayan_path))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.base')

# Django setup
django.setup()

# Import after Django setup
from django.core.management import call_command
from django.db import transaction, connection
from django.contrib.auth.models import User, Group
from django.apps import apps
from django.conf import settings
import traceback

class BackendVerificationSuite:
    """Comprehensive verification of the research platform backend"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        
    def print_header(self, title):
        """Print a formatted test section header"""
        print(f"\n{'='*60}")
        print(f"🔬 {title}")
        print(f"{'='*60}")
        
    def print_test(self, test_name, status, details=""):
        """Print test result"""
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   {details}")
        if status:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            self.errors.append(f"{test_name}: {details}")
            
    def test_django_configuration(self):
        """Test Django and Mayan configuration"""
        self.print_header("Django Configuration Tests")
        
        # Test Django setup
        try:
            self.print_test("Django Setup", True, f"Version: {django.get_version()}")
        except Exception as e:
            self.print_test("Django Setup", False, str(e))
            
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            self.print_test("Database Connection", result[0] == 1, f"Connection successful")
        except Exception as e:
            self.print_test("Database Connection", False, str(e))
            
        # Test Mayan settings
        try:
            installed_apps = len(settings.INSTALLED_APPS)
            self.print_test("Mayan Settings", installed_apps > 40, f"Loaded {installed_apps} apps")
        except Exception as e:
            self.print_test("Mayan Settings", False, str(e))
            
    def test_research_app_loading(self):
        """Test if research app is properly loaded"""
        self.print_header("Research App Loading Tests")
        
        # Test app registration
        try:
            research_app = apps.get_app_config('research')
            self.print_test("Research App Registration", True, f"App: {research_app.verbose_name}")
        except Exception as e:
            self.print_test("Research App Registration", False, str(e))
            return False
            
        # Test app in INSTALLED_APPS
        try:
            research_in_apps = any('research' in app for app in settings.INSTALLED_APPS)
            self.print_test("Research App in INSTALLED_APPS", research_in_apps, 
                          "Found in Django configuration")
        except Exception as e:
            self.print_test("Research App in INSTALLED_APPS", False, str(e))
            
        return True
        
    def test_research_models(self):
        """Test research models and database integration"""
        self.print_header("Research Models Tests")
        
        try:
            # Import research models
            from mayan.apps.research.models import Project, Study, Dataset
            self.print_test("Model Import", True, "Project, Study, Dataset imported successfully")
            
            # Test model structure
            project_fields = [field.name for field in Project._meta.fields]
            expected_fields = ['title', 'description', 'principal_investigator', 'start_date']
            fields_present = all(field in project_fields for field in expected_fields)
            self.print_test("Project Model Structure", fields_present, 
                          f"Fields: {', '.join(project_fields[:5])}...")
            
            # Test model relationships
            study_fields = [field.name for field in Study._meta.fields]
            has_project_fk = 'project' in study_fields
            self.print_test("Study-Project Relationship", has_project_fk, "ForeignKey to Project found")
            
            dataset_fields = [field.name for field in Dataset._meta.fields]
            has_study_fk = 'study' in dataset_fields
            self.print_test("Dataset-Study Relationship", has_study_fk, "ForeignKey to Study found")
            
            # Test database table existence
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_name LIKE 'research_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                expected_tables = 3  # project, study, dataset
                self.print_test("Database Tables", len(tables) >= expected_tables, 
                              f"Found tables: {', '.join(tables)}")
                
        except Exception as e:
            self.print_test("Research Models", False, f"Error: {str(e)}")
            traceback.print_exc()
            
    def test_research_permissions(self):
        """Test research permissions system"""
        self.print_header("Research Permissions Tests")
        
        try:
            from mayan.apps.research.permissions import (
                permission_project_view, permission_project_create,
                permission_study_view, permission_dataset_view
            )
            self.print_test("Permission Import", True, "Research permissions imported")
            
            # Test permission properties
            project_perm_valid = hasattr(permission_project_view, 'namespace')
            self.print_test("Permission Structure", project_perm_valid, 
                          f"Namespace: {getattr(permission_project_view, 'namespace', 'None')}")
            
        except Exception as e:
            self.print_test("Research Permissions", False, str(e))
            
    def test_research_events(self):
        """Test research events system"""
        self.print_header("Research Events Tests")
        
        try:
            from mayan.apps.research.events import (
                event_project_created, event_study_created, event_dataset_created
            )
            self.print_test("Event Import", True, "Research events imported")
            
            # Test event properties
            event_valid = hasattr(event_project_created, 'namespace')
            self.print_test("Event Structure", event_valid, "Event namespace found")
            
        except Exception as e:
            self.print_test("Research Events", False, str(e))
            
    def test_database_operations(self):
        """Test CRUD operations on research models"""
        self.print_header("Database Operations Tests")
        
        try:
            from mayan.apps.research.models import Project, Study, Dataset
            from django.utils import timezone
            import uuid
            
            test_id = str(uuid.uuid4())[:8]
            
            with transaction.atomic():
                # Create test project
                project = Project.objects.create(
                    title=f"Test Project {test_id}",
                    description="Automated test project",
                    principal_investigator="Test Researcher",
                    start_date=timezone.now().date(),
                    status='planning'
                )
                self.print_test("Project Creation", True, f"Created project: {project.title}")
                
                # Create test study
                study = Study.objects.create(
                    title=f"Test Study {test_id}",
                    description="Automated test study",
                    project=project,
                    start_date=timezone.now().date(),
                    status='planning'
                )
                self.print_test("Study Creation", True, f"Created study: {study.title}")
                
                # Create test dataset
                dataset = Dataset.objects.create(
                    title=f"Test Dataset {test_id}",
                    description="Automated test dataset",
                    study=study,
                    status='planning'
                )
                self.print_test("Dataset Creation", True, f"Created dataset: {dataset.title}")
                
                # Test relationships
                study_count = project.studies.count()
                dataset_count = study.datasets.count()
                self.print_test("Model Relationships", study_count == 1 and dataset_count == 1,
                              f"Project has {study_count} studies, Study has {dataset_count} datasets")
                
                # Test string representations
                str_valid = str(project) == project.title and str(study) == study.title
                self.print_test("String Representations", str_valid, "Model __str__ methods working")
                
                # Cleanup test data (rollback transaction)
                raise Exception("Rollback test data")
                
        except Exception as e:
            if "Rollback test data" in str(e):
                self.print_test("Test Data Cleanup", True, "Test data rolled back successfully")
            else:
                self.print_test("Database Operations", False, str(e))
                
    def test_research_admin(self):
        """Test Django admin integration"""
        self.print_header("Django Admin Tests")
        
        try:
            from django.contrib import admin
            from mayan.apps.research.models import Project, Study, Dataset
            
            # Check if models are registered
            project_registered = Project in admin.site._registry
            study_registered = Study in admin.site._registry
            dataset_registered = Dataset in admin.site._registry
            
            registered_count = sum([project_registered, study_registered, dataset_registered])
            self.print_test("Admin Registration", registered_count == 3, 
                          f"{registered_count}/3 models registered")
            
            if project_registered:
                project_admin = admin.site._registry[Project]
                has_list_display = hasattr(project_admin, 'list_display')
                self.print_test("Admin Configuration", has_list_display, "Admin classes configured")
                
        except Exception as e:
            self.print_test("Django Admin", False, str(e))
            
    def test_api_integration(self):
        """Test REST API integration"""
        self.print_header("API Integration Tests")
        
        try:
            # Test API views import
            from mayan.apps.research.api_views import (
                APIProjectListView, APIStudyListView, APIDatasetListView
            )
            self.print_test("API Views Import", True, "Research API views imported")
            
            # Test serializers
            from mayan.apps.research.serializers import (
                ProjectSerializer, StudySerializer, DatasetSerializer
            )
            self.print_test("API Serializers", True, "Research serializers imported")
            
        except ImportError as e:
            self.print_test("API Integration", False, f"Missing API components: {str(e)}")
        except Exception as e:
            self.print_test("API Integration", False, str(e))
            
    def test_task_system(self):
        """Test Celery task integration"""
        self.print_header("Task System Tests")
        
        try:
            # Test task imports
            from mayan.apps.research.tasks import task_analyze_dataset
            self.print_test("Task Import", True, "Research tasks imported")
            
            # Test queue configuration
            from mayan.apps.research.queues import queue_research_analysis
            self.print_test("Queue Configuration", True, "Research queues configured")
            
        except ImportError as e:
            self.print_test("Task System", False, f"Missing task components: {str(e)}")
        except Exception as e:
            self.print_test("Task System", False, str(e))
            
    def test_navigation_integration(self):
        """Test navigation menu integration"""
        self.print_header("Navigation Integration Tests")
        
        try:
            from mayan.apps.research.links import (
                link_project_list, link_project_create, 
                link_study_list, link_dataset_list
            )
            self.print_test("Navigation Links", True, "Research navigation links imported")
            
            # Test link properties
            link_valid = hasattr(link_project_list, 'text') and hasattr(link_project_list, 'view')
            self.print_test("Link Configuration", link_valid, "Links properly configured")
            
        except ImportError as e:
            self.print_test("Navigation Integration", False, f"Missing navigation: {str(e)}")
        except Exception as e:
            self.print_test("Navigation Integration", False, str(e))
            
    def run_all_tests(self):
        """Run complete verification suite"""
        print("🚀 Starting Mayan EDMS Research Platform Backend Verification")
        print("=" * 80)
        
        # Run all test suites
        self.test_django_configuration()
        
        if self.test_research_app_loading():
            self.test_research_models()
            self.test_research_permissions()
            self.test_research_events()
            self.test_database_operations()
            self.test_research_admin()
            self.test_api_integration()
            self.test_task_system()
            self.test_navigation_integration()
        else:
            print("\n⚠️  Research app not loaded - skipping dependent tests")
            
        # Print final results
        self.print_final_results()
        
    def print_final_results(self):
        """Print final test results"""
        print("\n" + "="*80)
        print("🏁 FINAL RESULTS")
        print("="*80)
        
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.tests_failed > 0:
            print(f"\n🚨 FAILED TESTS:")
            for error in self.errors:
                print(f"   • {error}")
                
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT! Backend is ready for deployment")
        elif success_rate >= 75:
            print(f"\n👍 GOOD! Minor issues need attention")
        else:
            print(f"\n⚠️  NEEDS WORK! Several critical issues found")
            
        return success_rate >= 75

if __name__ == '__main__':
    verifier = BackendVerificationSuite()
    success = verifier.run_all_tests()
    sys.exit(0 if success else 1) 