"""
Dataset parsers for research analysis.
Handles CSV, Excel, and other data file formats.
"""
import logging
import io
from pathlib import Path

from django.apps import apps

from .utils import detect_file_type

logger = logging.getLogger(name=__name__)


class DatasetParser:
    """
    Main parser class for datasets following Mayan patterns.
    Registry-based system for different file types.
    """
    _registry = {}
    
    @classmethod
    def register(cls, mime_types, parser_classes):
        """Register parser classes for specific MIME types."""
        for mime_type in mime_types:
            for parser_class in parser_classes:
                cls._registry.setdefault(mime_type, []).append(parser_class)
    
    @classmethod
    def parse_document_file(cls, document_file):
        """
        Parse a document file and return structured data.
        Main entry point for dataset analysis.
        """
        mime_type = document_file.mimetype
        parser_classes = cls._registry.get(mime_type, [])
        
        # Fallback to CSV parser for unknown types (demo reliability)
        if not parser_classes:
            parser_classes = cls._registry.get('text/csv', [])
        
        for parser_class in parser_classes:
            try:
                parser = parser_class()
                return parser.process_file(document_file)
            except Exception as exception:
                logger.warning(
                    'Parser %s failed for document file %s: %s',
                    parser_class.__name__, document_file, exception
                )
                continue
        
        # If all parsers fail, return None for graceful handling
        logger.error(
            'No parser could process document file: %s', document_file
        )
        return None
    
    def process_file(self, document_file):
        """
        Process a document file and return structured data.
        To be implemented by subclasses.
        """
        raise NotImplementedError


class CSVParser(DatasetParser):
    """Parser for CSV files using pandas."""
    
    def process_file(self, document_file):
        """Process CSV file and return pandas DataFrame."""
        try:
            # Import pandas here to avoid startup dependency
            import pandas as pd
            
            logger.info('Parsing CSV file: %s', document_file.filename)
            
            with document_file.open() as file_object:
                # Read CSV data
                content = file_object.read()
                
                # Handle both bytes and string content
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                
                # Create StringIO for pandas
                data_io = io.StringIO(content)
                
                # Parse CSV with pandas
                dataframe = pd.read_csv(data_io)
                
                logger.info(
                    'Successfully parsed CSV: %d rows, %d columns',
                    len(dataframe), len(dataframe.columns)
                )
                
                return dataframe
                
        except ImportError:
            logger.error('pandas not available for CSV parsing')
            return self._fallback_csv_parse(document_file)
        except Exception as exception:
            logger.error(
                'Error parsing CSV file %s: %s',
                document_file.filename, exception
            )
            return None
    
    def _fallback_csv_parse(self, document_file):
        """Fallback CSV parsing without pandas."""
        import csv
        
        try:
            with document_file.open() as file_object:
                content = file_object.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                
                # Simple CSV parsing
                lines = content.strip().split('\n')
                if not lines:
                    return None
                
                # Use csv module for basic parsing
                reader = csv.reader(lines)
                rows = list(reader)
                
                if not rows:
                    return None
                
                # Create simple dict structure
                headers = rows[0]
                data_rows = rows[1:]
                
                return {
                    'columns': headers,
                    'data': data_rows,
                    'rows': len(data_rows),
                    'parser': 'fallback_csv'
                }
                
        except Exception as exception:
            logger.error(
                'Fallback CSV parsing failed for %s: %s',
                document_file.filename, exception
            )
            return None


class ExcelParser(DatasetParser):
    """Parser for Excel files using pandas and openpyxl."""
    
    def process_file(self, document_file):
        """Process Excel file and return pandas DataFrame."""
        try:
            # Import required packages
            import pandas as pd
            
            logger.info('Parsing Excel file: %s', document_file.filename)
            
            with document_file.open() as file_object:
                # Read Excel data
                dataframe = pd.read_excel(file_object, engine='openpyxl')
                
                logger.info(
                    'Successfully parsed Excel: %d rows, %d columns',
                    len(dataframe), len(dataframe.columns)
                )
                
                return dataframe
                
        except ImportError as exception:
            logger.error(
                'Required packages not available for Excel parsing: %s',
                exception
            )
            return None
        except Exception as exception:
            logger.error(
                'Error parsing Excel file %s: %s',
                document_file.filename, exception
            )
            return None


class JSONParser(DatasetParser):
    """Parser for JSON files."""
    
    def process_file(self, document_file):
        """Process JSON file and return structured data."""
        try:
            import json
            import pandas as pd
            
            logger.info('Parsing JSON file: %s', document_file.filename)
            
            with document_file.open() as file_object:
                content = file_object.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                
                data = json.loads(content)
                
                # Try to convert to DataFrame if possible
                if isinstance(data, list) and data:
                    dataframe = pd.DataFrame(data)
                    return dataframe
                elif isinstance(data, dict):
                    # Simple dict to DataFrame conversion
                    dataframe = pd.DataFrame([data])
                    return dataframe
                
                return data
                
        except Exception as exception:
            logger.error(
                'Error parsing JSON file %s: %s',
                document_file.filename, exception
            )
            return None


# Register parsers for their respective MIME types
DatasetParser.register(
    mime_types=['text/csv'],
    parser_classes=[CSVParser]
)

DatasetParser.register(
    mime_types=[
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    ],
    parser_classes=[ExcelParser]
)

DatasetParser.register(
    mime_types=['application/json'],
    parser_classes=[JSONParser]
) 