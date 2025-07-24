import logging

from celery import current_app

from django.apps import apps

from mayan.apps.events.decorators import method_event
from mayan.apps.lock_manager.backends.base import LockingBackend
from mayan.apps.lock_manager.exceptions import LockError

from .events import event_dataset_analysis_completed, event_dataset_processed
from .literals import LOCK_EXPIRE_TIME_DATASET_ANALYSIS

logger = logging.getLogger(name=__name__)


@current_app.task(bind=True, ignore_result=True, retry_backoff=True)
def task_dataset_analyze(self, dataset_id, user_id=None):
    """
    Task to analyze a dataset and generate statistics.
    """
    Dataset = apps.get_model(app_label='research', model_name='Dataset')
    
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        logger.error('Dataset with ID %s not found', dataset_id)
        return
    
    lock_id = f'dataset_analysis_{dataset_id}'
    
    try:
        # Acquire lock to prevent concurrent analysis
        lock = LockingBackend.get_backend().acquire_lock(
            name=lock_id, timeout=LOCK_EXPIRE_TIME_DATASET_ANALYSIS
        )
    except LockError:
        logger.warning(
            'Unable to acquire lock for dataset analysis: %s', lock_id
        )
        return
    
    try:
        logger.info('Starting analysis for dataset: %s', dataset.title)
        
        # Update status to processing
        dataset.analysis_status = 'processing'
        dataset.save(update_fields=['analysis_status'])
        
        # Simulate analysis process (in real implementation, this would
        # analyze actual data files)
        analysis_results = _perform_dataset_analysis(dataset)
        
        # Update dataset with results
        dataset.analysis_status = 'completed'
        dataset.analysis_results = analysis_results
        dataset.save(update_fields=['analysis_status', 'analysis_results'])
        
        # Fire completion event
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(pk=user_id)
                dataset._event_actor = user
            except User.DoesNotExist:
                pass
        
        event_dataset_analysis_completed.commit(
            actor=getattr(dataset, '_event_actor', None),
            target=dataset
        )
        
        logger.info('Completed analysis for dataset: %s', dataset.title)
        
    except Exception as exception:
        logger.exception(
            'Error during dataset analysis for dataset ID: %s; %s',
            dataset_id, exception
        )
        
        # Update status to failed
        dataset.analysis_status = 'failed'
        dataset.save(update_fields=['analysis_status'])
        
        raise
    finally:
        try:
            lock.release()
        except Exception:
            logger.exception('Error releasing lock: %s', lock_id)


@current_app.task(bind=True, ignore_result=True)
def task_dataset_process_file(self, dataset_id, document_file_id):
    """
    Task to process a file associated with a dataset.
    """
    Dataset = apps.get_model(app_label='research', model_name='Dataset')
    DocumentFile = apps.get_model(app_label='documents', model_name='DocumentFile')
    
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        document_file = DocumentFile.objects.get(pk=document_file_id)
    except (Dataset.DoesNotExist, DocumentFile.DoesNotExist) as exception:
        logger.error('Object not found: %s', exception)
        return
    
    logger.info(
        'Processing file %s for dataset %s', 
        document_file.filename, dataset.title
    )
    
    try:
        # Process the file (extract metadata, validate format, etc.)
        _process_dataset_file(dataset, document_file)
        
        # Fire processed event
        event_dataset_processed.commit(
            actor=getattr(dataset, '_event_actor', None),
            target=dataset,
            action_object=document_file
        )
        
        logger.info(
            'Successfully processed file %s for dataset %s',
            document_file.filename, dataset.title
        )
        
    except Exception as exception:
        logger.exception(
            'Error processing file %s for dataset %s: %s',
            document_file.filename, dataset.title, exception
        )
        raise


@current_app.task(bind=True, ignore_result=True)
def task_generate_dataset_preview(self, dataset_id):
    """
    Task to generate a preview for a dataset.
    """
    Dataset = apps.get_model(app_label='research', model_name='Dataset')
    
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        logger.error('Dataset with ID %s not found', dataset_id)
        return
    
    logger.info('Generating preview for dataset: %s', dataset.title)
    
    try:
        # Generate preview (charts, sample data, etc.)
        preview_data = _generate_preview_data(dataset)
        
        # Store preview in dataset's extra_data
        dataset.set_extra_data_key('preview_data', preview_data)
        dataset.save()
        
        logger.info('Generated preview for dataset: %s', dataset.title)
        
    except Exception as exception:
        logger.exception(
            'Error generating preview for dataset %s: %s',
            dataset.title, exception
        )
        raise


