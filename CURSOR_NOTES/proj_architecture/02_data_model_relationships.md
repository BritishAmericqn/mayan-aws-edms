# 📊 Data Model Relationships

> **Core System**: Document-centric architecture with 4-tier hierarchy  
> **Key Pattern**: Central Document model with versioning, file management, and extensible metadata

## 🏗️ Core Document Hierarchy

```
DocumentType (Category/Template)
    ↓ (One-to-Many)
Document (Main Entity)
    ↓ (One-to-Many)
DocumentFile (Physical Files)
    ↓ (One-to-Many)  
DocumentFilePage (Page-level Content)

Document (Visual Representation)
    ↓ (One-to-Many)
DocumentVersion (Visual Versions)
    ↓ (One-to-Many)
DocumentVersionPage (Page Mapping)
```

## 📋 Document Model Structure

### 1. DocumentType (Template/Category)
```python
# Location: mayan/apps/documents/models/document_type_models.py
class DocumentType(models.Model):
    label = models.CharField(max_length=196, unique=True)
    filename_generator_backend = models.CharField(...)
    filename_generator_backend_arguments = models.TextField(...)
    
    # Retention policies
    trash_time_period = models.PositiveIntegerField(...)
    delete_time_period = models.PositiveIntegerField(...)
    
    # Relationships
    documents = models.ForeignKey(Document, related_name='documents')
```

### 2. Document (Central Entity)
```python
# Location: mayan/apps/documents/models/document_models.py
class Document(models.Model):
    # Core identifiers
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    # Type relationship
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    
    # File references
    file_latest = models.OneToOneField('DocumentFile', null=True, blank=True)
    version_active = models.OneToOneField('DocumentVersion', null=True, blank=True)
    
    # Metadata
    datetime_created = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=8, default=DEFAULT_LANGUAGE)
    
    # State management
    in_trash = models.BooleanField(default=False)
    is_stub = models.BooleanField(default=True)  # No files uploaded yet
    
    # Managers
    objects = DocumentManager()
    trash = TrashCanManager()
    valid = ValidDocumentManager()
```

### 3. DocumentFile (Physical Storage)
```python
# Location: mayan/apps/documents/models/document_file_models.py
class DocumentFile(models.Model):
    # Parent relationship
    document = models.ForeignKey(Document, related_name='files')
    
    # File storage
    file = models.FileField(storage=DefinedStorageLazy(...))
    filename = models.CharField(max_length=255)
    
    # File metadata
    mimetype = models.CharField(max_length=255, editable=False)
    encoding = models.CharField(max_length=64, editable=False)
    checksum = models.CharField(max_length=64, editable=False)
    size = models.PositiveBigIntegerField(editable=False)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    
    # Managers
    objects = DocumentFileManager()
    valid = ValidDocumentFileManager()
```

### 4. DocumentVersion (Visual Representation)
```python
# Location: mayan/apps/documents/models/document_version_models.py
class DocumentVersion(models.Model):
    # Parent relationship
    document = models.ForeignKey(Document, related_name='versions')
    
    # Version metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    
    # Managers
    objects = models.Manager()
    valid = ValidDocumentVersionManager()
```

### 5. DocumentVersionPage (Page Mapping)
```python
# Location: mayan/apps/documents/models/document_version_page_models.py
class DocumentVersionPage(models.Model):
    # Parent relationship
    document_version = models.ForeignKey(DocumentVersion, related_name='version_pages')
    page_number = models.PositiveIntegerField(db_index=True)
    
    # Generic foreign key to source page (usually DocumentFilePage)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ('document_version', 'page_number')
```

## 🔗 Extended Relationships

### User-Related Models
```python
# Favorites
class FavoriteDocument(models.Model):
    user = models.ForeignKey(User, related_name='favorites')
    document = models.ForeignKey(Document, related_name='favorites')
    datetime_added = models.DateTimeField(auto_now=True)

# Recent Access
class RecentlyAccessedDocument(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document, related_name='recent')
    datetime_accessed = models.DateTimeField(auto_now=True)
```

### Organizational Models
```python
# From other apps that extend documents

# Cabinets (Document Organization)
class Cabinet(models.Model):
    label = models.CharField(max_length=128)
    # Documents linked via M2M through CabinetDocument

# Metadata (Document Properties)
class DocumentMetadata(models.Model):
    document = models.ForeignKey(Document)
    metadata_type = models.ForeignKey(MetadataType)
    value = models.TextField()

# Tags (Document Classification)
class DocumentTag(models.Model):
    document = models.ForeignKey(Document)
    tag = models.ForeignKey(Tag)
```

