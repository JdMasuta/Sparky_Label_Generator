import tkinter as tk
from tkinter import ttk, messagebox
from pdf_generator import create_pdf

class LabelGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Barcode Label Generator")
        master.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        # Number of items input
        ttk.Label(self.master, text="Number of items:").pack(pady=5)
        self.num_items = ttk.Entry(self.master)
        self.num_items.pack(pady=5)
        ttk.Button(self.master, text="Generate Input Fields", command=self.generate_input_fields).pack(pady=5)

        # Scrollable frame for item inputs
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Generate Labels button
        self.generate_button = ttk.Button(self.master, text="Generate Labels", command=self.generate_labels)
        self.generate_button.pack(pady=10)

    def generate_input_fields(self):
        # Clear previous inputs
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            num_items = int(self.num_items.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of items.")
            return

        self.item_inputs = []
        for i in range(num_items):
            frame = ttk.LabelFrame(self.scrollable_frame, text=f"Item {i+1}")
            frame.pack(pady=5, padx=10, fill="x")

            title1 = ttk.Entry(frame)
            title1.insert(0, f"Title 1 for item {i+1}")
            title1.pack(fill="x", padx=5, pady=2)

            title2 = ttk.Entry(frame)
            title2.insert(0, f"Title 2 for item {i+1}")
            title2.pack(fill="x", padx=5, pady=2)

            barcode = ttk.Entry(frame)
            barcode.insert(0, f"Barcode for item {i+1}")
            barcode.pack(fill="x", padx=5, pady=2)

            self.item_inputs.append((title1, title2, barcode))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def generate_labels(self):
        if not hasattr(self, 'item_inputs'):
            messagebox.showerror("Error", "Please generate input fields first.")
            return

        items = []
        for title1, title2, barcode in self.item_inputs:
            items.append({
                'title1': title1.get(),
                'title2': title2.get(),
                'barcode': barcode.get()
            })

        pdf_bytes = create_pdf(items)
        
        with open("labels.pdf", "wb") as f:
            f.write(pdf_bytes)
        
        messagebox.showinfo("Success", "Labels generated successfully! Check 'labels.pdf' in the current directory.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelGeneratorApp(root)
    root.mainloop()