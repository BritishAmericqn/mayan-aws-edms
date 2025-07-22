# 🔄 Inter-System Communication

> **Core System**: Event-driven architecture with signals, tasks, and API integration  
> **Key Pattern**: Async communication via events + sync communication via direct calls

## 🎯 Communication Layers

```
┌─────────────────────────────────────────┐
│              UI Layer                   │
├─────────────────────────────────────────┤
│         API Layer (REST/GraphQL)        │
├─────────────────────────────────────────┤
│            View Layer                   │
├─────────────────────────────────────────┤
│          Business Logic                 │ ← Events & Signals
├─────────────────────────────────────────┤
│         Task Layer (Celery)             │ ← Async Processing  
├─────────────────────────────────────────┤
│          Data Layer                     │ ← Direct DB Access
└─────────────────────────────────────────┘
```

## ⚡ Event System Architecture

### Event Type Namespaces
```python
# In each app's events.py
namespace = EventTypeNamespace(
    label=_('Documents'), name='documents'
)

event_document_created = namespace.add_event_type(
    label=_('Document created'), name='document_created'  
)
event_document_trashed = namespace.add_event_type(
    label=_('Document trashed'), name='document_trashed'
)
```

### Event Commit Patterns
```python
# Sync event (immediate)
event_document_created.commit(
    actor=user,           # Who did it
    target=document,      # What was affected
    action_object=file    # What was used (optional)
)

# Async event (via Celery)
event_document_processed.commit(
    actor=user, target=document
)  # Automatically queued to events_fast queue
```

### Event Propagation Flow
```
User Action → Business Logic → Event Commit → Signal → Event Task → Event Storage → Notifications
```

### Event Handlers & Signal Connections
```python
# In app ready() method
from django.db.models.signals import post_save

def handler_document_created(sender, instance, created, **kwargs):
    if created:
        event_document_created.commit(target=instance)

post_save.connect(
    sender=Document,
    receiver=handler_document_created,
    dispatch_uid='documents_handler_document_created'
)
```

## 🔗 Signal Communication Patterns

### 1. Model Signals (Django Built-in)
```python
# Pre/post save/delete signals
pre_save.connect(receiver=handler_pre_document_save, sender=Document)
post_save.connect(receiver=handler_post_document_save, sender=Document)
m2m_changed.connect(receiver=handler_m2m_changed, sender=Document.tags.through)
```

### 2. Custom Signals (Mayan-specific)
```python
# In signals.py
signal_pre_initial_setup = Signal()
signal_post_upgrade = Signal()

# Broadcasting
signal_pre_initial_setup.send(sender=None)

# Listening
signal_pre_initial_setup.connect(
    receiver=handler_pre_initial_setup,
    dispatch_uid='common_handler_pre_initial_setup'
)
```

### 3. Event Manager Decorators
```python
# Automatic event emission
@method_event(
    event_manager_class=EventManagerSave,
    created={
        'event': event_document_created,
        'target': 'self'
    },
    edited={
        'event': event_document_edited,
        'target': 'self'
    }
)
def save(self, *args, **kwargs):
    return super().save(*args, **kwargs)
```

## 🎭 Task System Communication

### Queue Architecture (Priority-based)
```python
# Worker assignment by priority
worker_a = Worker(description='Low latency high volume tasks')
worker_b = Worker(description='Medium latency tasks') 
worker_c = Worker(description='Medium latency tasks')
worker_d = Worker(description='Heavy processing tasks')
worker_e = Worker(description='Background maintenance tasks')

# Queue routing
queue_events_fast = CeleryQueue(name='events_fast', worker=worker_a)
queue_documents = CeleryQueue(name='documents', worker=worker_b)
queue_converter = CeleryQueue(name='converter', worker=worker_d)
queue_search = CeleryQueue(name='search', worker=worker_e)
```

### Task Communication Patterns
```python
# Sync task execution
result = task_process_document.apply(args=[document_id])

# Async task execution  
task_process_document.apply_async(
    args=[document_id],
    kwargs={'user_id': user.id}
)

# Chain tasks
from celery import chain
workflow = chain(
    task_upload_document.s(file_data),
    task_extract_metadata.s(),
    task_generate_preview.s()
)
workflow.apply_async()

# Group parallel tasks
from celery import group
parallel_tasks = group(
    task_ocr_page.s(page_id) for page_id in page_ids
)
parallel_tasks.apply_async()
```

### Task Error Handling & Retries
```python
@app.task(
    bind=True, 
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600
)
def task_process_document(self, document_id):
    try:
        # Processing logic
        pass
    except RetryableException as exc:
        raise self.retry(exc=exc)
    except FatalException:
        # Log and fail permanently
        logger.error("Fatal error processing document %s", document_id)
```

## 🔌 API Communication Patterns

### DRF Integration Architecture
```python
# Mayan API view base classes
class ListCreateAPIView(
    CheckQuerysetAPIViewMixin,
    DynamicFieldListAPIViewMixin,
    InstanceExtraDataAPIViewMixin,
    rest_framework_generics.ListCreateAPIView
):
    filter_backends = (
        MayanObjectPermissionsFilter,    # ACL filtering
        MayanSortingFilter,             # Sorting
        RESTAPISearchFilter             # Search integration
    )
    permission_classes = (MayanPermission,)
```

