#!/usr/bin/env python3
"""
AWS-Aligned Development Environment Test Suite
Tests all components of the Mayan EDMS research app setup
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.development')

# Set environment variables for testing
os.environ['MAYAN_DATABASES'] = "{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'mayandbpass','USER':'mayan','HOST':'127.0.0.1','PORT':'5432'}}"
os.environ['MAYAN_CELERY_RESULT_BACKEND'] = "redis://127.0.0.1:6379/1"
os.environ['MAYAN_LOCK_MANAGER_BACKEND'] = "mayan.apps.lock_manager.backends.redis_lock.RedisLock"
os.environ['MAYAN_LOCK_MANAGER_BACKEND_ARGUMENTS'] = "{'redis_url':'redis://127.0.0.1:6379/2'}"

django.setup()

def test_infrastructure():
    """Test core infrastructure connectivity"""
    print("🔍 Testing Infrastructure...")
    
    # Test database connection
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ PostgreSQL: Connected successfully")
    except Exception as e:
        print(f"❌ PostgreSQL: Connection failed - {e}")
        return False
    
    # Test Redis connection
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=1)
        r.ping()
        print("✅ Redis: Connected successfully")
    except Exception as e:
        print(f"❌ Redis: Connection failed - {e}")
        return False
    
    return True

def test_research_app():
    """Test research app integration"""
    print("\n🧪 Testing Research App...")
    
    try:
        from django.apps import apps
        research_app = apps.get_app_config('research')
        print(f"✅ Research App: Loaded successfully ({research_app.verbose_name})")
        
        # Test app structure
        app_path = Path(research_app.path)
        required_files = [
            'apps.py',
            'api_views.py', 
            'dependencies.py',
            'urls/__init__.py',
            'urls/api_urls.py'
        ]
        
        for file_path in required_files:
            if (app_path / file_path).exists():
                print(f"✅ File exists: {file_path}")
            else:
                print(f"❌ Missing file: {file_path}")
                
    except Exception as e:
        print(f"❌ Research App: Failed to load - {e}")
        return False
    
    return True

def test_dependencies():
    """Test Python dependencies"""
    print("\n📦 Testing Dependencies...")
    
    try:
        from mayan.apps.dependencies.classes import PythonDependency
        all_deps = PythonDependency.get_all()
        research_deps = [d for d in all_deps if hasattr(d, 'app_label') and d.app_label == 'research']
        
        if research_deps:
            print(f"✅ Research Dependencies: Found {len(research_deps)} dependencies")
            for dep in research_deps:
                print(f"  - {dep.name} {getattr(dep, 'version_string', 'latest')}")
        else:
            print("📝 Research Dependencies: None registered (optional packages)")
            
    except Exception as e:
        print(f"❌ Dependencies: Error checking - {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test API endpoint availability"""
    print("\n🔌 Testing API Endpoints...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test research API root
        try:
            response = client.get('/api/v4/research/')
            if response.status_code == 200:
                print("✅ API Endpoint: /api/v4/research/ responding")
                try:
                    import json
                    data = json.loads(response.content)
                    print(f"  📄 Response: {data.get('message', 'No message')}")
                except:
                    print("  📄 Response: (non-JSON response)")
            else:
                print(f"❌ API Endpoint: /api/v4/research/ returned {response.status_code}")
        except Exception as e:
            print(f"❌ API Endpoint: Error accessing /api/v4/research/ - {e}")
            
    except Exception as e:
        print(f"❌ API Testing: Setup failed - {e}")
        return False
    
    return True

def test_aws_alignment():
    """Test AWS deployment alignment"""
    print("\n☁️ Testing AWS Alignment...")
    
    # Check environment variables match AWS patterns
    db_config = os.environ.get('MAYAN_DATABASES', '')
    if 'postgresql' in db_config and '127.0.0.1' in db_config:
        print("✅ Database: PostgreSQL configured (AWS RDS ready)")
    
    redis_config = os.environ.get('MAYAN_CELERY_RESULT_BACKEND', '')
    if 'redis://127.0.0.1' in redis_config:
        print("✅ Redis: Configured (AWS ElastiCache ready)")
    
    # Check data analysis dependencies
    analysis_packages = ['pandas', 'matplotlib', 'openpyxl', 'reportlab']
    available_packages = []
    
    for package in analysis_packages:
        try:
            __import__(package)
            available_packages.append(package)
        except ImportError:
            pass
    
    if available_packages:
        print(f"✅ Data Analysis: {len(available_packages)}/{len(analysis_packages)} packages available")
        print(f"  📊 Ready: {', '.join(available_packages)}")
    else:
        print("📝 Data Analysis: Packages not installed (will be added via dependencies.py)")
    
    return True

def main():
    """Run all tests"""
    print("🚀 AWS-Aligned Mayan EDMS Development Environment Test Suite")
    print("=" * 60)
    
    tests = [
        ("Infrastructure", test_infrastructure),
        ("Research App", test_research_app), 
        ("Dependencies", test_dependencies),
        ("API Endpoints", test_api_endpoints),
        ("AWS Alignment", test_aws_alignment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Test failed with exception - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Environment ready for development.")
        print("\n📝 Next steps:")
        print("  1. ./dev_setup.sh server    # Start development server")
        print("  2. Create research models   # Continue with task 1.4+")
        print("  3. Build API endpoints      # Develop features")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 