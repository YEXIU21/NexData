# Professional Data Analysis Tool - Shopify Edition

A comprehensive GUI-based data analysis application built with Python for data analyst professionals and Shopify/E-commerce analysts.

## 📚 Documentation

- **[Complete Workflow Guide](docs/DATA_ANALYST_WORKFLOW.md)** - 8-phase data analysis workflow
- **[Features Map](docs/FEATURES_MAP.md)** - Complete feature navigation guide
- **[Detailed README](docs/README.md)** - Full feature documentation

## ✨ Key Highlights

- **10+ Visualization Types** with interactive zoom/pan
- **E-commerce Dashboard** for Shopify analytics
- **Time Series Analysis** for sales trends
- **Advanced Data Cleaning** with 5+ methods
- **Real-time Statistics** panel
- **Professional UI** with modern design

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### Basic Usage

1. **Import Data**: File > Import CSV/Excel
2. **Clean Data**: Clean menu > Remove Duplicates, Handle Missing Values
3. **Analyze**: Analysis menu > E-commerce Dashboard, Time Series
4. **Visualize**: Visualize menu > Select chart type
5. **Export**: File > Export CSV/Excel

## 📂 Project Structure

```
DATA_ANALYST_TOOL/
├── src/                        # Source code (SEPARATION OF CONCERNS)
│   ├── main.py                # Entry point
│   ├── ui/                    # User interface components
│   │   ├── __init__.py
│   │   └── main_window.py    # Main application window
│   ├── data_ops/              # Data operations
│   │   ├── __init__.py
│   │   ├── import_export.py  # Import/Export functions
│   │   └── cleaning.py       # Data cleaning functions
│   ├── analysis/              # Analysis modules
│   │   ├── __init__.py
│   │   ├── statistics.py     # Statistical analysis
│   │   └── ecommerce.py      # E-commerce specific analysis
│   └── visualization/         # Visualization modules
│       ├── __init__.py
│       └── charts.py          # Chart creation
│
├── docs/                       # Documentation
│   ├── README.md              # Detailed documentation
│   ├── DATA_ANALYST_WORKFLOW.md
│   ├── FEATURES_MAP.md
│   ├── BUILD_INSTRUCTIONS.md
│   └── FEATURES_CHECKLIST.md
│
├── data/                       # Sample data
│   └── sample_data.csv
│
├── build_scripts/             # Build scripts for EXE
│   ├── build.bat             # Windows build script
│   ├── build_exe.py          # Python build script
│   └── README.md             # Build instructions
│
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🛠️ Technologies Used

- **Python 3.8+**
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Matplotlib** - Visualization
- **Seaborn** - Statistical visualization
- **Tkinter** - GUI framework
- **OpenPyXL** - Excel support

## 📊 Features

### Data Import/Export
✅ CSV, Excel, JSON import  
✅ Multi-sheet Excel support  
✅ Multiple encodings  
✅ Auto-detect data types  

### Data Cleaning
✅ Remove duplicates  
✅ Handle missing values (5 methods)  
✅ Remove outliers (IQR)  
✅ Data type conversion  
✅ Sort data  

### Analysis
✅ Descriptive statistics  
✅ Correlation analysis  
✅ Time series analysis  
✅ E-commerce dashboard  
✅ Column analysis  

### Visualizations (10+ types)
✅ Histogram, Box plot, Scatter plot  
✅ Bar chart, Line chart, Pie chart  
✅ Correlation heatmap, Distribution plot  
✅ Violin plot  
✅ Interactive navigation toolbar  

## 🎯 Perfect For

- **Shopify Data Analysts**
- **E-commerce Analysts**
- **Business Intelligence Analysts**
- **Data Analysts**
- **Market Research Analysts**

## 📝 Code Quality

This project follows **CLEAN CODE** principles:

- ✅ **Separation of Concerns** - Modular architecture
- ✅ **Single Responsibility** - Each module has one purpose
- ✅ **DRY Principle** - Don't Repeat Yourself
- ✅ **Clear Naming** - Descriptive function/variable names
- ✅ **Proper Documentation** - Comments and docstrings
- ✅ **Error Handling** - Try-except blocks
- ✅ **Consistent Style** - PEP 8 compliant

## 🔄 Version History

- **v2.0** (January 2025) - Added Shopify features, reorganized with clean code principles
- **v1.0** (October 2024) - Initial release with core features

## 📄 License

MIT License - Free for personal and commercial use

## 🤝 Contributing

This is a portfolio project for demonstrating data analyst skills. Feedback and suggestions welcome!

## 📧 Contact

Created for Shopify Data Analyst job applications.

---

**© 2025 - Built with ❤️ for Data Analysis**
