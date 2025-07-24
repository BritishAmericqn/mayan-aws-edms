# 📋 Mayan EDMS Research Platform - Demonstrator Checklist

> **Last Updated**: December 2024 - Task 1.6 Complete  
> **Current Phase**: Day 1-2 - Foundation & Models (Phase 1 Complete)  
> **Overall Progress**: 40% (Foundation Complete, Integration Starting)

## 🎯 Project Overview

**Goal**: Build a compelling demonstrator of research-specific features for Mayan EDMS targeting University Research Departments.

**Key Focus**: **Demo fidelity and live presentation success** - not production robustness.

**Timeline**: 6-day sprint (Tuesday evening → Sunday night)

---

## ✅ **What Mayan ALREADY Has** (Skip These!)
- **Django 4.2.18** (current LTS) - No upgrade needed
- **Comprehensive REST API v4** with Swagger docs
- **Full Django Admin** for all models  
- **AWS S3 Storage Support** (boto3, django-storages ready)
- **Advanced Permission System** (ACLs, roles, groups)
- **Token Authentication** & API documentation
- **Event System** & audit trails
- **Search System** (Elasticsearch support)

---

## 📊 Status Legend
- ✅ **Completed** - Task finished and demo-ready
- 🟨 **In Progress** - Currently working on this task
- 🎪 **Demo Critical** - Essential for live demo success
- ❌ **Not Started** - Task not yet begun

---

## 🏗️ **Day 1-2: Foundation & Models** (Tuesday Night - Wednesday)
**Goal**: Research hierarchy working with clean UI and demo data

### Core Research Models & Demo Data
- ❌ **1.1** 🎪 Setup Python Dependencies for Data Analysis
  - **Action**: Add pandas, matplotlib, openpyxl to Mayan's dependency system
  - **Location**: Create `mayan/apps/research/dependencies.py` (in research app)
  - **Pattern**: Use Mayan's `PythonDependency` class with version pinning
  - **Required Packages**:
    ```python
    PythonDependency(
        module=__name__, name='pandas', version_string='==2.2.0'
    )
    PythonDependency(
        module=__name__, name='matplotlib', version_string='==3.8.0'
    )
    PythonDependency(
        module=__name__, name='openpyxl', version_string='==3.1.2'
    )
    PythonDependency(
        module=__name__, name='reportlab', version_string='==4.0.7'
    )
    PythonDependency(
        module=__name__, name='boto3', version_string='==1.34.0'
    )
    ```
  - **Success**: Dependencies working locally, can import packages

- ❌ **1.2** 🎪 Create Research App Structure
  - **Action**: Create new `mayan/apps/research/` app following MayanAppConfig pattern
  - **Files to Create**:
    - `apps.py` with `ResearchApp(MayanAppConfig)` 
    - Add `'mayan.apps.research'` to INSTALLED_APPS
    - Basic app structure (models/, admin.py, etc.)
  - **Success**: Research app loads without errors

- ❌ **1.3** 🎪 Design & Create Research Models
  - **Location**: Create new `mayan/apps/research/` app
  - **App Structure**:
    ```
    mayan/apps/research/
    ├── __init__.py
    ├── apps.py              # ResearchApp(MayanAppConfig)
    ├── models/
    │   ├── __init__.py
    │   ├── project_models.py
    │   ├── study_models.py  
    │   └── dataset_models.py
    ├── dependencies.py
    └── migrations/
    ```
  - **Models**: Project, Study, Dataset, DatasetDocument (many-to-many)
  - **Success**: New research app created following Mayan patterns

- ❌ **1.4** 🎪 Create Demo Data Fixtures
  - **Location**: `mayan/apps/research/fixtures/demo_research_data.json`
  - **Content**: 
    - 2-3 realistic research projects
    - 4-6 studies with compelling names
    - 8-10 datasets with clean sample data
  - **Success**: `python manage.py loaddata demo_research_data` works perfectly

- ❌ **1.5** Generate & Apply Migrations
  - **Action**: `python manage.py makemigrations research`
  - **Action**: `python manage.py migrate`
  - **Success**: Database schema updated without conflicts

