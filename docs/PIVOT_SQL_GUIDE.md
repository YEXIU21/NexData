# Pivot Tables & SQL Query - Complete Guide

## 🎯 What is a Pivot Table?

A **Pivot Table** summarizes large datasets by:
- **Grouping** data by categories
- **Aggregating** values (sum, average, count, etc.)
- **Creating summary reports**

### Real-World Example 1: Sales Analysis

**Original Data** (100 transactions):
```
Product    | Region | Sales
iPhone     | East   | 1000
iPhone     | West   | 1200
Samsung    | East   | 800
Samsung    | West   | 900
iPhone     | East   | 1100
...
```

**Pivot Table** (Total Sales by Product and Region):
```
Product  | East  | West  | Total
iPhone   | 2100  | 1200  | 3300
Samsung  | 800   | 900   | 1700
```

---

## 💡 SQL Query - The MOST POWERFUL Feature!

**SQL Query** can do EVERYTHING including pivot tables and much more!

### Why SQL Query?
✅ More flexible than traditional pivot tables  
✅ Can filter, sort, aggregate, and join data  
✅ Industry-standard skill (used everywhere)  
✅ Results CAN be exported!  

---

## 📝 How to Create Pivot Tables with SQL

### Basic Pivot Table: Group BY

**Task**: Average salary by department

**SQL Query**:
```sql
SELECT Department, 
       AVG(Salary) as Average_Salary,
       COUNT(*) as Employee_Count
FROM data
GROUP BY Department
ORDER BY Average_Salary DESC
```

**Result**:
```
Department   | Average_Salary | Employee_Count
Engineering  | 75000          | 5
Marketing    | 68000          | 3
Sales        | 60000          | 4
```

### Advanced Pivot: Multiple Groups

**Task**: Average salary by department AND experience level

**SQL Query**:
```sql
SELECT Department,
       CASE 
           WHEN Experience < 3 THEN 'Junior'
           WHEN Experience BETWEEN 3 AND 7 THEN 'Mid'
           ELSE 'Senior'
       END as Level,
       AVG(Salary) as Avg_Salary,
       COUNT(*) as Count
FROM data
GROUP BY Department, Level
ORDER BY Department, Level
```

**Result**:
```
Department  | Level  | Avg_Salary | Count
Engineering | Junior | 65000      | 2
Engineering | Mid    | 75000      | 2
Engineering | Senior | 88000      | 1
Marketing   | Junior | 55000      | 1
Marketing   | Mid    | 70000      | 2
...
```

### True Pivot: Columns from Rows

**Task**: Create columns for each department

**SQL Query**:
```sql
SELECT 
    CASE WHEN Experience < 3 THEN 'Junior'
         WHEN Experience BETWEEN 3 AND 7 THEN 'Mid'
         ELSE 'Senior' END as Level,
    AVG(CASE WHEN Department = 'Engineering' THEN Salary END) as Engineering,
    AVG(CASE WHEN Department = 'Marketing' THEN Salary END) as Marketing,
    AVG(CASE WHEN Department = 'Sales' THEN Salary END) as Sales
FROM data
GROUP BY Level
```

**Result**:
```
Level  | Engineering | Marketing | Sales
Junior | 65000       | 55000     | 52000
Mid    | 75000       | 70000     | 65000
Senior | 88000       | 80000     | 75000
```

---

## 🎨 Common SQL Pivot Patterns

### 1. Sum by Category
```sql
SELECT Category, SUM(Amount) as Total
FROM data
GROUP BY Category
```

### 2. Count by Month
```sql
SELECT 
    strftime('%Y-%m', Date) as Month,
    COUNT(*) as Transactions,
    SUM(Revenue) as Total_Revenue
FROM data
GROUP BY Month
ORDER BY Month
```

### 3. Top N by Group
```sql
SELECT Department, Name, Salary
FROM (
    SELECT *, 
           ROW_NUMBER() OVER (PARTITION BY Department ORDER BY Salary DESC) as rank
    FROM data
)
WHERE rank <= 3
```

### 4. Percentage Distribution
```sql
SELECT Department,
       COUNT(*) as Count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM data), 2) as Percentage
FROM data
GROUP BY Department
```

---

## 💾 How to Export SQL Query Results

### Method 1: Copy from Output Window
1. Run your SQL Query
2. Results appear in **Output tab**
3. Select all text (Ctrl+A)
4. Copy (Ctrl+C)
5. Paste into Excel/Google Sheets

### Method 2: Export Filtered Data
1. Run SQL Query with filtering:
   ```sql
   SELECT * FROM data WHERE Salary > 70000
   ```
2. The main DataFrame (`self.df`) is NOT modified
3. To export filtered results, you need to create a subset first

### Method 3: Create Report
1. Run your analysis/SQL query
2. Go to **File > Generate Executive Report**
3. Results included in HTML report
4. Open in browser and save as PDF

---

## 🔧 SQL Query Step-by-Step Tutorial

### Example: Analyze Employee Performance

**Step 1: Open SQL Query**
```
Analysis > SQL Query
```

**Step 2: Write Query**
```sql
SELECT Department, 
       ROUND(AVG(Performance_Score), 2) as Avg_Performance,
       ROUND(AVG(Salary), 2) as Avg_Salary,
       COUNT(*) as Employees
FROM data
GROUP BY Department
HAVING COUNT(*) > 2
ORDER BY Avg_Performance DESC
```

