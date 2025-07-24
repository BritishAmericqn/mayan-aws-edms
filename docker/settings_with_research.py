"""
Custom Mayan EDMS settings that includes the research platform.
This extends the base settings and adds our research app to INSTALLED_APPS.
"""

# Import all base Mayan settings
from mayan.settings.base import *

# Add our research app to INSTALLED_APPS
# Insert it after documents app for proper dependency order
INSTALLED_APPS = list(INSTALLED_APPS)

# Find the position of documents app
documents_app_index = None
for i, app in enumerate(INSTALLED_APPS):
    if 'documents' in app and 'DocumentsApp' in app:
        documents_app_index = i
        break

if documents_app_index is not None:
    # Insert research app after documents app
    INSTALLED_APPS.insert(documents_app_index + 1, 'mayan.apps.research.apps.ResearchApp')
else:
    # Fallback: append at the end
    INSTALLED_APPS.append('mayan.apps.research.apps.ResearchApp')

# Convert back to tuple (Mayan expects tuple)
INSTALLED_APPS = tuple(INSTALLED_APPS)

# Optional: Add any research-specific settings here
# For example, if we needed specific research configurations:
# RESEARCH_DEFAULT_ANALYSIS_TIMEOUT = 300
# RESEARCH_MAX_DATASET_SIZE = 100 * 1024 * 1024  # 100MB

print("✅ Research app added to INSTALLED_APPS")
print(f"📊 Total apps loaded: {len(INSTALLED_APPS)}") 