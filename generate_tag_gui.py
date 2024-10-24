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
        master.geometry("600x600")
        
        # Try to load last save directory
        self.config_file = os.path.join(os.path.expanduser("~"), ".label_generator_config")
        self.last_directory = self.load_last_directory()
        
        self.create_widgets()

    def load_last_directory(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('last_directory', os.path.expanduser("~"))
        except Exception:
            pass
        return os.path.expanduser("~")

    def save_last_directory(self, directory):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'last_directory': directory}, f)
        except Exception:
            pass

    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Title
        title_label = ttk.Label(self.main_frame, 
                              text="Barcode Label Generator", 
                              font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=10)

        # Number of items input frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Number of Labels")
        input_frame.pack(fill="x", padx=5, pady=5)

        # Number of items input with label
        self.num_items = ttk.Entry(input_frame, width=10)
        self.num_items.pack(side="left", padx=5, pady=5)
        
        ttk.Button(input_frame, 
                  text="Generate Input Fields",
                  command=self.generate_input_fields).pack(side="left", padx=5, pady=5)

        # Create container frame for canvas and scrollbar
        self.container = ttk.LabelFrame(self.main_frame, text="Label Details")
        self.container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create canvas
        self.canvas = tk.Canvas(self.container)
        
        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        
        # Create frame inside canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Place the frame in the canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas and scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind canvas resizing
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Mouse wheel scrolling
        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        # Generate Labels button
        self.generate_button = ttk.Button(button_frame, 
                                        text="Generate Labels", 
                                        command=self.generate_labels)
        self.generate_button.pack(side="right", padx=5)

    def on_canvas_configure(self, event):
        # Update the width of the canvas window to fit the frame
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

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

        # Update the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def generate_labels(self):
        if not hasattr(self, 'item_inputs'):
            messagebox.showerror("Error", "Please generate input fields first.")
            return

        try:
            # Validate inputs
            items = []
            for i, (title1, title2, barcode) in enumerate(self.item_inputs):
                if not all([title1.get(), title2.get(), barcode.get()]):
                    messagebox.showerror("Error", 
                                       f"Please fill in all fields for Label {i+1}")
                    return
                
                items.append({
                    'title1': title1.get(),
                    'title2': title2.get(),
                    'barcode': barcode.get()
                })

            # Generate PDF
            pdf_bytes = pdf_generator.create_pdf(items)
            
            # Ask user where to save the file
            initial_dir = self.last_directory
            file_path = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile="labels.pdf",
                title="Save Labels PDF"
            )
            
            if file_path:  # User didn't cancel
                # Save the new directory
                self.last_directory = os.path.dirname(file_path)
                self.save_last_directory(self.last_directory)
                
                try:
                    with open(file_path, "wb") as f:
                        f.write(pdf_bytes)
                    messagebox.showinfo("Success", 
                                      f"Labels saved successfully to:\n{file_path}")
                    
                    # Ask if user wants to open the generated PDF
                    if messagebox.askyesno("Open PDF", 
                                         "Would you like to open the generated PDF?"):
                        try:
                            if sys.platform.startswith('win'):
                                os.startfile(file_path)
                            elif sys.platform.startswith('darwin'):  # macOS
                                os.system(f'open "{file_path}"')
                            else:  # Linux
                                os.system(f'xdg-open "{file_path}"')
                        except Exception as e:
                            messagebox.showwarning("Warning", 
                                                 f"Could not open PDF automatically: {str(e)}")
                            
                except Exception as e:
                    messagebox.showerror("File Error", 
                        f"Error saving PDF file: {str(e)}\n"
                        "Make sure you have write permissions for the selected location.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating PDF: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelGeneratorApp(root)
    root.mainloop()
