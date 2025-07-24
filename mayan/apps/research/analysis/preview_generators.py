"""
Preview generators for research datasets.
Creates charts, visualizations, and data previews for demo display.
"""
import logging
import base64
import io
from datetime import datetime

logger = logging.getLogger(name=__name__)


class ChartGenerator:
    """
    Chart and visualization generator for datasets.
    Creates matplotlib-based charts optimized for demo presentation.
    """
    
    def __init__(self, dataframe=None):
        self.dataframe = dataframe
        self.charts = []
    
    def generate_all_charts(self, dataframe=None):
        """
        Generate all applicable charts for the dataset.
        Returns list of chart data for display.
        """
        if dataframe is not None:
            self.dataframe = dataframe
        
        if self.dataframe is None or self.dataframe.empty:
            return []
        
        try:
            # Import required packages
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
            
            logger.info('Generating charts for dataset visualization')
            
            self.charts = []
            
            # Generate different chart types
            self._generate_distribution_charts()
            self._generate_correlation_heatmap()
            self._generate_categorical_charts()
            self._generate_time_series_charts()
            self._generate_summary_charts()
            
            logger.info('Generated %d charts successfully', len(self.charts))
            return self.charts
            
        except ImportError:
            logger.warning('matplotlib not available, skipping chart generation')
            return self._generate_text_charts()
        except Exception as exception:
            logger.error('Error generating charts: %s', exception)
            return []
    
    def _generate_distribution_charts(self):
        """Generate histograms and distribution charts for numeric columns."""
        import matplotlib.pyplot as plt
        import numpy as np
        
        numeric_columns = self.dataframe.select_dtypes(include=['number']).columns
        
        for column in numeric_columns[:4]:  # Limit to first 4 for demo
            try:
                data = self.dataframe[column].dropna()
                
                if len(data) < 2:
                    continue
                
                plt.figure(figsize=(10, 6))
                plt.hist(data, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                plt.title(f'Distribution of {column}', fontsize=14, fontweight='bold')
                plt.xlabel(column, fontsize=12)
                plt.ylabel('Frequency', fontsize=12)
                plt.grid(True, alpha=0.3)
                
                # Add statistics text
                mean_val = data.mean()
                std_val = data.std()
                plt.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
                plt.axvline(mean_val + std_val, color='orange', linestyle='--', alpha=0.7, label=f'+1 SD: {mean_val + std_val:.2f}')
                plt.axvline(mean_val - std_val, color='orange', linestyle='--', alpha=0.7, label=f'-1 SD: {mean_val - std_val:.2f}')
                plt.legend()
                
                # Convert to base64
                chart_data = self._plt_to_base64()
                self.charts.append({
                    'type': 'histogram',
                    'title': f'Distribution of {column}',
                    'column': column,
                    'image_data': chart_data,
                    'description': f'Histogram showing the distribution of {column} values'
                })
                
                plt.close()
                
            except Exception as exception:
                logger.warning('Failed to generate histogram for %s: %s', column, exception)
    
    def _generate_correlation_heatmap(self):
        """Generate correlation heatmap for numeric columns."""
        import matplotlib.pyplot as plt
        import numpy as np
        
        numeric_columns = self.dataframe.select_dtypes(include=['number']).columns
        
        if len(numeric_columns) < 2:
            return
        
        try:
            # Calculate correlation matrix
            corr_matrix = self.dataframe[numeric_columns].corr()
            
            plt.figure(figsize=(12, 8))
            
            # Create heatmap
            im = plt.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
            
            # Add colorbar
            cbar = plt.colorbar(im)
            cbar.set_label('Correlation Coefficient', fontsize=12)
            
            # Set ticks and labels
            plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45, ha='right')
            plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
            
            # Add correlation values to cells
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    value = corr_matrix.iloc[i, j]
                    if not np.isnan(value):
                        color = 'white' if abs(value) > 0.5 else 'black'
                        plt.text(j, i, f'{value:.2f}', ha='center', va='center', color=color, fontweight='bold')
            
            plt.title('Correlation Heatmap', fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            
            chart_data = self._plt_to_base64()
            self.charts.append({
                'type': 'heatmap',
                'title': 'Correlation Matrix',
                'image_data': chart_data,
                'description': 'Heatmap showing correlations between numeric variables'
            })
            
            plt.close()
            
        except Exception as exception:
            logger.warning('Failed to generate correlation heatmap: %s', exception)
    
    def _generate_categorical_charts(self):
        """Generate bar charts for categorical columns."""
        import matplotlib.pyplot as plt
        
        categorical_columns = self.dataframe.select_dtypes(include=['object', 'category']).columns
        
        for column in categorical_columns[:3]:  # Limit to first 3
            try:
                value_counts = self.dataframe[column].value_counts().head(10)  # Top 10 values
                
                if len(value_counts) == 0:
                    continue
                
                plt.figure(figsize=(12, 6))
                bars = plt.bar(range(len(value_counts)), value_counts.values, color='lightcoral', edgecolor='black')
                
                # Add value labels on bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{int(height)}', ha='center', va='bottom', fontweight='bold')
                
                plt.title(f'Distribution of {column}', fontsize=14, fontweight='bold')
                plt.xlabel(column, fontsize=12)
                plt.ylabel('Count', fontsize=12)
                plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')
                plt.grid(True, alpha=0.3, axis='y')
                plt.tight_layout()
                
                chart_data = self._plt_to_base64()
                self.charts.append({
                    'type': 'bar',
                    'title': f'Distribution of {column}',
                    'column': column,
                    'image_data': chart_data,
                    'description': f'Bar chart showing frequency of {column} categories'
                })
                
                plt.close()
                
            except Exception as exception:
                logger.warning('Failed to generate bar chart for %s: %s', column, exception)
    
    def _generate_time_series_charts(self):
        """Generate time series charts if datetime columns exist."""
        import matplotlib.pyplot as plt
        import pandas as pd
        
        datetime_columns = self.dataframe.select_dtypes(include=['datetime64']).columns
        numeric_columns = self.dataframe.select_dtypes(include=['number']).columns
        
        # Look for timestamp column (common in research data)
        timestamp_col = None
        for col in self.dataframe.columns:
            if 'timestamp' in col.lower() or 'time' in col.lower() or 'date' in col.lower():
                try:
                    # Try to convert to datetime
                    self.dataframe[col] = pd.to_datetime(self.dataframe[col])
                    timestamp_col = col
                    break
                except:
                    continue
        
        if timestamp_col and len(numeric_columns) > 0:
            try:
                # Sort by timestamp
                df_sorted = self.dataframe.sort_values(timestamp_col)
                
                # Plot first numeric column over time
                numeric_col = numeric_columns[0]
                
                plt.figure(figsize=(14, 6))
                plt.plot(df_sorted[timestamp_col], df_sorted[numeric_col], 
                        marker='o', linestyle='-', markersize=4, linewidth=2, color='green')
                
                plt.title(f'{numeric_col} Over Time', fontsize=14, fontweight='bold')
                plt.xlabel('Time', fontsize=12)
                plt.ylabel(numeric_col, fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                chart_data = self._plt_to_base64()
                self.charts.append({
                    'type': 'time_series',
                    'title': f'{numeric_col} Time Series',
                    'x_column': timestamp_col,
                    'y_column': numeric_col,
                    'image_data': chart_data,
                    'description': f'Time series plot of {numeric_col} over time'
                })
                
                plt.close()
                
            except Exception as exception:
                logger.warning('Failed to generate time series chart: %s', exception)
    
    def _generate_summary_charts(self):
        """Generate summary charts showing dataset overview."""
        import matplotlib.pyplot as plt
        import numpy as np
        
        try:
            # Data type distribution pie chart
            data_types = self.dataframe.dtypes.astype(str).value_counts()
            
            if len(data_types) > 1:
                plt.figure(figsize=(10, 8))
                colors = ['lightblue', 'lightcoral', 'lightgreen', 'lightyellow', 'lightpink']
                wedges, texts, autotexts = plt.pie(data_types.values, labels=data_types.index, 
                                                  autopct='%1.1f%%', colors=colors[:len(data_types)],
                                                  explode=[0.05] * len(data_types))
                
                # Enhance text appearance
                for autotext in autotexts:
                    autotext.set_color('black')
                    autotext.set_fontweight('bold')
                
                plt.title('Dataset Composition by Data Type', fontsize=16, fontweight='bold')
                
                chart_data = self._plt_to_base64()
                self.charts.append({
                    'type': 'pie',
                    'title': 'Data Type Distribution',
                    'image_data': chart_data,
                    'description': 'Pie chart showing the distribution of data types in the dataset'
                })
                
                plt.close()
            
            # Missing data visualization
            missing_data = self.dataframe.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            
            if len(missing_data) > 0:
                plt.figure(figsize=(12, 6))
                bars = plt.bar(range(len(missing_data)), missing_data.values, color='orange', edgecolor='black')
                
                # Add value labels
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{int(height)}', ha='center', va='bottom', fontweight='bold')
                
                plt.title('Missing Data by Column', fontsize=14, fontweight='bold')
                plt.xlabel('Columns', fontsize=12)
                plt.ylabel('Missing Values Count', fontsize=12)
                plt.xticks(range(len(missing_data)), missing_data.index, rotation=45, ha='right')
                plt.grid(True, alpha=0.3, axis='y')
                plt.tight_layout()
                
                chart_data = self._plt_to_base64()
                self.charts.append({
                    'type': 'missing_data',
                    'title': 'Missing Data Analysis',
                    'image_data': chart_data,
                    'description': 'Bar chart showing missing data count by column'
                })
                
                plt.close()
                
        except Exception as exception:
            logger.warning('Failed to generate summary charts: %s', exception)
    
    def _plt_to_base64(self):
        """Convert matplotlib plot to base64 string for web display."""
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _generate_text_charts(self):
        """Generate text-based chart representations when matplotlib is unavailable."""
        text_charts = []
        
        numeric_columns = self.dataframe.select_dtypes(include=['number']).columns
        
        for column in numeric_columns[:2]:  # First 2 columns
            try:
                data = self.dataframe[column].dropna()
                
                if len(data) == 0:
                    continue
                
                # Simple text histogram
                hist_data = self._create_text_histogram(data)
                
                text_charts.append({
                    'type': 'text_histogram',
                    'title': f'Distribution of {column}',
                    'column': column,
                    'data': hist_data,
                    'description': f'Text-based histogram of {column} (matplotlib not available)'
                })
                
            except Exception as exception:
                logger.warning('Failed to generate text chart for %s: %s', column, exception)
        
        return text_charts
    
    def _create_text_histogram(self, data, bins=10):
        """Create a simple text-based histogram."""
        try:
            import numpy as np
            
            # Calculate histogram
            counts, bin_edges = np.histogram(data, bins=bins)
            
            # Create text representation
            max_count = max(counts) if len(counts) > 0 else 1
            scale = 50 / max_count  # Scale to 50 characters max
            
            hist_lines = []
            for i, count in enumerate(counts):
                bar_length = int(count * scale)
                bar = '█' * bar_length
                range_str = f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}"
                hist_lines.append(f"{range_str:>10} | {bar} ({count})")
            
            return {
                'histogram': hist_lines,
                'stats': {
                    'mean': round(float(data.mean()), 2),
                    'std': round(float(data.std()), 2),
                    'min': round(float(data.min()), 2),
                    'max': round(float(data.max()), 2),
                    'count': len(data)
                }
            }
            
        except ImportError:
            # Fallback without numpy
            return {
                'histogram': ['Simple histogram not available without numpy'],
                'stats': {
                    'count': len(data),
                    'min': float(min(data)),
                    'max': float(max(data))
                }
            }


class DataPreviewGenerator:
    """
    Generator for data previews and sample displays.
    Creates formatted previews for demo display.
    """
    
    def __init__(self, dataframe=None):
        self.dataframe = dataframe
    
    def generate_preview(self, dataframe=None, num_rows=10):
        """Generate comprehensive data preview."""
        if dataframe is not None:
            self.dataframe = dataframe
        
        if self.dataframe is None or self.dataframe.empty:
            return {
                'status': 'empty',
                'message': 'No data available for preview'
            }
        
        try:
            preview = {
                'status': 'success',
                'sample_data': self._format_sample_data(num_rows),
                'column_info': self._generate_column_info(),
                'basic_stats': self._generate_basic_stats(),
                'data_shape': {
                    'rows': len(self.dataframe),
                    'columns': len(self.dataframe.columns)
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return preview
            
        except Exception as exception:
            logger.error('Error generating data preview: %s', exception)
            return {
                'status': 'error',
                'message': f'Preview generation failed: {exception}'
            }
    
    def _format_sample_data(self, num_rows):
        """Format sample data for display."""
        sample_df = self.dataframe.head(num_rows)
        
        # Convert to list of dictionaries for easy display
        sample_data = []
        for _, row in sample_df.iterrows():
            row_data = {}
            for col in self.dataframe.columns:
                value = row[col]
                # Format values for display
                if pd.isna(value):
                    row_data[col] = 'N/A'
                elif isinstance(value, float):
                    row_data[col] = round(value, 3)
                else:
                    row_data[col] = str(value)
            sample_data.append(row_data)
        
        return {
            'headers': list(self.dataframe.columns),
            'rows': sample_data,
            'total_shown': len(sample_data),
            'total_available': len(self.dataframe)
        }
    
    def _generate_column_info(self):
        """Generate information about each column."""
        column_info = {}
        
        for column in self.dataframe.columns:
            series = self.dataframe[column]
            
            info = {
                'data_type': str(series.dtype),
                'non_null_count': int(series.count()),
                'null_count': int(series.isnull().sum()),
                'unique_count': int(series.nunique()),
                'sample_values': []
            }
            
            # Get sample unique values
            unique_values = series.dropna().unique()[:5]  # First 5 unique values
            info['sample_values'] = [str(val) for val in unique_values]
            
            column_info[column] = info
        
        return column_info
    
    def _generate_basic_stats(self):
        """Generate basic statistics."""
        stats = {
            'numeric_columns': 0,
            'categorical_columns': 0,
            'datetime_columns': 0,
            'total_missing': int(self.dataframe.isnull().sum().sum()),
            'completeness_percent': 0
        }
        
        # Count column types
        for column in self.dataframe.columns:
            dtype = str(self.dataframe[column].dtype)
            
            if 'int' in dtype or 'float' in dtype:
                stats['numeric_columns'] += 1
            elif 'datetime' in dtype:
                stats['datetime_columns'] += 1
            else:
                stats['categorical_columns'] += 1
        
        # Calculate completeness
        total_cells = self.dataframe.size
        if total_cells > 0:
            stats['completeness_percent'] = round(
                ((total_cells - stats['total_missing']) / total_cells) * 100, 1
            )
        
        return stats 