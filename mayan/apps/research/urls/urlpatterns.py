from django.urls import re_path

from ..views import (
    DatasetDeleteView, DatasetDetailView, DatasetEditView, DatasetCreateView,
    DatasetListView, ProjectCreateView, ProjectDeleteView, ProjectDetailView,
    ProjectEditView, ProjectListView, StudyCreateView, StudyDeleteView,
    StudyDetailView, StudyEditView, StudyListView
)

# Tasks 3.2-3.3: Import sharing and public views
from ..views import sharing_views, public_views

# Task 3.5: Compliance dashboard URLs
from ..views import compliance_views

# Task 3.6: PDF Report URLs
from ..views import report_views

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

    # Task 3.5: Compliance dashboard URLs
    re_path(
        route=r'^compliance/dashboard/$',
        view=compliance_views.ComplianceDashboardView.as_view(),
        name='compliance_dashboard'
    ),
    re_path(
        route=r'^compliance/api/$',
        view=compliance_views.ComplianceAPIView.as_view(),
        name='compliance_api'
    ),

    # Task 3.6: PDF Report URLs
    re_path(
        route=r'^reports/$',
        view=report_views.ReportDashboardView.as_view(),
        name='report_dashboard'
    ),
    re_path(
        route=r'^reports/request/$',
        view=report_views.ReportRequestView.as_view(),
        name='report_request'
    ),
    re_path(
        route=r'^reports/list/$',
        view=report_views.ReportListView.as_view(),
        name='report_list'
    ),
    
    # Individual report management
    re_path(
        route=r'^reports/(?P<report_id>\d+)/$',
        view=report_views.ReportDetailView.as_view(),
        name='report_detail'
    ),
    re_path(
        route=r'^reports/(?P<report_id>\d+)/download/$',
        view=report_views.ReportDownloadView.as_view(),
        name='report_download'
    ),
    re_path(
        route=r'^reports/(?P<report_id>\d+)/delete/$',
        view=report_views.ReportDeleteView.as_view(),
        name='report_delete'
    ),
    
    # AJAX and API endpoints
    re_path(
        route=r'^reports/quick-generate/$',
        view=report_views.QuickReportView.as_view(),
        name='report_quick_generate'
    ),
    re_path(
        route=r'^reports/(?P<report_id>\d+)/status/$',
        view=report_views.ReportStatusAPIView.as_view(),
        name='report_status_api'
    ),
    
    # Project-specific reports
    re_path(
        route=r'^projects/(?P<project_id>\d+)/report/$',
        view=report_views.ProjectReportView.as_view(),
        name='project_report'
    ),
    
    # Tasks 3.2-3.3: Sharing URLs (authenticated users only)
    re_path(
        route=r'^documents/(?P<document_id>\d+)/share/$',
        view=sharing_views.DocumentShareView.as_view(),
        name='document_share'
    ),
    re_path(
        route=r'^documents/(?P<document_id>\d+)/quick-share/$',
        view=sharing_views.DocumentQuickShareView.as_view(),
        name='document_quick_share'
    ),
    re_path(
        route=r'^documents/(?P<document_id>\d+)/share/success/$',
        view=sharing_views.DocumentShareSuccessView.as_view(),
        name='document_share_success'
    ),
    re_path(
        route=r'^shared-documents/$',
        view=sharing_views.SharedDocumentListView.as_view(),
        name='shared_document_list'
    ),
] 

# Public URLs that need to be at root level (NO authentication required)
passthru_urlpatterns = [
    re_path(
        route=r'^test-public/$',
        view=public_views.TestPublicView.as_view(),
        name='test_public'
    ),
    re_path(
        route=r'^shared/(?P<url_key>[0-9a-f-]+)/$',
        view=public_views.SharedDocumentAccessView.as_view(),
        name='shared_document_access'
    ),
    re_path(
        route=r'^shared/(?P<url_key>[0-9a-f-]+)/download/$',
        view=public_views.SharedDocumentDownloadView.as_view(),
        name='shared_document_download'
    ),
    re_path(
        route=r'^shared/(?P<url_key>[0-9a-f-]+)/preview/$',
        view=public_views.SharedDocumentPreviewView.as_view(),
        name='shared_document_preview'
    ),
] 

# Task 3.5: Compliance dashboard URLs
urlpatterns.extend([
    re_path(
        route=r'^compliance/dashboard/$',
        view=compliance_views.ComplianceDashboardView.as_view(),
        name='compliance_dashboard'
    ),
    re_path(
        route=r'^compliance/api/$',
        view=compliance_views.ComplianceAPIView.as_view(),
        name='compliance_api'
    ),
])

# Task 3.6: PDF Report URLs
urlpatterns.extend([
    # Report dashboard and management
    re_path(
        route=r'^reports/$',
        view=report_views.ReportDashboardView.as_view(),
        name='report_dashboard'
    ),
    re_path(
        route=r'^reports/request/$',
        view=report_views.ReportRequestView.as_view(),
        name='report_request'
    ),
    re_path(
        route=r'^reports/list/$',
        view=report_views.ReportListView.as_view(),
        name='report_list'
    ),
    
    # Individual report management
    re_path(
        route=r'^reports/(?P<report_id>\d+)/$',
        view=report_views.ReportDetailView.as_view(),
        name='report_detail'
    ),
    re_path(
        route=r'^reports/(?P<report_id>\d+)/download/$',
        view=report_views.ReportDownloadView.as_view(),
        name='report_download'
    ),
    re_path(
        route=r'^reports/(?P<report_id>\d+)/delete/$',
        view=report_views.ReportDeleteView.as_view(),
        name='report_delete'
    ),
    
    # AJAX and API endpoints
    re_path(
        route=r'^reports/quick-generate/$',
        view=report_views.QuickReportView.as_view(),
        name='report_quick_generate'
    ),
    re_path(
        route=r'^reports/(?P<report_id>\d+)/status/$',
        view=report_views.ReportStatusAPIView.as_view(),
        name='report_status_api'
    ),
    
    # Project-specific reports
    re_path(
        route=r'^projects/(?P<project_id>\d+)/report/$',
        view=report_views.ProjectReportView.as_view(),
        name='project_report'
    ),
]) 