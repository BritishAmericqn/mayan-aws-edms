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
- **Modern UI enhancements** with Tailwind CSS

**Current Phase**: Local Development Environment Setup (Step 1 of checklist)

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
├── documents/          # Core document management
├── storage/           # Storage abstraction layer
├── acls/              # Access Control Lists
├── permissions/       # Permission system
├── metadata/          # Document metadata
├── cabinets/          # Document organization
├── task_manager/      # Celery task management
└── rest_api/          # DRF-based API
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

### Document Management Core
- **Models**: `mayan/apps/documents/models/`
  - `document_models.py` - Main Document model
  - `document_file_models.py` - File storage
  - `document_type_models.py` - Document types
- **Storage**: `mayan/apps/documents/storages.py`
- **Views**: `mayan/apps/documents/views/`
- **API**: `mayan/apps/documents/api_views/`

### Our Extension Points
- **New Models**: Will extend in `mayan/apps/documents/models/`
- **API Extensions**: `mayan/apps/documents/api_views/`
- **Admin UI**: `mayan/apps/documents/admin.py`
- **Permissions**: `mayan/apps/documents/permissions.py`

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
# When extending models
from mayan.apps.documents.models import Document

class DatasetDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE)
    # Add fields following Mayan patterns
```

### Migration Strategy
1. Check existing migrations: `ls mayan/apps/documents/migrations/`
2. Create new migrations: `python manage.py makemigrations documents`
3. Test locally before applying
4. Document migration dependencies

## 🏗️ Extension Implementation Guide

### Phase 1: Model Extensions
1. **Location**: Create in `mayan/apps/documents/models/`
2. **Pattern**: Follow existing Mayan model patterns
3. **Relationships**: Use Django's ORM appropriately
```python
# Example structure
class Project(ExtraDataModelMixin, models.Model):
    name = models.CharField(max_length=255)
    # Follow Mayan's naming conventions
    
class Study(models.Model):
    project = models.ForeignKey(Project, related_name='studies')
    
class Dataset(models.Model):
    study = models.ForeignKey(Study, related_name='datasets')
```

### Phase 2: API Extensions
1. Use Django REST Framework serializers
2. Follow Mayan's permission decorators
3. Integrate with existing viewsets

### Phase 3: UI Enhancements
1. Template location: `mayan/apps/documents/templates/`
2. Static files: `mayan/apps/documents/static/`
3. Use Mayan's existing UI components where possible

## 🚨 Common Pitfalls & Solutions

### Pitfall 1: Storage Configuration
- **Issue**: Direct S3 integration during development
- **Solution**: Use Minio locally, configure via environment variables

### Pitfall 2: Permission System
- **Issue**: Bypassing Mayan's ACL system
- **Solution**: Always use `permission_required` decorators

### Pitfall 3: Migration Conflicts
- **Issue**: Creating migrations that conflict with existing ones
- **Solution**: Always check migration history first

### Pitfall 4: Celery Task Management
- **Issue**: Not using Mayan's task queues properly
- **Solution**: Use appropriate queue classes (A-E based on priority)

## 🔄 Effective AI Collaboration Tips

### When Exploring Code
1. Start with: "How does Mayan EDMS handle [concept]?"
2. Use codebase_search for understanding patterns
3. Read related documentation in `docs/` directory
4. Check test files for usage examples (when they exist)

### When Making Changes
1. Always read existing code first
2. Follow established patterns in the codebase
3. Make minimal changes to achieve goals
4. Test locally with Docker setup

### When Stuck
1. Check `mayan/apps/documents/tests/` for patterns
2. Look at similar features in other apps
3. Review Django admin implementations
4. Consult Docker logs for errors

## 📊 Progress Tracking

### Completed
- [ ] Project setup and understanding
- [ ] Local development environment
- [ ] Docker and Minio configuration

### In Progress
- [ ] Model design for Project/Study/Dataset
- [ ] Initial Django app structure

### Upcoming
- [ ] API endpoint implementation
- [ ] Admin UI customization
- [ ] Preview generation logic
- [ ] AWS migration preparation

## 🔗 Quick References

### Key Documentation
- Django Models: `mayan/apps/documents/models/__init__.py`
- API Views: `mayan/apps/documents/api_views/`
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

# Run migrations
docker-compose exec app python manage.py migrate

# Create test data
docker-compose exec app python manage.py loaddata <fixture>

# Check logs
docker-compose logs -f app
```

## 📚 Essential Documentation

### Primary References (READ FIRST)
1. **`@project_knowledge_hub.md`** - This document (project overview & AI guidelines)
2. **`@mayan_edms_architecture_deep_dive.md`** - Comprehensive Mayan EDMS architecture guide
3. **`@dream_ai_feature_prompt_template.md`** - Optimal AI prompt template for feature implementation
4. **`@proj_architecture/`** - Detailed codebase architecture mapping (4 focused documents)
5. **`@memory_bank.md`** - Lessons learned, debugging approaches, and working memory

### Documentation Structure
- **Knowledge Hub** (this file): Project overview, AI workflows, quick references
- **Architecture Deep Dive**: Complete Mayan EDMS system documentation (1000+ lines)
  - Document management workflows
  - Storage system architecture
  - Permission & ACL system
  - Task management & Celery
  - Event system & signals
  - Navigation & UI framework
  - Extension patterns & hooks
- **Dream AI Prompt Template**: Optimal AI prompt for feature implementation
  - Comprehensive context integration
  - Quality requirements & standards
  - Pitfall avoidance strategies
  - Step-by-step execution guide
  - Success criteria & validation
- **Architecture Mapping** (`proj_architecture/`): Detailed codebase operation maps
  - `01_app_dependencies_and_loading.md`: App initialization & load order
  - `02_data_model_relationships.md`: Database models & relationships
  - `03_inter_system_communication.md`: Events, signals, tasks & API integration
  - `04_extension_patterns_and_best_practices.md`: Safe extension guidelines
- **Memory Bank**: Working memory for lessons learned and debugging approaches
  - Structured problem-solution format
  - Mayan-specific gotchas and patterns
  - Success/failure patterns with prevention strategies
  - Debug commands and development tools

## 📝 Notes for Future Sessions

1. **Always start by reading this document AND the architecture deep dive**
2. **Check proj_checklist.md for current phase**
3. **Review memory_bank.md for previous lessons learned**
4. **Use parallel tool calls for file exploration**
5. **Follow Mayan's established patterns (detailed in deep dive)**
6. **Test everything locally first**
7. **Update ALL documents with new insights and lessons**

---

**Remember**: All documentation should evolve as we progress. Each AI assistant should:
- Update **memory_bank.md** after solving any problem (following the template format)
- Update **architecture docs** with new technical discoveries
- Update **knowledge hub** with workflow improvements
- Create comprehensive, searchable knowledge for future sessions 