- ✅ **1.6** 🎪 Define Research Permissions
  - **Location**: `mayan/apps/research/permissions.py`, `events.py`, `apps.py` (updated)
  - **Action**: Create permission namespace and specific permissions
  - **Completed**:
    - ✅ 19 research permissions across 4 categories (Project, Study, Dataset, Analysis)
    - ✅ 19 research events for comprehensive audit trail
    - ✅ Permission inheritance: Study → Project, Dataset → Study → Project
    - ✅ Full integration with Mayan's ACL system
    - ✅ Event system integration with @method_event decorators
    - ✅ ModelPermission registration for all research models
  - **Results**: 26 Project + 9 Study + 16 Dataset permissions registered successfully
  - **Success**: ✅ Enterprise-grade permission system ready for demo

- ❌ **1.7** 🎪 Setup URL Configuration  
  - **Location**: `mayan/apps/research/urls/`
  - **Files to Create**:
    - `api_urls.py` - API endpoint routing
    - `urlpatterns.py` - View URL patterns  
  - **Integration**: Add to main URL configuration
  - **Success**: All research URLs accessible via browser

- ❌ **1.8** 🎪 Configure App Registration
  - **Location**: `mayan/apps/research/apps.py`
  - **Action**: Implement complete `ResearchApp.ready()` method
  - **Integration**: 
    - Register permissions with models
    - Register events  
    - Bind navigation menus
    - Add to INSTALLED_APPS in correct position
  - **Success**: App fully integrated into Mayan ecosystem

- ❌ **1.9** 🎪 Polish Django Admin Interface
  - **Location**: `mayan/apps/research/admin.py`
  - **Features**: Inline editing, search, filters, attractive list views
  - **Demo Focus**: Looks professional and intuitive for live demo
  - **Success**: Admin interface impresses during demo walkthrough

- ❌ **1.10** 🎪 Setup Event System Integration
  - **Location**: `mayan/apps/research/events.py`
  - **Action**: Define research-specific events for audit trails
  - **Required Events**:
    ```python
    namespace = EventTypeNamespace(label='Research', name='research')
    event_project_created = namespace.add_event_type(name='project_created', label='Project created')
    event_dataset_analyzed = namespace.add_event_type(name='dataset_analyzed', label='Dataset analyzed')
    ```
  - **Success**: Events fire correctly and appear in audit logs

- ❌ **1.11** 🎪 Setup Navigation Integration
  - **Location**: `mayan/apps/research/links.py`  
  - **Action**: Create navigation links and bind to main menu
  - **Required Links**:
    ```python
    link_project_list = Link(text='Projects', view='research:project_list', permission=permission_project_view)
    link_project_create = Link(text='Create Project', view='research:project_create', permission=permission_project_create)
    ```
  - **Integration**: Bind to `menu_main` in app ready() method
  - **Success**: Navigation links visible in Mayan's main menu

- ❌ **1.12** Create Basic API Endpoints
  - **Location**: `mayan/apps/research/api_views.py`
  - **Endpoints**: `/api/v4/projects/`, `/api/v4/studies/`, `/api/v4/datasets/`
  - **Demo Focus**: Fast, reliable responses with demo data
  - **Success**: API browser shows clean, working endpoints

- ❌ **1.13** 🎪 Setup Task Management Infrastructure
  - **Location**: `mayan/apps/research/queues.py` and `mayan/apps/research/tasks.py`
  - **Action**: Create research-specific Celery queues and tasks
  - **Required Components**:
    ```python
    # queues.py
    queue_research = CeleryQueue(
        label=_('Research Analysis'), name='research_analysis', 
        worker=worker_c  # Medium latency for data processing
    )
    
    queue_research.add_task_type(
        dotted_path='mayan.apps.research.tasks.task_analyze_dataset',
        label=_('Analyze dataset'), name='task_analyze_dataset'
    )
    ```
  - **Success**: Tasks can be queued and executed for data analysis

- ❌ **1.14** 🎪 Create Comprehensive Demo Data Strategy
  - **Location**: `mayan/apps/research/fixtures/` and `mayan/apps/research/demo_data/`
  - **Action**: Create specific demo datasets with guaranteed success
  - **Required Demo Files**:
    - `weather_station_data.csv` (100 rows, 5 columns, clean data)
    - `research_survey_results.csv` (200 rows, 8 columns, some missing values)
    - `lab_measurements.xlsx` (150 rows, 6 columns, perfect for charts)
  - **Pre-computed Results**: JSON files with analysis results for each dataset
  - **Success**: Demo never fails due to data issues

