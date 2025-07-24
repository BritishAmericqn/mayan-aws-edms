from rest_framework.response import Response
from rest_framework.views import APIView

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
    DatasetDocumentSerializer
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


class APIDatasetAnalysisView(APIView):
    """
    get: Return analysis results for the selected dataset.
    post: Trigger analysis for the selected dataset.
    """
    mayan_object_permission_map = {
        'GET': permission_dataset_view,
        'POST': permission_dataset_analyze
    }
    
    def get_dataset(self):
        """Get the dataset object from URL parameter."""
        dataset_id = self.kwargs.get('dataset_id')
        return Dataset.objects.get(pk=dataset_id)
    
    def get(self, request, dataset_id):
        """Return analysis results for the dataset."""
        dataset = self.get_dataset()
        return Response({
            'dataset_id': dataset.pk,
            'title': dataset.title,
            'analysis_status': dataset.analysis_status,
            'analysis_results': dataset.analysis_results or {},
            'last_analyzed': dataset.datetime_modified.isoformat() if dataset.datetime_modified else None
        })
    
    def post(self, request, dataset_id):
        """Trigger analysis for the dataset."""
        dataset = self.get_dataset()
        
        # For demo purposes, return immediate mock analysis
        # In production, this would trigger an async task
        mock_analysis = {
            'status': 'completed',
            'row_count': 1000,
            'column_count': 8,
            'data_quality': {
                'missing_values': 0.05,
                'data_types': ['numeric', 'categorical', 'datetime'],
                'completeness': 0.95
            },
            'summary_stats': {
                'mean_age': 42.5,
                'std_age': 12.3,
                'categories': ['A', 'B', 'C']
            }
        }
        
        dataset.analysis_status = 'completed'
        dataset.analysis_results = mock_analysis
        dataset.save()
        
        return Response({
            'message': 'Analysis completed successfully',
            'dataset_id': dataset.pk,
            'results': mock_analysis
        })


class APIDatasetDocumentListView(generics.ListAPIView):
    """
    get: Returns a list of documents associated with the selected dataset.
    """
    mayan_object_permission_map = {'GET': permission_dataset_view}
    serializer_class = DatasetDocumentSerializer
    
    def get_source_queryset(self):
        dataset_id = self.kwargs.get('dataset_id')
        return DatasetDocument.objects.filter(dataset_id=dataset_id) 