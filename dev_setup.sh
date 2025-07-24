#!/bin/bash
# AWS-Aligned Development Environment Setup Script
# This mirrors the production setup you'll use on EC2

echo "🚀 Starting AWS-Aligned Mayan Development Environment"

# Set production-like environment variables (matching current Docker setup)
export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'mayandbpass','USER':'mayan','HOST':'127.0.0.1','PORT':'5432'}}"
export MAYAN_CELERY_BROKER_URL="amqp://mayan:mayanrabbitpass@127.0.0.1:5672/mayan"
export MAYAN_CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/1"  # No password for current setup
export MAYAN_LOCK_MANAGER_BACKEND="mayan.apps.lock_manager.backends.redis_lock.RedisLock"
export MAYAN_LOCK_MANAGER_BACKEND_ARGUMENTS="{'redis_url':'redis://127.0.0.1:6379/2'}"  # No password

echo "✅ Environment variables set for AWS-like configuration"
echo "📝 Note: Using simplified Redis auth for development (production will use passwords)"

# Commands for common development tasks
case "${1:-}" in
    "check")
        echo "🔍 Running system check..."
        ./venv/bin/python manage.py check --settings=mayan.settings.development
        ;;
    "migrate")
        echo "📚 Running database migrations..."
        ./venv/bin/python manage.py migrate --settings=mayan.settings.development
        ;;
    "server")
        echo "🌐 Starting development server..."
        ./venv/bin/python manage.py runserver --settings=mayan.settings.development
        ;;
    "shell")
        echo "🐚 Starting Django shell..."
        ./venv/bin/python manage.py shell --settings=mayan.settings.development
        ;;
    "makemigrations")
        echo "📝 Creating migrations for research app..."
        ./venv/bin/python manage.py makemigrations research --settings=mayan.settings.development
        ;;
    "superuser")
        echo "👤 Creating superuser..."
        ./venv/bin/python manage.py createsuperuser --settings=mayan.settings.development
        ;;
    "test-api")
        echo "🔌 Testing research API endpoint..."
        curl -s http://localhost:8000/api/v4/research/ | python -m json.tool || echo "Server not running or endpoint error"
        ;;
    "initial-setup")
        echo "🏗️ Running initial setup..."
        ./venv/bin/python manage.py migrate --settings=mayan.settings.development
        ./venv/bin/python manage.py createsuperuser --settings=mayan.settings.development
        echo "✅ Initial setup complete!"
        echo "📝 Next steps:"
        echo "  1. ./dev_setup.sh server    # Start development server"
        echo "  2. Open http://localhost:8000 in browser"
        echo "  3. Login with superuser credentials"
        ;;
    "docker-status")
        echo "🐳 Checking Docker services..."
        cd docker && docker-compose ps
        ;;
    "aws-deploy-prep")
        echo "☁️ Preparing for AWS deployment..."
        echo "📋 Production environment variables for EC2:"
        echo ""
        echo "# PostgreSQL (AWS RDS)"
        echo "MAYAN_DATABASES=\"{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'YOUR_RDS_PASSWORD','USER':'mayan','HOST':'your-rds-endpoint.amazonaws.com','PORT':'5432'}}\""
        echo ""
        echo "# Redis (AWS ElastiCache)"
        echo "MAYAN_CELERY_RESULT_BACKEND=\"redis://your-elasticache-endpoint.amazonaws.com:6379/1\""
        echo "MAYAN_LOCK_MANAGER_BACKEND_ARGUMENTS=\"{'redis_url':'redis://your-elasticache-endpoint.amazonaws.com:6379/2'}\""
        echo ""
        echo "# RabbitMQ (AWS MQ)"
        echo "MAYAN_CELERY_BROKER_URL=\"amqp://your-username:your-password@your-mq-endpoint.amazonaws.com:5672/mayan\""
        ;;
    *)
        echo "🔧 Available commands:"
        echo "  ./dev_setup.sh check          # Check system"
        echo "  ./dev_setup.sh migrate        # Run migrations"  
        echo "  ./dev_setup.sh server         # Start dev server"
        echo "  ./dev_setup.sh shell          # Django shell"
        echo "  ./dev_setup.sh makemigrations # Create migrations"
        echo "  ./dev_setup.sh superuser      # Create admin user"
        echo "  ./dev_setup.sh test-api       # Test API endpoint"
        echo "  ./dev_setup.sh initial-setup  # Complete setup"
        echo "  ./dev_setup.sh docker-status  # Check Docker services"
        echo "  ./dev_setup.sh aws-deploy-prep # AWS deployment info"
        echo ""
        echo "📊 AWS Deployment Ready:"
        echo "  - PostgreSQL (like AWS RDS)"
        echo "  - Redis (like AWS ElastiCache)"  
        echo "  - RabbitMQ (like AWS MQ)"
        echo "  - Production-like config"
        ;;
esac 