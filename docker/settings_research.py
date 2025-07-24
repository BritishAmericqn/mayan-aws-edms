"""
Production-ready Mayan EDMS settings with Research Platform integration.
This extends the base Mayan settings and properly adds the research app.
"""

# Import all base Mayan EDMS settings
from mayan.settings.base import *

# Override INSTALLED_APPS to include research app
INSTALLED_APPS = list(INSTALLED_APPS)

# Find the position of documents app and insert research app after it
# This ensures proper loading order and dependency resolution
documents_app_index = None
for i, app in enumerate(INSTALLED_APPS):
    if 'documents.apps.DocumentsApp' in app:
        documents_app_index = i
        break

if documents_app_index is not None:
    # Insert research app after documents app for proper dependency order
    INSTALLED_APPS.insert(documents_app_index + 1, 'mayan.apps.research.apps.ResearchApp')
else:
    # Fallback: append at the end if documents app not found
    INSTALLED_APPS.append('mayan.apps.research.apps.ResearchApp')

# Research-specific settings
RESEARCH_ENABLED = True
RESEARCH_DEFAULT_PERMISSIONS = True

# Ensure research app URLs are included
# This will be handled by the research app's ready() method

# Optional: Override any other settings specific to research deployment
# ALLOWED_HOSTS can be extended if needed
# STATIC_URL and other settings remain as configured in base

# Log that research app has been loaded
import logging
logger = logging.getLogger(__name__)
logger.info("✅ Research Platform loaded successfully")
logger.info(f"📊 Total apps loaded: {len(INSTALLED_APPS)}")

# Validate that research app is properly included
if 'mayan.apps.research.apps.ResearchApp' in INSTALLED_APPS:
    logger.info("🎯 Research app confirmed in INSTALLED_APPS")
else:
    logger.error("❌ Research app NOT found in INSTALLED_APPS") 