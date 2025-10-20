"""
AI Dialog Classes
Contains all AI-powered dialogs extracted from main_window.py
Following SEPARATION OF CONCERNS and CLEAN CODE principles
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog


class AIDialogs:
    """Factory class for AI-powered dialogs"""
    
    @staticmethod
    def show_quality_advisor_dialog(parent, df, ai_service, action_map):
        """
        Show Data Quality Advisor dialog
        
        Args:
            parent: Parent window
            df: DataFrame to analyze
            ai_service: AI service instance
            action_map: Dict mapping tool names to action methods
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Data Quality Advisor - AI Recommendations")
        dialog.geometry("700x600")
        
        ttk.Label(dialog, text="🤖 Data Quality Advisor", font=('Arial', 14, 'bold')).pack(pady=15)
        ttk.Label(dialog, text="Analyzing your data and recommending actions...", font=('Arial', 10)).pack(pady=5)
        
        # Create notebook for categories
        advisor_notebook = ttk.Notebook(dialog)
        advisor_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Analyze data using AI service
        recommendations = ai_service.analyze_data_quality(df)
        
        # Add action callbacks to recommendations
        for rec in recommendations:
            tool_name = rec['tool']
            rec['action'] = action_map.get(tool_name, lambda: messagebox.showinfo("Info", "Tool coming soon!"))
        
        # Group by priority
        high_priority = [r for r in recommendations if r['priority'] == 'High']
        medium_priority = [r for r in recommendations if r['priority'] == 'Medium']
        low_priority = [r for r in recommendations if r['priority'] == 'Low']
        
        # High Priority Tab
        if high_priority:
            high_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(high_frame, text=f"🔴 High Priority ({len(high_priority)})")
            AIDialogs._create_recommendations_view(high_frame, high_priority, dialog)
        
        # Medium Priority Tab
        if medium_priority:
            med_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(med_frame, text=f"🟡 Medium Priority ({len(medium_priority)})")
            AIDialogs._create_recommendations_view(med_frame, medium_priority, dialog)
        
        # Low Priority Tab
        if low_priority:
            low_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(low_frame, text=f"🟢 Low Priority ({len(low_priority)})")
            AIDialogs._create_recommendations_view(low_frame, low_priority, dialog)
        
        # All Clear Tab
        if not recommendations:
            clear_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(clear_frame, text="✅ All Clear")
            ttk.Label(clear_frame, text="✅ No data quality issues detected!", 
                     font=('Arial', 12, 'bold'), foreground='green').pack(pady=50)
            ttk.Label(clear_frame, text="Your data looks clean and ready for analysis!", 
                     font=('Arial', 10)).pack(pady=10)
        
        # Summary at bottom
        summary_frame = ttk.Frame(dialog)
        summary_frame.pack(fill=tk.X, padx=15, pady=10)
        
        summary_text = f"Found {len(recommendations)} issue(s): "
        summary_text += f"{len(high_priority)} High, {len(medium_priority)} Medium, {len(low_priority)} Low"
        ttk.Label(summary_frame, text=summary_text, font=('Arial', 10, 'bold')).pack()
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    @staticmethod
    def _create_recommendations_view(parent, recommendations, dialog):
        """Create scrollable view of recommendations"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add recommendations
        for idx, rec in enumerate(recommendations, 1):
            rec_frame = ttk.LabelFrame(scrollable_frame, text=f"Issue #{idx}: {rec['issue']}", padding=10)
            rec_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(rec_frame, text=f"Impact: {rec['impact']}", 
                     font=('Arial', 9), wraplength=550).pack(anchor='w', pady=2)
            
            ttk.Label(rec_frame, text=f"Recommended Tool: {rec['tool']}", 
                     font=('Arial', 9, 'bold'), foreground='blue').pack(anchor='w', pady=2)
            
            def make_action(action, dlg):
                def run_action():
                    dlg.destroy()
                    action()
                return run_action
            
            ttk.Button(rec_frame, text=f"🔧 Fix with {rec['tool']}", 
                      command=make_action(rec['action'], dialog),
                      style='Action.TButton').pack(anchor='w', pady=5)
    
    @staticmethod
    def show_ai_report_generator_dialog(parent, df, ai_service, root):
        """
        Show AI Report Generator dialog
        
        Args:
            parent: Parent window
            df: DataFrame to analyze
            ai_service: AI service instance
            root: Root window for clipboard operations
        """
        dialog = tk.Toplevel(parent)
        dialog.title("AI Report Generator")
        dialog.geometry("800x700")
        
        ttk.Label(dialog, text="🤖 AI Report Generator", font=('Arial', 14, 'bold')).pack(pady=15)
        ttk.Label(dialog, text="Generating comprehensive analysis report...", font=('Arial', 10)).pack(pady=5)
        
        # Report display
        report_frame = ttk.LabelFrame(dialog, text="Generated Report", padding=10)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, font=('Courier', 9))
        report_text.pack(fill=tk.BOTH, expand=True)
        
        # Generate report using AI service
        report_content = ai_service.generate_report(df)
        report_text.insert(1.0, report_content)
        report_text.config(state=tk.DISABLED)
        
        # Export buttons
        export_frame = ttk.Frame(dialog)
        export_frame.pack(pady=10)
        
        def export_txt():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                messagebox.showinfo("Success", f"Report exported to:\n{file_path}")
        
        def copy_to_clipboard():
            root.clipboard_clear()
            root.clipboard_append(report_content)
            messagebox.showinfo("Success", "Report copied to clipboard!")
        
        ttk.Button(export_frame, text="📄 Export as TXT", command=export_txt, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📋 Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
