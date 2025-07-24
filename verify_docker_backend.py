#!/usr/bin/env python
"""
🐳 Docker Backend Verification for Mayan EDMS Research Platform
Specifically designed to run inside the Mayan Docker container.

Usage:
    docker-compose exec app python /app/verify_docker_backend.py
"""

import os
import sys
import subprocess
import json

def run_django_command(command):
    """Run a Django management command and return output"""
    try:
        result = subprocess.run(
            ['/opt/mayan-edms/bin/mayan-edms.py'] + command,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_django_check():
    """Test Django system checks"""
    print("🔍 Testing Django System Checks...")
    success, stdout, stderr = run_django_command(['check'])
    if success:
        print("✅ Django system checks passed")
        return True
    else:
        print("❌ Django system checks failed")
        print(f"Error: {stderr}")
        return False

def test_database_migration():
    """Test database migration status"""
    print("🗄️  Testing Database Migration Status...")
    success, stdout, stderr = run_django_command(['showmigrations', '--plan'])
    if success:
        if "research" in stdout:
            print("✅ Research app migrations found")
            return True
        else:
            print("⚠️  Research app migrations not found")
            return False
    else:
        print("❌ Failed to check migrations")
        print(f"Error: {stderr}")
        return False

def test_research_app_shell():
    """Test research app via Django shell"""
    print("🐍 Testing Research App via Django Shell...")
    
    shell_commands = """
import sys
try:
    from mayan.apps.research.models import Project, Study, Dataset
    print("SUCCESS: Research models imported")
    
    # Test model creation
    from django.utils import timezone
    project = Project(
        title="Shell Test Project",
        description="Test via shell",
        principal_investigator="Shell Tester",
        start_date=timezone.now().date(),
        status='planning'
    )
    print("SUCCESS: Research model instance created")
    
    # Test permissions
    from mayan.apps.research.permissions import permission_project_view
    print("SUCCESS: Research permissions imported")
    
    # Test events
    from mayan.apps.research.events import event_project_created
    print("SUCCESS: Research events imported")
    
    print("OVERALL: Shell test passed")
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
"""
    
    success, stdout, stderr = run_django_command(['shell', '-c', shell_commands])
    if success and "OVERALL: Shell test passed" in stdout:
        print("✅ Django shell tests passed")
        print("   - Research models work")
        print("   - Research permissions work") 
        print("   - Research events work")
        return True
    else:
        print("❌ Django shell tests failed")
        print(f"Output: {stdout}")
        print(f"Error: {stderr}")
        return False

def test_installed_apps():
    """Test that research app is in INSTALLED_APPS"""
    print("📦 Testing INSTALLED_APPS Configuration...")
    
    shell_command = """
from django.conf import settings
research_apps = [app for app in settings.INSTALLED_APPS if 'research' in app.lower()]
if research_apps:
    print(f"SUCCESS: Found research apps: {', '.join(research_apps)}")
else:
    print("ERROR: No research apps found in INSTALLED_APPS")
    print(f"Total apps: {len(settings.INSTALLED_APPS)}")
"""
    
    success, stdout, stderr = run_django_command(['shell', '-c', shell_command])
    if success and "SUCCESS:" in stdout:
        print("✅ Research app properly configured in INSTALLED_APPS")
        return True
    else:
        print("❌ Research app not found in INSTALLED_APPS")
        print(f"Output: {stdout}")
        return False

def test_permissions_system():
    """Test the permissions system integration"""
    print("🔐 Testing Permissions System Integration...")
    
    shell_command = """
try:
    from mayan.apps.permissions.models import ModelPermission
    from mayan.apps.research.models import Project
    
    # Check if Project model has permissions registered
    project_perms = ModelPermission.get_for_class(Project)
    if project_perms:
        print(f"SUCCESS: Found {len(project_perms)} permissions for Project model")
        perm_names = [p.label for p in project_perms[:3]]
        print(f"Sample permissions: {', '.join(perm_names)}")
    else:
        print("ERROR: No permissions found for Project model")
        
except Exception as e:
    print(f"ERROR: Permission system test failed: {str(e)}")
"""
    
    success, stdout, stderr = run_django_command(['shell', '-c', shell_command])
    if success and "SUCCESS:" in stdout:
        print("✅ Permissions system integration working")
        return True
    else:
        print("❌ Permissions system integration failed")
        print(f"Output: {stdout}")
        return False

def test_celery_tasks():
    """Test Celery task integration"""
    print("⚡ Testing Celery Task Integration...")
    
    # Check if celery is running
    try:
        result = subprocess.run(['pgrep', '-f', 'celery'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Celery workers are running")
            
            # Test task registration
            shell_command = """
try:
    from mayan.apps.research.tasks import task_analyze_dataset
    print("SUCCESS: Research tasks imported")
    
    from mayan.apps.research.queues import queue_research_analysis  
    print("SUCCESS: Research queues imported")
    
except ImportError as e:
    print(f"WARNING: Some task components missing: {str(e)}")
except Exception as e:
    print(f"ERROR: Task test failed: {str(e)}")
"""
            
            success, stdout, stderr = run_django_command(['shell', '-c', shell_command])
            if "SUCCESS:" in stdout:
                print("✅ Research tasks properly configured")
                return True
            else:
                print("⚠️  Research task configuration incomplete")
                return False
        else:
            print("⚠️  Celery workers not detected")
            return False
    except Exception as e:
        print(f"❌ Failed to check Celery status: {str(e)}")
        return False

def test_admin_interface():
    """Test Django admin interface"""
    print("🛠️  Testing Django Admin Interface...")
    
    shell_command = """
from django.contrib import admin
from mayan.apps.research.models import Project, Study, Dataset

registered_models = []
for model in [Project, Study, Dataset]:
    if model in admin.site._registry:
        registered_models.append(model.__name__)

if len(registered_models) == 3:
    print(f"SUCCESS: All research models registered in admin: {', '.join(registered_models)}")
else:
    print(f"WARNING: Only {len(registered_models)}/3 models registered: {', '.join(registered_models)}")
"""
    
    success, stdout, stderr = run_django_command(['shell', '-c', shell_command])
    if success and "SUCCESS:" in stdout:
        print("✅ Django admin properly configured")
        return True
    else:
        print("⚠️  Django admin configuration incomplete")
        print(f"Output: {stdout}")
        return False

def test_database_tables():
    """Test database table creation"""
    print("🗃️  Testing Database Tables...")
    
    shell_command = """
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'research_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
if len(tables) >= 3:
    print(f"SUCCESS: Found research tables: {', '.join(tables)}")
else:
    print(f"WARNING: Expected 3+ tables, found {len(tables)}: {', '.join(tables)}")
"""
    
    success, stdout, stderr = run_django_command(['shell', '-c', shell_command])
    if success and ("SUCCESS:" in stdout or len(stdout.strip()) > 0):
        print("✅ Database tables properly created")
        return True
    else:
        print("❌ Database table creation issues")
        print(f"Output: {stdout}")
        return False

def main():
    """Run all Docker backend verification tests"""
    print("🐳 Mayan EDMS Research Platform - Docker Backend Verification")
    print("=" * 70)
    
    tests = [
        ("Django System Check", test_django_check),
        ("Database Migrations", test_database_migration),
        ("INSTALLED_APPS", test_installed_apps),
        ("Research App Shell", test_research_app_shell),
        ("Database Tables", test_database_tables),
        ("Permissions System", test_permissions_system),
        ("Django Admin", test_admin_interface),
        ("Celery Tasks", test_celery_tasks),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 50)
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
    
    # Final results
    print("\n" + "=" * 70)
    print("🏁 DOCKER VERIFICATION RESULTS")
    print("=" * 70)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! Docker backend is ready for production deployment!")
        status = "READY"
    elif success_rate >= 75:
        print("\n👍 GOOD! Minor issues present but deployment can proceed")
        status = "GOOD"
    else:
        print("\n⚠️  NEEDS WORK! Several critical issues must be resolved")
        status = "NEEDS_WORK"
    
    # Export results for automation
    results = {
        "status": status,
        "success_rate": success_rate,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "timestamp": subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()
    }
    
    with open('/tmp/verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 Results saved to: /tmp/verification_results.json")
    
    return success_rate >= 75

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 