import customtkinter as ctk
import json
import os
import pandas as pd
from datetime import datetime
from tkinter import messagebox, filedialog

# Define the path for the JSON file to store data
JSON_FILE = "data.json"

# Load data (transactions and budget) from the JSON file
def load_data():
    """
    Load transaction and budget data from a JSON file.
    If the file doesn't exist, return an empty data structure.
    """
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            return json.load(file)
    return {"transactions": [], "budget": 0.0}

# Save data (transactions and budget) to the JSON file
def save_data(data):
    """
    Save the provided data (transactions and budget) to the JSON file.
    """
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Format currency according to Rupees
def format_currency(amount):
    """
    Format the given amount as Rupees.
    """
    return f"Rs {amount:,.2f}"

# Convert date to DD-MM-YY format
def format_date(date_str):
    """
    Convert a date string from DD-MM-YYYY to DD-MM-YY format.
    Returns 'Invalid Date' if the conversion fails.
    """
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%d-%m-%y")
    except ValueError:
        return "Invalid Date"

# Add a transaction to the list
def add_transaction(date, amount, description):
    """
    Add a new transaction to the data.
    Validates input, converts date format, and updates the UI.
    """
    try:
        amount = float(amount)  # Convert amount to float
        date = datetime.strptime(date, "%d-%m-%y").strftime("%d-%m-%Y")  # Convert to consistent format
    except ValueError:
        messagebox.showwarning("Input Error", "Amount must be a valid number and date must be in DD-MM-YY format!")
        return

    data = load_data()
    data['transactions'].append({
        "date": date,
        "amount": amount,
        "description": description
    })
    save_data(data)
    update_transaction_list()
    update_budget_status()

# Calculate the total expenses
def calculate_total_expenses():
    """
    Calculate the sum of all transaction amounts.
    """
    data = load_data()
    return sum(float(transaction['amount']) for transaction in data['transactions'])

# Update the list of transactions displayed in the GUI
def update_transaction_list():
    """
    Refresh the transaction list displayed in the UI.
    """
    data = load_data()
    transactions = data['transactions']
    transaction_textbox.delete("0.0", ctk.END)
    for transaction in transactions:
        formatted_amount = format_currency(float(transaction['amount']))
        formatted_date = format_date(transaction['date'])
        transaction_textbox.insert(ctk.END, f"{formatted_date} - {formatted_amount}: {transaction['description']}\n")

# Update the budget status display
def update_budget_status():
    """
    Update the budget status label and progress bar based on current expenses and budget.
    """
    try:
        budget = float(budget_entry.get())
        if budget < 0:
            raise ValueError("Budget must be positive.")
    except ValueError:
        messagebox.showwarning("Input Error", "Invalid budget amount! Please enter a valid number.")
        return

    data = load_data()
    data['budget'] = budget
    save_data(data)

    total_expenses = calculate_total_expenses()
    remaining_budget = budget - total_expenses
    status_label.configure(text=f"Current Status: Spent {format_currency(total_expenses)} of {format_currency(budget)} budget. Remaining: {format_currency(remaining_budget)}")

    # Update progress bar
    progress = (total_expenses / budget) if budget > 0 else 0
    progress = min(progress, 1)  # Ensure progress doesn't exceed 100%
    budget_progress.set(progress)

# Export transactions to an Excel file
def export_to_excel():
    """
    Export all transactions to an Excel file.
    """
    data = load_data()
    if not data['transactions']:
        messagebox.showwarning("Export Error", "No transactions to export!")
        return
    
    df = pd.DataFrame(data['transactions'])
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                           filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if file_path:
        try:
            df.to_excel(file_path, index=False, engine='openpyxl')
            messagebox.showinfo("Export Successful", f"Transactions have been exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")

