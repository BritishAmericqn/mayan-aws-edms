from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from mayan.apps.rest_api import generics

from .models import Project, Study, Dataset, DatasetDocument
from .permissions import (
    permission_project_view, permission_project_create, 
    permission_project_edit, permission_project_delete,
    permission_study_view, permission_study_create,
    permission_study_edit, permission_study_delete,
    permission_dataset_view, permission_dataset_create,
    permission_dataset_edit, permission_dataset_delete,
    permission_dataset_analyze
)
from .serializers import (
    ProjectSerializer, StudySerializer, DatasetSerializer,
    DatasetDocumentSerializer, DatasetAnalysisSerializer
)
from .literals import (
    ANALYSIS_STATUS_PENDING, ANALYSIS_STATUS_PROCESSING, 
    ANALYSIS_STATUS_COMPLETED, ANALYSIS_STATUS_FAILED
)


class APIResearchRootView(APIView):
    """
    Root endpoint for the Research app API.
    """
    def get(self, request, *args, **kwargs):
        """Return API information for the Research app."""
        return Response({
            'message': 'Research API Root',
            'version': '1.0',
            'endpoints': {
                'projects': request.build_absolute_uri('/api/v4/research/projects/'),
                'studies': request.build_absolute_uri('/api/v4/research/studies/'),
                'datasets': request.build_absolute_uri('/api/v4/research/datasets/'),
            }
        })


# Project API Views
class APIProjectListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all research projects.
    post: Create a new research project.
    """
    mayan_object_permission_map = {
        'GET': permission_project_view,
        'POST': permission_project_create
    }
    serializer_class = ProjectSerializer
    
    def get_source_queryset(self):
        return Project.objects.all()


class APIProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected project.
    get: Return the details of the selected project.
    patch: Edit the selected project.
    put: Edit the selected project.
    """
    lookup_url_kwarg = 'project_id'
    mayan_object_permission_map = {
        'GET': permission_project_view,
        'PATCH': permission_project_edit,
        'PUT': permission_project_edit,
        'DELETE': permission_project_delete
    }
    serializer_class = ProjectSerializer
    
    def get_source_queryset(self):
        return Project.objects.all()


# Study API Views
class APIStudyListView(generics.ListCreateAPIView):
    """
    get: Returns a list of studies (optionally filtered by project).
    post: Create a new study.
    """
    mayan_object_permission_map = {
        'GET': permission_study_view,
        'POST': permission_study_create
    }
    serializer_class = StudySerializer
    
    def get_source_queryset(self):
        project_id = self.kwargs.get('project_id')
        queryset = Study.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset


class APIStudyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected study.
    get: Return the details of the selected study.
    patch: Edit the selected study.
    put: Edit the selected study.
    """
    lookup_url_kwarg = 'study_id'
    mayan_object_permission_map = {
        'GET': permission_study_view,
        'PATCH': permission_study_edit,
        'PUT': permission_study_edit,
        'DELETE': permission_study_delete
    }
    serializer_class = StudySerializer
    
    def get_source_queryset(self):
        return Study.objects.all()


# Dataset API Views
class APIDatasetListView(generics.ListCreateAPIView):
    """
    get: Returns a list of datasets (optionally filtered by study).
    post: Create a new dataset.
    """
    mayan_object_permission_map = {
        'GET': permission_dataset_view,
        'POST': permission_dataset_create
    }
    serializer_class = DatasetSerializer
    
    def get_source_queryset(self):
        study_id = self.kwargs.get('study_id')
        queryset = Dataset.objects.all()
        
        if study_id:
            queryset = queryset.filter(study_id=study_id)
            
        return queryset


class APIDatasetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected dataset.
    get: Return the details of the selected dataset.
    patch: Edit the selected dataset.
    put: Edit the selected dataset.
    """
    lookup_url_kwarg = 'dataset_id'
    mayan_object_permission_map = {
        'GET': permission_dataset_view,
        'PATCH': permission_dataset_edit,
        'PUT': permission_dataset_edit,
        'DELETE': permission_dataset_delete
    }
    serializer_class = DatasetSerializer
    
    def get_source_queryset(self):
        return Dataset.objects.all()