@current_app.task(bind=True, ignore_result=True)
def task_export_dataset(self, dataset_id, export_format='csv'):
    """
    Task to export a dataset in specified format.
    """
    Dataset = apps.get_model(app_label='research', model_name='Dataset')
    
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        logger.error('Dataset with ID %s not found', dataset_id)
        return
    
    logger.info(
        'Exporting dataset %s in format %s', dataset.title, export_format
    )
    
    try:
        # Export dataset (in real implementation, this would create
        # downloadable files)
        export_path = _export_dataset_data(dataset, export_format)
        
        # Store export info in dataset's extra_data
        exports = dataset.get_extra_data_key('exports', default={})
        exports[export_format] = {
            'path': export_path,
            'timestamp': dataset.datetime_modified.isoformat()
        }
        dataset.set_extra_data_key('exports', exports)
        dataset.save()
        
        logger.info(
            'Exported dataset %s to %s', dataset.title, export_path
        )
        
    except Exception as exception:
        logger.exception(
            'Error exporting dataset %s: %s', dataset.title, exception
        )
        raise


@current_app.task(bind=True, ignore_result=True)
def task_generate_share_link(self, dataset_id, expiration_hours=24):
    """
    Task to generate a secure share link for a dataset.
    """
    Dataset = apps.get_model(app_label='research', model_name='Dataset')
    
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        logger.error('Dataset with ID %s not found', dataset_id)
        return
    
    logger.info('Generating share link for dataset: %s', dataset.title)
    
    try:
        # Generate secure share link (would integrate with S3 pre-signed URLs)
        share_data = _generate_share_link(dataset, expiration_hours)
        
        # Store share info
        shares = dataset.get_extra_data_key('shares', default=[])
        shares.append(share_data)
        dataset.set_extra_data_key('shares', shares)
        dataset.save()
        
        logger.info('Generated share link for dataset: %s', dataset.title)
        
    except Exception as exception:
        logger.exception(
            'Error generating share link for dataset %s: %s',
            dataset.title, exception
        )
        raise


@current_app.task(bind=True, ignore_result=True)
def task_cleanup_expired_shares(self):
    """
    Task to cleanup expired share links.
    """
    Dataset = apps.get_model(app_label='research', model_name='Dataset')
    
    logger.info('Starting cleanup of expired share links')
    
    try:
        # Clean up expired shares across all datasets
        cleaned_count = _cleanup_expired_shares()
        
        logger.info('Cleaned up %d expired share links', cleaned_count)
        
    except Exception as exception:
        logger.exception('Error during share link cleanup: %s', exception)
        raise


# Helper functions (demo implementations)

def _perform_dataset_analysis(dataset):
    """Perform analysis on dataset (demo implementation)."""
    import random
    
    # Mock analysis results
    return {
        'row_count': random.randint(100, 10000),
        'column_count': random.randint(5, 20),
        'data_quality': {
            'completeness': round(random.uniform(0.85, 1.0), 2),
            'missing_values': round(random.uniform(0.0, 0.15), 2),
            'duplicates': round(random.uniform(0.0, 0.05), 2)
        },
        'summary_statistics': {
            'numeric_columns': random.randint(2, 10),
            'categorical_columns': random.randint(1, 5),
            'datetime_columns': random.randint(0, 2)
        },
        'generated_at': dataset.datetime_modified.isoformat()
    }


def _process_dataset_file(dataset, document_file):
    """Process a dataset file (demo implementation)."""
    # In real implementation, this would validate file format,
    # extract metadata, check data quality, etc.
    pass


def _generate_preview_data(dataset):
    """Generate preview data for dataset (demo implementation)."""
    import random
    
    return {
        'sample_rows': [
            ['Name', 'Age', 'City', 'Score'],
            ['John Doe', 30, 'New York', 85.5],
            ['Jane Smith', 25, 'Boston', 92.3],
            ['Bob Johnson', 35, 'Chicago', 78.9]
        ],
        'charts': [
            {
                'type': 'histogram',
                'title': 'Age Distribution',
                'data': [random.randint(20, 60) for _ in range(10)]
            },
            {
                'type': 'bar',
                'title': 'Score by City',
                'data': {'New York': 85.5, 'Boston': 92.3, 'Chicago': 78.9}
            }
        ]
    }


def _export_dataset_data(dataset, export_format):
    """Export dataset data (demo implementation)."""
    # In real implementation, this would create actual export files
    return f'/exports/dataset_{dataset.pk}.{export_format}'


def _generate_share_link(dataset, expiration_hours):
    """Generate share link (demo implementation)."""
    import uuid
    from datetime import datetime, timedelta
    
    return {
        'token': str(uuid.uuid4()),
        'url': f'/shared/dataset/{dataset.pk}/',
        'expires_at': (datetime.now() + timedelta(hours=expiration_hours)).isoformat(),
        'created_at': datetime.now().isoformat()
    }


def _cleanup_expired_shares():
    """Cleanup expired shares (demo implementation)."""
    # In real implementation, this would actually clean up expired shares
    return 0 