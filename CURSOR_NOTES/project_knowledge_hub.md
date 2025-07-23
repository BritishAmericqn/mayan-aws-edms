# 🏛️ Mayan EDMS Extension Project - Knowledge Hub

> **Last Updated**: December 2024
> **Purpose**: Central reference for AI assistants working on the Mayan EDMS extension project
> **Include**: Always include this document as context in all project-related prompts

## 🎯 Project Overview

We're extending Mayan EDMS (v4.x) to support:
- **Hierarchical data model**: Project → Study → Dataset → Document
- **Dataset preview generation** with statistics and visualizations
- **Enhanced role-based access control** with shareable pre-signed URLs
- **AWS integration** for scalable cloud deployment
- **Modern UI enhancements** for research workflows

**Current Phase**: Day 1 - Research App Foundation (27 detailed tasks in proj_checklist.md)

## 🤖 AI-First Development Guidelines for This Project

### Token Optimization Strategy
1. **Use semantic search first** - Start broad with high-level queries
2. **Parallel tool calls** - Always execute multiple read operations simultaneously
3. **Focused context** - Only include relevant files in prompts
4. **Hierarchical understanding** - Understand parent apps before diving into specifics

### Cursor-Specific Best Practices
1. **Multi-file awareness**: Mayan uses extensive Django app structure - use `@folder` references
2. **Migration safety**: Always check existing migrations before creating new ones
3. **Test-driven approach**: Despite no existing tests, create tests for new features
4. **Incremental changes**: Make minimal, focused edits to preserve existing functionality

## 🗺️ Mayan EDMS Architecture Overview

### Core Concepts
- **Document**: Central entity, stored in `mayan/apps/documents/`
- **Document Type**: Template/category for documents
- **Document File**: Physical file storage (supports multiple files per document)
- **Document Version**: Visual representation with page remapping capabilities
- **Storage**: Abstracted storage layer supporting various backends

### Key Django Apps Structure
```
mayan/apps/
├── documents/          # Core document management (DO NOT MODIFY)
├── storage/           # Storage abstraction layer
├── acls/              # Access Control Lists
├── permissions/       # Permission system
├── metadata/          # Document metadata
├── cabinets/          # Document organization
├── task_manager/      # Celery task management
├── rest_api/          # DRF-based API
└── research/          # OUR NEW APP (follows same patterns)
```

### Database Models Hierarchy
1. `DocumentType` → defines document categories
2. `Document` → main document entity
3. `DocumentFile` → physical file storage
4. `DocumentVersion` → version management
5. `DocumentVersionPage` → page-level control

## 📍 Critical Files & Locations

### Configuration
- **Django Settings**: `mayan/settings/base.py` (main config)
- **Docker Setup**: `docker/docker-compose.yml`
- **Development Settings**: `mayan/settings/development/`

### Document Management Core (READ-ONLY for us)
- **Models**: `mayan/apps/documents/models/`
  - `document_models.py` - Main Document model
  - `document_file_models.py` - File storage
  - `document_type_models.py` - Document types
- **Storage**: `mayan/apps/documents/storages.py`
- **Views**: `mayan/apps/documents/views/`
- **API**: `mayan/apps/documents/api_views/`

### Our Extension Points (RESEARCH APP)
- **New App Location**: `mayan/apps/research/` (CREATE this entire app)
- **Models**: `mayan/apps/research/models/` (Project, Study, Dataset models)
- **API Extensions**: `mayan/apps/research/api_views.py`
- **Admin UI**: `mayan/apps/research/admin.py`
- **Permissions**: `mayan/apps/research/permissions.py`
- **Events**: `mayan/apps/research/events.py`
- **Navigation**: `mayan/apps/research/links.py`
- **App Config**: `mayan/apps/research/apps.py`

## 🛠️ Development Workflow

### Local Setup Commands
```bash
# Clone and setup
git clone <repo>
cd mayan-edms

# Docker-based development
docker-compose -f docker/docker-compose.yml up -d
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser

# Minio setup for S3 emulation
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

### Django Development Patterns
```python
# When creating research models
from mayan.apps.documents.models import Document
from mayan.apps.databases.model_mixins import ExtraDataModelMixin

class Dataset(ExtraDataModelMixin, models.Model):
    study = models.ForeignKey('Study', on_delete=models.CASCADE)
    # Many-to-many relationship with documents
    
class DatasetDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # primary, supplementary, etc.
```

### Migration Strategy
1. Check existing migrations: `ls mayan/apps/research/migrations/` (after creating app)
2. Create new migrations: `python manage.py makemigrations research`
3. Test locally before applying
4. Document migration dependencies

## 🏗️ Extension Implementation Guide

### Phase 1: Research App Creation
1. **Location**: Create entire `mayan/apps/research/` app structure
2. **App Structure**:
```
mayan/apps/research/
├── __init__.py
├── apps.py              # ResearchApp(MayanAppConfig)
├── models/
│   ├── __init__.py
│   ├── project_models.py
│   ├── study_models.py
│   └── dataset_models.py
├── permissions.py       # Research permission namespace
├── events.py           # Research event definitions
├── admin.py            # Django admin interface
├── api_views.py        # REST API endpoints
├── links.py            # Navigation links
├── urls/               # URL routing
├── templates/          # UI templates
├── static/             # Static files (if needed)
├── migrations/         # Database migrations
└── dependencies.py     # Python package dependencies
```

3. **Models Pattern**: Follow Mayan's ExtraDataModelMixin pattern
```python
# Example: mayan/apps/research/models/project_models.py
from mayan.apps.databases.model_mixins import ExtraDataModelMixin

