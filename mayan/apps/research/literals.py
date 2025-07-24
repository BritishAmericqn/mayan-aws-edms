# Task timeout values
LOCK_EXPIRE_TIME_DATASET_ANALYSIS = 60 * 60  # 1 hour

# Analysis status choices
ANALYSIS_STATUS_PENDING = 'pending'
ANALYSIS_STATUS_PROCESSING = 'processing'
ANALYSIS_STATUS_COMPLETED = 'completed'
ANALYSIS_STATUS_FAILED = 'failed'

ANALYSIS_STATUS_CHOICES = (
    (ANALYSIS_STATUS_PENDING, 'Pending'),
    (ANALYSIS_STATUS_PROCESSING, 'Processing'),
    (ANALYSIS_STATUS_COMPLETED, 'Completed'),
    (ANALYSIS_STATUS_FAILED, 'Failed'),
)

# Data type choices for datasets
DATA_TYPE_CSV = 'csv'
DATA_TYPE_EXCEL = 'excel'
DATA_TYPE_JSON = 'json'
DATA_TYPE_XML = 'xml'
DATA_TYPE_IMAGE = 'image'
DATA_TYPE_VIDEO = 'video'
DATA_TYPE_AUDIO = 'audio'
DATA_TYPE_TEXT = 'text'
DATA_TYPE_OTHER = 'other'

DATA_TYPE_CHOICES = (
    (DATA_TYPE_CSV, 'CSV'),
    (DATA_TYPE_EXCEL, 'Excel'),
    (DATA_TYPE_JSON, 'JSON'),
    (DATA_TYPE_XML, 'XML'),
    (DATA_TYPE_IMAGE, 'Image'),
    (DATA_TYPE_VIDEO, 'Video'),
    (DATA_TYPE_AUDIO, 'Audio'),
    (DATA_TYPE_TEXT, 'Text'),
    (DATA_TYPE_OTHER, 'Other'),
)

# File format choices
FORMAT_CSV = 'csv'
FORMAT_XLSX = 'xlsx'
FORMAT_JSON = 'json'
FORMAT_XML = 'xml'
FORMAT_PDF = 'pdf'
FORMAT_PNG = 'png'
FORMAT_JPG = 'jpg'
FORMAT_MP4 = 'mp4'
FORMAT_MP3 = 'mp3'
FORMAT_TXT = 'txt'

FORMAT_CHOICES = (
    (FORMAT_CSV, 'CSV'),
    (FORMAT_XLSX, 'Excel (XLSX)'),
    (FORMAT_JSON, 'JSON'),
    (FORMAT_XML, 'XML'),
    (FORMAT_PDF, 'PDF'),
    (FORMAT_PNG, 'PNG'),
    (FORMAT_JPG, 'JPEG'),
    (FORMAT_MP4, 'MP4'),
    (FORMAT_MP3, 'MP3'),
    (FORMAT_TXT, 'Text'),
)

# Dataset document role choices
ROLE_PRIMARY = 'primary'
ROLE_SUPPLEMENTARY = 'supplementary'
ROLE_REFERENCE = 'reference'
ROLE_METADATA = 'metadata'

ROLE_CHOICES = (
    (ROLE_PRIMARY, 'Primary Data'),
    (ROLE_SUPPLEMENTARY, 'Supplementary Data'),
    (ROLE_REFERENCE, 'Reference Material'),
    (ROLE_METADATA, 'Metadata'),
) 