### Permission Integration
```python
# Permission-aware API views
class APIDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    mayan_object_permission_map = {
        'DELETE': permission_document_trash,
        'GET': permission_document_view,
        'PATCH': permission_document_edit
    }
    
    # Automatic ACL filtering via MayanObjectPermissionsFilter
```

### API Event Integration
```python
# API actions trigger events
def perform_update(self, serializer):
    instance = serializer.save()
    event_document_edited.commit(
        actor=self.request.user,
        target=instance
    )
```

## 🎨 UI Communication Patterns

### Menu System
```python
# Dynamic menu binding based on context
menu_main.bind_links(
    links=(link_document_create, link_document_list),
    sources=(Document,)  # Show when Document is in context
)

# Permission-aware menu rendering
menu.resolve(
    context=context,      # Template context
    request=request       # For permission checking
)
```

### Navigation Framework
```python
# Context-aware navigation
class Link:
    def resolve(self, context=None, resolved_object=None):
        # Permission checking
        if self.permission:
            AccessControlList.objects.check_access(
                obj=resolved_object,
                permission=self.permission,
                user=request.user
            )
        
        # URL generation with context
        return ResolvedLink(...)
```

### Template Integration
```python
# Navigation tags
{% load navigation_tags %}
{% navigation_resolve_menu name='document_actions' as menu_results %}

# Event integration
{% load events_tags %}  
{% events_for_object object as object_events %}
```

## 🔍 Search Integration Communication

### Search Backend Communication
```python
# Search models register for indexing
class SearchBackend:
    def search(self, query, search_model, user):
        # 1. Parse query
        search_interpreter = SearchInterpreter.init(query, search_model)
        id_list = search_interpreter.do_resolve(self)
        
        # 2. Build queryset  
        queryset = search_model.get_queryset().filter(pk__in=id_list)
        
        # 3. Apply permissions
        if search_model.permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=search_model.permission,
                queryset=queryset,
                user=user
            )
        
        return queryset
```

### Automatic Index Updates
```python
# Signal-based index maintenance
def handler_index_instance(sender, instance, **kwargs):
    search_backend = SearchBackend.get_instance()
    search_backend.index_instance(instance=instance)

# Connected in search backend initialization
post_save.connect(
    receiver=handler_index_instance,
    sender=Document
)
```

## 🗂️ Storage Communication

### Storage Abstraction Layer
```python
# Defined storage pattern
storage_documents = DefinedStorage(
    dotted_path='django.core.files.storage.FileSystemStorage',
    name='documents',
    kwargs={'location': '/var/lib/mayan/documents'}
)

# Runtime storage swapping
class PassthroughStorage(Storage):
    def __init__(self, next_storage_backend, **kwargs):
        self.next_storage_class = import_string(next_storage_backend)
        self.next_storage_backend = self.next_storage_class(**kwargs)
```

### File Processing Pipeline
```python
# Multi-stage file processing
DocumentFile.save() →
    File Upload →
    Checksum Calculation →
    MIME Type Detection →
    Event Emission →
    Async Processing Tasks →
    Index Updates
```

## 🔐 Security Communication

### ACL System Integration
```python
# 3-tier permission checking
AccessControlList.objects.check_access(
    obj=document,              # Object
    permission=permission,     # Permission  
    user=user                 # Actor (via role)
)

# Query filtering
queryset = AccessControlList.objects.restrict_queryset(
    queryset=Document.objects.all(),
    permission=permission_document_view,
    user=user
)
```

### Permission Inheritance
```python
# Hierarchical permission inheritance
ModelPermission.register_inheritance(
    model=DocumentFile,
    related='document'  # DocumentFile inherits from Document
)
```

## 🎯 Extension Communication Patterns

### Adding New Communication Channels
```python
# 1. Create custom events
namespace = EventTypeNamespace(name='our_extension')
event_dataset_processed = namespace.add_event_type(...)

# 2. Create custom tasks
@app.task
def task_process_dataset(dataset_id):
    # Processing logic
    pass

# 3. Add to appropriate queue
queue_datasets = CeleryQueue(name='datasets', worker=worker_c)
queue_datasets.add_task_type(
    dotted_path='our_extension.tasks.task_process_dataset'
)

# 4. Connect signals
post_save.connect(
    receiver=handler_dataset_saved,
    sender=Dataset
)
```

### API Extensions
```python
# Extend existing APIs
class APIDatasetDocumentListView(ExternalObjectAPIViewMixin, 
                                 generics.ListCreateAPIView):
    mayan_external_object_permission_map = {
        'GET': permission_dataset_view,
        'POST': permission_dataset_edit  
    }
    
    def get_external_object(self):
        return get_object_or_404(Dataset, pk=self.kwargs['dataset_id'])
```

## 📊 Communication Flow Examples

### Document Upload Flow
```
User Upload → API View → Document.save() → 
Signal → Event → Task Queue → 
File Processing → Metadata Extraction → 
Index Update → Notification
```

### Search Query Flow  
```
Search Form → API → Search Backend → 
Query Parser → Index Search → 
Permission Filter → Results → UI
```

### Permission Check Flow
```
User Request → View → Permission Check → 
ACL Query → Role Check → 
Allow/Deny → Response
```

## 🎯 Key Takeaways

- **Event-driven**: Core communication via events and signals
- **Async processing**: Heavy work via Celery task queues  
- **Permission-aware**: All communication respects ACL system
- **Extensible**: Clean interfaces for adding new communication patterns
- **Reliable**: Retry mechanisms and error handling built-in
- **Performance**: Efficient querying and caching strategies 