class Project(ExtraDataModelMixin, models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    principal_investigator = models.CharField(max_length=255)
    start_date = models.DateField()
    
    class Meta:
        ordering = ('title',)
        
    def __str__(self):
        return self.title
```

### Phase 2: API Extensions
1. **Location**: `mayan/apps/research/api_views.py`
2. **Pattern**: Follow DRF viewsets with Mayan permission integration
3. **Integration**: Add to `mayan/apps/research/urls/api_urls.py`

### Phase 3: UI Enhancements
1. **Template location**: `mayan/apps/research/templates/research/`
2. **Static files**: `mayan/apps/research/static/research/`
3. **Pattern**: Use Mayan's existing UI components and navigation framework

## 🚨 Common Pitfalls & Solutions

### Pitfall 1: Wrong App Extension
- **Issue**: Trying to extend `mayan/apps/documents/` directly
- **Solution**: Create separate `mayan/apps/research/` app following Mayan patterns

### Pitfall 2: Migration Conflicts
- **Issue**: Creating migrations that conflict with existing ones
- **Solution**: Always check migration history first, use research app migrations

### Pitfall 3: Wrong INSTALLED_APPS Position
- **Issue**: Adding research app in wrong position
- **Solution**: Add after documents app in INSTALLED_APPS:
```python
# In mayan/settings/base.py INSTALLED_APPS
'mayan.apps.documents.apps.DocumentsApp',
'mayan.apps.cabinets.apps.CabinetsApp',  
# ... other document-related apps ...
'mayan.apps.research.apps.ResearchApp',  # ← ADD HERE
```

### Pitfall 4: Permission System
- **Issue**: Bypassing Mayan's ACL system
- **Solution**: Always use `permission_required` decorators and define proper permission namespaces

## 🔄 Effective AI Collaboration Tips

### When Exploring Code
1. Start with: "How does Mayan EDMS handle [concept]?"
2. Use codebase_search for understanding patterns
3. Read related documentation in `docs/` directory
4. Check existing apps like `cabinets` or `metadata` for similar patterns

### When Making Changes
1. Always read existing code first
2. Follow established patterns in the codebase
3. Create new app structure following MayanAppConfig pattern
4. Test locally with Docker setup

### When Stuck
1. Check `mayan/apps/cabinets/` for similar hierarchical organization patterns
2. Look at `mayan/apps/metadata/` for document relationship examples
3. Review Django admin implementations in other apps
4. Consult Docker logs for errors

## 📊 Progress Tracking

### Completed
- [ ] Project setup and understanding
- [ ] Local development environment
- [ ] Docker and Minio configuration

### In Progress
- [ ] Research app structure creation
- [ ] Model design for Project/Study/Dataset

### Upcoming
- [ ] API endpoint implementation
- [ ] Admin UI customization
- [ ] Preview generation logic
- [ ] AWS migration preparation

## 🔗 Quick References

### Key Documentation
- Research Models: `mayan/apps/research/models/` (to be created)
- Research API: `mayan/apps/research/api_views.py` (to be created)
- Storage Config: `mayan/apps/storage/`
- Docker Setup: `docker/docker-compose.yml`

### Environment Variables
```bash
MAYAN_DATABASES
MAYAN_CELERY_BROKER_URL
MAYAN_MEDIA_ROOT
MAYAN_DOCKER_WAIT
```

### Useful Commands
```bash
# Django shell
docker-compose exec app python manage.py shell

# Run migrations for research app
docker-compose exec app python manage.py migrate research

# Create test data
docker-compose exec app python manage.py loaddata demo_research_data

# Check logs
docker-compose logs -f app
```

## 📚 Essential Documentation

### Primary References (READ FIRST)
1. **`@project_knowledge_hub.md`** - This document (project overview & AI guidelines)
2. **`@proj_checklist.md`** - Current development phase and tasks
3. **`@feature_specification.md`** - Demo scenarios and requirements
4. **`@mayan_edms_architecture_deep_dive.md`** - Comprehensive Mayan EDMS architecture guide
5. **`@dream_ai_feature_prompt_template.md`** - Optimal AI prompt template for feature implementation
6. **`@proj_architecture/`** - Detailed codebase architecture mapping (4 focused documents)
7. **`@memory_bank.md`** - Lessons learned, debugging approaches, and working memory

### Documentation Structure
- **Knowledge Hub** (this file): Project overview, AI workflows, quick references
- **Checklist**: Current development phase and task breakdown
- **Feature Specification**: Demo scenarios and business requirements
- **Architecture Deep Dive**: Complete Mayan EDMS system documentation
- **Dream AI Prompt Template**: Optimal AI prompt for feature implementation
- **Architecture Mapping** (`proj_architecture/`): Detailed codebase operation maps
- **Memory Bank**: Working memory for lessons learned and debugging approaches

## 📝 Notes for Future Sessions

1. **Always start by reading this document AND proj_checklist.md**
2. **Check proj_checklist.md for current phase**
3. **Review memory_bank.md for previous lessons learned**
4. **Use parallel tool calls for file exploration**
5. **Follow Mayan's established patterns (CREATE research app, don't extend documents)**
6. **Test everything locally first**
7. **Update ALL documents with new insights and lessons**

---

**Remember**: 
- **CREATE** `mayan/apps/research/` - don't extend documents app
- **FOLLOW** MayanAppConfig patterns from existing apps
- **ADD** to INSTALLED_APPS after documents app
- **USE** Mayan's permission, event, and navigation systems
- **TEST** locally with Docker setup before proceeding

All documentation should evolve as we progress. Each AI assistant should update memory_bank.md and architecture docs with new discoveries. 