### **Complete App Structure Summary**
After completing Day 1-2, we'll have a fully integrated Mayan app:
```
mayan/apps/research/
├── __init__.py
├── apps.py              # ResearchApp(MayanAppConfig) with complete ready() method
├── models/              # Project, Study, Dataset models
├── permissions.py       # Research permission namespace
├── events.py           # Research event definitions  
├── links.py            # Navigation link definitions
├── admin.py            # Polished admin interface
├── api_views.py        # REST API endpoints
├── urls/               # URL routing configuration
├── dependencies.py     # Python package dependencies
├── fixtures/           # Demo data
├── migrations/         # Database migrations
├── queues.py           # Celery queue definitions
├── tasks.py            # Background processing tasks
├── forms.py            # Django forms for research objects
├── templates/research/ # Professional Django templates
├── static/research/    # CSS/JS for charts and styling
├── demo_data/          # Specific demo CSV files
├── analysis/           # Data processing modules
├── sharing/            # Pre-signed URL generation
├── views/              # Django views (sharing, compliance, public)
└── reports/            # PDF report generation
```

---

## 📊 **Day 3-4: Data Analysis & Visualizations** (Thursday - Friday)  
**Goal**: Impressive data analysis with polished visualizations for demo

### Data Processing Engine
- ❌ **2.1** 🎪 Dataset Analysis Module with Demo Data
  - **Location**: `mayan/apps/research/analysis/`
  - **Demo Strategy**: Use pre-selected, clean CSV files that always work
  - **Components**: 
    - `parsers.py` - Handles demo CSV files perfectly
    - `analyzers.py` - Generates impressive statistics
    - `preview_generators.py` - Creates beautiful charts
  - **Success**: Demo datasets produce consistent, impressive results

- ❌ **2.2** 🎪 Statistical Analysis with Visual Polish
  - **Features**: 
    - Clean statistical summaries (formatted for presentation)
    - Data quality indicators with green/yellow/red status
    - Beautiful visualizations (histograms, box plots, correlation heatmaps)
  - **Demo Focus**: Charts look professional and load quickly
  - **Success**: Analysis results are visually impressive in live demo

- ❌ **2.3** Analysis API Endpoints
  - **Location**: `mayan/apps/research/api_views.py`
  - **Endpoints**: 
    - `POST /api/v4/datasets/{id}/analyze/` - Triggers analysis
    - `GET /api/v4/datasets/{id}/analysis/` - Returns cached results
  - **Demo Focus**: Fast response times with demo data
  - **Success**: API calls complete in <3 seconds for demo

### UI Integration & Polish
- ❌ **2.4** 🎪 Django Forms for Research Hierarchy
  - **Location**: `mayan/apps/research/forms.py`
  - **Action**: Create Django forms for Project, Study, Dataset creation
  - **Required Forms**:
    ```python
    class ProjectForm(forms.ModelForm):
        class Meta:
            model = Project
            fields = ['title', 'description', 'principal_investigator', 'start_date']
    
    class DatasetForm(forms.ModelForm):
        documents = forms.ModelMultipleChoiceField(queryset=Document.objects.none())
    ```
  - **Success**: Clean, professional forms for all research objects

- ❌ **2.5** 🎪 Template System with Visual Polish
  - **Location**: `mayan/apps/research/templates/research/`
  - **Action**: Create Django templates extending Mayan's base templates
  - **Required Templates**:
    - `project_list.html` - Professional project listing
    - `dataset_detail.html` - Charts, statistics, document links
    - `analysis_results.html` - Data visualizations and insights
  - **Pattern**: `{% extends 'appearance/base.html' %}` with research-specific blocks
  - **Success**: Templates look professional and integrate with Mayan UI

- ❌ **2.6** 🎪 Static Files & Chart Integration
  - **Location**: `mayan/apps/research/static/research/`
  - **Action**: Add CSS/JS for charts and research-specific styling
  - **Required Files**:
    - `research.css` - Professional styling for research views
    - `charts.js` - Chart.js integration for data visualizations
    - Integration with Mayan's static file system
  - **Success**: Charts render properly and styling is consistent

