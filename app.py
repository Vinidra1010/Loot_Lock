import streamlit as st
import pandas as pd
import altair as alt

# Define a function to load data from the CSV file
def load_data():
    try:
        data = pd.read_csv("loot_lock_data.csv")
    except FileNotFoundError:
        data = pd.DataFrame(columns=["Month", "Income", "Food", "Transport", "Bills", "Entertainment",
                                     "Shopping", "Subscriptions", "Healthcare", "Education", "Other",
                                     "Total Expenses", "Savings"])
    return data

# Define a function to save data to the CSV file
def save_data(data):
    data.to_csv("loot_lock_data.csv", index=False)

# Set the page configuration
st.set_page_config(page_title="LootLock", page_icon="💰", layout="centered")

# Title and description
st.markdown("<h1 style='text-align: center; color: black;'> - Budget Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Track your expenses, save more, and stay on top of your budget!</p>", unsafe_allow_html=True)

# User input section for income
income = st.number_input("**Enter your monthly income**", min_value=0, value=3000, step=50, help="Your total monthly income")

# Expense categories and input fields with styled text boxes
st.subheader("**Enter your expenses for each category**")

# CSS styling for textboxes (category labels inside a box)
textbox_style = """
    <style>
        .textbox {
            padding: 10px;
            margin: 10px;
            border-radius: 5px;
            border: 2px solid black;
            background-color: #F8E1E1;
            font-size: 16px;
            width: 100%;
        }
        .textbox:focus {
            outline: none;
            border-color: #FF69B4;
        }
        .textbox-label {
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            background-color: #FFB6C1;
            border-radius: 5px;
            color: white;
        }
    </style>
"""
st.markdown(textbox_style, unsafe_allow_html=True)

# Define the categories as a list to loop through
categories = [
    "Food", "Transport", "Bills", "Entertainment", "Shopping",
    "Subscriptions", "Healthcare", "Education", "Other"
]

# Create textboxes for each category using a loop
expenses = {}

# Initialize session state if not already set
for category in categories:
    if category not in st.session_state:
        st.session_state[category] = "0"  # Initialize session state with default value of "0"

    with st.expander(f"**{category}**", expanded=True):
        expense = st.text_input("", key=category, placeholder=f"Enter {category.lower()} expenses")
        expenses[category] = float(st.session_state[category]) if st.session_state[category] else 0

# Calculate total expenses and savings
total_expenses = sum(expenses.values())
remaining = income - total_expenses

# Display the total expenses and savings
st.markdown(f"### **Total Expenses: ${total_expenses}**")
st.markdown(f"### **Savings: ${remaining}**")

# Save data locally
data = load_data()

# New entry for the month
new_entry = {
    "Month": pd.to_datetime("today").strftime('%B %Y'),
    "Income": income,
    **expenses,
    "Total Expenses": total_expenses,
    "Savings": remaining
}

# Convert the new entry into a DataFrame
new_entry_df = pd.DataFrame([new_entry])

# Concatenate the new entry with the existing data
data = pd.concat([data, new_entry_df], ignore_index=True)

# Save the updated data back to CSV
save_data(data)

# Display the data as a table
st.subheader("**Your Expense Data**")
st.dataframe(data)

# Pie chart for category-wise expense split
expense_data = {
    "Category": categories,
    "Amount": [expenses[category] for category in categories]
}

df_expenses = pd.DataFrame(expense_data)

pie_chart = alt.Chart(df_expenses).mark_arc().encode(
    theta=alt.Theta(field="Amount", type="quantitative"),
    color=alt.Color(field="Category", type="nominal"),
    tooltip=["Category", "Amount"]
).properties(width=500, height=400)

st.altair_chart(pie_chart, use_container_width=True)

# Bar chart for expense categories
bar_chart = alt.Chart(df_expenses).mark_bar().encode(
    x="Category:N",
    y="Amount:Q",
    color="Category:N",
    tooltip=["Category", "Amount"]
).properties(width=600, height=400)

st.altair_chart(bar_chart, use_container_width=True)

# Button to download data as CSV
csv = data.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="loot_lock_data.csv",
    mime="text/csv",
)
expenses = {}

