# 🧠 Memory Bank - Lessons Learned & Debugging Journal

> **Purpose**: Working memory for lessons learned, debugging approaches, and project nuances  
> **Usage**: Update after solving problems, discovering patterns, or learning Mayan-specific behaviors  
> **Format**: Problem → Attempts → Solution → Key Insight

---

## 📋 Quick Reference Index

- [🐛 Bug Fixes & Debugging](#-bug-fixes--debugging)
- [🔍 Mayan-Specific Gotchas](#-mayan-specific-gotchas)
- [🛠️ Development Patterns](#️-development-patterns)
- [⚡ Performance Insights](#-performance-insights)
- [🔐 Security & Permissions](#-security--permissions)
- [🐳 Docker & Infrastructure](#-docker--infrastructure)
- [📊 Database & Migrations](#-database--migrations)
- [🎨 UI & Frontend](#-ui--frontend)
- [🔄 API & Integration](#-api--integration)

---

## 🐛 Bug Fixes & Debugging

### [Template] Problem Resolution Format
```
**Problem**: [Clear description of the issue]
**Context**: [What you were trying to achieve]
**Symptoms**: [Error messages, unexpected behavior]
**Attempts**: 
  1. [What you tried first]
  2. [Second approach]
  3. [etc.]
**Solution**: [What actually worked]
**Root Cause**: [Why it happened]
**Key Insight**: [Important learning to remember]
**Prevention**: [How to avoid this in future]
```

### Example Entry
**Problem**: Docker container fails to start with database connection error  
**Context**: Setting up local development environment  
**Symptoms**: `django.db.utils.OperationalError: could not connect to server`  
**Attempts**:
  1. Checked database credentials
  2. Verified Docker network connectivity  
  3. Restarted containers
**Solution**: Database container needed more time to initialize - added healthcheck and depends_on  
**Root Cause**: Race condition between app and database startup  
**Key Insight**: Always use proper Docker service dependencies  
**Prevention**: Use healthchecks in docker-compose for database services

---

## 🔍 Mayan-Specific Gotchas

### App Loading Order Issues
**Problem**: Custom app functionality not working properly  
**Context**: Adding new Django app to Mayan  
**Solution**: Apps must be loaded in specific order in INSTALLED_APPS  
**Key Insight**: Events app MUST be first, then appearance, then logging  
**Reference**: See `proj_architecture/01_app_dependencies_and_loading.md`

### Model Inheritance Patterns
**Problem**: Custom models not integrating with Mayan's permission system  
**Context**: Extending document-related models  
**Solution**: Always inherit from Mayan's base model mixins (ExtraDataModelMixin, etc.)  
**Key Insight**: Mayan provides specific mixins for different functionalities  
**Reference**: Check existing models in `mayan/apps/documents/models/`

### Signal Registration Timing
**Problem**: Custom signals not firing  
**Context**: Adding event tracking to new features  
**Solution**: Register signals in AppConfig.ready() method  
**Key Insight**: Signal registration timing is critical in Django apps  
**Reference**: See how existing Mayan apps register signals

---

## 🛠️ Development Patterns

### Successful Extension Pattern
**Context**: Adding new functionality to Mayan  
**Approach**: Always extend existing patterns rather than creating new ones  
**Example**: When adding new document metadata, extend MetadataType rather than creating separate system  
**Key Insight**: Mayan's architecture is designed for extension, not replacement

### Migration Strategy That Works
**Context**: Database schema changes  
**Approach**: 
  1. Check existing migrations first
  2. Create small, focused migrations
  3. Test with sample data
  4. Document dependencies
**Key Insight**: Mayan has complex migration history - always check for conflicts

### Testing Approach
**Context**: Limited existing test coverage  
**Approach**: Create tests for new features even if surrounding code lacks them  
**Pattern**: Use Django's TestCase with Mayan's existing test utilities  
**Key Insight**: Tests become documentation for how your extensions work

---

## ⚡ Performance Insights

### Storage Backend Optimization
**Context**: File upload/download performance  
**Solution**: Use appropriate storage backend for environment (Minio local, S3 production)  
**Key Insight**: Storage abstraction allows seamless backend switching

### Query Optimization Patterns
**Context**: Database performance with large document sets  
**Approach**: Use Mayan's existing query optimizations and select_related patterns  
**Key Insight**: Follow existing QuerySet patterns in Mayan views

---

## 🔐 Security & Permissions

### ACL Integration Best Practices
**Context**: Adding access control to custom features  
**Approach**: Always use Mayan's ACL system rather than custom permissions  
**Pattern**: Use `@permission_required` decorators consistently  
**Key Insight**: Mayan's ACL system is comprehensive - don't bypass it

### Pre-signed URL Security
**Context**: Implementing shareable document links  
**Approach**: Use time-limited pre-signed URLs with appropriate scoping  
**Security Note**: Always validate user permissions before generating URLs  
**Key Insight**: Don't rely solely on URL obscurity for security

---

## 🐳 Docker & Infrastructure

### Local Development Setup
**Working Configuration**:
```yaml
# Successful docker-compose.yml additions for Minio
minio:
  image: minio/minio
  ports:
    - "9000:9000"
    - "9001:9001"
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
  command: server /data --console-address ":9001"
```
**Key Insight**: Minio provides excellent S3 emulation for local development

### Environment Variable Management
**Pattern**: Use .env files for local development, AWS Parameter Store for production  
**Security**: Never commit credentials to git  
**Key Insight**: Mayan supports extensive environment variable configuration

---

## 📊 Database & Migrations

### Migration Conflict Resolution
**Problem**: [To be filled when encountered]  
**Solution**: [To be documented]  
**Key Insight**: [To be learned]

### Index Strategy
**Context**: Optimizing database performance for hierarchical queries  
**Approach**: Add indexes for foreign keys and commonly queried fields  
**Key Insight**: Consider query patterns when designing schema

---

## 🎨 UI & Frontend

### Template Extension Pattern
**Context**: Customizing Mayan's UI  
**Approach**: Override templates in your app's templates directory  
**Pattern**: Use `{% extends %}` to build on existing templates  
**Key Insight**: Mayan's template hierarchy allows selective overrides

### CSS/JS Integration
**Context**: Adding modern UI elements  
**Approach**: Use Mayan's static file handling system  
**Pattern**: Add to app's static directory, use collectstatic  
**Key Insight**: Follow Django's static file conventions

---

## 🔄 API & Integration

### DRF Serializer Patterns
**Context**: Adding REST API endpoints  
**Approach**: Follow Mayan's existing serializer patterns  
**Pattern**: Use ModelSerializer with explicit field definitions  
**Key Insight**: Consistency with existing API structure is crucial

### Pagination Strategy
**Context**: Large dataset API responses  
**Approach**: Use Mayan's existing pagination classes  
**Key Insight**: Don't reinvent pagination - use established patterns

---

## 🔧 Development Tools & Debugging

### Useful Debug Commands
```bash
# Check migration status
docker-compose exec app python manage.py showmigrations

# Django shell with Mayan context
docker-compose exec app python manage.py shell

# View SQL queries (debug mode)
docker-compose exec app python manage.py shell
>>> from django.db import connection
>>> connection.queries

# Check app loading order
docker-compose exec app python manage.py shell
>>> from django.conf import settings
>>> settings.INSTALLED_APPS
```

### Log Analysis Patterns
**Context**: Debugging application issues  
**Approach**: Use structured logging and check multiple log sources  
**Tools**: Docker logs, Django logs, Celery logs  
**Key Insight**: Mayan provides comprehensive logging when properly configured

---

## 📝 Documentation & Communication

### Code Comment Standards
**Pattern**: Follow Mayan's existing comment style  
**Focus**: Explain "why" not "what"  
**Key Insight**: Good comments help future AI assistants understand decisions

### Git Commit Message Strategy
**Pattern**: Use clear, descriptive commit messages  
**Format**: `[app_name] Brief description of change`  
**Key Insight**: Good commit history helps track changes and debug issues

---

## 🎯 Success Patterns

### What Works Well
1. **Follow Mayan Patterns**: Always extend existing patterns
2. **Start Small**: Implement minimal viable features first
3. **Test Locally**: Use Docker setup for all development
4. **Document Everything**: Update this memory bank after solving problems
5. **Check Existing Code**: Always read similar implementations first

### What Doesn't Work
1. **Bypassing Mayan Systems**: Don't create parallel permission/storage systems
2. **Large Changes**: Avoid massive refactors - make incremental improvements
3. **Ignoring Dependencies**: App loading order and dependencies matter
4. **Custom Patterns**: Don't invent new patterns when Mayan provides them

---

## 🔄 Update Instructions for AI Assistants

When you encounter and solve a problem:

1. **Add an entry** using the template format above
2. **Update the Quick Reference Index** if adding new categories
3. **Cross-reference** with architecture documents when relevant
4. **Include specific code examples** when helpful
5. **Update "Success Patterns"** with new insights

### Categories for New Entries
- Use existing categories when possible
- Create new category only if significantly different
- Always update the index when adding categories
- Follow the emoji + title format for consistency

---

**Remember**: This memory bank should grow with every problem solved. The goal is to create a knowledge base that prevents repeating mistakes and accelerates development. 