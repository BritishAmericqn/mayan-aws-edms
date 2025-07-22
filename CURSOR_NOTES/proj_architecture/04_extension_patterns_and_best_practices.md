# 🛠️ Extension Patterns & Best Practices

> **Purpose**: Definitive guide for extending Mayan EDMS safely and efficiently  
> **Audience**: Developers implementing new features or modifications

## 🎯 Core Extension Principles

### 1. **Follow Mayan Patterns** 
Always extend using established Mayan patterns rather than inventing new ones.

### 2. **Respect Dependencies**
Understand and respect the app loading order and dependency hierarchy.

### 3. **Use Mayan Infrastructure**
Leverage existing systems for permissions, events, tasks, storage, etc.

### 4. **Maintain Backwards Compatibility**
Don't break existing functionality when extending.

## 🏗️ App Creation Pattern

### 1. App Structure Template
```
mayan/apps/our_extension/
├── __init__.py
├── apps.py                  # MayanAppConfig
├── models/
│   ├── __init__.py
│   ├── project_models.py    # Project model
│   ├── study_models.py      # Study model
│   └── dataset_models.py    # Dataset model
├── api_views/
│   ├── __init__.py
│   ├── project_api_views.py
│   └── dataset_api_views.py
├── serializers/
│   ├── __init__.py
│   └── project_serializers.py
├── permissions.py           # Permission definitions
├── events.py               # Event definitions
├── tasks.py                # Celery tasks
├── queues.py               # Task queue definitions
├── signals.py              # Signal definitions
├── handlers.py             # Signal handlers
├── views/
│   └── ...
├── templates/
│   └── ...
├── static/
│   └── ...
├── migrations/
│   └── ...
├── tests/
│   └── ...
└── urls/
    ├── __init__.py
    ├── api_urls.py
    └── urlpatterns.py
```

### 2. App Configuration
```python
# apps.py
from mayan.apps.app_manager.apps import MayanAppConfig

class OurExtensionApp(MayanAppConfig):
    app_namespace = 'our_extension'
    app_url = 'projects'  # URL prefix
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.our_extension'
    verbose_name = _('Project Management')

    def ready(self):
        super().ready()
        
        # 1. Import and register models
        from .models import Project, Study, Dataset
        
        # 2. Register permissions
        from .permissions import permission_project_view
        from mayan.apps.acls.classes import ModelPermission
        ModelPermission.register(
            model=Project,
            permissions=(permission_project_view, permission_project_edit)
        )
        
        # 3. Register events
        from .events import event_project_created
        
        # 4. Connect signals
        from django.db.models.signals import post_save
        from .handlers import handler_project_created
        post_save.connect(
            sender=Project,
            receiver=handler_project_created,
            dispatch_uid='our_extension_project_created'
        )
        
        # 5. Register search models
        from .search import project_search
        
        # 6. Register navigation
        from .links import link_project_list
        from mayan.apps.common.menus import menu_main
        menu_main.bind_links(links=(link_project_list,))
```

## 📊 Model Extension Patterns

### 1. Extending Document Relationships
```python
# models/dataset_models.py
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models import Document

class Dataset(ExtraDataModelMixin, models.Model):
    name = models.CharField(max_length=255)
    study = models.ForeignKey('Study', related_name='datasets')
    
    class Meta:
        ordering = ('name',)
        
    def __str__(self):
        return self.name

# Linking documents to datasets
class DatasetDocument(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='documents')
    document = models.ForeignKey(Document, related_name='datasets')
    added_by = models.ForeignKey(User)
    datetime_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('dataset', 'document')

# Add methods to Document model
def document_get_datasets(self):
    return Dataset.objects.filter(documents__document=self)

def document_get_projects(self):
    return Project.objects.filter(
        studies__datasets__documents__document=self
    ).distinct()

# Add to Document model in app ready()
Document.add_to_class('get_datasets', document_get_datasets)
Document.add_to_class('get_projects', document_get_projects)
```

### 2. Permission Integration
```python
# permissions.py
from django.utils.translation import gettext_lazy as _
from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_('Project management'), name='projects'
)

permission_project_view = namespace.add_permission(
    label=_('View projects'), name='project_view'
)
permission_project_edit = namespace.add_permission(
    label=_('Edit projects'), name='project_edit'
)
permission_dataset_create = namespace.add_permission(
    label=_('Create datasets'), name='dataset_create'
)

# Register in app ready()
ModelPermission.register(
    model=Project,
    permissions=(permission_project_view, permission_project_edit)
)

# Set up inheritance (datasets inherit from projects)
ModelPermission.register_inheritance(
    model=Dataset,
    related='study__project'
)
```