## 🎯 Key Relationship Patterns

### 1. Document Lifecycle
```python
# Creation flow
document_type = DocumentType.objects.get(...)
document = Document.objects.create(document_type=document_type)
document_file = DocumentFile.objects.create(document=document, file=...)
document_version = DocumentVersion.objects.create(document=document)
```

### 2. File-Version Separation
```python
# Multiple files per document
document.files.all()  # All uploaded files

# Visual versions can remap pages from any file
version = document.versions.first()
version.version_pages.all()  # Pages mapped to this version
```

### 3. Manager Patterns
```python
# Different object managers for different states
Document.objects.all()     # All documents (including trash)
Document.valid.all()       # Only non-trashed documents  
Document.trash.all()       # Only trashed documents
```

## 🔧 Extension Patterns for Our Project

### Adding Hierarchical Models
```python
# Our planned hierarchy: Project → Study → Dataset → Document
class Project(ExtraDataModelMixin, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User)
    datetime_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('name',)

class Study(models.Model):
    project = models.ForeignKey(Project, related_name='studies')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
        unique_together = ('project', 'name')

class Dataset(models.Model):
    study = models.ForeignKey(Study, related_name='datasets')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Optional direct relationship to documents
    # Alternative: Use intermediate model
    
    class Meta:
        ordering = ('name',)
        unique_together = ('study', 'name')

# Link documents to datasets
class DatasetDocument(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='documents')
    document = models.ForeignKey(Document, related_name='datasets')
    
    # Additional metadata for the relationship
    added_by = models.ForeignKey(User)
    datetime_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('dataset', 'document')
```

### Extending Document Metadata
```python
# Add custom fields to existing models via mixins
class DocumentExtensionMixin:
    def get_datasets(self):
        """Get all datasets this document belongs to"""
        return Dataset.objects.filter(documents__document=self)
    
    def get_project_hierarchy(self):
        """Get the full project hierarchy for this document"""
        datasets = self.get_datasets()
        return [(d.study.project, d.study, d) for d in datasets]

# Add to Document class
Document.add_to_class('get_datasets', DocumentExtensionMixin.get_datasets)
Document.add_to_class('get_project_hierarchy', DocumentExtensionMixin.get_project_hierarchy)
```

## 🔍 Query Patterns

### Basic Queries
```python
# Get documents by type
Document.valid.filter(document_type__label='Research Paper')

# Get files for a document
document.files.all().order_by('-timestamp')

# Get active version
document.version_active or document.versions.filter(active=True).first()
```

### Complex Relationships
```python
# Documents with specific metadata
Document.valid.filter(
    metadata__metadata_type__name='priority',
    metadata__value__gte='5'
)

# Documents in multiple cabinets
Document.valid.filter(
    cabinets__label__in=['Research', 'Published']
)

# Recent documents for user
user.recent_documents.filter(
    datetime_accessed__gte=timezone.now() - timedelta(days=7)
)
```

### Our Extension Queries
```python
# Get all documents in a project
project_documents = Document.valid.filter(
    datasets__dataset__study__project=project
)

# Get documents in a study
study_documents = Document.valid.filter(
    datasets__dataset__study=study
)

# Get documents in a dataset
dataset_documents = Document.valid.filter(
    datasets__dataset=dataset
)

# Hierarchical aggregation
project_stats = Project.objects.annotate(
    study_count=Count('studies'),
    dataset_count=Count('studies__datasets'),
    document_count=Count('studies__datasets__documents')
)
```

## 📝 Migration Considerations

When extending models:

1. **Use ExtraDataModelMixin**: For flexible data storage
2. **Create proper indexes**: On foreign keys and query fields
3. **Add managers**: For different object states
4. **Consider permissions**: Register models with permission system
5. **Add to admin**: For management interface
6. **Register events**: For audit trail
7. **Update serializers**: For API access

## 🎯 Key Takeaways

- **Document-centric**: Everything revolves around the Document model
- **File-version separation**: Physical files vs visual representations
- **Manager patterns**: Different querysets for different object states
- **Extension-friendly**: Use mixins and add_to_class for extending
- **Relationship complexity**: Many optional relationships via other apps
- **Query efficiency**: Use select_related/prefetch_related for performance 