- ❌ **2.7** Background Processing for Demo Reliability
  - **Implementation**: Use research queue (from Task 1.13) for analysis
  - **Demo Strategy**: Pre-compute analysis for backup during live demo
  - **Pattern**: Call `task_analyze_dataset.apply_async()` but have JSON backup
  - **Success**: Analysis never hangs or fails during demonstration

---

## 🔗 **Day 5: Sharing & Compliance Features** (Saturday)
**Goal**: Secure sharing and compliance dashboard ready for demo

### Pre-Signed URL Sharing System
- ❌ **3.1** 🎪 Pre-Signed URL Generation Backend
  - **Location**: `mayan/apps/research/sharing/`
  - **Action**: Create AWS S3 pre-signed URL generation system
  - **Required Components**:
    ```python
    # sharing/generators.py
    class PreSignedURLGenerator:
        def generate_url(self, document, expiration_hours=24):
            # Uses boto3 to generate S3 pre-signed URLs
            # Integrates with Mayan's storage system
    
    # sharing/models.py  
    class SharedDocument(models.Model):
        document = models.ForeignKey(Document)
        url_key = models.UUIDField(default=uuid.uuid4)
        expires_at = models.DateTimeField()
    ```
  - **Success**: Generate working pre-signed URLs for demo documents

- ❌ **3.2** 🎪 Sharing Forms & Views
  - **Location**: `mayan/apps/research/views/sharing_views.py`
  - **Action**: Create Django views and forms for sharing workflow
  - **Required Components**:
    - `ShareDocumentForm` with expiration dropdown (1hr, 1day, 1week)
    - `DocumentShareView` with modal integration
    - Copy-to-clipboard JavaScript functionality
  - **Success**: Complete sharing workflow works smoothly in browser

- ❌ **3.3** 🎪 External Access View (No Authentication)
  - **Location**: `mayan/apps/research/views/public_views.py`
  - **Action**: Create public view for external document access
  - **Requirements**:
    - No Mayan authentication required
    - URL validation and expiration checking
    - Professional "shared document" interface
    - Download tracking for compliance
  - **Success**: External users can access documents via shared links

### Research Compliance Dashboard
- ❌ **3.4** Enhanced Audit Events for Research
  - **Location**: `mayan/apps/research/events.py` (extend from Task 1.10)
  - **Action**: Add research-specific events beyond basic CRUD
  - **Required Events**:
    ```python
    event_dataset_analyzed = namespace.add_event_type(name='dataset_analyzed', label='Dataset analyzed')
    event_document_shared_externally = namespace.add_event_type(name='document_shared_externally', label='Document shared externally')
    event_compliance_report_generated = namespace.add_event_type(name='compliance_report_generated', label='Compliance report generated')
    ```
  - **Success**: Research activities create meaningful audit trails

- ❌ **3.5** 🎪 Compliance Dashboard Views & Logic
  - **Location**: `mayan/apps/research/views/compliance_views.py`
  - **Action**: Create dashboard with activity timeline and metrics
  - **Required Components**:
    - `ComplianceDashboardView` with event aggregation
    - Activity timeline (last 30 days of research events)
    - Document access statistics
    - External sharing audit log
  - **Success**: Dashboard shows comprehensive research activity overview

- ❌ **3.6** 🎪 PDF Report Generation with ReportLab
  - **Location**: `mayan/apps/research/reports/`
  - **Action**: Create PDF compliance reports using ReportLab
  - **Required Components**:
    ```python
    # reports/generators.py
    class ComplianceReportGenerator:
        def generate_pdf(self, project, date_range):
            # Professional PDF with:
            # - Project summary
            # - Document access logs  
            # - Sharing activity
            # - Compliance metrics
    ```
  - **Demo Strategy**: Pre-generated sample reports as backup
  - **Success**: Generate and download professional reports in live demo

---

## ☁️ **Day 6: AWS Integration & Demo Preparation** (Sunday)
**Goal**: AWS features working + demo-ready system

### AWS Integration
- ❌ **4.1** S3 Storage Integration
  - **Action**: Configure S3 storage backend for documents
  - **Demo Strategy**: Local Minio as backup if AWS issues arise
  - **Success**: Documents upload to cloud storage seamlessly