### 3. Event System Integration
```python
# events.py
from django.utils.translation import gettext_lazy as _
from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(
    label=_('Projects'), name='projects'
)

event_project_created = namespace.add_event_type(
    label=_('Project created'), name='project_created'
)
event_dataset_processed = namespace.add_event_type(
    label=_('Dataset processed'), name='dataset_processed'
)

# handlers.py
def handler_project_created(sender, instance, created, **kwargs):
    if created:
        event_project_created.commit(
            target=instance,
            actor=getattr(instance, '_event_actor', None)
        )

# Model integration
@method_event(
    event_manager_class=EventManagerSave,
    created={
        'event': event_dataset_processed,
        'target': 'self'
    }
)
def save(self, *args, **kwargs):
    return super().save(*args, **kwargs)

# Add to Dataset model
Dataset.add_to_class('save', save)
```

## 🔌 API Extension Patterns

### 1. REST API Views
```python
# api_views/project_api_views.py
from mayan.apps.rest_api import generics
from ..models import Project
from ..permissions import permission_project_view, permission_project_edit
from ..serializers import ProjectSerializer

class APIProjectListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all projects.
    post: Create a new project.
    """
    mayan_object_permission_map = {'GET': permission_project_view}
    mayan_view_permission_map = {'POST': permission_project_edit}
    serializer_class = ProjectSerializer
    source_queryset = Project.objects.all()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'created_by': self.request.user
        }

class APIProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected project.
    get: Return the details of the selected project.
    patch: Edit the selected project.
    put: Edit the selected project.
    """
    lookup_url_kwarg = 'project_id'
    mayan_object_permission_map = {
        'DELETE': permission_project_edit,
        'GET': permission_project_view,
        'PATCH': permission_project_edit,
        'PUT': permission_project_edit
    }
    serializer_class = ProjectSerializer
    source_queryset = Project.objects.all()
```

### 2. Nested Resource APIs
```python
# api_views/dataset_api_views.py
from mayan.apps.rest_api.api_view_mixins import ExternalObjectAPIViewMixin

class APIDatasetDocumentListView(
    ExternalObjectAPIViewMixin, generics.ListCreateAPIView
):
    """
    get: Returns documents in the dataset.
    post: Add a document to the dataset.
    """
    mayan_external_object_permission_map = {
        'GET': permission_dataset_view,
        'POST': permission_dataset_edit
    }
    serializer_class = DatasetDocumentSerializer

    def get_external_object(self):
        return get_object_or_404(Dataset, pk=self.kwargs['dataset_id'])

    def get_source_queryset(self):
        return self.get_external_object().documents.all()
```

### 3. Serializer Patterns
```python
# serializers/project_serializers.py
from mayan.apps.rest_api import serializers
from ..models import Project, Study, Dataset

class ProjectSerializer(serializers.ModelSerializer):
    study_count = serializers.SerializerMethodField()
    dataset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'created_by', 
            'datetime_created', 'study_count', 'dataset_count'
        )
        read_only_fields = ('id', 'created_by', 'datetime_created')

    def get_study_count(self, obj):
        return obj.studies.count()

    def get_dataset_count(self, obj):
        return Dataset.objects.filter(study__project=obj).count()

class StudySerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Study
        fields = ('id', 'name', 'description', 'project', 'project_name')
```

## 🎭 Task System Integration

### 1. Task Definition
```python
# tasks.py
from mayan.celery import app
from .models import Dataset

@app.task(bind=True, ignore_result=True)
def task_process_dataset(self, dataset_id, user_id=None):
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        
        # Heavy processing logic here
        # - Generate statistics
        # - Create previews
        # - Extract metadata
        
        if user_id:
            user = User.objects.get(pk=user_id)
            event_dataset_processed.commit(
                actor=user, target=dataset
            )
            
    except Exception as exc:
        # Retry on failure
        raise self.retry(exc=exc)

@app.task(ignore_result=True)
def task_generate_dataset_preview(dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    
    # Generate preview logic
    # - Statistics charts
    # - Document thumbnails
    # - Summary reports
```

### 2. Queue Registration
```python
# queues.py
from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_c, worker_d

# Medium priority queue for dataset operations
queue_datasets = CeleryQueue(
    label=_('Datasets'), name='datasets', worker=worker_c
)

# Heavy processing queue for data analysis
queue_data_processing = CeleryQueue(
    label=_('Data processing'), name='data_processing', worker=worker_d
)

queue_datasets.add_task_type(
    dotted_path='mayan.apps.our_extension.tasks.task_process_dataset',
    label=_('Process dataset'),
    name='task_process_dataset'
)

queue_data_processing.add_task_type(
    dotted_path='mayan.apps.our_extension.tasks.task_generate_dataset_preview',
    label=_('Generate dataset preview'),
    name='task_generate_dataset_preview'
)
```

## 🔍 Search Integration

### 1. Search Model Registration
```python
# search.py
from mayan.apps.dynamic_search.search_models import SearchModel
from .models import Project, Dataset
from .permissions import permission_project_view

project_search = SearchModel(
    app_label='our_extension', model_name='Project',
    permission=permission_project_view
)

project_search.add_model_field(
    field='name', label=_('Name')
)
project_search.add_model_field(
    field='description', label=_('Description')
)
project_search.add_model_field(
    field='created_by__username', label=_('Created by')
)

dataset_search = SearchModel(
    app_label='our_extension', model_name='Dataset',
    permission=permission_dataset_view
)

dataset_search.add_model_field(field='name')
dataset_search.add_model_field(field='study__name', label=_('Study'))
dataset_search.add_model_field(field='study__project__name', label=_('Project'))
```