# Import transactions from JSON or Excel file
def import_transactions():
    """
    Import transactions from a JSON or Excel file.
    Prevents duplicate entries and handles potential errors.
    """
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("Excel files", "*.xlsx"), ("All files", "*.*")])
    if not file_path:
        return

    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r') as file:
                imported_data = json.load(file)
                if 'transactions' not in imported_data:
                    raise ValueError("Invalid JSON structure. 'transactions' key not found.")
                new_transactions = imported_data['transactions']
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
            new_transactions = df.to_dict('records')
        else:
            messagebox.showwarning("Import Error", "Unsupported file format. Please use JSON or Excel.")
            return

        data = load_data()
        existing_transactions = data['transactions']
        
        # Convert existing transactions to a set of tuples for efficient comparison
        existing_set = set((t['date'], t['amount'], t['description']) for t in existing_transactions)
        
        added_count = 0
        skipped_count = 0
        
        for transaction in new_transactions:
            # Ensure the transaction has all required fields
            if all(key in transaction for key in ['date', 'amount', 'description']):
                # Create a tuple of the transaction details
                transaction_tuple = (transaction['date'], transaction['amount'], transaction['description'])
                
                # Check if this transaction already exists
                if transaction_tuple not in existing_set:
                    existing_transactions.append(transaction)
                    existing_set.add(transaction_tuple)
                    added_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1  # Skip transactions with missing fields
        
        data['transactions'] = existing_transactions
        save_data(data)
        update_transaction_list()
        update_budget_status()
        
        messagebox.showinfo("Import Successful", 
                            f"Imported {added_count} new transactions.\n"
                            f"Skipped {skipped_count} duplicate or invalid transactions.")
    except Exception as e:
        messagebox.showerror("Import Error", f"An error occurred while importing: {str(e)}")

# Function called when the Add button is pressed
def on_add_button_pressed():
    """
    Handle the Add Transaction button click event.
    """
    date = date_entry.get()
    amount = amount_entry.get()
    description = description_entry.get()
    if date and amount and description:
        add_transaction(date, amount, description)
        date_entry.delete(0, ctk.END)
        amount_entry.delete(0, ctk.END)
        description_entry.delete(0, ctk.END)
    else:
        messagebox.showwarning("Input Error", "All fields must be filled out!")

# Function called when the Set Budget button is pressed
def on_set_budget_button_pressed():
    """
    Handle the Set Budget button click event.
    """
    update_budget_status()

# Function called when the Export button is pressed
def on_export_button_pressed():
    """
    Handle the Export to Excel button click event.
    """
    export_to_excel()

# Function called when the Import button is pressed
def on_import_button_pressed():
    """
    Handle the Import Transactions button click event.
    """
    import_transactions()

# Create the main window
app = ctk.CTk()
app.title("Personal Finance Tracker")

# Make the app responsive
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

# Create main frame
main_frame = ctk.CTkFrame(app)
main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Left frame for input and buttons
left_frame = ctk.CTkFrame(main_frame)
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

ctk.CTkLabel(left_frame, text="Date (DD-MM-YY):").pack(pady=5)
date_entry = ctk.CTkEntry(left_frame)
date_entry.pack(pady=5, padx=10, fill="x")

ctk.CTkLabel(left_frame, text="Amount:").pack(pady=5)
amount_entry = ctk.CTkEntry(left_frame)
amount_entry.pack(pady=5, padx=10, fill="x")

ctk.CTkLabel(left_frame, text="Description:").pack(pady=5)
description_entry = ctk.CTkEntry(left_frame)
description_entry.pack(pady=5, padx=10, fill="x")

add_button = ctk.CTkButton(left_frame, text="Add Transaction", command=on_add_button_pressed)
add_button.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(left_frame, text="Set Monthly Budget:").pack(pady=5)
budget_entry = ctk.CTkEntry(left_frame)
budget_entry.pack(pady=5, padx=10, fill="x")

set_budget_button = ctk.CTkButton(left_frame, text="Set Budget", command=on_set_budget_button_pressed)
set_budget_button.pack(pady=10, padx=10, fill="x")

export_button = ctk.CTkButton(left_frame, text="Export to Excel", command=on_export_button_pressed)
export_button.pack(pady=10, padx=10, fill="x")

import_button = ctk.CTkButton(left_frame, text="Import Transactions", command=on_import_button_pressed)
import_button.pack(pady=10, padx=10, fill="x")

# Right frame for transaction list and status
right_frame = ctk.CTkFrame(main_frame)
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

transaction_textbox = ctk.CTkTextbox(right_frame, width=400, height=200)
transaction_textbox.grid(row=0, column=0, pady=5, padx=10, sticky="nsew")

status_label = ctk.CTkLabel(right_frame, text="Current Status: ")
status_label.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

budget_progress = ctk.CTkProgressBar(right_frame)
budget_progress.grid(row=2, column=0, pady=5, padx=10, sticky="ew")
budget_progress.set(0)

# Initialize the GUI with existing data
def initialize_gui():
    """
    Initialize the GUI with existing data from the JSON file.
    """
    data = load_data()
    if 'budget' in data:
        budget_entry.insert(0, format_currency(data['budget']).replace('Rs ', '').replace(',', ''))
    update_transaction_list()
    update_budget_status()

initialize_gui()

# Start the application
app.mainloop()