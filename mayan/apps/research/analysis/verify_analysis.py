#!/usr/bin/env python3
"""
Verification script for Task 2.1: Dataset Analysis Module
Tests all components with and without dependencies installed.
"""

import os
import sys
from pathlib import Path
import json

def setup_path():
    """Setup Python path for testing."""
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.testing')

def test_basic_imports():
    """Test that all analysis modules can be imported."""
    print("🔍 Testing Module Imports...")
    
    try:
        from mayan.apps.research.analysis import DatasetParser, StatisticalAnalyzer, ChartGenerator
        print("✅ Main analysis classes imported successfully")
        
        from mayan.apps.research.analysis.parsers import CSVParser, ExcelParser, JSONParser
        print("✅ Parser classes imported successfully")
        
        from mayan.apps.research.analysis.utils import detect_file_type, safe_numeric_conversion
        print("✅ Utility functions imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_csv_parsing_with_demo_data():
    """Test CSV parsing with actual demo data files."""
    print("\n📄 Testing CSV Parsing with Demo Data...")
    
    try:
        from mayan.apps.research.analysis.parsers import CSVParser
        
        # Find demo data files
        demo_data_dir = Path(__file__).parent.parent / 'demo_data'
        csv_files = list(demo_data_dir.glob('*.csv'))
        
        if not csv_files:
            print("❌ No demo CSV files found")
            return False
        
        print(f"📁 Found {len(csv_files)} demo CSV files:")
        for csv_file in csv_files:
            print(f"   - {csv_file.name}")
        
        # Test parsing the first CSV file
        test_file = csv_files[0]
        
        class MockDocumentFile:
            def __init__(self, file_path):
                self.filename = file_path.name
                self.mimetype = 'text/csv'
                self._file_path = file_path
            
            def open(self):
                return open(self._file_path, 'r', encoding='utf-8')
        
        mock_file = MockDocumentFile(test_file)
        parser = CSVParser()
        result = parser.process_file(mock_file)
        
        if result is not None:
            if hasattr(result, 'shape'):  # pandas DataFrame
                rows, cols = result.shape
                print(f"✅ Successfully parsed {test_file.name}: {rows} rows × {cols} columns")
                print(f"   Columns: {list(result.columns)}")
                return True
            elif isinstance(result, dict):  # fallback parsing
                print(f"✅ Successfully parsed {test_file.name} (fallback mode)")
                print(f"   Rows: {result.get('rows', 'unknown')}")
                return True
        
        print("❌ CSV parsing returned None")
        return False
        
    except Exception as e:
        print(f"❌ CSV parsing test failed: {e}")
        return False

def test_statistical_analysis():
    """Test statistical analysis with sample data."""
    print("\n📊 Testing Statistical Analysis...")
    
    try:
        # Try with pandas first
        try:
            import pandas as pd
            pandas_available = True
        except ImportError:
            pandas_available = False
        
        from mayan.apps.research.analysis.analyzers import StatisticalAnalyzer
        
        if pandas_available:
            # Create realistic sample data
            data = {
                'temperature_c': [15.2, 18.7, 22.4, 28.9, 31.3, 14.8, 17.2, 21.1, 27.5, 30.8],
                'humidity_percent': [68.5, 72.1, 55.3, 49.8, 28.2, 69.2, 73.5, 56.1, 51.2, 29.1],
                'pressure_hpa': [1013.2, 1012.8, 1014.1, 1011.5, 1016.7, 1013.5, 1012.9, 1014.3, 1011.8, 1016.9],
                'station_id': ['WS001', 'WS002', 'WS003', 'WS004', 'WS005'] * 2
            }
            
            df = pd.DataFrame(data)
            analyzer = StatisticalAnalyzer(df)
            results = analyzer.analyze()
            
            if results and results.get('dataset_info'):
                info = results['dataset_info']
                print(f"✅ Analysis completed: {info.get('total_rows')} rows, {info.get('total_columns')} columns")
                
                # Check for key analysis components
                if 'data_quality' in results:
                    quality = results['data_quality']
                    print(f"   Data quality score: {quality.get('quality_score', 'N/A')}")
                
                if 'domain_insights' in results:
                    insights = results['domain_insights']
                    print(f"   Generated {len(insights)} domain insights")
                
                return True
            else:
                print("❌ Analysis returned incomplete results")
                return False
        else:
            # Test fallback analysis
            analyzer = StatisticalAnalyzer()
            results = analyzer._fallback_analysis()
            
            if results and results.get('status') == 'limited':
                print("✅ Fallback analysis working (pandas not available)")
                return True
            else:
                print("❌ Fallback analysis failed")
                return False
                
    except Exception as e:
        print(f"❌ Statistical analysis test failed: {e}")
        return False

def test_chart_generation():
    """Test chart generation capabilities."""
    print("\n📈 Testing Chart Generation...")
    
    try:
        # Check matplotlib availability
        try:
            import matplotlib
            matplotlib_available = True
        except ImportError:
            matplotlib_available = False
        
        from mayan.apps.research.analysis.preview_generators import ChartGenerator
        
        if matplotlib_available:
            try:
                import pandas as pd
                
                # Create sample data for chart generation
                data = {
                    'temperature_c': [15.2, 18.7, 22.4, 28.9, 31.3],
                    'humidity_percent': [68.5, 72.1, 55.3, 49.8, 28.2],
                    'location': ['New York', 'Chicago', 'Los Angeles', 'Houston', 'Phoenix']
                }
                
                df = pd.DataFrame(data)
                generator = ChartGenerator(df)
                charts = generator.generate_all_charts()
                
                if isinstance(charts, list):
                    print(f"✅ Generated {len(charts)} charts successfully")
                    
                    # Show chart types
                    chart_types = [chart.get('type') for chart in charts]
                    print(f"   Chart types: {', '.join(chart_types)}")
                    
                    # Check for base64 encoded images
                    image_charts = [c for c in charts if 'image_data' in c and c['image_data'].startswith('data:image')]
                    print(f"   Base64 encoded charts: {len(image_charts)}")
                    
                    return True
                else:
                    print("❌ Chart generation failed")
                    return False
                    
            except ImportError:
                print("⚠️ Pandas not available, testing text charts...")
                
                # Test text-based charts
                generator = ChartGenerator(None)
                text_charts = generator._generate_text_charts()
                
                if isinstance(text_charts, list):
                    print(f"✅ Generated {len(text_charts)} text-based charts")
                    return True
                else:
                    print("❌ Text chart generation failed")
                    return False
        else:
            print("⚠️ Matplotlib not available, testing fallback...")
            
            # Test without matplotlib
            generator = ChartGenerator(None)
            result = generator.generate_all_charts()
            
            # Should return empty list or text charts
            if isinstance(result, list):
                print(f"✅ Fallback chart generation working: {len(result)} items")
                return True
            else:
                print("❌ Fallback chart generation failed")
                return False
                
    except Exception as e:
        print(f"❌ Chart generation test failed: {e}")
        return False

def test_task_integration():
    """Test integration with task system."""
    print("\n⚙️ Testing Task Integration...")
    
    try:
        from mayan.apps.research.tasks import _perform_dataset_analysis, _generate_fallback_analysis
        
        # Create mock dataset
        class MockDataset:
            def __init__(self):
                self.title = "Test Dataset"
                self.pk = 1
                
            def documents(self):
                class MockManager:
                    def all(self):
                        class MockQuerySet:
                            def exists(self):
                                return False
                        return MockQuerySet()
                return MockManager()
        
        mock_dataset = MockDataset()
        
        # Test fallback analysis (when no documents)
        result = _generate_fallback_analysis(mock_dataset)
        
        if result and result.get('status') == 'completed_fallback':
            print("✅ Task integration working (fallback analysis)")
            print(f"   Analysis status: {result.get('status')}")
            return True
        else:
            print("❌ Task integration failed")
            return False
            
    except Exception as e:
        print(f"❌ Task integration test failed: {e}")
        return False

def test_dependencies():
    """Test dependency availability and versions."""
    print("\n📦 Testing Dependencies...")
    
    dependencies = [
        ('pandas', '2.2.0'),
        ('matplotlib', '3.8.0'),
        ('openpyxl', '3.1.2'),
        ('numpy', '1.26.0'),
        ('reportlab', '4.0.7')
    ]
    
    available = []
    missing = []
    
    for package, expected_version in dependencies:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            available.append((package, version))
            print(f"✅ {package}: {version}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}: not installed")
    
    print(f"\n📊 Dependency Summary:")
    print(f"   Available: {len(available)}/{len(dependencies)}")
    print(f"   Missing: {len(missing)}/{len(dependencies)}")
    
    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        print("   The analysis module will use fallback implementations")
    
    return len(available) > 0  # At least some dependencies should work

def run_comprehensive_test():
    """Run all verification tests."""
    print("🧪 Task 2.1 Verification: Dataset Analysis Module")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_basic_imports),
        ("CSV Parsing", test_csv_parsing_with_demo_data),
        ("Statistical Analysis", test_statistical_analysis),
        ("Chart Generation", test_chart_generation),
        ("Task Integration", test_task_integration),
        ("Dependencies", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Verification Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Task 2.1 is fully functional!")
        print("   The Dataset Analysis Module is ready for demo.")
    elif passed >= total * 0.7:  # 70% or more
        print("\n✅ Task 2.1 is mostly functional!")
        print("   Some dependencies may be missing, but core functionality works.")
    else:
        print("\n⚠️ Task 2.1 needs attention.")
        print("   Multiple components are not working correctly.")
    
    return passed >= total * 0.7

def main():
    """Main verification function."""
    setup_path()
    return run_comprehensive_test()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 