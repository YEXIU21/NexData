# NexData - Complete User Guide & Tutorials

**Version**: 3.0  
**Developed by**: YEXIU21  
**For**: Shopify Data Analysts & E-commerce Professionals

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Quick Start Tutorial](#quick-start-tutorial)
3. [Data Import & Export](#data-import--export)
4. [Data Cleaning](#data-cleaning)
5. [Data Analysis](#data-analysis)
6. [Visualizations](#visualizations)
7. [Advanced Features](#advanced-features)
8. [Reports & Exports](#reports--exports)
9. [Tips & Best Practices](#tips--best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

**Requirements**:
```bash
pip install pandas numpy matplotlib seaborn scipy openpyxl psutil
pip install python-pptx  # Optional, for PowerPoint export
```

**Launch Application**:
```bash
cd path/to/DATA_ANALYST_TOOL
python src/main.py
```

### Interface Overview

**Main Window Components**:
- **Menu Bar**: File, Data, Clean, Analysis, Visualize, Tools, View, Help
- **Left Panel**: Quick Actions + Dataset Info
- **Right Panel**: Output (text results) + Visualization (charts) tabs
- **Status Bar**: Real-time status updates

---

## Quick Start Tutorial

### Tutorial 1: Your First Analysis (5 minutes)

**Step 1: Import Data**
1. Click `File > Import CSV`
2. Select your CSV file (or use sample data)
3. ✅ Data loads automatically

**Step 2: View Your Data**
1. Click `Data > View Data` (or Quick Action button)
2. Browse your data in a new window
3. Check column names and data types

**Step 3: Get Summary Statistics**
1. Click `Data > Statistics` (or Quick Action button)
2. Review mean, median, min, max, std deviation
3. Understand your data distribution

**Step 4: Create Your First Visualization**
1. Click `Visualize > Histogram`
2. Select a numeric column (e.g., "Salary")
3. View the distribution chart
4. Use zoom/pan tools to explore

**Step 5: Export Results**
1. Click `File > Export CSV`
2. Choose save location
3. ✅ Done! Your first analysis complete!

---

## Data Import & Export

### Supported Formats

**Import**:
- ✅ CSV files (`.csv`)
- ✅ Excel files (`.xlsx`, `.xls`)

**Export**:
- ✅ CSV files
- ✅ Excel files
- ✅ JSON files
- ✅ HTML Reports
- ✅ PowerPoint Presentations

### Import Tutorial

**CSV Import**:
```
File > Import CSV > Select File > Open
```
- Automatically detects delimiters
- Handles headers
- Shows preview in Dataset Info

**Excel Import**:
```
File > Import Excel > Select File > Open
```
- Reads first sheet by default
- Preserves data types
- Converts dates automatically

### Export Tutorial

**Basic Export**:
```
File > Export CSV/Excel/JSON > Choose Location > Save
```

**Professional Reports**:
```
File > Generate Executive Report (HTML)
```
- Creates beautiful HTML report
- Includes key metrics, statistics, insights
- Opens in default browser
- Professional presentation quality

---

## Data Cleaning

### Remove Duplicates

**When to Use**: Multiple identical rows exist

**Steps**:
1. `Clean > Remove Duplicates`
2. View count of removed rows
3. Data updated automatically

**Example Use Case**:
- Customer list with duplicate emails
- Transaction records imported twice
- Product catalog with duplicate SKUs

### Handle Missing Values

**When to Use**: Data has null/NaN values

**Methods Available**:
1. **Drop Rows**: Remove rows with missing data
2. **Fill with Mean**: Replace with average (numeric columns)
3. **Fill with Median**: Replace with median (numeric columns)
4. **Forward Fill**: Use previous value
5. **Backward Fill**: Use next value

**Steps**:
1. `Clean > Handle Missing Values`
2. Select column with missing data
3. Choose method
4. Apply

**Best Practices**:
- Use **Mean** for normally distributed data
- Use **Median** for data with outliers
- Use **Drop** only if <5% data missing
- Use **Forward/Backward Fill** for time series

### Remove Outliers

**When to Use**: Extreme values skew analysis

**Steps**:
1. `Clean > Remove Outliers`
2. Select numeric column
3. Review outliers detected (IQR method)
4. Confirm removal

**Example**:
- Salaries: Remove data entry errors (e.g., $1M instead of $100K)
- Ages: Remove impossible values (e.g., age 200)
- Prices: Remove test records

---

## Data Analysis

### SQL Query Interface ⭐

**Most Powerful Feature**: Run SQL queries on your data!

**Steps**:
1. `Analysis > SQL Query`
2. Type SQL query (data table is called "data")
3. Click "Execute Query"
4. View results

**Common Queries**:

```sql
-- Basic filtering
SELECT * FROM data WHERE Salary > 50000

-- Grouping and aggregation
SELECT Department, AVG(Salary) as Avg_Salary, COUNT(*) as Employees
FROM data
GROUP BY Department

-- Multiple conditions
SELECT * FROM data 
WHERE Department = 'Sales' AND Experience > 5

-- Sorting
SELECT Name, Salary FROM data 
ORDER BY Salary DESC 
LIMIT 10

-- Complex aggregations (PIVOT-like)
SELECT Department, 
       SUM(CASE WHEN Age < 30 THEN 1 ELSE 0 END) as Under_30,
       SUM(CASE WHEN Age >= 30 THEN 1 ELSE 0 END) as Over_30
FROM data
GROUP BY Department
```

### Data Quality Check ⭐

**Automated Quality Assessment**

**Steps**:
1. `Data > Data Quality Check`
2. Review comprehensive report:
   - Overall Score (0-100)
   - Completeness (missing data)
   - Uniqueness (duplicates)
   - Consistency (data types)
   - Validity (outliers, negative values)
3. Follow recommendations

**Quality Levels**:
- **Excellent**: 90+ score
- **Good**: 75-89 score
- **Fair**: 60-74 score
- **Poor**: <60 score

### Auto Insights ⭐

**AI-Powered Pattern Detection**

**Steps**:
1. `Analysis > Auto Insights`
2. Review automatically generated insights:
   - Data summary
   - Trend detection
   - Correlation findings
   - Recommendations

**Example Insights**:
- "Column 'Revenue' shows high variance (CV > 1)"
- "Strong correlation between 'Experience' and 'Salary' (0.85)"
- "⚠️ Found 5 duplicate rows (2.5%)"

### Statistical Tests

**Available Tests**:
1. **T-Test**: Compare two groups
2. **ANOVA**: Compare multiple groups
3. **Chi-Square**: Test categorical associations
4. **Normality Tests**: Check if data is normally distributed

**Example - T-Test**:
```
Analysis > Statistical Tests > T-Test
Group 1: Sales Department Salaries
Group 2: Engineering Department Salaries
Result: p-value = 0.023 (significant difference!)
```

### A/B Testing

**Compare Conversion Rates or Metrics**

**Conversion Rate Test**:
```
Analysis > A/B Testing > Conversion Rate
Control: 1000 visitors, 50 conversions (5%)
Treatment: 1000 visitors, 75 conversions (7.5%)
Result: Significant improvement (p < 0.05)
```

### RFM Customer Segmentation ⭐

**Segment Customers by Value**

**Requirements**:
- Customer ID column
- Transaction date column
- Revenue/Amount column

**Segments Identified**:
1. **Champions**: Best customers (recent, frequent, high spend)
2. **Loyal Customers**: Regular buyers
3. **Potential Loyalists**: Recent customers with potential
4. **New Customers**: Just started buying
5. **Promising**: Recent, moderate spenders
6. **Need Attention**: Average, need nurturing
7. **About to Sleep**: Declining engagement
8. **At Risk**: Were frequent, now inactive
9. **Can't Lose Them**: High value but inactive
10. **Lost**: No recent activity

**Use Cases**:
- Target marketing campaigns by segment
- Identify churn risk (At Risk, Lost)
- Reward Champions and Loyal customers
- Re-engage "Can't Lose Them" segment

---

## Visualizations

### Available Chart Types

1. **Histogram**: Data distribution
2. **Box Plot**: Quartiles and outliers
3. **Scatter Plot**: Relationship between variables
4. **Pie Chart**: Category proportions
5. **Distribution Plot (KDE)**: Smooth distribution curve
6. **Violin Plot**: Distribution shape
7. **Correlation Heatmap**: All variable relationships
8. **Time Series**: Trends over time
9. **Line Chart**: Connected data points
10. **Bar Chart**: Category comparisons

### How to Create Charts

**General Steps**:
1. `Visualize > [Chart Type]`
2. Select column(s) from dropdown
3. Click "Plot"
4. Chart appears in Visualization tab

**Interactive Features**:
- 🔍 **Zoom**: Click and drag
- 👆 **Pan**: Right-click and drag
- 🏠 **Reset**: Click home icon
- 💾 **Save**: Click save icon

### Visualization Best Practices

**Histogram**:
- Use for: Understanding distribution
- Best for: Age, Salary, Revenue
- Look for: Normal distribution, skewness, outliers

**Box Plot**:
- Use for: Comparing groups
- Best for: Salary by Department
- Look for: Median differences, outliers

**Scatter Plot**:
- Use for: Relationships
- Best for: Experience vs Salary
- Look for: Positive/negative correlation

**Heatmap**:
- Use for: Multiple correlations
- Best for: All numeric columns at once
- Look for: Strong correlations (dark colors)

---

## Advanced Features

### Time Series Forecasting ⭐

**Predict Future Values**

**Methods Available**:
1. **Linear Trend**: Best for steady growth/decline
2. **Moving Average**: Best for smoothing fluctuations
3. **Exponential Smoothing**: Best for recent trends

**Example - Sales Forecasting**:
```
Analysis > Time Series Forecasting
Date Column: Order_Date
Value Column: Revenue
Method: Linear Trend
Periods: 30 days
Result: Next month revenue forecast
```

**Interpretation**:
- **Positive slope**: Growing trend
- **R² > 0.7**: Strong predictive power
- **P-value < 0.05**: Statistically significant

### Sales Dashboard ⭐

**Comprehensive Business Metrics**

**Requirements**:
- Date column
- Revenue column
- (Optional) Product column
- (Optional) Customer column

**Metrics Provided**:
- Total revenue
- Average transaction value
- Best performing day
- Month-over-month growth
- Top products
- Customer retention rate

**Access**:
```
Analysis > Sales Dashboard
Enter: date_col, revenue_col
View comprehensive metrics
```

### Compare Datasets ⭐

**Side-by-Side Comparison**

**Use Cases**:
- Compare this month vs last month sales
- Validate data migrations
- Identify changes between versions

**Steps**:
1. Load first dataset (main data)
2. `Tools > Compare Datasets`
3. Select second dataset file
4. Review comparison report:
   - Row/column differences
   - Common columns
   - Value differences
   - Statistical comparison

---

## Reports & Exports

### Executive Report (HTML)

**Professional Report Generation**

**Contents**:
- Executive summary
- Key metrics dashboard
- Statistical overview
- Data quality assessment
- Top/bottom performers
- Recommendations

**Steps**:
```
File > Generate Executive Report (HTML)
Choose save location
Report opens in browser automatically
```

**Perfect For**:
- Executive presentations
- Client reports
- Stakeholder updates
- Monthly reviews

### Quick Summary

**Fast Text Report**

**Contents**:
- Dataset overview
- Missing data summary
- Numeric statistics
- Recommendations

**Steps**:
```
File > Generate Quick Summary
Copy from output window
Paste into email/document
```

### Email Format

**Ready-to-Send Summary**

**Perfect For**:
- Quick email updates
- Slack messages
- Internal communications

### PowerPoint Export ⭐

**Auto-Generate Presentations**

**Requirements**:
```bash
pip install python-pptx
```

**Steps**:
```
File > Export to PowerPoint
Choose filename
Presentation created with:
- Title slide
- Data summary
- Key statistics
```

---

## Tips & Best Practices

### Data Preparation

✅ **DO**:
- Remove duplicates first
- Handle missing values before analysis
- Check data quality score
- Verify column data types
- Create backups (use Reset Data)

❌ **DON'T**:
- Skip data cleaning
- Ignore data quality warnings
- Remove outliers without investigation
- Forget to save exports

### Analysis Workflow

**Recommended Order**:
1. **Import** data
2. **View** data to understand structure
3. **Data Quality Check** to identify issues
4. **Clean** data (duplicates, missing values)
5. **Auto Insights** for quick overview
6. **Statistics** for detailed metrics
7. **Visualizations** for patterns
8. **Advanced Analysis** (SQL, RFM, Forecasting)
9. **Export** reports

### Performance Tips

**For Large Datasets (>100K rows)**:
- Use SQL Query for filtering first
- Create visualizations on filtered data
- Export subsets for detailed analysis
- Monitor Performance (Help > Performance Monitor)

**Optimization**:
- Close unused windows
- Reset data when switching files
- Use appropriate data types
- Filter before aggregating

### Keyboard Shortcuts

- **Ctrl+O**: Import CSV (coming soon)
- **Ctrl+D**: View Data (coming soon)
- **Ctrl+S**: Show Statistics (coming soon)

---

## Troubleshooting

### Common Issues

**Issue**: "No data loaded!" warning
**Solution**: Import data first (File > Import CSV/Excel)

**Issue**: Chart not displaying
**Solution**: 
1. Check if column has numeric data
2. Remove missing values first
3. Try different chart type

**Issue**: SQL Query error
**Solution**:
1. Use table name "data" (lowercase)
2. Check column names (case-sensitive)
3. Verify SQL syntax

**Issue**: Export failed
**Solution**:
1. Close file if already open
2. Check write permissions
3. Choose different location

**Issue**: Slow performance
**Solution**:
1. Check Performance Monitor (Help menu)
2. Reduce dataset size with SQL Query
3. Close other applications
4. Restart NexData

### Error Messages

**"No numeric columns!"**
- Select dataset with numeric data
- Check data types in Data Info

**"Column not found"**
- Verify column name spelling
- Check Dataset Info for exact names

**"Insufficient data for analysis"**
- Need minimum rows (varies by feature)
- Check if filtering removed too much data

### Getting Help

1. **Help > About**: Version info and feature list
2. **Help > Performance Monitor**: Check system resources
3. **Dataset Info Panel**: Quick data overview
4. **Status Bar**: Real-time operation status

---

## Example Workflows

### Workflow 1: E-commerce Sales Analysis

```
1. Import CSV (monthly_sales.csv)
2. Data Quality Check (ensure completeness)
3. Remove Duplicates (clean data)
4. View Statistics (understand metrics)
5. SQL Query: Top 10 products by revenue
6. Sales Dashboard (comprehensive metrics)
7. Time Series Chart (monthly trends)
8. RFM Segmentation (customer analysis)
9. Generate Executive Report (HTML)
10. Export to PowerPoint (presentation)
```

### Workflow 2: Customer Behavior Analysis

```
1. Import Excel (customer_data.xlsx)
2. Auto Insights (quick patterns)
3. RFM Segmentation (customer segments)
4. Scatter Plot: Purchase Frequency vs Value
5. Correlation Heatmap (relationships)
6. Customer Dashboard (metrics)
7. Export findings (CSV + Report)
```

### Workflow 3: Product Performance Review

```
1. Import CSV (product_sales.csv)
2. Handle Missing Values (clean data)
3. Remove Outliers (eliminate errors)
4. Box Plot: Sales by Product Category
5. Statistical Tests: Compare categories
6. SQL Query: Products below target
7. Generate Quick Summary
8. Format for Email (share with team)
```

---

## Glossary

**Terms**:
- **RFM**: Recency, Frequency, Monetary - customer segmentation method
- **KDE**: Kernel Density Estimation - smooth distribution curve
- **IQR**: Interquartile Range - outlier detection method
- **Correlation**: Statistical relationship between variables (-1 to +1)
- **p-value**: Statistical significance (< 0.05 = significant)
- **CLV**: Customer Lifetime Value
- **MAE**: Mean Absolute Error (forecast accuracy)
- **RMSE**: Root Mean Square Error (forecast accuracy)

---

## Additional Resources

**Documentation Files**:
- `README.md`: Project overview
- `FEATURES_MAP.md`: Complete feature list
- `DATA_ANALYST_WORKFLOW.md`: 8-phase workflow guide
- `FEATURE_SUMMARY_V3.md`: Version 3.0 features

**Sample Data**:
- `data/sample_data.csv`: Practice dataset
- Use for learning and testing

**Repository**:
- GitHub: https://github.com/YEXIU21/NexData.git
- Issues: Report bugs and suggest features

---

## Contact & Support

**Developer**: YEXIU21  
**Version**: 3.0.0  
**Last Updated**: January 2025  
**License**: Portfolio Use

---

**🎉 You're now ready to master NexData!**

Start with the Quick Start Tutorial and explore features at your own pace. Remember: practice makes perfect!
