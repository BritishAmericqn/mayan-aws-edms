"""
Utility functions for dataset analysis.
"""
import logging
from pathlib import Path

logger = logging.getLogger(name=__name__)


def detect_file_type(file_object):
    """
    Detect the file type from file object or filename.
    Returns the detected MIME type for processing.
    """
    if hasattr(file_object, 'name'):
        filename = Path(file_object.name)
        extension = filename.suffix.lower()
        
        if extension == '.csv':
            return 'text/csv'
        elif extension in ['.xlsx', '.xls']:
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif extension == '.json':
            return 'application/json'
        elif extension == '.xml':
            return 'application/xml'
    
    # Default to CSV for demo reliability
    return 'text/csv'


def safe_numeric_conversion(value):
    """
    Safely convert a value to numeric, returning None if conversion fails.
    """
    if value is None or str(value).strip() == '':
        return None
    
    try:
        # Try int first, then float
        if '.' not in str(value):
            return int(value)
        else:
            return float(value)
    except (ValueError, TypeError):
        return None


def generate_sample_rows(dataframe, num_rows=10):
    """
    Generate sample rows for preview display.
    """
    if dataframe is None or dataframe.empty:
        return []
    
    # Get column names as header
    header = dataframe.columns.tolist()
    
    # Get sample rows (first num_rows)
    sample_rows = [header]
    
    for _, row in dataframe.head(num_rows).iterrows():
        sample_rows.append(row.tolist())
    
    return sample_rows


def calculate_data_quality_metrics(dataframe):
    """
    Calculate data quality metrics for display.
    """
    if dataframe is None or dataframe.empty:
        return {
            'completeness': 0.0,
            'missing_values': 1.0,
            'duplicate_rows': 0.0
        }
    
    total_cells = dataframe.size
    missing_cells = dataframe.isnull().sum().sum()
    duplicate_rows = dataframe.duplicated().sum()
    
    return {
        'completeness': round((total_cells - missing_cells) / total_cells, 3),
        'missing_values': round(missing_cells / total_cells, 3),
        'duplicate_rows': round(duplicate_rows / len(dataframe), 3)
    }


def format_analysis_results(analysis_data):
    """
    Format analysis results for display in the UI.
    """
    if not analysis_data:
        return {}
    
    return {
        'status': 'completed',
        'summary': analysis_data.get('summary', {}),
        'data_quality': analysis_data.get('data_quality', {}),
        'sample_data': analysis_data.get('sample_data', []),
        'charts': analysis_data.get('charts', []),
        'statistics': analysis_data.get('statistics', {}),
        'generated_at': analysis_data.get('generated_at', None)
    } 