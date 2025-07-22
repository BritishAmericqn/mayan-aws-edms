# 📋 App Dependencies & Loading Order

> **Critical System**: App loading order determines feature availability and signal priorities  
> **Key Pattern**: Hierarchical dependency model with strict load order

## 🔄 App Loading Sequence

### Critical Load Order (INSTALLED_APPS)

```python
# In mayan/settings/base.py - THIS ORDER IS CRITICAL
INSTALLED_APPS = (
    # 1. EVENTS MUST BE FIRST - preloads all events
    'mayan.apps.events.apps.EventsApp',
    
    # 2. APPEARANCE - template overrides
    'mayan.apps.appearance.apps.AppearanceApp',
    
    # 3. LOGGING - early initialization
    'mayan.apps.logging.apps.LoggingApp',
    
    # 4. TASK MANAGER - queues before other apps use them
    'mayan.apps.task_manager.apps.TaskManagerApp',
    
    # 5. USER MANAGEMENT - before authentication
    'mayan.apps.user_management.apps.UserManagementApp',
    
    # 6. AUTHENTICATION & PERMISSIONS
    'mayan.apps.authentication.apps.AuthenticationApp',
    'mayan.apps.acls.apps.ACLsApp',
    'mayan.apps.permissions.apps.PermissionsApp',
    
    # 7. CORE FOUNDATION
    'mayan.apps.storage.apps.StorageApp',
    'mayan.apps.common.apps.CommonApp',
    
    # 8. DOCUMENTS FIRST (signal priorities)
    # Django doesn't support signal priorities, so documents must be first
    'mayan.apps.documents.apps.DocumentsApp',
    
    # 9. DOCUMENT-RELATED APPS (depend on documents)
    'mayan.apps.cabinets.apps.CabinetsApp',
    'mayan.apps.checkouts.apps.CheckoutsApp',
    'mayan.apps.metadata.apps.MetadataApp',
    # ... many more document-related apps
)
```

### 🚨 Why Order Matters

1. **Events First**: Must preload all event definitions before other apps register event handlers
2. **Task Manager Early**: Queues must exist before apps try to register tasks
3. **Documents Signal Priority**: No Django signal priorities → documents app loads first to get priority
4. **User Management Before Auth**: Group/User models must be setup before authentication

## 🏗️ MayanAppConfig Pattern

Every Mayan app extends `MayanAppConfig` with standardized structure:

```python
class DocumentsApp(MayanAppConfig):
    app_namespace = 'documents'      # URL namespace
    app_url = 'documents'           # URL prefix
    has_rest_api = True             # DRF integration
    has_tests = True                # Test suite
    name = 'mayan.apps.documents'
    verbose_name = _('Documents')
    
    def ready(self):
        super().ready()
        # App initialization order:
        # 1. Model registration
        # 2. Event registration  
        # 3. Permission setup
        # 4. Menu binding
        # 5. Signal connections
        # 6. Search model registration
```

## 📊 Dependency Hierarchy

```
┌─────────────────┐
│   Core Layer    │ ← Never imports from children
├─────────────────┤
│   Documents     │ ← Central entity
│   Permissions   │ ← Base permission system
│   Common        │ ← Shared utilities
│   Navigation    │ ← UI framework
├─────────────────┤
│  Foundation     │ ← Core services
│   Storage       │ ← File abstraction
│   Events        │ ← Event system
│   Task Manager  │ ← Background processing
├─────────────────┤
│  Extensions     │ ← Feature apps
│   Cabinets      │ ← Document organization
│   Metadata      │ ← Document metadata
│   Indexing      │ ← Search & indexing
│   Checkouts     │ ← Document checkout
└─────────────────┘
```

## 🔗 Inter-App Communication Patterns

### 1. Direct Import Pattern (Parent → Child Only)
```python
# ✅ CORRECT: Parent imports child
from mayan.apps.documents.models import Document

# ❌ WRONG: Child imports parent creates circular dependency
```

### 2. Late Import Pattern (Avoiding Circular Imports)
```python
def my_function():
    # Hidden import inside function to avoid circular import
    from mayan.apps.documents.models import Document
    # ... use Document
```

### 3. Apps Module Loader Pattern
```python
class AppsModuleLoaderMixin:
    _loader_module_name = 'permissions'  # Module to load from each app
    
    @classmethod
    def load_modules(cls):
        for app in apps.get_app_configs():
            try:
                import_module(f'{app.name}.{cls._loader_module_name}')
            except ImportError:
                # Non-fatal if module doesn't exist
                pass
```

### 4. Signal-Based Communication
```python
# Apps communicate via signals without direct imports
from django.dispatch import Signal

signal_document_created = Signal()
signal_document_created.send(sender=Document, instance=document)
```

## 🎯 App Registration Patterns

### Permission Registration
```python
# In app ready() method
ModelPermission.register(
    model=Document, 
    permissions=(permission_document_view, permission_document_edit)
)
```

### Event Registration
```python
# In events.py
namespace = EventTypeNamespace(
    label=_('Documents'), name='documents'
)
event_document_created = namespace.add_event_type(
    label=_('Document created'), name='document_created'
)
```

### Menu Registration
```python
# In app ready() method
menu_main.bind_links(
    links=(link_document_list, link_document_create),
    sources=(Document,)
)
```

### Task Registration
```python
# In queues.py
queue_documents.add_task_type(
    dotted_path='mayan.apps.documents.tasks.task_document_upload',
    label=_('Process document upload'),
    name='task_document_upload'
)
```

### Search Registration
```python
# In search.py
document_search = SearchModel(
    app_label='documents', model_name='Document',
    permission=permission_document_view
)
```

## ⚠️ Common Dependency Pitfalls

### 1. Circular Import Hell
```python
# ❌ BAD: app1/models.py imports app2/models.py
#         app2/models.py imports app1/models.py

# ✅ GOOD: Use late imports or signals
```

### 2. Wrong Load Order
```python
# ❌ BAD: Using task queues before TaskManager is loaded
# ✅ GOOD: Register tasks in ready() method after super().ready()
```

### 3. Missing Dependencies
```python
# ❌ BAD: Using permissions before PermissionsApp is loaded
# ✅ GOOD: Check INSTALLED_APPS order
```

## 🔧 Extension Guidelines

When creating new apps:

1. **Follow naming**: `mayan.apps.{name}.apps.{Name}App`
2. **Extend MayanAppConfig**: Use standard app configuration
3. **Respect hierarchy**: Don't import from sibling apps
4. **Use signals**: For cross-app communication
5. **Register in ready()**: All app components in ready() method
6. **Consider order**: Think about dependencies when adding to INSTALLED_APPS

## 📝 Key Takeaways

- **Order matters**: Events → Task Manager → Documents → Extensions
- **No circular imports**: Use late imports or signals
- **Signal priorities**: Documents app loads first to get signal priority
- **Standard patterns**: Follow MayanAppConfig and registration patterns
- **Dependency awareness**: Understand parent→child relationship hierarchy 