**Step 3: Click "Execute Query"**

**Step 4: View Results in Output Tab**
```
Department  | Avg_Performance | Avg_Salary | Employees
Engineering | 89.2            | 75000      | 5
Marketing   | 84.5            | 68000      | 3
Sales       | 78.3            | 60000      | 4
```

**Step 5: Copy Results**
- Select all (Ctrl+A)
- Copy (Ctrl+C)
- Paste into Excel

---

## 📊 Every Tool's Export Capabilities

### ✅ CAN Export Results:
1. **Data Quality Check** → Copy from Output window
2. **Auto Insights** → Copy from Output window
3. **SQL Query** → Copy from Output window
4. **Statistical Tests** → Copy from Output window
5. **Column Analysis** → Copy from Output window
6. **Time Series Analysis** → Copy from Output window
7. **Executive Report** → Exports to HTML automatically
8. **Quick Summary** → Copy from Output window

### ✅ Exports Automatically:
1. **Executive Report (HTML)** → File > Generate Executive Report
2. **PowerPoint Export** → File > Export to PowerPoint
3. **CSV/Excel Export** → File > Export CSV/Excel
4. **JSON Export** → File > Export JSON

### 📊 Visualizations Export:
- All charts have **Save button** (disk icon) in toolbar
- Saves as PNG image file
- Perfect for presentations and reports

---

## 🎯 Quick Reference: When to Use What

| Task | Use This | Example |
|------|----------|---------|
| Summary by category | SQL GROUP BY | `SELECT Dept, AVG(Salary) FROM data GROUP BY Dept` |
| Filter data | SQL WHERE | `SELECT * FROM data WHERE Salary > 50000` |
| Top performers | SQL ORDER BY + LIMIT | `SELECT * FROM data ORDER BY Score DESC LIMIT 10` |
| Complex calculations | SQL CASE | `SELECT *, CASE WHEN Score > 80 THEN 'High' END as Rating FROM data` |
| Multiple aggregations | SQL multiple functions | `SELECT Dept, AVG(Salary), MIN(Salary), MAX(Salary) FROM data GROUP BY Dept` |
| Time-based analysis | SQL date functions | `SELECT strftime('%Y-%m', Date), COUNT(*) FROM data GROUP BY 1` |

---

## 💡 Pro Tips

### Tip 1: Save Your Queries
Copy useful SQL queries to a text file for reuse:
```sql
-- My Saved Queries.txt

-- Top 10 Salaries:
SELECT Name, Salary, Department FROM data ORDER BY Salary DESC LIMIT 10

-- Department Summary:
SELECT Department, AVG(Salary), COUNT(*) FROM data GROUP BY Department

-- High Performers:
SELECT * FROM data WHERE Performance_Score > 85
```

### Tip 2: Build Complex Queries Step-by-Step
1. Start simple: `SELECT * FROM data LIMIT 5`
2. Add filtering: `SELECT * FROM data WHERE Department = 'Sales' LIMIT 5`
3. Add grouping: `SELECT Department, COUNT(*) FROM data WHERE ... GROUP BY Department`
4. Add ordering: `... ORDER BY COUNT(*) DESC`

### Tip 3: Verify Results
- Always check row counts
- Verify calculations manually on a few rows
- Use LIMIT to preview before running on full data

### Tip 4: Export Workflow
```
1. Run analysis (SQL Query, Statistics, etc.)
2. Copy results from Output window
3. Paste into Excel
4. Format as needed
5. OR Generate Executive Report for presentation-ready output
```

---

## 🆘 Common Mistakes

### ❌ Mistake 1: Wrong table name
```sql
SELECT * FROM mydata  -- Wrong! Table is always called "data"
```
✅ Correct:
```sql
SELECT * FROM data
```

### ❌ Mistake 2: Column name typo
```sql
SELECT Departmnet FROM data  -- Typo!
```
✅ Check exact column names in Dataset Info panel

### ❌ Mistake 3: Forgetting GROUP BY
```sql
SELECT Department, AVG(Salary) FROM data  -- Error!
```
✅ Correct:
```sql
SELECT Department, AVG(Salary) FROM data GROUP BY Department
```

---

## 📚 Learning Resources

### Within NexData:
1. **Help > Quick Start Guide** - Basic usage
2. **Help > User Guide & Tutorials** - Comprehensive guide
3. **Dataset Info Panel** - See your column names

### SQL Learning:
- The SQL queries in NexData use **SQLite syntax**
- Most standard SQL works
- Practice with your own data!

---

## ✨ Summary

### Pivot Tables in NexData:
- Use **SQL Query** (Analysis > SQL Query)
- More powerful and flexible than traditional pivot tables
- Can do EVERYTHING Excel pivot tables can do + more

### Exporting Results:
- ✅ All analysis results can be copied from Output window
- ✅ Generate HTML reports automatically
- ✅ Export visualizations as images
- ✅ Export processed data as CSV/Excel/JSON

### Key Benefit:
**Learning SQL Query gives you a valuable professional skill** used in:
- Data analysis jobs
- Business intelligence
- Database management
- Data science

**SQL is the #1 most requested skill in data analyst job postings!**

---

**Still confused? Run `Help > Quick Start Guide` for hands-on examples!**
