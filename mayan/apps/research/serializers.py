from rest_framework import serializers

from mayan.apps.documents.serializers.document_serializers import DocumentSerializer

from .models import Project, Study, Dataset, DatasetDocument


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    
    studies_count = serializers.SerializerMethodField()
    datasets_count = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = (
            'id', 'title', 'description', 'principal_investigator',
            'institution', 'status', 'start_date', 'end_date',
            'funding_source', 'funding_amount', 'datetime_created',
            'datetime_modified', 'studies_count', 'datasets_count', 'url'
        )
        read_only_fields = ('id', 'datetime_created', 'datetime_modified')
    
    def get_studies_count(self, instance):
        """Return the count of studies in this project."""
        return instance.studies_count
    
    def get_datasets_count(self, instance):
        """Return the total count of datasets in this project."""
        return instance.datasets_count
    
    def get_url(self, instance):
        """Return the URL for this project."""
        from django.urls import reverse
        return reverse(
            'rest_api:project-detail', 
            kwargs={'project_id': instance.pk},
            request=self.context.get('request')
        )


class StudySerializer(serializers.ModelSerializer):
    """Serializer for Study model."""
    
    project_title = serializers.CharField(source='project.title', read_only=True)
    datasets_count = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Study
        fields = (
            'id', 'title', 'description', 'project', 'project_title',
            'status', 'study_type', 'methodology', 'start_date', 'end_date',
            'datetime_created', 'datetime_modified', 'datasets_count', 'url'
        )
        read_only_fields = ('id', 'datetime_created', 'datetime_modified')
    
    def get_datasets_count(self, instance):
        """Return the count of datasets in this study."""
        return instance.datasets.count()
    
    def get_url(self, instance):
        """Return the URL for this study."""
        from django.urls import reverse
        return reverse(
            'rest_api:study-detail',
            kwargs={'study_id': instance.pk},
            request=self.context.get('request')
        )


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset model."""
    
    study_title = serializers.CharField(source='study.title', read_only=True)
    project_title = serializers.CharField(source='study.project.title', read_only=True)
    document_count = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = (
            'id', 'title', 'description', 'study', 'study_title', 'project_title',
            'status', 'data_type', 'format', 'size_bytes', 'analysis_status',
            'analysis_results', 'datetime_created', 'datetime_modified',
            'document_count', 'url'
        )
        read_only_fields = ('id', 'datetime_created', 'datetime_modified')
    
    def get_document_count(self, instance):
        """Return the count of documents in this dataset."""
        return instance.documents.count()
    
    def get_url(self, instance):
        """Return the URL for this dataset."""
        from django.urls import reverse
        return reverse(
            'rest_api:dataset-detail',
            kwargs={'dataset_id': instance.pk},
            request=self.context.get('request')
        )


class DatasetDocumentSerializer(serializers.ModelSerializer):
    """Serializer for DatasetDocument model."""
    
    dataset_title = serializers.CharField(source='dataset.title', read_only=True)
    document_details = DocumentSerializer(source='document', read_only=True)
    
    class Meta:
        model = DatasetDocument
        fields = (
            'id', 'dataset', 'dataset_title', 'document', 'document_details',
            'role', 'order', 'notes', 'datetime_added'
        )
        read_only_fields = ('id', 'datetime_added') 