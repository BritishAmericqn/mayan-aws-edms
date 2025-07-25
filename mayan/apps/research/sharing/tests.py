import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from mayan.apps.documents.models import Document, DocumentType

from .models import SharedDocument
from .generators import PreSignedURLGenerator, create_demo_share, test_url_generation

User = get_user_model()


class SharedDocumentModelTest(TestCase):
    """Test cases for SharedDocument model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test document type and document
        self.document_type = DocumentType.objects.create(
            label='Test Document Type'
        )
        
        self.document = Document.objects.create(
            document_type=self.document_type,
            label='Test Document for Sharing'
        )
        
    def test_shared_document_creation(self):
        """Test SharedDocument model creation and basic functionality."""
        # Create shared document
        shared_doc = SharedDocument.objects.create_shared_document(
            document=self.document,
            created_by=self.user,
            expiration_hours=24,
            label='Test Share'
        )
        
        # Verify creation
        self.assertIsInstance(shared_doc, SharedDocument)
        self.assertEqual(shared_doc.document, self.document)
        self.assertEqual(shared_doc.created_by, self.user)
        self.assertEqual(shared_doc.label, 'Test Share')
        self.assertIsInstance(shared_doc.url_key, uuid.UUID)
        self.assertTrue(shared_doc.is_active)
        self.assertEqual(shared_doc.access_count, 0)
        
    def test_expiration_logic(self):
        """Test expiration checking logic."""
        # Create expired share
        expired_share = SharedDocument.objects.create(
            document=self.document,
            created_by=self.user,
            label='Expired Share',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create active share
        active_share = SharedDocument.objects.create(
            document=self.document,
            created_by=self.user,
            label='Active Share',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Test expiration
        self.assertTrue(expired_share.is_expired())
        self.assertFalse(active_share.is_expired())
        
        # Test access allowed
        self.assertFalse(expired_share.is_access_allowed())
        self.assertTrue(active_share.is_access_allowed())
        
    def test_access_tracking(self):
        """Test access tracking functionality."""
        shared_doc = SharedDocument.objects.create_shared_document(
            document=self.document,
            created_by=self.user,
            expiration_hours=24
        )
        
        # Record access
        success = shared_doc.record_access(ip_address='192.168.1.1')
        
        # Verify tracking
        self.assertTrue(success)
        self.assertEqual(shared_doc.access_count, 1)
        self.assertIsNotNone(shared_doc.last_accessed_at)
        self.assertEqual(shared_doc.last_accessed_from_ip, '192.168.1.1')
        
    def test_access_limits(self):
        """Test access count limits."""
        shared_doc = SharedDocument.objects.create(
            document=self.document,
            created_by=self.user,
            label='Limited Share',
            expires_at=timezone.now() + timedelta(hours=1),
            max_access_count=2
        )
        
        # First access should work
        self.assertTrue(shared_doc.record_access())
        self.assertEqual(shared_doc.access_count, 1)
        
        # Second access should work
        self.assertTrue(shared_doc.record_access())
        self.assertEqual(shared_doc.access_count, 2)
        
        # Third access should fail
        self.assertFalse(shared_doc.record_access())
        self.assertEqual(shared_doc.access_count, 2)  # Should not increment
        
    def test_demo_info_generation(self):
        """Test demo information generation."""
        shared_doc = SharedDocument.objects.create_shared_document(
            document=self.document,
            created_by=self.user,
            expiration_hours=2
        )
        
        demo_info = shared_doc.get_demo_info()
        
        # Verify demo info structure
        self.assertIn('share_key', demo_info)
        self.assertIn('document_name', demo_info)
        self.assertIn('created_by', demo_info)
        self.assertIn('access_count', demo_info)
        self.assertIn('expiration_status', demo_info)
        
        # Verify content
        self.assertEqual(demo_info['document_name'], self.document.label)
        self.assertEqual(demo_info['access_count'], 0)
        
    def test_manager_methods(self):
        """Test SharedDocumentManager methods."""
        # Create test shares
        active_share = SharedDocument.objects.create_shared_document(
            document=self.document,
            created_by=self.user,
            expiration_hours=24
        )
        
        expired_share = SharedDocument.objects.create(
            document=self.document,
            created_by=self.user,
            label='Expired',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Test get_valid_shares
        valid_shares = SharedDocument.objects.get_valid_shares()
        self.assertIn(active_share, valid_shares)
        self.assertNotIn(expired_share, valid_shares)
        
        # Test cleanup_expired
        cleanup_count = SharedDocument.objects.cleanup_expired()
        self.assertEqual(cleanup_count, 1)
        
        # Verify expired share was deleted
        self.assertFalse(
            SharedDocument.objects.filter(pk=expired_share.pk).exists()
        )


class PreSignedURLGeneratorTest(TestCase):
    """Test cases for PreSignedURLGenerator functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.document_type = DocumentType.objects.create(
            label='Test Document Type'
        )
        
        self.document = Document.objects.create(
            document_type=self.document_type,
            label='Test Document'
        )
        
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = PreSignedURLGenerator()
        self.assertIsInstance(generator, PreSignedURLGenerator)
        self.assertEqual(generator.DEFAULT_EXPIRATION_HOURS, 24)
        self.assertEqual(generator.MAX_EXPIRATION_HOURS, 168)
        
    def test_supported_storage_types(self):
        """Test storage type detection."""
        generator = PreSignedURLGenerator()
        storage_types = generator.get_supported_storage_types()
        
        # Should at least support Mayan Internal
        self.assertIn('Mayan Internal', storage_types)
        
    @patch('mayan.apps.research.sharing.generators.boto3')
    def test_s3_url_generation_with_mock(self, mock_boto3):
        """Test S3 URL generation with mocked boto3."""
        # Mock S3 client
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = 'https://s3.amazonaws.com/test-bucket/test-file?signature=123'
        mock_boto3.client.return_value = mock_client
        
        # Mock storage instance to look like S3
        generator = PreSignedURLGenerator()
        
        with patch.object(generator.storage, 'get_storage_instance') as mock_storage:
            mock_storage_instance = MagicMock()
            mock_storage_instance.bucket_name = 'test-bucket'
            mock_storage_instance.region_name = 'us-east-1'
            mock_storage_instance.access_key = 'test-key'
            mock_storage_instance.secret_key = 'test-secret'
            mock_storage.return_value = mock_storage_instance
            
            # Mock document file
            mock_document_file = MagicMock()
            mock_document_file.file.name = 'test-file.pdf'
            
            with patch.object(self.document, 'file_latest', mock_document_file):
                result = generator._generate_s3_presigned_url(
                    mock_document_file, 24
                )
                
                # Verify S3 client was called correctly
                mock_boto3.client.assert_called_once()
                mock_client.generate_presigned_url.assert_called_once()
                
                # Verify result
                self.assertIn('s3.amazonaws.com', result)
                
    def test_demo_generator(self):
        """Test demo generator creation."""
        demo_generator = PreSignedURLGenerator.get_demo_generator()
        
        self.assertTrue(hasattr(demo_generator, 'demo_mode'))
        self.assertTrue(demo_generator.demo_mode)
        self.assertEqual(demo_generator.demo_expiration_hours, 1)
        
    def test_create_demo_share(self):
        """Test demo share creation utility."""
        # Mock document file
        with patch.object(self.document, 'file_latest', MagicMock()):
            result = create_demo_share(
                document=self.document,
                user=self.user,
                hours=1
            )
            
            # Verify result structure
            self.assertIn('shared_document', result)
            self.assertIn('url_info', result)
            self.assertIn('demo_ready', result)
            
            self.assertTrue(result['demo_ready'])
            self.assertIsInstance(result['shared_document'], SharedDocument)
            
    def test_url_generation_test_function(self):
        """Test the test utility function."""
        result = test_url_generation()
        
        # Should return status information
        self.assertIn('generator_ready', result)
        self.assertIn('supported_storage', result)
        
        if result['generator_ready']:
            self.assertIsInstance(result['supported_storage'], list)


