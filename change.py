import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

class JSONEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("JSON Editor")
        
        # Create a frame for the file selection and buttons
        top_frame = tk.Frame(self.master)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        save_button = tk.Button(top_frame, text="Save", command=self.save_json_file)
        save_button.pack(side=tk.LEFT, padx=(5,0))
        
        # Scrollable frame setup
        container = tk.Frame(self.master)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.form_frame = tk.Frame(canvas)
        self.form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variables
        self.json_data = {}
        self.file_path = None
        self.entries = {}  # key: Entry widget for value editing
        self.load_json_file()

    def load_json_file(self):
        file_path = 'config.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            self.file_path = file_path
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Error", f"Failed to load JSON file:\n{e}")
            return
        
        self.build_form()

    def build_form(self):
        # Clear existing widgets in form_frame
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        self.entries = {}
        
        # Create a label & entry for each key-value pair
        row = 0
        for key, value in self.json_data.items():
            tk.Label(self.form_frame, text=key, anchor="w").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            
            val_str = str(value)
            entry = tk.Entry(self.form_frame, width=50)
            entry.insert(0, val_str)
            entry.grid(row=row, column=1, sticky="we", padx=5, pady=5)
            
            self.entries[key] = entry
            row += 1

    def save_json_file(self):
        if not self.file_path:
            messagebox.showwarning("No file loaded", "Please load a JSON file first.")
            return
        
        # Update json_data from entry widgets
        for key, entry in self.entries.items():
            val_str = entry.get()
            # Attempt to parse value if it looks like a number or boolean
            # Otherwise, treat as string
            try:
                # Try to interpret the value in a JSON-like manner
                possible_values = {
                    "true": True, "false": False, "null": None
                }
                val_lower = val_str.lower()
                if val_lower in possible_values:
                    val = possible_values[val_lower]
                else:
                    # Try number
                    if val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit()):
                        val = int(val_str)
                    else:
                        # Maybe float?
                        try:
                            val = float(val_str)
                        except ValueError:
                            # Just treat as string
                            val = val_str
                self.json_data[key] = val
            except Exception:
                # If any error occurs, keep it as string
                self.json_data[key] = val_str
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, indent=4)
            messagebox.showinfo("Success", "JSON file saved successfully!")
        except OSError as e:
            messagebox.showerror("Error", f"Failed to save JSON file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONEditor(root)
    root.mainloop()
