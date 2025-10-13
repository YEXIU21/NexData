# Professional Data Analysis Tool - Shopify Edition

A comprehensive GUI-based data analysis application built with Python for data analyst professionals and Shopify/E-commerce analysts.

📊 **[View Complete Workflow →](DATA_ANALYST_WORKFLOW.md)**  
🗺️ **[View Features Map →](FEATURES_MAP.md)**

## ✨ Key Highlights

- **10+ Visualization Types** with interactive zoom/pan
- **E-commerce Dashboard** for Shopify analytics
- **Time Series Analysis** for sales trends
- **Advanced Data Cleaning** with 5+ methods
- **Real-time Statistics** panel
- **Professional UI** with modern design

## Features

### 📊 Data Import/Export
- **Import**: CSV, Excel (.xlsx, .xls), JSON
- **Export**: CSV, Excel, JSON
- Automatic data type detection
- Multi-sheet Excel support
- Large file support (>100MB)

### 🧹 Data Cleaning
- **Remove Duplicates**: Automatically detect and remove duplicate rows
- **Handle Missing Values**: Multiple strategies
  - Drop rows with missing values
  - Fill with mean/median (numeric columns)
  - Forward/backward fill
- **Remove Outliers**: IQR-based outlier detection and removal
- **Reset Data**: Restore original dataset anytime

### 📈 Statistical Analysis
- **Data Information**: Column types, null counts, unique values
- **Descriptive Statistics**: Mean, median, std, quartiles, min/max
- **Data Preview**: View first 100 rows
- **Memory Usage**: Track dataset size

### 📉 Data Visualization
- **Histogram**: Distribution analysis for numeric columns
- **Box Plot**: Visualize data spread and outliers
- **Scatter Plot**: Relationship between two variables
- **Bar Chart**: Category comparisons
- **Line Chart**: Trends over time
- **Pie Chart**: Composition analysis
- **Correlation Heatmap**: Analyze correlations between numeric features
- **Distribution Plot**: Histogram with KDE curve
- **Violin Plot**: Distribution comparison
- Interactive matplotlib-based plots with zoom/pan
- Navigation toolbar for advanced controls
- Export plot capabilities

### 🛍️ E-commerce/Shopify Features
- **E-commerce Dashboard**: Quick insights for online store data
- **Time Series Analysis**: Analyze sales trends over time
- **Revenue Analysis**: Automatic detection of revenue columns
- **Customer Insights**: Unique customer tracking
- **Column Analysis**: Deep dive into specific metrics
- **Sort Data**: Order by any column
- **Data Type Conversion**: Convert to datetime for time-based analysis

### 🎨 User Interface
- Modern GUI with ttk styling
- Split panel layout with quick actions
- Tabbed output (Data Output / Visualization)
- Real-time status updates
- Dataset information panel

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this repository**

2. **Install required packages**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python data_analyst_tool.py
```

## Usage Guide

### Getting Started

1. **Launch the application**
   ```bash
   python data_analyst_tool.py
   ```

2. **Import your data**
   - Click `File > Import CSV` or `Import Excel`
   - Or use Quick Actions buttons in the left panel

3. **Explore your data**
   - Click `View Data` to see your dataset
   - Click `Statistics` for statistical summary
   - Use `Data > Data Info` for detailed column information

### Data Cleaning Workflow

1. **Check for issues**
   - View data info to identify missing values and data types
   - Check dataset information panel for duplicate count

2. **Clean your data**
   - `Clean > Remove Duplicates` - Remove duplicate rows
   - `Clean > Handle Missing Values` - Choose filling strategy
   - `Clean > Remove Outliers` - Remove statistical outliers using IQR method

3. **Reset if needed**
   - `Data > Reset to Original` - Restore original dataset

### Creating Visualizations

1. **Histogram**
   - `Visualize > Histogram`
   - Select a numeric column
   - View distribution

2. **Box Plot**
   - `Visualize > Box Plot`
   - Visualize all numeric columns
   - Identify outliers

3. **Scatter Plot**
   - `Visualize > Scatter Plot`
   - Select X and Y columns
   - Analyze relationships

4. **Correlation Heatmap**
   - `Visualize > Correlation Heatmap`
   - See correlations between all numeric features
   - Identify strong relationships

### Export Results

1. **Export cleaned data**
   - `File > Export CSV` or `Export Excel`
   - Choose destination and filename
   - Save processed data

## Keyboard Shortcuts

- **File Menu**: Alt + F
- **Data Menu**: Alt + D
- **Clean Menu**: Alt + C
- **Visualize Menu**: Alt + V
- **Help Menu**: Alt + H

## Tips for Data Analysts

### Best Practices

1. **Always make a backup**: The tool keeps an original copy that you can restore with `Reset Data`

2. **Check data quality first**:
   - Run `Data Info` to understand your dataset
   - Look for missing values, data types, and unique counts
   - Run `Statistics` for numeric summaries

3. **Clean systematically**:
   - Remove duplicates first
   - Handle missing values second
   - Remove outliers last (after understanding your data)

4. **Visualize before and after**:
   - Create plots before cleaning to understand raw data
   - Create plots after cleaning to verify results

5. **Export regularly**: Save your work after major cleaning steps

### Common Workflows

**Quick Data Exploration**:
1. Import CSV/Excel
2. View Data
3. Statistics
4. Create Histogram or Box Plot

**Data Cleaning Pipeline**:
1. Import data
2. Check Data Info
3. Remove Duplicates
4. Handle Missing Values (choose strategy)
5. Check Statistics
6. Remove Outliers (if needed)
7. Export cleaned data

**Correlation Analysis**:
1. Import data
2. Run Statistics to ensure numeric columns
3. Create Correlation Heatmap
4. Identify strong correlations (|r| > 0.7)
5. Create Scatter Plots for investigation

## Technical Details

### Dependencies
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Plotting and visualization
- **seaborn**: Statistical data visualization
- **openpyxl**: Excel file handling
- **tkinter**: GUI framework (included with Python)

### Supported File Formats
- **CSV**: Comma-separated values (.csv)
- **Excel**: Microsoft Excel (.xlsx, .xls)
- **JSON**: JavaScript Object Notation (.json)

### Data Type Support
- Numeric: int64, float64
- Categorical: object, string
- DateTime: datetime64
- Boolean: bool

## Troubleshooting

### Import Issues
- **"Failed to load CSV"**: Check file encoding, try UTF-8
- **"Failed to load Excel"**: Ensure openpyxl is installed
- **Large files slow**: Be patient, progress updates in status bar

### Cleaning Issues
- **"No numeric columns"**: Some operations require numeric data
- **"Need at least 2 columns"**: Correlation requires multiple columns
- **Memory errors**: Try cleaning in batches or use smaller dataset

### Visualization Issues
- **"No numeric columns found"**: Ensure dataset has numeric columns
- **Plot not showing**: Check Visualization tab in notebook
- **Poor plot quality**: Resize window or export plot

## Future Enhancements

Planned features:
- [ ] SQL database connectivity
- [ ] Advanced filtering and querying
- [ ] Time series analysis
- [ ] Machine learning integration
- [ ] Report generation (PDF/HTML)
- [ ] Batch processing
- [ ] Custom data transformations
- [ ] Data profiling dashboard

## License

MIT License - Free for personal and commercial use

## Author

Created for data analyst job preparation and professional use

## Support

For issues, questions, or feature requests, please create an issue in the repository.

---

**Happy Analyzing! 📊**