### 2. Search Integration in Views
```python
# views/search_views.py
from mayan.apps.dynamic_search.views.view_mixins import SearchResultViewMixin
from mayan.apps.views.generics import SimpleView

class ProjectSearchView(SearchResultViewMixin, SimpleView):
    search_model = project_search
    template_name = 'our_extension/project_search_results.html'

    def get_extra_context(self):
        return {
            'title': _('Project search results')
        }
```

## 🎨 UI Integration Patterns

### 1. Navigation Integration
```python
# links.py
from mayan.apps.navigation.classes import Link
from .permissions import permission_project_view, permission_project_create

link_project_list = Link(
    text=_('Projects'), view='our_extension:project_list',
    permission=permission_project_view
)

link_project_create = Link(
    text=_('Create project'), view='our_extension:project_create',
    permission=permission_project_create
)

link_dataset_document_list = Link(
    text=_('Documents'), view='our_extension:dataset_document_list',
    args='resolved_object.pk', permission=permission_dataset_view
)

# Register in app ready()
from mayan.apps.common.menus import menu_main, menu_object
menu_main.bind_links(links=(link_project_list,))
menu_object.bind_links(
    links=(link_dataset_document_list,), sources=(Dataset,)
)
```

### 2. Template Organization
```python
# templates/our_extension/project_list.html
{% extends 'appearance/base.html' %}
{% load navigation_tags %}

{% block content %}
    <div class="row">
        <div class="col-md-12">
            {% navigation_resolve_menu name='project_actions' as menu_results %}
            {% include 'navigation/actions_dropdown.html' %}
            
            <div class="panel panel-default">
                <div class="panel-body">
                    {% for project in object_list %}
                        {% include 'our_extension/project_card.html' %}
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

## 🔐 Security Best Practices

### 1. Permission Checking
```python
# Always check permissions in views
class ProjectDetailView(SingleObjectView):
    model = Project
    object_permission = permission_project_view
    
    def get_extra_context(self):
        return {
            'object_permission_required': permission_project_edit
        }

# Always filter querysets by permissions
class ProjectListView(ObjectListView):
    model = Project
    object_permission = permission_project_view
    
    def get_source_queryset(self):
        queryset = super().get_source_queryset()
        # Additional filtering if needed
        return queryset
```

### 2. ACL Integration
```python
# Use ACL system for fine-grained control
def assign_project_permissions(project, user, permissions):
    role = Role.objects.get(label='Project Member')
    role.groups.add(user.groups.first())
    
    for permission in permissions:
        AccessControlList.objects.grant(
            permission=permission, role=role, obj=project
        )
```

## ⚠️ Common Pitfalls & Solutions

### 1. **Circular Import Issues**
```python
# ❌ BAD: Direct imports in models.py
from mayan.apps.our_extension.models import Project

# ✅ GOOD: Late imports
def get_projects(self):
    from mayan.apps.our_extension.models import Project
    return Project.objects.filter(...)
```

### 2. **Migration Dependencies**
```python
# In migrations
dependencies = [
    ('documents', '0001_initial'),  # Always depend on documents
    ('acls', '0001_initial'),       # If using ACLs
    ('permissions', '0001_initial'), # If using permissions
]
```

### 3. **Event Actor Handling**
```python
# Always preserve event actor
def save(self, *args, **kwargs):
    # Set _event_actor before save for proper event attribution
    user = kwargs.pop('_event_actor', None)
    if user:
        self._event_actor = user
    return super().save(*args, **kwargs)
```

### 4. **API Serializer Context**
```python
# Provide full context to serializers
def get_serializer_context(self):
    context = super().get_serializer_context()
    context.update({
        'request': self.request,
        'view': self,
        'project': self.get_project()  # Additional context
    })
    return context
```

## 🎯 Testing Patterns

### 1. Model Tests
```python
# tests/test_models.py
from mayan.apps.testing.tests.base import BaseTestCase
from ..models import Project

class ProjectModelTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            name='Test Project',
            created_by=self._test_case_user
        )

    def test_project_str(self):
        self.assertEqual(str(self.project), 'Test Project')
```

### 2. API Tests
```python
# tests/test_api.py  
from mayan.apps.rest_api.tests.base import BaseAPITestCase

class ProjectAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.grant_permission(permission=permission_project_view)

    def test_project_list_api(self):
        response = self.get(viewname='rest_api:project-list')
        self.assertEqual(response.status_code, 200)
```

## 🎯 Key Success Patterns

1. **Follow Mayan conventions**: Use established patterns consistently
2. **Integrate deeply**: Use events, permissions, search, etc.
3. **Test thoroughly**: Cover models, views, and APIs
4. **Document extensively**: Help future developers
5. **Performance aware**: Use select_related, prefetch_related
6. **Error handling**: Graceful degradation and proper logging
7. **Backwards compatible**: Don't break existing functionality 