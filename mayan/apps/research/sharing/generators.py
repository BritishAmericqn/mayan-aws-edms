import boto3
import logging
from datetime import timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.models import Document
from mayan.apps.storage.classes import DefinedStorageLazy

logger = logging.getLogger(__name__)


class PreSignedURLGeneratorError(Exception):
    """Custom exception for pre-signed URL generation errors."""
    pass


class PreSignedURLGenerator:
    """
    Generates pre-signed URLs for secure document sharing.
    Supports both S3 storage and filesystem fallback for demo purposes.
    """
    
    DEFAULT_EXPIRATION_HOURS = 24
    MAX_EXPIRATION_HOURS = 168  # 7 days
    
    def __init__(self):
        self.storage = DefinedStorageLazy(name='documents__documentfile')
    
    def generate_url(self, document, expiration_hours=None, shared_document=None):
        """
        Generate a pre-signed URL for document access.
        
        Args:
            document: Document instance to share
            expiration_hours: Hours until URL expires (default: 24)
            shared_document: SharedDocument instance for tracking
            
        Returns:
            dict: Contains 'url', 'expires_at', 'method' and other metadata
        """
        if not expiration_hours:
            expiration_hours = self.DEFAULT_EXPIRATION_HOURS
            
        # Validate expiration time
        if expiration_hours > self.MAX_EXPIRATION_HOURS:
            raise PreSignedURLGeneratorError(
                f"Expiration hours cannot exceed {self.MAX_EXPIRATION_HOURS}"
            )
        
        expires_at = timezone.now() + timedelta(hours=expiration_hours)
        
        try:
            # Get the latest document file
            if not document.file_latest:
                raise PreSignedURLGeneratorError(
                    f"Document '{document}' has no files to share"
                )
            
            document_file = document.file_latest
            
            # Try S3 pre-signed URL first
            s3_url = self._generate_s3_presigned_url(
                document_file, expiration_hours
            )
            
            if s3_url:
                return {
                    'url': s3_url,
                    'expires_at': expires_at,
                    'method': 's3_presigned',
                    'storage_type': 'S3',
                    'document_file': document_file,
                    'demo_info': self._get_demo_info(document, expires_at, 'S3')
                }
                
        except Exception as e:
            logger.warning(f"S3 pre-signed URL generation failed: {e}")
        
        # Fallback to Mayan-based sharing URL
        return self._generate_mayan_sharing_url(
            document, expires_at, shared_document
        )
    
    def _generate_s3_presigned_url(self, document_file, expiration_hours):
        """
        Generate S3 pre-signed URL if storage backend supports it.
        """
        storage_instance = self.storage.get_storage_instance()
        
        # Check if this is an S3-compatible storage
        if not hasattr(storage_instance, 'bucket_name'):
            return None
            
        try:
            # Get S3 configuration from storage
            bucket_name = storage_instance.bucket_name
            region_name = getattr(storage_instance, 'region_name', 'us-east-1')
            
            # Get AWS credentials (from storage instance or environment)
            aws_access_key_id = getattr(storage_instance, 'access_key', None)
            aws_secret_access_key = getattr(storage_instance, 'secret_key', None)
            
            # Create boto3 S3 client
            s3_client = boto3.client(
                's3',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            
            # Get the file key (path in S3)
            file_key = document_file.file.name
            
            # Generate pre-signed URL
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_key},
                ExpiresIn=expiration_hours * 3600  # Convert to seconds
            )
            
            logger.info(f"Generated S3 pre-signed URL for document {document_file.document}")
            return presigned_url
            
        except Exception as e:
            logger.error(f"Failed to generate S3 pre-signed URL: {e}")
            raise PreSignedURLGeneratorError(f"S3 URL generation failed: {e}")
    
    def _generate_mayan_sharing_url(self, document, expires_at, shared_document):
        """
        Generate Mayan-based sharing URL as fallback.
        """
        if not shared_document:
            raise PreSignedURLGeneratorError(
                "SharedDocument instance required for Mayan-based sharing"
            )
        
        # Build the sharing URL
        sharing_url = urljoin(
            getattr(settings, 'BASE_URL', 'http://localhost'),
            reverse('research:shared_document_access', kwargs={
                'url_key': shared_document.url_key
            })
        )
        
        return {
            'url': sharing_url,
            'expires_at': expires_at,
            'method': 'mayan_sharing',
            'storage_type': 'Mayan Internal',
            'document_file': document.file_latest,
            'shared_document': shared_document,
            'demo_info': self._get_demo_info(document, expires_at, 'Mayan Internal')
        }
    
    def _get_demo_info(self, document, expires_at, storage_type):
        """
        Generate demo-friendly information for presentation.
        """
        time_until_expiry = expires_at - timezone.now()
        
        return {
            'document_name': document.label,
            'storage_type': storage_type,
            'expires_in_hours': round(time_until_expiry.total_seconds() / 3600, 1),
            'expires_at_formatted': expires_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'file_size': document.file_latest.size if document.file_latest else 0,
            'file_type': document.file_latest.mimetype if document.file_latest else 'unknown',
        }
    
    def validate_document_access(self, document, user):
        """
        Validate that user has permission to share this document.
        """
        from ..permissions import permission_dataset_share
        from mayan.apps.acls.models import AccessControlList
        
        try:
            AccessControlList.objects.check_access(
                obj=document,
                permission=permission_dataset_share,
                user=user
            )
            return True
        except Exception as e:
            logger.warning(f"Document sharing permission denied for user {user}: {e}")
            return False
    
    def get_supported_storage_types(self):
        """
        Get list of supported storage types for demo.
        """
        storage_instance = self.storage.get_storage_instance()
        
        types = ['Mayan Internal']
        
        if hasattr(storage_instance, 'bucket_name'):
            types.append('Amazon S3')
        
        return types
    
    @classmethod
    def get_demo_generator(cls):
        """
        Get a generator instance optimized for demo purposes.
        """
        generator = cls()
        
        # Add demo-specific configurations
        generator.demo_mode = True
        generator.demo_expiration_hours = 1  # Short expiration for demo
        
        return generator


