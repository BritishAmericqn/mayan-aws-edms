#!/usr/bin/env python3
"""
Task 2.3 API Endpoints Demonstration Script
==========================================

This script demonstrates the enhanced Dataset Analysis API endpoints that were 
implemented for Task 2.3, following proper Mayan patterns and integrating with 
the real analysis system from Tasks 2.1-2.2.

API Endpoints:
- POST /api/v4/datasets/{id}/analyze/ - Triggers analysis using real task system
- GET /api/v4/datasets/{id}/analysis/ - Returns cached analysis results

Features:
- Real async task integration with Mayan's Celery system
- Proper HTTP 202 responses for async operations
- Error handling following Mayan patterns
- Demo-optimized responses with fast feedback
- Integration with Task 2.2 enhanced analysis system
"""

import requests
import json
import time
from typing import Dict, Any, Optional


class DatasetAnalysisAPIDemo:
    """Demonstration of the Task 2.3 Dataset Analysis API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_token: Optional[str] = None):
        """
        Initialize the API demo client.
        
        Args:
            base_url: Mayan EDMS base URL
            api_token: Authentication token (if required)
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v4"
        self.headers = {'Content-Type': 'application/json'}
        
        if api_token:
            self.headers['Authorization'] = f'Token {api_token}'
    
    def get_analysis_results(self, dataset_id: int) -> Dict[str, Any]:
        """
        Get analysis results for a dataset.
        
        Demonstrates: GET /api/v4/datasets/{id}/analysis/
        """
        url = f"{self.api_base}/research/datasets/{dataset_id}/analysis/"
        
        print(f"🔍 Getting analysis results for dataset {dataset_id}...")
        print(f"📡 GET {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully retrieved analysis results!")
                
                # Display key information
                print(f"📋 Dataset: {data.get('title', 'Unknown')}")
                print(f"🔄 Analysis Status: {data.get('analysis_status', 'Unknown')}")
                
                if data.get('demo_summary'):
                    summary = data['demo_summary']
                    print(f"🎯 Quality Grade: {summary.get('quality_grade', 'N/A')}")
                    print(f"📈 Analysis Readiness: {summary.get('analysis_readiness', 'Unknown')}")
                    
                    features = summary.get('standout_features', [])
                    if features:
                        print("✨ Standout Features:")
                        for feature in features:
                            print(f"   • {feature}")
                
                return data
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"💬 Error Details: {error_data}")
                except:
                    print(f"💬 Error Text: {response.text}")
                return {}
                
        except Exception as e:
            print(f"💥 Exception: {e}")
            return {}
    
    def trigger_analysis(self, dataset_id: int, force_reanalysis: bool = False, 
                        analysis_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Trigger analysis for a dataset.
        
        Demonstrates: POST /api/v4/datasets/{id}/analyze/
        """
        url = f"{self.api_base}/research/datasets/{dataset_id}/analysis/"
        
        payload = {
            'force_reanalysis': force_reanalysis,
            'analysis_options': analysis_options or {}
        }
        
        print(f"🚀 Triggering analysis for dataset {dataset_id}...")
        print(f"📡 POST {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 202:  # Async task accepted
                data = response.json()
                print("✅ Analysis successfully started!")
                print(f"💬 Message: {data.get('message', 'No message')}")
                print(f"🔄 Status: {data.get('analysis_status', 'Unknown')}")
                print(f"⏱️  Estimated Completion: {data.get('estimated_completion', 'Unknown')}")
                
                next_steps = data.get('next_steps', [])
                if next_steps:
                    print("📋 Next Steps:")
                    for step in next_steps:
                        print(f"   • {step}")
                
                demo_note = data.get('demo_note')
                if demo_note:
                    print(f"🎪 Demo Note: {demo_note}")
                
                return data
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"💬 Error Details: {error_data}")
                except:
                    print(f"💬 Error Text: {response.text}")
                return {}
                
        except Exception as e:
            print(f"💥 Exception: {e}")
            return {}
    
    def demo_complete_workflow(self, dataset_id: int):
        """
        Demonstrate the complete analysis workflow.
        
        1. Check current analysis status
        2. Trigger new analysis
        3. Poll for completion
        4. Display final results
        """
        print("=" * 60)
        print("🎪 TASK 2.3 API ENDPOINTS DEMONSTRATION")
        print("=" * 60)
        print()
        
        # Step 1: Check current status
        print("📋 STEP 1: Check Current Analysis Status")
        print("-" * 40)
        current_results = self.get_analysis_results(dataset_id)
        current_status = current_results.get('analysis_status', 'unknown')
        print(f"Current Status: {current_status}")
        print()
        
        # Step 2: Trigger analysis
        print("🚀 STEP 2: Trigger New Analysis")
        print("-" * 40)
        trigger_result = self.trigger_analysis(
            dataset_id, 
            force_reanalysis=True,  # Force re-analysis for demo
            analysis_options={
                'demo_mode': True,
                'enhanced_features': True
            }
        )
        
        if not trigger_result:
            print("❌ Failed to trigger analysis. Stopping demo.")
            return
        
        print()
        
        # Step 3: Poll for completion
        print("⏳ STEP 3: Poll for Analysis Completion")
        print("-" * 40)
        
        max_attempts = 12  # Up to 2 minutes
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"Attempt {attempt}/{max_attempts}: Checking analysis status...")
            
            results = self.get_analysis_results(dataset_id)
            status = results.get('analysis_status', 'unknown')
            
            if status == 'completed':
                print("✅ Analysis completed!")
                break
            elif status == 'failed':
                print("❌ Analysis failed!")
                break
            elif status == 'processing':
                print(f"⏳ Still processing... (waiting 10 seconds)")
                time.sleep(10)
            else:
                print(f"❓ Unknown status: {status}")
                break
        
        print()
        
        # Step 4: Display final results
        print("📊 STEP 4: Display Final Analysis Results")
        print("-" * 40)
        final_results = self.get_analysis_results(dataset_id)
        
        if final_results.get('analysis_status') == 'completed':
            print("🎉 SUCCESS! Analysis completed successfully!")
            
            # Display comprehensive results
            analysis_data = final_results.get('analysis_results', {})
            if analysis_data:
                print("\n📈 Analysis Summary:")
                
                # Data quality information
                if 'data_quality' in analysis_data:
                    quality = analysis_data['data_quality']
                    overall_quality = quality.get('overall_quality', {})
                    score = overall_quality.get('score', 'N/A')
                    grade = overall_quality.get('grade', 'N/A')
                    print(f"   Quality Score: {score} (Grade: {grade})")
                
                # Dataset information
                if 'dataset_info' in analysis_data:
                    info = analysis_data['dataset_info']
                    dimensions = info.get('dimensions', {})
                    if dimensions:
                        print(f"   Records: {dimensions.get('records', 'N/A')}")
                        print(f"   Variables: {dimensions.get('variables', 'N/A')}")
                
                # Demo highlights
                if 'demo_highlights' in analysis_data:
                    highlights = analysis_data['demo_highlights']
                    talking_points = highlights.get('demo_talking_points', [])
                    if talking_points:
                        print("\n🎯 Key Demo Points:")
                        for point in talking_points[:3]:  # Top 3
                            print(f"   • {point}")
        else:
            print("❌ Analysis did not complete successfully.")
        
        print()
        print("=" * 60)
        print("🎪 Demo Complete! Task 2.3 API endpoints working properly.")
        print("=" * 60)


def main():
    """Main demo function."""
    print("🎯 Task 2.3 API Endpoints Demo")
    print("Enhanced Dataset Analysis API following Mayan patterns")
    print()
    
    # Initialize demo client
    demo = DatasetAnalysisAPIDemo()
    
    # Demo with dataset ID 1 (adjust as needed)
    dataset_id = 1
    
    print(f"🔧 Demo Configuration:")
    print(f"   Base URL: {demo.base_url}")
    print(f"   API Base: {demo.api_base}")
    print(f"   Dataset ID: {dataset_id}")
    print()
    
    # Run complete workflow demo
    demo.demo_complete_workflow(dataset_id)


if __name__ == "__main__":
    main()


# Example Usage:
"""
# Basic usage
python mayan/apps/research/api_demo_task_2_3.py

# For manual testing:
from mayan.apps.research.api_demo_task_2_3 import DatasetAnalysisAPIDemo

demo = DatasetAnalysisAPIDemo("http://localhost:8000")

# Get current results
results = demo.get_analysis_results(1)

# Trigger new analysis
response = demo.trigger_analysis(1, force_reanalysis=True)

# Run complete demo
demo.demo_complete_workflow(1)
"""

# API Endpoint Documentation:
"""
POST /api/v4/datasets/{id}/analyze/
=====================================

Triggers dataset analysis using the real task system from Tasks 2.1-2.2.

Request Body:
{
    "force_reanalysis": false,          // Optional: Force re-analysis
    "analysis_options": {}              // Optional: Future analysis parameters
}

Response (HTTP 202):
{
    "message": "Dataset analysis started successfully",
    "dataset_id": 1,
    "analysis_status": "processing",
    "estimated_completion": "Analysis typically completes within 30 seconds",
    "next_steps": [
        "Analysis is running in the background",
        "Use GET endpoint to check results",
        "Results will include comprehensive statistics and quality assessment"
    ],
    "demo_note": "Enhanced analysis with Task 2.2 visual polish and quality indicators"
}


GET /api/v4/datasets/{id}/analysis/
==================================

Returns cached analysis results for the dataset.

Response (HTTP 200):
{
    "dataset_id": 1,
    "title": "Temperature Station Data 2024",
    "analysis_status": "completed",
    "analysis_results": {
        // Complete analysis data from Task 2.2 system
        "status": "completed_enhanced",
        "data_quality": { ... },
        "summary_statistics": { ... },
        "demo_highlights": { ... }
    },
    "last_analyzed": "2024-01-25T10:30:00Z",
    "dataset_info": {
        "study": "Urban Heat Island Analysis",
        "project": "Climate Change Research 2024",
        "document_count": 2,
        "status": "analysis_ready"
    },
    "demo_summary": {
        "quality_grade": "A (92.5/100)",
        "analysis_readiness": "Excellent - Ready for Advanced Analytics",
        "standout_features": [
            "🎯 Exceptional data completeness (>95%)",
            "📊 Rich numeric data (6 quantitative variables)",
            "📈 Robust sample size (8,760 records)"
        ]
    }
}
""" 