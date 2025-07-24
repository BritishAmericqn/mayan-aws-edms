#!/bin/bash
set -e

echo "🚀 Starting Mayan EDMS with Research Platform..."

# Set the Django settings module to use our research settings
export DJANGO_SETTINGS_MODULE=mayan.settings.research

# Change to the Mayan directory
cd /opt/mayan-edms

echo "📋 Checking Django configuration..."
/opt/mayan-edms/bin/mayan-edms.py check --deploy --settings=mayan.settings.research

echo "🔄 Running database migrations..."
/opt/mayan-edms/bin/mayan-edms.py migrate --settings=mayan.settings.research

echo "📦 Collecting static files..."
/opt/mayan-edms/bin/mayan-edms.py collectstatic --noinput --settings=mayan.settings.research

echo "🔧 Setting up research platform..."
# Initialize research app data if needed
/opt/mayan-edms/bin/mayan-edms.py shell --settings=mayan.settings.research << 'EOF'
try:
    from django.contrib.auth.models import User
    from mayan.apps.research.models import Project
    
    print("✅ Research models are accessible")
    print(f"📊 Projects in database: {Project.objects.count()}")
    
    # Check if research app is properly loaded
    from django.conf import settings
    if 'mayan.apps.research.apps.ResearchApp' in settings.INSTALLED_APPS:
        print("🎯 Research app confirmed in INSTALLED_APPS")
    else:
        print("❌ Research app NOT in INSTALLED_APPS")
        
except Exception as e:
    print(f"⚠️  Research platform initialization warning: {e}")
    
print("🎉 Research platform check complete")
EOF

echo "🎯 Research Platform initialization complete!"

# Start the original Mayan EDMS entrypoint
exec /opt/mayan-edms/docker/entrypoint.sh "$@" 