class S3PreSignedURLGenerator(PreSignedURLGenerator):
    """
    Specialized generator for S3-only pre-signed URLs.
    Used when you know you're working with S3 storage.
    """
    
    def __init__(self, bucket_name=None, region_name=None):
        super().__init__()
        self.bucket_name = bucket_name
        self.region_name = region_name or 'us-east-1'
    
    def generate_url(self, document, expiration_hours=None, **kwargs):
        """Generate S3-only pre-signed URL."""
        if not expiration_hours:
            expiration_hours = self.DEFAULT_EXPIRATION_HOURS
            
        expires_at = timezone.now() + timedelta(hours=expiration_hours)
        
        try:
            s3_url = self._generate_s3_presigned_url(
                document.file_latest, expiration_hours
            )
            
            if not s3_url:
                raise PreSignedURLGeneratorError("S3 storage not configured")
                
            return {
                'url': s3_url,
                'expires_at': expires_at,
                'method': 's3_presigned_only',
                'storage_type': 'Amazon S3',
                'document_file': document.file_latest,
                'demo_info': self._get_demo_info(document, expires_at, 'Amazon S3')
            }
            
        except Exception as e:
            raise PreSignedURLGeneratorError(f"S3-only URL generation failed: {e}")


# Demo utility functions for Task 3.1 testing
def create_demo_share(document, user, hours=1):
    """
    Create a demo share for testing purposes.
    """
    from .models import SharedDocument
    
    generator = PreSignedURLGenerator.get_demo_generator()
    
    # Create SharedDocument instance
    shared_doc = SharedDocument.objects.create_shared_document(
        document=document,
        created_by=user,
        expiration_hours=hours,
        label=f"Demo Share: {document.label}"
    )
    
    # Generate the URL
    url_info = generator.generate_url(
        document=document,
        expiration_hours=hours,
        shared_document=shared_doc
    )
    
    return {
        'shared_document': shared_doc,
        'url_info': url_info,
        'demo_ready': True
    }


def test_url_generation():
    """
    Test function for verifying URL generation works.
    """
    try:
        generator = PreSignedURLGenerator()
        storage_types = generator.get_supported_storage_types()
        
        return {
            'generator_ready': True,
            'supported_storage': storage_types,
            'demo_mode': hasattr(generator, 'demo_mode')
        }
    except Exception as e:
        return {
            'generator_ready': False,
            'error': str(e)
        } 