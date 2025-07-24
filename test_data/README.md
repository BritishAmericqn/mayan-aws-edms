# Research Test Data

This directory contains organized test datasets for validating the Mayan EDMS Research Platform analysis capabilities.

## Directory Structure

### 📊 Dataset Categories

- **`climate_research/`** - Environmental monitoring data
  - Temperature, humidity, pressure, air quality measurements
  - Weather station data with temporal patterns
  - Ideal for testing time-series analysis

- **`water_quality/`** - Environmental water analysis
  - pH, dissolved oxygen, turbidity measurements
  - Multi-location sampling data
  - Good for testing quality assessment algorithms

- **`lab_measurements/`** - Laboratory experiment results
  - Controlled experimental conditions
  - Precise measurements with low variance
  - Perfect for testing statistical analysis

- **`survey_data/`** - Social science research
  - Questionnaire responses and ratings
  - Demographic information
  - Useful for testing qualitative data analysis

- **`demographics/`** - Population and social data
  - Age, education, income distributions
  - Geographic sampling data
  - Great for testing categorical analysis

## Usage Instructions

### For Testing Real Data Analysis:

1. **Upload CSV files** to Mayan through the web interface
2. **Link documents** to datasets via Admin → Dataset Documents
3. **Set document role** to "Raw Data"
4. **Run analysis** to see results from actual research data

### File Naming Convention:

```
[category]_[study_type]_[date_range].csv
```

Examples:
- `climate_daily_measurements_2024_q1.csv`
- `water_ph_analysis_river_stations.csv`
- `lab_enzyme_activity_controlled.csv`

## Data Quality Standards

All test files include:
- ✅ **Headers** - Clear column names
- ✅ **Clean data** - No malformed entries
- ✅ **Realistic values** - Representative of actual research
- ✅ **Sufficient size** - 10-50 rows for meaningful analysis
- ✅ **Multiple variables** - At least 4-6 columns for statistical analysis

## Quick Test Files

For immediate testing, use these curated datasets:
- `climate_research/sensor_data_sample.csv` - Perfect for environmental studies
- `water_quality/multi_station_analysis.csv` - Multi-location sampling
- `lab_measurements/precision_experiment.csv` - High-quality controlled data 