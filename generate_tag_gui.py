import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import json

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Import pdf_generator with path handling
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pdf_generator",
    resource_path("pdf_generator.py")
)
pdf_generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdf_generator)

class LabelGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Barcode Label Generator")
        master.geometry("600x600")  # Made window taller
        
        # Try to load last save directory
        self.config_file = os.path.join(os.path.expanduser("~"), ".label_generator_config")
        self.last_directory = self.load_last_directory()
        
        self.create_widgets()

    def load_last_directory(self):
        """Load the last used directory from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('last_directory', os.path.expanduser("~"))
        except Exception:
            pass
        return os.path.expanduser("~")

    def save_last_directory(self, directory):
        """Save the last used directory to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'last_directory': directory}, f)
        except Exception:
            pass

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Title
        title_label = ttk.Label(main_frame, 
                              text="Barcode Label Generator", 
                              font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=10)

        # Number of items input frame
        input_frame = ttk.LabelFrame(main_frame, text="Number of Labels")
        input_frame.pack(fill="x", padx=5, pady=5)

        # Number of items input with label
        self.num_items = ttk.Entry(input_frame, width=10)
        self.num_items.pack(side="left", padx=5, pady=5)
        
        ttk.Button(input_frame, 
                  text="Generate Input Fields",
                  command=self.generate_input_fields).pack(side="left", padx=5, pady=5)

        # Scrollable frame for item inputs
        scroll_container = ttk.LabelFrame(main_frame, text="Label Details")
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(scroll_container)
        self.scrollbar = ttk.Scrollbar(scroll_container, 
                                     orient="vertical", 
                                     command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Create window inside canvas
        self.canvas.create_window((0, 0), 
                                window=self.scrollable_frame, 
                                anchor="nw", 
                                width=self.canvas.winfo_width())

        # Configure canvas and scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)
        self.scrollbar.pack(side="right", fill="y", pady=5)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        # Generate Labels button
        self.generate_button = ttk.Button(button_frame, 
                                        text="Generate Labels", 
                                        command=self.generate_labels)
        self.generate_button.pack(side="right", padx=5)

    def generate_input_fields(self):
        # Clear previous inputs
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            num_items = int(self.num_items.get())
            if num_items < 1:
                raise ValueError("Number must be positive")
        except ValueError as e:
            messagebox.showerror("Error", 
                               "Please enter a valid number of items (positive integer).")
            return

        self.item_inputs = []
        for i in range(num_items):
            frame = ttk.LabelFrame(self.scrollable_frame, text=f"Label {i+1}")
            frame.pack(pady=5, padx=10, fill="x")

            # Grid layout for better alignment
            frame.grid_columnconfigure(1, weight=1)

            # Title 1
            ttk.Label(frame, text="Title 1:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            title1 = ttk.Entry(frame)
            title1.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

            # Title 2
            ttk.Label(frame, text="Title 2:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
            title2 = ttk.Entry(frame)
            title2.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

            # Barcode
            ttk.Label(frame, text="Barcode:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
            barcode = ttk.Entry(frame)
            barcode.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

            self.item_inputs.append((title1, title2, barcode))

    def generate_labels(self):
    if not hasattr(self, 'item_inputs'):
        messagebox.showerror("Error", "Please generate input fields first.")
        return

    try:
        items = []
        for title1, title2, barcode in self.item_inputs:
            items.append({
                'title1': title1.get(),
                'title2': title2.get(),
                'barcode': barcode.get()
            })

        pdf_bytes = pdf_generator.create_pdf(items)
        
        try:
            with open("labels.pdf", "wb") as f:
                f.write(pdf_bytes)
            messagebox.showinfo("Success", "Labels generated successfully! Check 'labels.pdf' in the current directory.")
        except Exception as e:
            messagebox.showerror("File Error", f"Error saving PDF file: {str(e)}\nMake sure you have write permissions in the current directory.")
            
    except Exception as e:
        messagebox.showerror("Error", f"Error generating PDF: {str(e)}")
        # Print for debugging
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelGeneratorApp(root)
    root.mainloop()