- ❌ **4.2** 🎪 S3 Pre-Signed URL Integration
  - **Action**: Connect sharing system to S3 pre-signed URLs
  - **Demo Focus**: External sharing works reliably
  - **Success**: Generated links work outside the system

### Demo Preparation & Polish
- ❌ **4.3** 🎪 End-to-End Demo Script Testing
  - **Test Scenarios**: 
    1. Create project → study → dataset hierarchy
    2. Upload demo CSV → see instant analysis
    3. Generate sharing link → test external access
    4. Show compliance dashboard and reports
  - **Success**: Complete demo runs smoothly in <15 minutes

- ❌ **4.4** 🎪 Demo Data & Environment Preparation
  - **Actions**:
    - Load clean demo data fixtures
    - Pre-compute analysis results as backup
    - Test all workflows with demo script
  - **Success**: Demo environment is 100% reliable

- ❌ **4.5** 🎪 UI Polish & Final Touches
  - **Focus Areas**:
    - Consistent styling across all new features
    - Professional loading states and transitions
    - Error-free navigation and workflows
  - **Success**: System looks polished and professional

- ❌ **4.6** 🎪 Integration Testing & Demo Validation
  - **Location**: `mayan/apps/research/tests/test_integration.py`
  - **Action**: Create comprehensive integration tests covering full demo workflow
  - **Test Coverage**:
    ```python
    def test_complete_demo_workflow(self):
        # 1. Create project → study → dataset hierarchy
        # 2. Upload demo CSV and trigger analysis
        # 3. Generate sharing link and verify external access
        # 4. Generate compliance report
        # 5. Verify all Mayan integrations (permissions, events, navigation)
    ```
  - **Success**: Full demo workflow passes automated testing

- ❌ **4.7** 🎪 Live Demo Backup Plans
  - **Preparations**:
    - Local development environment as backup
    - Pre-loaded demo data and analysis results
    - Multiple demo scenarios prepared
    - Screenshot/video backup if needed
  - **Success**: Multiple fallback options for live demo

---

## 🎯 **Demo Success Criteria**

### **Technical Demo Success**
- [ ] All 5 features demonstrate smoothly in live environment
- [ ] Demo completes in 15 minutes without technical issues
- [ ] UI looks professional and polished during screen sharing
- [ ] External sharing links work for demo audience

### **Business Demo Success**
- [ ] Clear value proposition demonstrated for each user type
- [ ] Competitive advantages are obvious and compelling
- [ ] Demo flows logically from problem to solution
- [ ] Audience can immediately see the research workflow benefits

### **Backup & Reliability**
- [ ] Local environment works as backup
- [ ] Pre-computed results available if live analysis fails
- [ ] Multiple demo scenarios prepared
- [ ] All demo data is clean and impressive

---

## 🎉 **Feature Delivery Summary**

### **Demonstrator Features** ✅
1. **Research Hierarchy**: Project → Study → Dataset → Document organization
2. **Intelligent Analysis**: Automated statistics and visualizations for datasets
3. **Secure Sharing**: Pre-signed URLs for external collaboration
4. **Compliance Dashboard**: Research-specific audit trails and reporting
5. **AWS Integration**: Cloud storage with lifecycle optimization

### **Demo-Focused Approach** ✅
- **Controlled Data**: Clean, impressive datasets that always work
- **Visual Polish**: Professional UI that looks great during screen sharing
- **Reliability**: Backup plans and pre-computed results
- **Performance**: Fast, responsive system optimized for live demo

### **Total Development Time**: ~50-60 hours over 6 days
### **Total Tasks**: 27 specific tasks with detailed implementation guidance

---

## 📚 **Essential References**
- **`@feature_specification.md`** - Complete feature details and demo scenarios
- **`@mayan_edms_architecture_deep_dive.md`** - Understanding existing Mayan patterns
- **`@project_knowledge_hub.md`** - Development workflow and AI assistance
- **Django 4.2 Documentation** - Modern Django patterns
- **Mayan REST API Docs** - `/api/v4/swagger/ui/` (already available)

---

**Key Success Factor**: Build for **"impressive demo"** not **"bulletproof production"** - focus on features that showcase value clearly and work reliably with controlled demo data.




