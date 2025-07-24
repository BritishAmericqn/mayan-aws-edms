from django.urls import re_path

from ..api_views import (
    APIResearchRootView,
    APIProjectListView, APIProjectDetailView,
    APIStudyListView, APIStudyDetailView,
    APIDatasetListView, APIDatasetDetailView,
    APIDatasetAnalysisView, APIDatasetDocumentListView
)

app_name = 'research'

urlpatterns = [
    re_path(
        route=r'^$',
        view=APIResearchRootView.as_view(),
        name='research-root'
    ),
    
    # Project endpoints
    re_path(
        route=r'^projects/$', name='project-list',
        view=APIProjectListView.as_view()
    ),
    re_path(
        route=r'^projects/(?P<project_id>[0-9]+)/$', name='project-detail',
        view=APIProjectDetailView.as_view()
    ),
    
    # Study endpoints
    re_path(
        route=r'^studies/$', name='study-list',
        view=APIStudyListView.as_view()
    ),
    re_path(
        route=r'^studies/(?P<study_id>[0-9]+)/$', name='study-detail',
        view=APIStudyDetailView.as_view()
    ),
    re_path(
        route=r'^projects/(?P<project_id>[0-9]+)/studies/$', name='project-study-list',
        view=APIStudyListView.as_view()
    ),
    
    # Dataset endpoints
    re_path(
        route=r'^datasets/$', name='dataset-list',
        view=APIDatasetListView.as_view()
    ),
    re_path(
        route=r'^datasets/(?P<dataset_id>[0-9]+)/$', name='dataset-detail',
        view=APIDatasetDetailView.as_view()
    ),
    re_path(
        route=r'^studies/(?P<study_id>[0-9]+)/datasets/$', name='study-dataset-list',
        view=APIDatasetListView.as_view()
    ),
    
    # Dataset analysis and documents
    re_path(
        route=r'^datasets/(?P<dataset_id>[0-9]+)/analysis/$', name='dataset-analysis',
        view=APIDatasetAnalysisView.as_view()
    ),
    re_path(
        route=r'^datasets/(?P<dataset_id>[0-9]+)/documents/$', name='dataset-document-list',
        view=APIDatasetDocumentListView.as_view()
    ),
] 