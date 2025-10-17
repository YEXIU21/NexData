# NexData Refactoring Strategy
## How to Continue the Refactoring Process

---

## 🎯 GOAL

Reduce `main_window.py` from **5,378 lines** to **~500-800 lines** by using service layer.

---

## ✅ PATTERN TO FOLLOW

### **Example: remove_duplicates() Refactoring**

**BEFORE (Lines 833-835):**
```python
before = len(self.df)
self.df = self.df.drop_duplicates(subset=subset_cols, keep=keep_option)
removed = before - len(self.df)
```

**AFTER (Lines 833-843):**
```python
before = len(self.df)
try:
    # Use cleaning service
    cleaned_df, removed = self.cleaning_service.remove_duplicates(
        self.df, 
        subset=subset_cols, 
        keep=keep_option
    )
    self.df = cleaned_df
except Exception as e:
    messagebox.showerror("Error", f"Failed to remove duplicates: {str(e)}")
    return
```

**KEY CHANGES:**
1. ✅ Replaced direct pandas call with service method
2. ✅ Service returns cleaned DataFrame AND count of changes
3. ✅ Wrapped in try-except for error handling
4. ✅ Display user-friendly error message if fails
5. ✅ Keep all UI code unchanged (dialog, buttons, output text)

---

## 📋 REFACTORING CHECKLIST

For EACH method in main_window.py:

### **Step 1: Identify Data Manipulation Line(s)**
Look for lines that directly manipulate `self.df`:
- `self.df.drop_duplicates(...)`
- `self.df.fillna(...)`
- `self.df.groupby(...)`
- `pd.read_csv(...)`
- etc.

### **Step 2: Replace with Service Call**
```python
# OLD:
self.df = self.df.some_operation(...)

# NEW:
try:
    result_df = self.service_name.method_name(self.df, parameters)
    self.df = result_df
except Exception as e:
    messagebox.showerror("Error", f"Operation failed: {str(e)}")
    return
```

### **Step 3: Keep UI Code Unchanged**
- Dialog creation code → Keep
- Button handlers → Keep
- Output formatting → Keep
- Messageboxes → Keep

### **Step 4: Test the Method**
- Run NexData
- Test the refactored method
- Verify it works correctly
- Check error handling

---

## 🗂️ METHOD REFACTORING PRIORITY

### **HIGH PRIORITY (Do First):**

**Cleaning Methods** - Use `cleaning_service`:
1. [x] ✅ remove_duplicates() - DONE
2. [ ] handle_missing_values() - Lines 924-961
3. [ ] smart_fill_missing() - Find and refactor
4. [ ] trim_all_columns() - Find and refactor
5. [ ] standardize_text_case() - Find and refactor
6. [ ] remove_empty() - Find and refactor

**AI Methods** - Use `ai_service`:
7. [ ] data_quality_advisor() - Lines ~1694-1754
8. [ ] generate_ai_report() - Find and refactor

**Data Import/Export** - Use `data_service`:
9. [ ] import_csv() - Find and refactor
10. [ ] import_excel() - Find and refactor
11. [ ] export_csv() - Find and refactor
12. [ ] export_excel() - Find and refactor

### **MEDIUM PRIORITY:**

**Analysis Methods** - Use `analysis_service`:
- group_by_analysis()
- pivot_analysis()
- correlation_matrix()
- show_statistics()

### **LOW PRIORITY:**

**Visualization Methods** - Keep as is for now
**UI Setup Methods** - Keep as is

---

## 🛠️ DETAILED REFACTORING GUIDE

### **Cleaning Methods Pattern:**

**Original Pattern:**
```python
def some_cleaning_method(self):
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    # ... dialog setup ...
    
    def apply():
        # Get parameters from UI
        param1 = var1.get()
        param2 = var2.get()
        
        # FIND THIS LINE - Direct data manipulation
        self.df = self.df.some_pandas_operation(param1, param2)
        
        # ... output formatting ...
```

