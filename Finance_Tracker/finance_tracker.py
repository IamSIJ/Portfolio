import customtkinter as ctk
import json
import os
import re
import pandas as pd
from datetime import datetime
from tkinter import messagebox, filedialog
import shutil
from typing import List, Dict
from transaction import Transaction
import config  # Import the config module

class FinanceTracker:
    def __init__(self):
        self.JSON_FILE = config.JSON_FILE
        self.CATEGORIES = config.CATEGORIES
        
        # Initialize main window
        self.window = ctk.CTk()
        self.window.title(config.WINDOW_TITLE)
        self.window.geometry(config.WINDOW_GEOMETRY)
        
        self.create_gui()
        self.load_data()
        self.update_ui()

    def create_gui(self):
        # Create frames
        self.left_frame = ctk.CTkFrame(self.window)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.right_frame = ctk.CTkFrame(self.window)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Input fields
        ctk.CTkLabel(self.left_frame, text="Date (DD-MM-YY):").pack(pady=5)
        self.date_entry = ctk.CTkEntry(self.left_frame)
        self.date_entry.insert(0, datetime.now().strftime("%d-%m-%y"))
        self.date_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.left_frame, text="Amount:").pack(pady=5)
        self.amount_entry = ctk.CTkEntry(self.left_frame)
        self.amount_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.left_frame, text="Description:").pack(pady=5)
        self.description_entry = ctk.CTkEntry(self.left_frame)
        self.description_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.left_frame, text="Category:").pack(pady=5)
        self.category_combo = ctk.CTkComboBox(self.left_frame, values=self.CATEGORIES)
        self.category_combo.set(self.CATEGORIES[0])
        self.category_combo.pack(pady=5, padx=10, fill="x")

        # Buttons
        ctk.CTkButton(self.left_frame, text="Add Transaction", command=self.add_transaction).pack(pady=10)
        
        # Budget section
        ctk.CTkLabel(self.left_frame, text="Monthly Budget:").pack(pady=5)
        self.budget_entry = ctk.CTkEntry(self.left_frame)
        self.budget_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self.left_frame, text="Set Budget", command=self.update_budget).pack(pady=5)

        # Import/Export buttons
        ctk.CTkButton(self.left_frame, text="Import", command=self.import_data).pack(pady=5)
        ctk.CTkButton(self.left_frame, text="Export", command=self.export_data).pack(pady=5)

        # Status section
        self.status_label = ctk.CTkLabel(self.right_frame, text="")
        self.status_label.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.right_frame)
        self.progress_bar.pack(pady=5, padx=10, fill="x")

        # Transaction list
        self.transaction_text = ctk.CTkTextbox(self.right_frame, width=400, height=400)
        self.transaction_text.pack(pady=10, padx=10, fill="both", expand=True)

    def load_data(self):
        if os.path.exists(self.JSON_FILE):
            with open(self.JSON_FILE, "r") as file:
                self.data = json.load(file)
        else:
            self.data = {"transactions": [], "budget": 0.0}

    def save_data(self):
        with open(self.JSON_FILE, "w") as file:
            json.dump(self.data, file, indent=4)
        self.backup_data()

    def backup_data(self):
        if not os.path.exists(config.BACKUP_FOLDER):
            os.makedirs(config.BACKUP_FOLDER)
        backup_file = os.path.join(config.BACKUP_FOLDER, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        shutil.copy2(self.JSON_FILE, backup_file)

    def add_transaction(self):
        try:
            date = self.date_entry.get()
            amount = float(self.amount_entry.get())
            description = self.description_entry.get()
            category = self.category_combo.get()

            # Validate date format
            if not re.match(r"\d{2}-\d{2}-\d{2}", date):
                messagebox.showwarning("Input Error", "Date must be in DD-MM-YY format!")
                return

            # Validate amount
            if amount <= 0:
                messagebox.showwarning("Input Error", "Amount must be a positive number!")
                return

            if not all([date, amount, description, category]):
                messagebox.showwarning("Input Error", "All fields must be filled!")
                return

            transaction = Transaction(date, amount, description, category)
            self.data['transactions'].append(transaction.to_dict())
            self.save_data()
            self.update_ui()
            
            # Clear inputs
            self.date_entry.delete(0, 'end')
            self.amount_entry.delete(0, 'end')
            self.description_entry.delete(0, 'end')
            
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input values!")

    def update_budget(self):
        try:
            budget = float(self.budget_entry.get())
            if budget <= 0:
                messagebox.showwarning("Input Error", "Budget must be a positive number!")
                return
            self.data['budget'] = budget
            self.save_data()
            self.update_ui()
            messagebox.showinfo("Success", "Budget updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid budget value!")

    def update_ui(self):
        # Update transaction list
        self.transaction_text.delete("1.0", "end")
        for t in self.data['transactions']:
            self.transaction_text.insert("end", 
                f"{t['date']} - Rs.{t['amount']:.2f} - {t['description']} ({t['category']})\n")

        # Update status
        total_spent = sum(t['amount'] for t in self.data['transactions'])
        budget = self.data['budget']
        remaining = budget - total_spent
        
        self.status_label.configure(
            text=f"Budget: Rs.{budget:.2f}\nSpent: Rs.{total_spent:.2f}\nRemaining: Rs.{remaining:.2f}")
        
        # Update progress bar
        progress = min(1.0, total_spent / budget if budget > 0 else 0)
        self.progress_bar.set(progress)

    def import_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("JSON files", "*.json")])
        if not file_path:
            return

        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                new_transactions = df.to_dict('records')
            else:
                with open(file_path, 'r') as file:
                    new_data = json.load(file)
                    new_transactions = new_data['transactions']

            self.data['transactions'].extend(new_transactions)
            self.save_data()
            self.update_ui()
            messagebox.showinfo("Success", "Data imported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {str(e)}")

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("JSON files", "*.json")])
        if not file_path:
            return

        try:
            if file_path.endswith('.xlsx'):
                df = pd.DataFrame(self.data['transactions'])
                df.to_excel(file_path, index=False)
            else:
                with open(file_path, 'w') as file:
                    json.dump(self.data, file, indent=4)
            messagebox.showinfo("Success", "Data exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def run(self):
        self.window.mainloop()