class APIDatasetAnalysisView(generics.ObjectActionAPIView):
    """
    Enhanced Analysis API View following proper Mayan patterns.
    
    get: Return analysis results for the selected dataset.
    post: Trigger analysis for the selected dataset using real task system.
    """
    action_response_status = status.HTTP_202_ACCEPTED
    lookup_url_kwarg = 'dataset_id'
    mayan_object_permission_map = {
        'GET': permission_dataset_view,
        'POST': permission_dataset_analyze
    }
    serializer_class = DatasetAnalysisSerializer
    source_queryset = Dataset.objects.all()
    
    def get(self, request, *args, **kwargs):
        """Return analysis results for the dataset."""
        try:
            dataset = self.get_object()
            
            # Get analysis status and results from extra_data or model fields
            analysis_status = getattr(dataset, 'analysis_status', ANALYSIS_STATUS_PENDING)
            analysis_results = getattr(dataset, 'analysis_results', {})
            
            # Determine last analyzed timestamp
            last_analyzed = None
            if analysis_status == ANALYSIS_STATUS_COMPLETED and analysis_results:
                # Try to get timestamp from analysis results or model modification
                if isinstance(analysis_results, dict) and 'timestamp' in analysis_results:
                    last_analyzed = analysis_results['timestamp']
                else:
                    last_analyzed = dataset.datetime_modified.isoformat() if dataset.datetime_modified else None
            
            response_data = {
                'dataset_id': dataset.pk,
                'title': dataset.title,
                'analysis_status': analysis_status,
                'analysis_results': analysis_results or {},
                'last_analyzed': last_analyzed,
                'dataset_info': {
                    'study': dataset.study.title,
                    'project': dataset.study.project.title,
                    'document_count': dataset.documents.count(),
                    'status': dataset.status
                }
            }
            
            # Add demo-specific enhancements for fast response
            if analysis_status == ANALYSIS_STATUS_COMPLETED and analysis_results:
                # Extract key demo highlights for quick display
                if isinstance(analysis_results, dict):
                    demo_highlights = analysis_results.get('demo_highlights', {})
                    if demo_highlights:
                        response_data['demo_summary'] = {
                            'quality_grade': demo_highlights.get('key_metrics', {}).get('data_quality_grade', 'N/A'),
                            'analysis_readiness': demo_highlights.get('key_metrics', {}).get('analysis_readiness', 'Unknown'),
                            'standout_features': demo_highlights.get('standout_features', [])[:3]  # Top 3 for API
                        }
            
            return Response(response_data)
            
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error retrieving analysis results: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def object_action(self, obj, request, serializer):
        """
        Trigger analysis for the dataset using real task system.
        Follows Mayan's async task submission patterns.
        """
        try:
            from .tasks import task_analyze_dataset
            
            # Get validated data from serializer
            force_reanalysis = serializer.validated_data.get('force_reanalysis', False)
            analysis_options = serializer.validated_data.get('analysis_options', {})
            
            # Check if analysis is already in progress
            current_status = getattr(obj, 'analysis_status', ANALYSIS_STATUS_PENDING)
            if current_status == ANALYSIS_STATUS_PROCESSING and not force_reanalysis:
                return {
                    'message': 'Analysis already in progress',
                    'dataset_id': obj.pk,
                    'analysis_status': current_status,
                    'note': 'Use force_reanalysis=true to restart'
                }
            
            # Update status to processing immediately for responsive UI
            if hasattr(obj, 'analysis_status'):
                obj.analysis_status = ANALYSIS_STATUS_PROCESSING
            else:
                # Use extra_data if no direct field
                extra_data = getattr(obj, 'extra_data', {})
                extra_data['analysis_status'] = ANALYSIS_STATUS_PROCESSING
                obj.extra_data = extra_data
            
            obj.save()
            
            # Submit real analysis task (following Mayan patterns)
            task_analyze_dataset.apply_async(
                kwargs={
                    'dataset_id': obj.pk,
                    'user_id': request.user.pk,
                    'analysis_options': analysis_options
                }
            )
            
            # Return demo-optimized response for fast UI feedback
            return {
                'message': 'Dataset analysis started successfully',
                'dataset_id': obj.pk,
                'analysis_status': ANALYSIS_STATUS_PROCESSING,
                'estimated_completion': 'Analysis typically completes within 30 seconds',
                'next_steps': [
                    'Analysis is running in the background',
                    'Use GET endpoint to check results',
                    'Results will include comprehensive statistics and quality assessment'
                ],
                'demo_note': 'Enhanced analysis with Task 2.2 visual polish and quality indicators'
            }
            
        except Exception as e:
            # Update status to failed on error
            if hasattr(obj, 'analysis_status'):
                obj.analysis_status = ANALYSIS_STATUS_FAILED
            else:
                extra_data = getattr(obj, 'extra_data', {})
                extra_data['analysis_status'] = ANALYSIS_STATUS_FAILED
                obj.extra_data = extra_data
            obj.save()
            
            return Response(
                {'error': f'Failed to start analysis: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class APIDatasetDocumentListView(generics.ListAPIView):
    """
    get: Returns a list of documents associated with the selected dataset.
    """
    mayan_object_permission_map = {'GET': permission_dataset_view}
    serializer_class = DatasetDocumentSerializer
    
    def get_source_queryset(self):
        dataset_id = self.kwargs.get('dataset_id')
        return DatasetDocument.objects.filter(dataset_id=dataset_id) 