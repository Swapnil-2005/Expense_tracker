import sys
import matplotlib.pyplot as plt
import pandas as pd  # For saving data to Excel
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate, QDateTime, QTimer


class ExpenseTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(200, 200, 800, 600)

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Expense input section
        self.amount_label = QLabel("Amount (₹):")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")

        self.category_label = QLabel("Category:")
        self.category_input = QComboBox()
        self.category_input.addItems(["Food", "Travel", "Utilities", "Entertainment", "Others"])

        self.custom_category_label = QLabel("Custom Category:")
        self.custom_category_input = QLineEdit()
        self.custom_category_label.hide()
        self.custom_category_input.hide()

        # Connect category input to show/hide custom category
        self.category_input.currentTextChanged.connect(self.toggle_custom_category)

        self.date_label = QLabel("Date of Entry:")
        self.date_input = QLabel(QDate.currentDate().toString("dd/MM/yyyy"))
        self.date_input.setStyleSheet("background-color: lightgray; padding: 4px;")

        self.time_label = QLabel("Time of Entry:")
        self.time_input = QLabel(QDateTime.currentDateTime().toString("HH:mm:ss"))
        self.time_input.setStyleSheet("background-color: lightgray; padding: 4px;")

        # Add a QTimer to update time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every 1000 ms (1 second)

        self.add_button = QPushButton("Add Expense")
        self.add_button.clicked.connect(self.add_expense)

        # Input layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.amount_label)
        input_layout.addWidget(self.amount_input)
        input_layout.addWidget(self.category_label)
        input_layout.addWidget(self.category_input)
        input_layout.addWidget(self.custom_category_label)
        input_layout.addWidget(self.custom_category_input)
        input_layout.addWidget(self.date_label)
        input_layout.addWidget(self.date_input)
        input_layout.addWidget(self.time_label)
        input_layout.addWidget(self.time_input)
        input_layout.addWidget(self.add_button)
        self.layout.addLayout(input_layout)

        # Expense table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Adjusted to include time
        self.table.setHorizontalHeaderLabels(["Amount", "Category", "Date", "Time"])
        self.layout.addWidget(self.table)

        # Buttons for data handling
        self.save_excel_button = QPushButton("Save as Excel")  # New button for saving as Excel
        self.save_excel_button.clicked.connect(self.save_as_excel)
        self.plot_button = QPushButton("Generate Report")
        self.plot_button.clicked.connect(self.generate_report)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_excel_button)  # Add Save as Excel button
        button_layout.addWidget(self.plot_button)
        self.layout.addLayout(button_layout)

        # Expense data
        self.expenses = []

    def toggle_custom_category(self, category):
        """Show or hide custom category input based on selection."""
        if category == "Others":
            self.custom_category_label.show()
            self.custom_category_input.show()
        else:
            self.custom_category_label.hide()
            self.custom_category_input.hide()
            self.custom_category_input.clear()

    def add_expense(self):
        """Add an expense to the table and list."""
        try:
            amount = float(self.amount_input.text())
            category = self.category_input.currentText()

            # If "Others" is selected, use the custom category
            if category == "Others":
                custom_category = self.custom_category_input.text().strip()
                if not custom_category:
                    QMessageBox.warning(self, "Input Error", "Please specify a custom category for 'Others'.")
                    return
                category = custom_category

                # Add custom category to the dropdown if not already present
                if custom_category not in [self.category_input.itemText(i) for i in range(self.category_input.count())]:
                    self.category_input.addItem(custom_category)

            # Date and Time of Entry (non-editable)
            date = self.date_input.text()
            time = self.time_input.text()

            # Append to the expenses list
            self.expenses.append({"amount": amount, "category": category, "date": date, "time": time})

            # Add data to table
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f"₹{amount:.2f}"))
            self.table.setItem(row, 1, QTableWidgetItem(category))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            self.table.setItem(row, 3, QTableWidgetItem(time))

            # Clear inputs
            self.amount_input.clear()
            self.custom_category_input.clear()

        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")

    def save_as_excel(self):
        """Save expense data to an Excel file."""
        if not self.expenses:
            QMessageBox.warning(self, "No Data", "No expenses to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save as Excel", "", "Excel Files (*.xlsx)")
        if file_path:
            df = pd.DataFrame(self.expenses)
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Success", "Data saved as Excel successfully!")

    def generate_report(self):
        """Generate a pie chart for expense categories."""
        categories = {}
        for expense in self.expenses:
            category = expense["category"]
            categories[category] = categories.get(category, 0) + expense["amount"]

        if not categories:
            QMessageBox.warning(self, "No Data", "No expenses to generate a report.")
            return

        y = list(categories.keys())
        x = list(categories.values())

        plt.figure(figsize=(8, 6))
        plt.pie(x, labels=y, autopct='%1.1f%%', startangle=140,shadow=True)
        plt.title("Expense Distribution")
        plt.show()

    def update_time(self):
        """Update the time label every second."""
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.time_input.setText(current_time)


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec_())