class SharingIntegrationTest(TestCase):
    """Integration tests for the complete sharing system."""
    
    def setUp(self):
        """Set up integration test data."""
        self.user = User.objects.create_user(
            username='integrationuser',
            password='testpass123'
        )
        
        self.document_type = DocumentType.objects.create(
            label='Integration Test Documents'
        )
        
        self.document = Document.objects.create(
            document_type=self.document_type,
            label='Integration Test Document'
        )
        
    def test_end_to_end_sharing_workflow(self):
        """Test complete sharing workflow from creation to access."""
        # Step 1: Create shared document
        shared_doc = SharedDocument.objects.create_shared_document(
            document=self.document,
            created_by=self.user,
            expiration_hours=1,
            label='Integration Test Share'
        )
        
        # Step 2: Verify creation
        self.assertIsInstance(shared_doc, SharedDocument)
        self.assertTrue(shared_doc.is_access_allowed())
        
        # Step 3: Simulate access
        initial_access_count = shared_doc.access_count
        success = shared_doc.record_access(ip_address='127.0.0.1')
        
        # Step 4: Verify access tracking
        self.assertTrue(success)
        self.assertEqual(shared_doc.access_count, initial_access_count + 1)
        self.assertEqual(shared_doc.last_accessed_from_ip, '127.0.0.1')
        
        # Step 5: Test demo information
        demo_info = shared_doc.get_demo_info()
        self.assertGreater(len(demo_info), 0)
        
    def test_sharing_with_url_generator(self):
        """Test sharing integration with URL generator."""
        generator = PreSignedURLGenerator()
        
        # Mock document file for URL generation
        with patch.object(self.document, 'file_latest', MagicMock()):
            shared_doc = SharedDocument.objects.create_shared_document(
                document=self.document,
                created_by=self.user,
                expiration_hours=2
            )
            
            # Generate URL info
            url_info = generator._generate_mayan_sharing_url(
                self.document, shared_doc.expires_at, shared_doc
            )
            
            # Verify URL info structure
            self.assertIn('url', url_info)
            self.assertIn('expires_at', url_info)
            self.assertIn('method', url_info)
            self.assertIn('storage_type', url_info)
            self.assertIn('demo_info', url_info)
            
            # Verify method type
            self.assertEqual(url_info['method'], 'mayan_sharing')
            self.assertEqual(url_info['storage_type'], 'Mayan Internal') 