**Refactored Pattern:**
```python
def some_cleaning_method(self):
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    # ... dialog setup (UNCHANGED) ...
    
    def apply():
        # Get parameters from UI (UNCHANGED)
        param1 = var1.get()
        param2 = var2.get()
        
        # REPLACE THIS SECTION
        try:
            cleaned_df = self.cleaning_service.method_name(
                self.df, 
                param1, 
                param2
            )
            self.df = cleaned_df
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {str(e)}")
            return
        
        # ... output formatting (UNCHANGED) ...
```

---

## 🔍 HOW TO FIND METHODS TO REFACTOR

### **Search Commands:**

**Find cleaning methods:**
```bash
# In VS Code or grep:
grep -n "def.*clean\|def.*remove\|def.*fill\|def.*trim" main_window.py
```

**Find data manipulation:**
```bash
grep -n "self.df\s*=" main_window.py
grep -n "self.df\." main_window.py
```

**Find methods by category:**
```bash
# Cleaning
grep -n "def handle_missing\|def remove_\|def smart_fill" main_window.py

# Analysis
grep -n "def group_by\|def pivot\|def correlation" main_window.py

# Import/Export
grep -n "def import_\|def export_" main_window.py
```

---

## 📝 REFACTORING TEMPLATE

Use this template for each method:

```python
# ORIGINAL (find this pattern):
self.df = self.df.some_operation(params)

# REFACTORED (replace with this):
try:
    result_df = self.service.method_name(self.df, params)
    self.df = result_df
except ValueError as e:
    messagebox.showerror("Error", f"Invalid input: {str(e)}")
    return
except Exception as e:
    messagebox.showerror("Error", f"Operation failed: {str(e)}")
    return
```

---

## 🎯 COMPLETION CRITERIA

A method is "refactored" when:

1. ✅ Direct pandas operations replaced with service calls
2. ✅ Wrapped in try-except error handling
3. ✅ User-friendly error messages shown
4. ✅ Method tested and working
5. ✅ UI code unchanged
6. ✅ Output formatting unchanged

---

## 📊 TRACKING PROGRESS

Update `REFACTORING_PROGRESS.md` after refactoring each method:

```markdown
**Cleaning Methods (using CleaningService):**
- [x] remove_duplicates() - DONE ✅
- [x] handle_missing_values() - DONE ✅
- [x] smart_fill_missing() - DONE ✅
... etc
```

---

## 🚀 QUICK START (Next Session)

**To continue refactoring:**

1. **Open** `main_window.py`
2. **Search** for next unchecked method in REFACTORING_PROGRESS.md
3. **Find** the data manipulation line(s) in that method
4. **Replace** with service call using the pattern above
5. **Test** the method
6. **Check** it off in REFACTORING_PROGRESS.md
7. **Repeat** for next method

---

## 💡 TIPS

- **One method at a time** - Don't rush
- **Test immediately** - Catch bugs early
- **Keep UI separate** - Only refactor data logic
- **Use services** - That's what we built them for!
- **Error handling** - Always wrap in try-except
- **User feedback** - Show clear error messages

---

## 🎓 EXAMPLE WALKTHROUGH

**Let's refactor `trim_all_columns()`:**

**Step 1:** Find the method (search for "def trim_all_columns")

**Step 2:** Find the data manipulation:
```python
for col in text_cols:
    self.df[col] = self.df[col].str.strip()
    self.df[col] = self.df[col].str.replace(r'\s+', ' ', regex=True)
```

**Step 3:** Replace with service:
```python
try:
    cleaned_df = self.cleaning_service.trim_all_columns(self.df)
    self.df = cleaned_df
except Exception as e:
    messagebox.showerror("Error", f"Failed to trim columns: {str(e)}")
    return
```

**Step 4:** Test it - Load data, click Clean → Trim All Columns, verify it works

**Step 5:** Check it off:
```markdown
- [x] trim_all_columns() - DONE ✅
```

**Done!** Move to next method.

---

*Created: October 17, 2025*
*For: Systematic refactoring of main_window.py*
*Goal: Clean, maintainable, service-based architecture*
