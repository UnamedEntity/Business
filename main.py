import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from google import genai

# Initialize Gemini client
# Option 1: Set your API key directly (not recommended for production)
API_KEY = "AIzaSyAmShMF_z9MqEEZKzw0e2N8hgSHiWGKYdA"


try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"Failed to initialize Gemini client: {e}")
    client = None

astronaut_knowledge = """
You are an AI Essay Grader designed specifically for high school students. 
Your job is to evaluate essays using the categories stored in the knowledge base. 
Follow these rules:

1. ALWAYS provide structured feedback.
2. Grade the essay according to the stored categories. 
   - For each category, provide:
     (a) A score out of 10  
     (b) A short explanation  
     (c) Specific examples from the essay  
     (d) A clear suggestion to improve
3. Give an overall grade at the end (0–100%).
4. Never rewrite the full essay. Only improve small sections as examples.
5. Prioritize clarity, organization, thesis strength, evidence quality, and grammar.
6. If no categories match the essay, evaluate using your general high-school rubric.
7. Keep your tone helpful and teacher-like, not robotic.
8. Always show your reasoning in simple steps, but DO NOT reveal chain-of-thought.

Your output structure must be:

=== Essay Evaluation ===

Category 1: <Name>
Score: X/10
Feedback:
- Strength:
- Weakness:
- Specific fix:

Category 2: <Name>
Score: X/10
Feedback:
- Strength:
- Weakness:
- Specific fix:

...continue for all matching categories...

=== Overall Grade ===
Final Score: XX/100
Summary:
(1–2 sentences)

=== Suggested Improvements ===
- Bullet list of next steps

End of output.

"""

knowledge_base = []

def add_data(category, description):
    knowledge_base.append({
        'category': category,
        'description': description,
    })
    return True

def search_knowledge(query):
    results = []
    query_lower = query.lower()
    for entry in knowledge_base:
        if (query_lower in entry['category'].lower() or 
            query_lower in entry['description'].lower()):
            results.append(entry)
    return results[:5]

def list_all_data():
    return knowledge_base

def delete_data(category):
    global knowledge_base
    original_len = len(knowledge_base)
    knowledge_base = [entry for entry in knowledge_base if entry['category'] != category]
    return len(knowledge_base) < original_len

class EssayWriterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Essay Writer")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Color scheme
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.accent_color = "#e74c3c"
        self.bg_color = "#ecf0f1"
        self.text_color = "#2c3e50"
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="✍️ AI Essay Writer",
            font=("Helvetica", 24, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_grade_tab()
        self.create_category_tab()
        self.create_view_tab()
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Helvetica', 10, 'bold'))
        
    def create_grade_tab(self):
        grade_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(grade_frame, text="📝 Grade Essay")
        
        # Instructions
        inst_label = tk.Label(
            grade_frame,
            text="Enter your essay below and click 'Grade Essay' to receive AI feedback",
            font=("Helvetica", 11),
            bg="white",
            fg=self.text_color
        )
        inst_label.pack(pady=10)
        
        # Essay input
        input_frame = tk.Frame(grade_frame, bg="white")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            input_frame,
            text="Your Essay:",
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg=self.text_color
        ).pack(anchor=tk.W)
        
        self.essay_input = scrolledtext.ScrolledText(
            input_frame,
            font=("Helvetica", 11),
            wrap=tk.WORD,
            height=8,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.essay_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Grade button
        grade_btn = tk.Button(
            grade_frame,
            text="🎯 Grade Essay",
            font=("Helvetica", 12, "bold"),
            bg=self.secondary_color,
            fg="white",
            command=self.grade_essay,
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=10
        )
        grade_btn.pack(pady=10)
        
        # Response output
        output_frame = tk.Frame(grade_frame, bg="white")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            output_frame,
            text="AI Feedback:",
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg=self.text_color
        ).pack(anchor=tk.W)
        
        self.response_output = scrolledtext.ScrolledText(
            output_frame,
            font=("Helvetica", 11),
            wrap=tk.WORD,
            height=8,
            relief=tk.SOLID,
            borderwidth=1,
            state=tk.DISABLED
        )
        self.response_output.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def create_category_tab(self):
        category_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(category_frame, text="➕ Add Category")
        
        # Center form
        form_frame = tk.Frame(category_frame, bg="white")
        form_frame.pack(expand=True, pady=50)
        
        tk.Label(
            form_frame,
            text="Add New Grading Category",
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg=self.text_color
        ).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Category name
        tk.Label(
            form_frame,
            text="Category Name:",
            font=("Helvetica", 11),
            bg="white",
            fg=self.text_color
        ).grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
        
        self.category_entry = tk.Entry(
            form_frame,
            font=("Helvetica", 11),
            width=40,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.category_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Description
        tk.Label(
            form_frame,
            text="Description:",
            font=("Helvetica", 11),
            bg="white",
            fg=self.text_color
        ).grid(row=2, column=0, sticky=tk.NW, pady=10, padx=10)
        
        self.description_text = tk.Text(
            form_frame,
            font=("Helvetica", 11),
            width=40,
            height=6,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.description_text.grid(row=2, column=1, pady=10, padx=10)
        
        # Add button
        add_btn = tk.Button(
            form_frame,
            text="✅ Add Category",
            font=("Helvetica", 12, "bold"),
            bg=self.secondary_color,
            fg="white",
            command=self.add_category,
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=10
        )
        add_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
    def create_view_tab(self):
        view_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(view_frame, text="📚 View Categories")
        
        # Toolbar
        toolbar = tk.Frame(view_frame, bg="white")
        toolbar.pack(fill=tk.X, padx=20, pady=10)
        
        refresh_btn = tk.Button(
            toolbar,
            text="🔄 Refresh",
            font=("Helvetica", 10),
            bg=self.secondary_color,
            fg="white",
            command=self.refresh_categories,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            toolbar,
            text="🗑️ Delete Selected",
            font=("Helvetica", 10),
            bg=self.accent_color,
            fg="white",
            command=self.delete_category,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview for categories
        tree_frame = tk.Frame(view_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_tree = ttk.Treeview(
            tree_frame,
            columns=("Category", "Description"),
            show="headings",
            yscrollcommand=tree_scroll.set,
            height=15
        )
        tree_scroll.config(command=self.category_tree.yview)
        
        self.category_tree.heading("Category", text="Category")
        self.category_tree.heading("Description", text="Description")
        
        self.category_tree.column("Category", width=200)
        self.category_tree.column("Description", width=500)
        
        self.category_tree.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_categories()
        
    def grade_essay(self):
        if client is None:
            messagebox.showerror("Error", "Gemini client not initialized. Please check your API key.")
            return
            
        essay = self.essay_input.get("1.0", tk.END).strip()
        
        if not essay:
            messagebox.showwarning("Input Required", "Please enter an essay to grade.")
            return
        
        # Search for relevant categories
        results = search_knowledge(essay)
        context = ""
        if results:
            context = "\n\n[Stored Categories]:\n"
            for entry in results:
                context += f"- {entry['category']} | {entry['description']}\n"
        
        full_prompt = essay + context
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config={
                    "system_instruction": astronaut_knowledge
                }
            )
            
            self.response_output.config(state=tk.NORMAL)
            self.response_output.delete("1.0", tk.END)
            self.response_output.insert("1.0", response.text)
            self.response_output.config(state=tk.DISABLED)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                messagebox.showerror(
                    "API Quota Issue", 
                    "429 Error - Possible solutions:\n\n"
                    "1. Generate a NEW API key at:\n"
                    "   https://aistudio.google.com/apikey\n\n"
                    "2. Make sure billing is enabled (even free tier needs it)\n\n"
                    "3. Wait 1 minute and try again\n\n"
                    "4. Try a different Google account\n\n"
                    "Note: This is a common issue with new Gemini accounts."
                )
            else:
                messagebox.showerror("Error", f"Failed to grade essay:\n\n{error_msg[:200]}")
    
    def add_category(self):
        category = self.category_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        
        if not category or not description:
            messagebox.showwarning("Input Required", "Please fill in all fields.")
            return
        
        add_data(category, description)
        messagebox.showinfo("Success", "Category added successfully!")
        
        self.category_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.refresh_categories()
        
    def refresh_categories(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        for entry in list_all_data():
            self.category_tree.insert(
                "",
                tk.END,
                values=(entry['category'], entry['description'])
            )
    
    def delete_category(self):
        selected = self.category_tree.selection()
        
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category to delete.")
            return
        
        item = self.category_tree.item(selected[0])
        category = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete category '{category}'?"):
            if delete_data(category):
                messagebox.showinfo("Success", "Category deleted successfully!")
                self.refresh_categories()
            else:
                messagebox.showerror("Error", "Failed to delete category.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EssayWriterGUI(root)
    root.mainloop()