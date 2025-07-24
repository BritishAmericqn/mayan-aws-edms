from django.urls import re_path

from ..views import (
    # Project views
    ProjectListView, ProjectDetailView, ProjectCreateView, 
    ProjectEditView, ProjectDeleteView,
    
    # Study views  
    StudyListView, StudyDetailView, StudyCreateView,
    StudyEditView, StudyDeleteView,
    
    # Dataset views
    DatasetListView, DatasetDetailView, DatasetCreateView,
    DatasetEditView, DatasetDeleteView
)

app_name = 'research'

urlpatterns = [
    # Project URLs
    re_path(
        route=r'^projects/$',
        view=ProjectListView.as_view(),
        name='project_list'
    ),
    re_path(
        route=r'^projects/create/$',
        view=ProjectCreateView.as_view(),
        name='project_create'
    ),
    re_path(
        route=r'^projects/(?P<project_id>\d+)/$',
        view=ProjectDetailView.as_view(),
        name='project_detail'
    ),
    re_path(
        route=r'^projects/(?P<project_id>\d+)/edit/$',
        view=ProjectEditView.as_view(),
        name='project_edit'
    ),
    re_path(
        route=r'^projects/(?P<project_id>\d+)/delete/$',
        view=ProjectDeleteView.as_view(),
        name='project_delete'
    ),
    
    # Study URLs
    re_path(
        route=r'^projects/(?P<project_id>\d+)/studies/$',
        view=StudyListView.as_view(),
        name='study_list'
    ),
    re_path(
        route=r'^projects/(?P<project_id>\d+)/studies/create/$',
        view=StudyCreateView.as_view(),
        name='study_create'
    ),
    re_path(
        route=r'^studies/(?P<study_id>\d+)/$',
        view=StudyDetailView.as_view(),
        name='study_detail'
    ),
    re_path(
        route=r'^studies/(?P<study_id>\d+)/edit/$',
        view=StudyEditView.as_view(),
        name='study_edit'
    ),
    re_path(
        route=r'^studies/(?P<study_id>\d+)/delete/$',
        view=StudyDeleteView.as_view(),
        name='study_delete'
    ),
    
    # Dataset URLs
    re_path(
        route=r'^studies/(?P<study_id>\d+)/datasets/$',
        view=DatasetListView.as_view(),
        name='dataset_list'
    ),
    re_path(
        route=r'^studies/(?P<study_id>\d+)/datasets/create/$',
        view=DatasetCreateView.as_view(),
        name='dataset_create'
    ),
    re_path(
        route=r'^datasets/(?P<dataset_id>\d+)/$',
        view=DatasetDetailView.as_view(),
        name='dataset_detail'
    ),
    re_path(
        route=r'^datasets/(?P<dataset_id>\d+)/edit/$',
        view=DatasetEditView.as_view(),
        name='dataset_edit'
    ),
    re_path(
        route=r'^datasets/(?P<dataset_id>\d+)/delete/$',
        view=DatasetDeleteView.as_view(),
        name='dataset_delete'
    ),
] 