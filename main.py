import os
import matplotlib.pyplot as plt
from datetime import datetime

# Directory for storing budgets
DATA_DIR = "../../../PycharmProjects/budget_tracker/budgets"
SALARY_FILE = "../../../PycharmProjects/budget_tracker/salary.txt"
INCOME_FILE = "../../../PycharmProjects/budget_tracker/income_log.txt"

# Ensure that the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def parse_amount(text):
    """
    Parses a string amount (e.g., '10 000') and converts it to a float.

    Args:
    - text (str): The string representation of the amount, potentially with spaces.

    Returns:
    - float: The parsed amount as a float.
    """
    return float(text.replace(" ", ""))


def set_salary():
    """
    Prompts the user to input their base monthly salary and stores it in a file.
    If the input is invalid, it will prompt the user to try again.
    """
    try:
        # Asking for the salary input and parsing it
        amount = parse_amount(input("Enter your base monthly salary: $"))
        # Save the salary to a file
        with open(SALARY_FILE, "w") as f:
            f.write(str(amount))
        print("Base salary updated.")
    except ValueError:
        print("Invalid input. Try again.")


def view_salary():
    """
    Displays the user's current base monthly salary from the saved file.
    If no salary is recorded, informs the user that there is no salary set.
    """
    try:
        with open(SALARY_FILE, "r") as f:
            salary = parse_amount(f.read())
            print(f"Your current base monthly salary is: ${salary:,.2f}")
    except (FileNotFoundError, ValueError):
        print("No salary recorded yet.")


