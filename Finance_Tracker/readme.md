# Personal Finance Tracker

## Description
This Personal Finance Tracker is a desktop application built with Python and CustomTkinter. It allows users to track their expenses, set budgets, and manage their financial transactions with ease. The application provides a user-friendly interface for adding, viewing, and analyzing personal financial data.

## Features
- Add and view transactions with date, amount, and description
- Set and track monthly budgets
- View current spending status and remaining budget
- Import transactions from JSON or Excel files
- Export transactions to Excel files
- Prevent duplicate transactions during import
- Responsive UI that scales with window size

## Requirements
- Python 3.x
- CustomTkinter
- pandas
- openpyxl

## Installation
1. Clone this repository or download the source code.
2. Install the required packages:
   ```
   pip install customtkinter pandas openpyxl
   ```

## Usage
1. Run the script:
   ```
   python finance_tracker.py
   ```
2. Use the left panel to add transactions and set your budget.
3. View your transactions and budget status in the right panel.
4. Use the Import and Export buttons to manage your data in bulk.

## File Structure
- `finance_tracker.py`: The main Python script containing the application code.
- `data.json`: JSON file where transactions and budget data are stored.

## Functions
- `load_data()`: Load transaction and budget data from the JSON file.
- `save_data(data)`: Save data to the JSON file.
- `add_transaction(date, amount, description)`: Add a new transaction.
- `import_transactions()`: Import transactions from JSON or Excel files.
- `export_to_excel()`: Export transactions to an Excel file.
- `update_budget_status()`: Update the budget display and progress bar.

## UI Components
- Left Frame:
  - Input fields for date, amount, and description
  - Buttons for adding transactions, setting budget, importing, and exporting data
- Right Frame:
  - Text box displaying all transactions
  - Label showing current budget status
  - Progress bar indicating budget usage

## Data Storage
Transactions and budget information are stored in a `data.json` file in the following format:
```json
{
  "transactions": [
    {
      "date": "DD-MM-YYYY",
      "amount": 100.00,
      "description": "Sample transaction"
    }
  ],
  "budget": 1000.00
}
```

## Customization
- The currency format is set to Pakistani Rupees (Rs). Modify the `format_currency()` function to change this.
- The date format is DD-MM-YY. Adjust the `format_date()` function if a different format is preferred.

## License
This project is open-source and available under the MIT License.