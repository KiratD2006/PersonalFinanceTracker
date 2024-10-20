import pandas as pd
import csv
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description
import matplotlib.pyplot as plt


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)
            

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added Successfully")
    
    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)
        
        mask = (df["date"] >=start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transaction found in the given date range.")
        else:
            print(f"Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}")
            print(filtered_df.to_string(index=False, formatters={"date": lambda x: x.strftime(CSV.FORMAT)}))

            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            print("\nSummary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Savings: ${(total_income - total_expense):.2f}")

        return filtered_df 

def add():
    CSV.initialize_csv()
    date = get_date("Enter the date of the transaction (dd-mm-yyyy) or enter for today's date: ", allow_default=True,)
    amount  = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)

def plot_transactions(df):
    df.set_index('date', inplace=True)

    income_df = df[df["category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0)
    expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()

import matplotlib.pyplot as plt

def dashboard(df):
    # Ensure the 'date' column is in datetime format
    df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)

    # 1. Pie Chart: Breakdown of Expenses by Description
    expense_data = df[df["category"] == "Expense"].groupby("description")["amount"].sum()
    plt.figure(figsize=(6, 6))
    expense_data.plot.pie(autopct='%1.1f%%', legend=False, title="Expenses Breakdown")
    plt.ylabel("")  # Remove default ylabel

    # 2. Bar Chart: Monthly Income and Expense Summary
    df["month"] = df["date"].dt.to_period("M")
    monthly_data = df.groupby(["month", "category"])["amount"].sum().unstack().fillna(0)
    
    plt.figure(figsize=(10, 5))
    monthly_data.plot(kind="bar", stacked=False, ax=plt.gca())
    plt.title("Monthly Income and Expense Summary")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.legend(["Income", "Expense"])

    # 3. Line Graph: Net Savings Over Time
    df["net_savings"] = df.apply(lambda row: row["amount"] if row["category"] == "Income" else -row["amount"], axis=1)
    savings_trend = df.groupby("date")["net_savings"].sum().cumsum()

    plt.figure(figsize=(10, 5))
    plt.plot(savings_trend.index, savings_trend.values, marker="o", linestyle="-", color="b")
    plt.title("Net Savings Over Time")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Savings")
    plt.grid(True)

    # Show all the plots
    plt.tight_layout()
    plt.show()





def main():
    while True:
        print("\n1. Add a new transaction")
        print("2. View transactions and summary within a date range")
        print("3. Exit")
        choice = input("ENTER YOUR CHOICE (1-3): ")

        if choice == "1":
            add()
        elif choice == "2":
            start_date =get_date("Enter the start date (dd-mm-yyyy):  ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
            if input("Do you want to see a plot? (y/n) ").lower() == "y":
                plot_transactions(df)
            if input("Do you want to see a dashboard? (y/n) ").lower() == "y":
                dashboard(df)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Enter1, 2, or 3.")

if __name__ == "__main__":
    main()

# 1. reads a line from the CIBC CSV file
# 2. reads the info in between the first and second comma, ignores any numbers in the info
# 3. checks to see if the info matches any already existing transaction types
# 4. if there are no existing transaction types that match, promts the user for an transaction type
# 5. if there is an already existing transaction type moves onto the next line