def log_side_income():
    """
    Prompts the user to log side income from a specified source (e.g., tutoring or freelance work).
    The data is appended to a file with the current date.
    """
    try:
        # User input for source and amount of side income
        source = input("Enter source of side income (e.g. tutoring, freelance): ").strip()
        amount = parse_amount(input("Enter income amount: $"))
        # Append side income to the income log file
        with open(INCOME_FILE, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d')},{source},{amount}\n")
        print("Side income logged.")
    except ValueError:
        print("Invalid amount. Try again.")


def view_total_income():
    """
    Displays the total monthly income, including both base salary and any side income.
    It sums the income from the salary file and side income log.
    """
    base_salary = 0.0
    side_income = 0.0
    try:
        with open(SALARY_FILE, "r") as f:
            base_salary = parse_amount(f.read())
    except (FileNotFoundError, ValueError):
        pass
    try:
        with open(INCOME_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    try:
                        side_income += parse_amount(parts[2])
                    except ValueError:
                        continue
    except FileNotFoundError:
        pass
    total_income = base_salary + side_income
    print(f"\n💰 Income Summary:")
    print(f"- Base Salary: ${base_salary:,.2f}")
    print(f"- Side Income: ${side_income:,.2f}")
    print(f"- Total Monthly Income: ${total_income:,.2f}")


def add_budget():
    """
    Allows the user to create a new budget by providing a name and a monthly spending limit.
    The budget is saved to a text file, and the user is notified if the budget already exists.
    """
    name = input("Enter a name for your new budget: ").strip().lower()
    if not name:
        print("Budget name cannot be empty.")
        return
    budget_file = os.path.join(DATA_DIR, f"{name}.txt")
    if os.path.exists(budget_file):
        print("This budget already exists.")
        return
    try:
        limit = parse_amount(input("Enter monthly budget limit for this budget: $"))
        with open(budget_file, "w") as f:
            f.write(f"#LIMIT:{limit}\n")
        print(f"Budget '{name}' created with a limit of ${limit:,.2f}.")
    except ValueError:
        print("Invalid amount. Try again.")


def add_expense():
    """
    Allows the user to add an expense to an existing budget by specifying the budget name,
    category, and the amount. If the total expenses exceed the budget limit, a warning is displayed.
    """
    budget_name = input("Enter the budget name: ").strip().lower()
    budget_file = os.path.join(DATA_DIR, f"{budget_name}.txt")
    if not os.path.exists(budget_file):
        print("This budget does not exist.")
        return
    try:
        category = input("Enter category (Food, Transport, etc): ")
        amount = parse_amount(input("Enter amount: $"))
    except ValueError:
        print("Invalid amount. Try again.")
        return

    with open(budget_file, "r") as f:
        lines = f.readlines()

    try:
        limit_line = next(line for line in lines if line.startswith("#LIMIT:"))
        limit = float(limit_line.strip().split(":")[1])
    except (StopIteration, ValueError):
        print("Could not read budget limit.")
        return

    expenses = [line for line in lines if not line.startswith("#")]
    total = sum(float(line.strip().split(",")[2]) for line in expenses)
    if total + amount > limit:
        print(f"⚠️ Warning: You are about to exceed the budget limit of ${limit:,.2f}.")
    else:
        print(f"Your remaining budget: ${limit - (total + amount):,.2f}")

    with open(budget_file, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d')},{category},{amount}\n")
    print("Expense added.")


def view_summary():
    """
    Displays a summary of all expenses for a specific budget.
    The summary includes the total spent in each category and a pie chart visualization of expenses.
    """
    budget_name = input("Enter budget name to view summary: ").strip().lower()
    budget_file = os.path.join(DATA_DIR, f"{budget_name}.txt")
    if not os.path.exists(budget_file):
        print("This budget does not exist.")
        return

    with open(budget_file, "r") as f:
        lines = f.readlines()

    expenses = {}
    for line in lines:
        if line.startswith("#"):
            continue
        parts = line.strip().split(",")
        if len(parts) != 3:
            continue
        _, category, amount = parts
        try:
            amount = float(amount)
        except ValueError:
            continue
        expenses[category] = expenses.get(category, 0) + amount

    if not expenses:
        print("No expenses found.")
        return

    print("\n📊 Expense Summary:")
    for cat, amt in expenses.items():
        print(f"- {cat}: ${amt:,.2f}")

    plt.figure(figsize=(6, 6))
    plt.pie(expenses.values(), labels=expenses.keys(), autopct='%1.1f%%', startangle=140)
    plt.title(f"Expense Breakdown - {budget_name.capitalize()}")
    plt.axis("equal")
    plt.show()


def view_overall_expense_summary():
    """
    Displays a summary of all expenses across all budgets, broken down by category.
    The function generates a pie chart showing the distribution of expenses by category.
    """
    total_by_category = {}
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".txt"):
            continue
        with open(os.path.join(DATA_DIR, filename), "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.strip().split(",")
                if len(parts) != 3:
                    continue
                _, category, amount = parts
                try:
                    amount = float(amount)
                except ValueError:
                    continue
                total_by_category[category] = total_by_category.get(category, 0) + amount

    if not total_by_category:
        print("No expenses found across all budgets.")
        return

    print("\n📊 Overall Expense Summary:")
    for cat, amt in total_by_category.items():
        print(f"- {cat}: ${amt:,.2f}")

    # Ensure labels are strings
    labels = list(map(str, total_by_category.keys()))

    plt.figure(figsize=(6, 6))
    plt.pie(total_by_category.values(), labels=total_by_category.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("Overall Expense Breakdown")
    plt.axis("equal")
    plt.show()


def menu():
    """
    Displays the main menu of the application, prompting the user to choose an action.
    This function runs in a loop until the user chooses to exit the program.
    """
    while True:
        print("\n💼 Loot Lock - Budget Tracker")
        print("1. Add Budget")
        print("2. Add Expense")
        print("3. View Budget Summary")
        print("4. Set Base Salary")
        print("5. View Base Salary")
        print("6. Log Side Income")
        print("7. View Total Monthly Income")
        print("8. View Overall Expense Summary")
        print("9. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            add_budget()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            view_summary()
        elif choice == "4":
            set_salary()
        elif choice == "5":
            view_salary()
        elif choice == "6":
            log_side_income()
        elif choice == "7":
            view_total_income()
        elif choice == "8":
            view_overall_expense_summary()
        elif choice == "9":
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    menu()
































