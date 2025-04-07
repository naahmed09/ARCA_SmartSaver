"""
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def read_csv_data_list(file_path):
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            data.append(header)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        messagebox.showerror("Error", f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: An error occurred while reading '{file_path}': {e}")
        messagebox.showerror("Error", f"An error occurred while reading '{file_path}': {e}")
        return None
    return data


def write_csv_data(file_path, data):
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error writing to '{file_path}': {e}")
        messagebox.showerror("Error", f"Error writing to '{file_path}': {e}")
        return False


def sort_data_by_date(data):
    if not data or len(data) < 2:
        return data
    header = data[0]
    data_rows = data[1:]
    date_column_index = -1
    if "Date" in header:
        date_column_index = header.index("Date")
    elif "date" in header:
        date_column_index = header.index("date")

    if date_column_index != -1:
        def parse_date(row):
            try:
                return datetime.strptime(row[date_column_index], '%m/%d/%Y')
            except ValueError:
                return datetime.min  # Handle cases with incorrect date format

        sorted_data = sorted(data_rows, key=parse_date, reverse=True)
        return [header] + sorted_data
    else:
        print("Warning: 'Date' column not found. Data will not be sorted.")
        return data


def get_available_months_years(data):
    if not data or len(data) < 2:
        return [], []
    header = data[0]
    date_index = -1
    if "Date" in header:
        date_index = header.index("Date")
    elif "date" in header:
        date_index = header.index("date")

    if date_index == -1:
        return [], []

    months = set()
    years = set()
    for row in data[1:]:
        try:
            date_str = row[date_index]
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            months.add(date_obj.strftime('%Y-%m'))
            years.add(str(date_obj.year))
        except ValueError:
            pass
    return sorted(list(months), reverse=True), sorted(list(years), reverse=True)


def get_available_weeks(data):
    if not data or len(data) < 2:
        return []
    header = data[0]
    date_index = -1
    if "Date" in header:
        date_index = header.index("Date")
    elif "date" in header:
        date_index = header.index("date")

    if date_index == -1:
        return []

    weeks = set()
    for row in data[1:]:
        try:
            date_str = row[date_index]
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            year, week, _ = date_obj.isocalendar()
            weeks.add(f'{year}-W{week:02d}')
        except ValueError:
            pass
    return sorted(list(weeks), reverse=True)


def analyze_spending(data, start_date, end_date, category_col="Category", amount_col="Cost", date_col="Date"):
    if not data or len(data) < 2:
        return None

    header = data[0]
    try:
        category_index = header.index(category_col)
        amount_index = header.index(amount_col)
        date_index = header.index(date_col)
    except ValueError:
        messagebox.showerror("Error", f"Could not find '{category_col}', '{amount_col}', and '{date_col}' columns.")
        return None

    spending_by_category = {}

    for row in data[1:]:
        try:
            date_str = row[date_index]
            row_date = datetime.strptime(date_str, '%m/%d/%Y')
            if start_date <= row_date < end_date:
                category = row[category_index].strip()
                amount_str = str(row[amount_index]).replace('$', '').replace(',', '').strip()
                try:
                    amount = float(amount_str)
                    spending_by_category[category] = spending_by_category.get(category, 0) + amount
                except ValueError:
                    print(f"Warning: Could not parse amount '{row[amount_index]}'")
        except ValueError:
            print(f"Warning: Could not parse date '{row[date_index]}'")
        except IndexError:
            print("Warning: Incomplete row found.")

    return spending_by_category


def show_pie_chart(parent_frame, title, spending):
    chart_window = tk.Toplevel(parent_frame)
    chart_window.title(title)
    chart_window.geometry("500x600")

    if not spending:
        ttk.Label(chart_window, text=f"No data found for {title}.").pack(pady=20)
        close_button = ttk.Button(chart_window, text="Close Chart", command=chart_window.destroy)
        close_button.pack(pady=10)
        return

    categories = spending.keys()
    amounts = list(spending.values())
    total_spent = sum(amounts)

    if not categories:
        ttk.Label(chart_window, text=f"No categories found for {title}.").pack(pady=20)
        close_button = ttk.Button(chart_window, text="Close Chart", command=chart_window.destroy)
        close_button.pack(pady=10)
        return

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(amounts, labels=categories,
                                      autopct=lambda p: f'{p:.1f}% (${total_spent * p / 100:.2f})', startangle=140)
    ax.axis('equal')
    ax.set_title(title)

    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    close_button = ttk.Button(chart_window, text="Close Chart", command=chart_window.destroy)
    close_button.pack(pady=10)



def create_charts_tab(parent_window, data, tab_name, analyze_func_kwargs):
    charts_frame = ttk.Frame(parent_window, padding=10)

    # --- Month Selection ---
    available_months, _ = get_available_months_years(data)
    selected_month = tk.StringVar(charts_frame)
    selected_month.set(available_months[0] if available_months else "")

    month_label = ttk.Label(charts_frame, text="Select Month:")
    month_label.pack(pady=5)
    month_dropdown = ttk.Combobox(charts_frame, textvariable=selected_month, values=available_months, state="readonly")
    month_dropdown.pack(pady=5)

    def show_monthly_chart():
        if selected_month.get():
            year, month = map(int, selected_month.get().split('-'))
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            spending = analyze_spending(data, start_date, end_date, **analyze_func_kwargs)
            show_pie_chart(charts_frame, f"Monthly {tab_name} - {selected_month.get()}", spending)

    month_button = ttk.Button(charts_frame, text=f"Show Monthly {tab_name} Chart", command=show_monthly_chart)
    month_button.pack(pady=5)

    # --- Year Selection ---
    _, available_years = get_available_months_years(data)
    selected_year = tk.StringVar(charts_frame)
    selected_year.set(available_years[0] if available_years else "")

    year_label = ttk.Label(charts_frame, text="Select Year:")
    year_label.pack(pady=5)
    year_dropdown = ttk.Combobox(charts_frame, textvariable=selected_year, values=available_years, state="readonly")
    year_dropdown.pack(pady=5)

    def show_yearly_chart():
        if selected_year.get():
            year = int(selected_year.get())
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            spending = analyze_spending(data, start_date, end_date, **analyze_func_kwargs)
            show_pie_chart(charts_frame, f"Yearly {tab_name} - {selected_year.get()}", spending)

    year_button = ttk.Button(charts_frame, text=f"Show Yearly {tab_name} Chart", command=show_yearly_chart)
    year_button.pack(pady=5)

    # --- Week Selection ---
    available_weeks = get_available_weeks(data)
    selected_week = tk.StringVar(charts_frame)
    selected_week.set(available_weeks[0] if available_weeks else "")

    week_label = ttk.Label(charts_frame, text="Select Week:")
    week_label.pack(pady=5)
    week_dropdown = ttk.Combobox(charts_frame, textvariable=selected_week, values=available_weeks, state="readonly")
    week_dropdown.pack(pady=5)

    def show_weekly_chart():
        if selected_week.get():
            year_str, week_str = selected_week.get().split('-W')
            year = int(year_str)
            week = int(week_str)
            start_date = datetime.fromisocalendar(year, week, 1)
            end_date = start_date + timedelta(days=7)
            spending = analyze_spending(data, start_date, end_date, **analyze_func_kwargs)
            show_pie_chart(charts_frame, f"Weekly {tab_name} - {selected_week.get()}", spending)

    week_button = ttk.Button(charts_frame, text=f"Show Weekly {tab_name} Chart", command=show_weekly_chart)
    week_button.pack(pady=5)

    return charts_frame


def create_add_entry_tab(parent_window, expense_data, income_data, expense_file, income_file):
    add_frame = ttk.Frame(parent_window, padding=10)

    entry_type_label = ttk.Label(add_frame, text="Entry Type:")
    entry_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_type_var = tk.StringVar(add_frame)
    entry_type_var.set("Expense")  # Default value
    entry_type_dropdown = ttk.Combobox(add_frame, textvariable=entry_type_var, values=["Expense", "Income"],
                                       state="readonly")
    entry_type_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    category_label = ttk.Label(add_frame, text="Category:")
    category_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    category_var = tk.StringVar(add_frame)
    category_dropdown = ttk.Combobox(add_frame, textvariable=category_var, values=[], state="readonly")
    category_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    date_label = ttk.Label(add_frame, text="Date (MM/DD/YYYY):")
    date_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    date_entry = ttk.Entry(add_frame)
    date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    amount_label = ttk.Label(add_frame, text="Amount:")
    amount_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    amount_entry = ttk.Entry(add_frame)
    amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    necessity_label = ttk.Label(add_frame, text="Necessity:")
    necessity_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    necessity_var = tk.StringVar(add_frame)
    necessity_var.set("Yes")
    necessity_dropdown = ttk.Combobox(add_frame, textvariable=necessity_var, values=["Yes", "No"], state="readonly")
    necessity_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    def update_categories(*args):
        entry_type = entry_type_var.get()
        if entry_type == "Expense" and expense_data and len(expense_data) > 0:
            categories = sorted(list(set([row[expense_data[0].index("Category")] for row in expense_data[1:] if
                                          "Category" in expense_data[0]])))
            category_dropdown['values'] = categories
            if categories:
                category_var.set(categories[0])
            else:
                category_var.set("")
            necessity_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
            necessity_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        elif entry_type == "Income" and income_data and len(income_data) > 0:
            categories = ["Work","Misc", "Refund"]  # Set income categories
            category_dropdown['values'] = categories
            if categories:
                category_var.set(categories[0])
            else:
                category_var.set("")
            necessity_label.grid_forget()
            necessity_dropdown.grid_forget()
        else:
            category_dropdown['values'] = []
            category_var.set("")
            necessity_label.grid_forget()
            necessity_dropdown.grid_forget()

    entry_type_var.trace_add("write", update_categories)
    update_categories()  # Initial update

    def add_new_entry():
        entry_type = entry_type_var.get()
        category = category_var.get()
        date_str = date_entry.get()
        amount_str = amount_entry.get()
        necessity = necessity_var.get()

        try:
            datetime.strptime(date_str, '%m/%d/%Y')
            amount = float(amount_str.replace('$', '').replace(',', '').strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format (MM/DD/YYYY) or Amount.")
            return

        if not category:
            messagebox.showerror("Error", "Category cannot be empty.")
            return

        if entry_type == "Expense":
            # Read existing expense data
            existing_expense_data = read_csv_data_list(expense_file)
            headers = existing_expense_data[0] if existing_expense_data else ["Date", "Category", "Cost", "Necessity"]
            new_row = [date_str, category, amount, necessity]
            if not existing_expense_data:
                expense_data = [headers, new_row]
            else:
                expense_data = existing_expense_data + [new_row]  # Append the new row
            if write_csv_data(expense_file, expense_data):
                messagebox.showinfo("Success", "Expense added successfully.")
                # Clear the fields after successful addition
                date_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                update_categories()  # Reset the category dropdown
            else:
                messagebox.showerror("Error", "Failed to add expense.")

        elif entry_type == "Income":
            # Read existing income data
            existing_income_data = read_csv_data_list(income_file)
            headers = existing_income_data[0] if existing_income_data else ["Date", "Category", "Amount"]
            new_row = [date_str, category, amount]
            if not existing_income_data:
                income_data = [headers, new_row]
            else:
                income_data = existing_income_data + [new_row]  # Append new row
            if write_csv_data(income_file, income_data):
                messagebox.showinfo("Success", "Income added successfully.")
                date_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                update_categories()
            else:
                messagebox.showerror("Error", "Failed to add income.")
        return True

    add_button = ttk.Button(add_frame, text="Add Entry", command=add_new_entry)
    add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    for child in add_frame.winfo_children():
        child.grid_configure(sticky='ew')
    add_frame.columnconfigure(1, weight=1)

    return add_frame


def display_data_in_treeview(parent_window, data, title, has_filter_and_sort=False):
    # Use the parent_window provided, don't create a new Toplevel
    # window = tk.Toplevel(parent_window) # Removed this line
    parent_window.title(title)  # Use parent_window
    parent_window.geometry("800x600")

    # --- Frame for filter and sort controls ---
    if has_filter_and_sort:
        filter_sort_frame = ttk.Frame(parent_window) # Use parent_window
        filter_sort_frame.pack(pady=10, fill="x")

        tree_frame = ttk.Frame(parent_window)  # Frame for the Treeview # Use parent_window
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    else:
        tree_frame = ttk.Frame(parent_window) # Use parent_window
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    tree = ttk.Treeview(tree_frame)

    if data and data[0]:
        tree["columns"] = data[0]
        for col_index, col in enumerate(data[0]):
            tree.heading(col, text=col, anchor=tk.CENTER)

        # Calculate max width for each column based on header and data
        column_widths = [0] * len(data[0])
        for i, header_name in enumerate(data[0]):
            column_widths[i] = max(column_widths[i], len(header_name) * 8)  # 8 pixels per char

        for row in data[1:]:
            for i, cell_value in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(cell_value)) * 8)

        # Apply the calculated widths with a minimum width of 100
        for i, col in enumerate(data[0]):
            tree.column(col, width=max(100, column_widths[i]), anchor=tk.CENTER)
        tree.column("#0", width=0, stretch=tk.NO)

        for row in data[1:]:
            tree.insert("", tk.END, values=row)
    elif data is None:
        pass
    else:
        messagebox.showinfo("Info", f"No {title} data to display or the CSV file is empty.")

    tree.pack(fill="both", expand=True)

    if has_filter_and_sort:
        return tree, parent_window, filter_sort_frame # Return parent_window
    else:
        return tree, parent_window # Return parent_window



def open_expenses(parent, data=None): # added parent and data
    global expense_window, tree_expenses
    if not hasattr(globals(), 'expense_window') or not tk.Toplevel.winfo_exists(expense_window):
        expense_window = tk.Toplevel(parent)
        expense_window.title("Expenses")
        expense_window.geometry("800x600")
        expense_window.iconbitmap("ss.ico")
        if data is None:
            expense_data = read_csv_data_list(expense_file)
        else:
            expense_data = data
        sorted_expense_data = sort_data_by_date(expense_data) if expense_data else []
        tree_expenses, expense_window, expense_filter_sort_frame = display_data_in_treeview(expense_window,
                                                                                           sorted_expense_data,
                                                                                           "Expenses",
                                                                                           True)

        # --- Expense Category Filter ---
        expense_category_label = ttk.Label(expense_filter_sort_frame, text="Filter by Category:")
        expense_category_label.pack(pady=5)
        expense_categories = ["All"] + sorted(list(
            set([row[expense_data[0].index("Category")] for row in expense_data[1:] if
                 "Category" in expense_data[0]]))) if expense_data and len(expense_data) > 1 else ["All"]
        expense_category_var = tk.StringVar(expense_filter_sort_frame)
        expense_category_var.set("All")
        expense_category_dropdown = ttk.Combobox(expense_filter_sort_frame, textvariable=expense_category_var,
                                                 values=expense_categories, state="readonly")
        expense_category_dropdown.pack(pady=5)

        # --- Expense Sorting ---
        expense_sort_label = ttk.Label(expense_filter_sort_frame, text="Sort by:")
        expense_sort_label.pack(pady=5)
        expense_sort_var = tk.StringVar(expense_filter_sort_frame)
        expense_sort_var.set("Date: Most Recent to Least Recent")  # Default sort option
        expense_sort_options = [
            "Date: Most Recent to Least Recent",
            "Date: Least Recent to Most Recent",
            "Price: High to Low",
            "Price: Low to High"
        ]
        expense_sort_dropdown = ttk.Combobox(expense_filter_sort_frame, textvariable=expense_sort_var,
                                               values=expense_sort_options, state="readonly")
        expense_sort_dropdown.pack(pady=5)

        def update_expense_treeview():
            # Clear existing data in the Treeview
            for item in tree_expenses.get_children():
                tree_expenses.delete(item)

            # Read the updated data from the CSV files
            updated_expense_data = read_csv_data_list(expense_file) if data is None else data

            # Sort the data
            sorted_expense_data = sort_data_by_date(updated_expense_data) if updated_expense_data else []

            # --- Expense Sorting Logic ---
            selected_expense_sort = expense_sort_var.get()
            if selected_expense_sort == "Date: Most Recent to Least Recent":
                sorted_expense_data = sort_data_by_date(updated_expense_data) if updated_expense_data else []
            elif selected_expense_sort == "Date: Least Recent to Most Recent":
                sorted_expense_data = sort_data_by_date(updated_expense_data) if updated_expense_data else []
                if sorted_expense_data and len(sorted_expense_data) > 1:
                    sorted_expense_data = [sorted_expense_data[0]] + list(reversed(sorted_expense_data[1:]))
            elif selected_expense_sort == "Price: High to Low":
                if updated_expense_data and len(updated_expense_data) > 1:
                    try:
                        sorted_expense_data = [updated_expense_data[0]] + sorted(updated_expense_data[1:],
                                                                                 key=lambda x: float(str(x[
                                                                                                                            updated_expense_data[
                                                                                                                                0].index(
                                                                                                                                "Cost")]).replace(
                                                                                                    '$',
                                                                                                    '').replace(',',
                                                                                                                 '').strip()),
                                                                                 reverse=True)
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format. Please ensure 'Cost' is a valid number.")
                        sorted_expense_data = updated_expense_data
            elif selected_expense_sort == "Price: Low to High":
                if updated_expense_data and len(updated_expense_data) > 1:
                    try:
                        sorted_expense_data = [updated_expense_data[0]] + sorted(updated_expense_data[1:],
                                                                                 key=lambda x: float(str(x[
                                                                                                                            updated_expense_data[
                                                                                                                                0].index(
                                                                                                                                "Cost")]).replace(
                                                                                                    '$',
                                                                                                    '').replace(',',
                                                                                                                 '').strip()))
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format. Please ensure 'Cost' is a valid number.")
                        sorted_expense_data = updated_expense_data

            # Repopulate the Treeviews with the updated data
            if sorted_expense_data and sorted_expense_data[0]:
                tree_expenses["columns"] = sorted_expense_data[0]
                # Clear old headers
                for col in tree_expenses["columns"]:
                    tree_expenses.heading(col, text=col, anchor=tk.CENTER)

                # Calculate max width for each column based on header and data
                column_widths = [0] * len(sorted_expense_data[0])
                for i, header_name in enumerate(sorted_expense_data[0]):
                    column_widths[i] = max(column_widths[i], len(header_name) * 8)  # 8 pixels per char

                for row in sorted_expense_data[1:]:
                    for i, cell_value in enumerate(row):
                        column_widths[i] = max(column_widths[i], len(str(cell_value)) * 8)

                # Apply the calculated widths with a minimum width of 100
                for i, col in enumerate(sorted_expense_data[0]):
                    tree_expenses.column(col, width=max(100, column_widths[i]), anchor=tk.CENTER)
                tree_expenses.column("#0", width=0, stretch=tk.NO)

                filtered_expense_data = sorted_expense_data[1:]
                selected_expense_category = expense_category_var.get()  # Get the selected value.
                if selected_expense_category != "All":
                    filtered_expense_data = [row for row in filtered_expense_data if
                                             row[sorted_expense_data[0].index("Category")] == selected_expense_category]
                for row in filtered_expense_data:
                    tree_expenses.insert("", tk.END, values=row)
            expense_window.update()

        expense_category_var.trace_add("write", lambda *args: update_expense_treeview())
        expense_sort_var.trace_add("write", lambda *args: update_expense_treeview())
        return expense_window

    elif tk.Toplevel.winfo_exists(expense_window):
        expense_window.lift()
        return expense_window
    return expense_window



def open_income(parent, data=None): # added parent and data
    global income_window, tree_income
    if not hasattr(globals(), 'income_window') or not tk.Toplevel.winfo_exists(income_window):
        income_window = tk.Toplevel(parent)
        income_window.title("Income")
        income_window.geometry("800x600")
        income_window.iconbitmap("ss.ico")
        if data is None:
            income_data = read_csv_data_list(income_file)
        else:
            income_data = data
        sorted_income_data = sort_data_by_date(income_data) if income_data else []
        tree_income, income_window, income_filter_sort_frame = display_data_in_treeview(income_window, sorted_income_data,
                                                                                       "Income",
                                                                                       True)

        # --- Income Category Filter ---
        income_category_label = ttk.Label(income_filter_sort_frame, text="Filter by Category:")
        income_category_label.pack(pady=5)
        income_categories = ["All", "Work", "Misc", "Refund"]  # Set income categories for the dropdown
        income_category_var = tk.StringVar(income_filter_sort_frame)
        income_category_var.set("All")
        income_category_dropdown = ttk.Combobox(income_filter_sort_frame, textvariable=income_category_var,
                                                values=income_categories, state="readonly")
        income_category_dropdown.pack(pady=5)

        # --- Income Sorting ---
        income_sort_label = ttk.Label(income_filter_sort_frame, text="Sort by:")
        income_sort_label.pack(pady=5)
        income_sort_var = tk.StringVar(income_filter_sort_frame)
        income_sort_var.set("Date: Most Recent to Least Recent")  # Default sort option
        income_sort_options = [
            "Date: Most Recent to Least Recent",
            "Date: Least Recent to Most Recent",
            "Price: High to Low",
            "Price: Low to High"
        ]
        income_sort_dropdown = ttk.Combobox(income_filter_sort_frame, textvariable=income_sort_var,
                                            values=income_sort_options, state="readonly")
        income_sort_dropdown.pack(pady=5)

        def update_income_treeview():
            # Clear existing data in the Treeviews
            for item in tree_income.get_children():
                tree_income.delete(item)

            # Read the updated data from the CSV files
            updated_income_data = read_csv_data_list(income_file) if data is None else data

            # Sort the data
            sorted_income_data = sort_data_by_date(updated_income_data) if updated_income_data else []

            # --- Income Sorting Logic ---
            selected_income_sort = income_sort_var.get()
            if selected_income_sort == "Date: Most Recent to Least Recent":
                sorted_income_data = sort_data_by_date(updated_income_data) if updated_income_data else []
            elif selected_income_sort == "Date: Least Recent to Most Recent":
                sorted_income_data = sort_data_by_date(updated_income_data) if updated_income_data else []
                if sorted_income_data and len(sorted_income_data) > 1:
                    sorted_income_data = [sorted_income_data[0]] + list(reversed(sorted_income_data[1:]))
            elif selected_income_sort == "Price: High to Low":
                if updated_income_data and len(updated_income_data) > 1:
                    try:
                        sorted_income_data = [updated_income_data[0]] + sorted(updated_income_data[1:],
                                                                               key=lambda x: float(str(x[
                                                                                                                           updated_income_data[
                                                                                                                               0].index(
                                                                                                                               "Amount")]).replace(
                                                                                                  '$',
                                                                                                  '').replace(',',
                                                                                                               '').strip()),
                                                                               reverse=True)
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format.  Please ensure 'Amount' is a valid number.")
                        sorted_income_data = updated_income_data
            elif selected_income_sort == "Price: Low to High":
                if updated_income_data and len(updated_income_data) > 1:
                    try:
                        sorted_income_data = [updated_income_data[0]] + sorted(updated_income_data[1:],
                                                                               key=lambda x: float(str(x[
                                                                                                                           updated_income_data[
                                                                                                                               0].index(
                                                                                                                               "Amount")]).replace(
                                                                                                  '$',
                                                                                                  '').replace(',',
                                                                                                               '').strip()))
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format. Please ensure 'Amount' is a valid number.")
                        sorted_income_data = updated_income_data

            # Repopulate the Treeviews with the updated data
            if sorted_income_data and sorted_income_data[0]:
                tree_income["columns"] = sorted_income_data[0]
                for col in tree_income["columns"]:
                    tree_income.heading(col, text=col, anchor=tk.CENTER)

                # Calculate max width for each column
                column_widths = [0] * len(sorted_income_data[0])
                for i, header_name in enumerate(sorted_income_data[0]):
                    column_widths[i] = max(column_widths[i], len(header_name) * 8)  # 8 pixels per char

                for row in sorted_income_data[1:]:
                    for i, cell_value in enumerate(row):
                        column_widths[i] = max(column_widths[i], len(str(cell_value)) * 8)

                # Apply the calculated widths with a minimum width of 100
                for i, col in enumerate(sorted_income_data[0]):
                    tree_income.column(col, width=max(100, column_widths[i]), anchor=tk.CENTER)
                tree_income.column("#0", width=0, stretch=tk.NO)

                filtered_income_data = sorted_income_data[1:]
                selected_income_category = income_category_var.get()  # Get the selected value.
                if selected_income_category != "All":
                    filtered_income_data = [row for row in filtered_income_data if
                                            row[sorted_income_data[0].index("Category")] == selected_income_category]
                for row in filtered_income_data:
                    tree_income.insert("", tk.END, values=row)
            income_window.update()

        income_category_var.trace_add("write", lambda *args: update_income_treeview())
        income_sort_var.trace_add("write", lambda *args: update_income_treeview())
        return income_window
    elif tk.Toplevel.winfo_exists(income_window):
        income_window.lift()
        return income_window
    return income_window



def open_expenses_chart(parent, data=None): # added parent and data
    global expense_chart_window
    if not hasattr(globals(), 'expense_chart_window') or not tk.Toplevel.winfo_exists(expense_chart_window):
        expense_chart_window = tk.Toplevel(parent)
        expense_chart_window.title("Expense Charts")
        expense_chart_window.iconbitmap("ss.ico")
        if data is None:
            expense_data = read_csv_data_list(expense_file)
        else:
            expense_data = data
        expense_chart_frame = create_charts_tab(expense_chart_window, expense_data, "Expenses",
                                                {"category_col": "Category", "amount_col": "Cost",
                                                 "date_col": "Date"})
        expense_chart_frame.pack(fill="both", expand=True)
    elif tk.Toplevel.winfo_exists(expense_chart_window):
        expense_chart_window.lift()

def open_income_chart(parent, data=None): # added parent and data
    global income_chart_window
    if not hasattr(globals(), 'income_chart_window') or not tk.Toplevel.winfo_exists(income_chart_window):
        income_chart_window = tk.Toplevel(parent)
        income_chart_window.title("Income Charts")
        income_chart_window.iconbitmap("ss.ico")
        if data is None:
            income_data = read_csv_data_list(income_file)
        else:
            income_data = data
        income_chart_frame = create_charts_tab(income_chart_window, income_data, "Income",
                                                 {"category_col": "Category", "amount_col": "Amount",
                                                  "date_col": "Date"})
        income_chart_frame.pack(fill="both", expand=True)
    elif tk.Toplevel.winfo_exists(income_chart_window):
        income_chart_window.lift()

def open_entry(parent,e_file="DBs/expense_data.csv",i_file="DBs/income_data.csv"):
    global add_entry_window
    if not hasattr(globals(), 'add_entry_window') or not tk.Toplevel.winfo_exists(add_entry_window):
        add_entry_window = tk.Toplevel(parent)
        add_entry_window.title("Add Entry")
        add_entry_window.iconbitmap("ss.ico")
        expense_data = read_csv_data_list(e_file)
        income_data = read_csv_data_list(i_file)
        add_entry_frame = create_add_entry_tab(add_entry_window, expense_data, income_data, e_file, i_file)
        add_entry_frame.pack(fill="both", expand=True)
    elif tk.Toplevel.winfo_exists(add_entry_window):
        add_entry_window.lift()


def main():
    global root, expense_file, income_file
    root = tk.Tk()
    root.title("SmartSaver")
    default_height = 800
    default_width = int(default_height * 9 / 16) + 200
    root.geometry(f"{default_width}x{default_height}")
    root.resizable(False, False)  # Make the window non-resizable

    expense_file = "DBs/expense_data.csv"
    income_file = "DBs/income_data.csv"

    # --- Buttons to open windows ---
    open_expenses_button = ttk.Button(root, text="Open Expenses", command=lambda: open_expenses(root))
    open_expenses_button.pack(pady=10)
    open_income_button = ttk.Button(root, text="Open Income", command=lambda: open_income(root))
    open_income_chart_button = ttk.Button(root, text="Open Expenses Chart", command=lambda: open_expenses_chart(root))
    open_income_chart_button.pack(pady=10)
    open_expenses_chart_button = ttk.Button(root, text="Open Income Chart", command=lambda: open_income_chart(root))
    open_expenses_chart_button.pack(pady=10)
    open_entry_button = ttk.Button(root, text="Open Add Entry", command=lambda: open_entry(root))
    open_entry_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
"""














import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def read_csv_data_list(file_path):
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            data.append(header)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        messagebox.showerror("Error", f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: An error occurred while reading '{file_path}': {e}")
        messagebox.showerror("Error", f"An error occurred while reading '{file_path}': {e}")
        return None
    return data


def write_csv_data(file_path, data):
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error writing to '{file_path}': {e}")
        messagebox.showerror("Error", f"Error writing to '{file_path}': {e}")
        return False


def sort_data_by_date(data):
    if not data or len(data) < 2:
        return data
    header = data[0]
    data_rows = data[1:]
    date_column_index = -1
    if "Date" in header:
        date_column_index = header.index("Date")
    elif "date" in header:
        date_column_index = header.index("date")

    if date_column_index != -1:
        def parse_date(row):
            try:
                return datetime.strptime(row[date_column_index], '%m/%d/%Y')
            except ValueError:
                return datetime.min  # Handle cases with incorrect date format

        sorted_data = sorted(data_rows, key=parse_date, reverse=True)
        return [header] + sorted_data
    else:
        print("Warning: 'Date' column not found. Data will not be sorted.")
        return data


def get_available_months_years(data):
    if not data or len(data) < 2:
        return [], []
    header = data[0]
    date_index = -1
    if "Date" in header:
        date_index = header.index("Date")
    elif "date" in header:
        date_index = header.index("date")

    if date_index == -1:
        return [], []

    months = set()
    years = set()
    for row in data[1:]:
        try:
            date_str = row[date_index]
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            months.add(date_obj.strftime('%Y-%m'))
            years.add(str(date_obj.year))
        except ValueError:
            pass
    return sorted(list(months), reverse=True), sorted(list(years), reverse=True)


def get_available_weeks(data):
    if not data or len(data) < 2:
        return []
    header = data[0]
    date_index = -1
    if "Date" in header:
        date_index = header.index("Date")
    elif "date" in header:
        date_index = header.index("date")

    if date_index == -1:
        return []

    weeks = set()
    for row in data[1:]:
        try:
            date_str = row[date_index]
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            year, week, _ = date_obj.isocalendar()
            weeks.add(f'{year}-W{week:02d}')
        except ValueError:
            pass
    return sorted(list(weeks), reverse=True)


def analyze_spending(data, start_date, end_date, category_col="Category", amount_col="Cost", date_col="Date"):
    if not data or len(data) < 2:
        return None

    header = data[0]
    try:
        category_index = header.index(category_col)
        amount_index = header.index(amount_col)
        date_index = header.index(date_col)
    except ValueError:
        messagebox.showerror("Error", f"Could not find '{category_col}', '{amount_col}', and '{date_col}' columns.")
        return None

    spending_by_category = {}

    for row in data[1:]:
        try:
            date_str = row[date_index]
            row_date = datetime.strptime(date_str, '%m/%d/%Y')
            if start_date <= row_date < end_date:
                category = row[category_index].strip()
                amount_str = str(row[amount_index]).replace('$', '').replace(',', '').strip()
                try:
                    amount = float(amount_str)
                    spending_by_category[category] = spending_by_category.get(category, 0) + amount
                except ValueError:
                    print(f"Warning: Could not parse amount '{row[amount_index]}'")
        except ValueError:
            print(f"Warning: Could not parse date '{row[date_index]}'")
        except IndexError:
            print("Warning: Incomplete row found.")

    return spending_by_category


def show_pie_chart(parent_frame, title, spending):
    chart_window = tk.Toplevel(parent_frame)
    chart_window.title(title)
    chart_window.geometry("500x600")

    if not spending:
        ttk.Label(chart_window, text=f"No data found for {title}.").pack(pady=20)
        close_button = ttk.Button(chart_window, text="Close Chart", command=chart_window.destroy)
        close_button.pack(pady=10)
        return

    categories = spending.keys()
    amounts = list(spending.values())
    total_spent = sum(amounts)

    if not categories:
        ttk.Label(chart_window, text=f"No categories found for {title}.").pack(pady=20)
        close_button = ttk.Button(chart_window, text="Close Chart", command=chart_window.destroy)
        close_button.pack(pady=10)
        return

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(amounts, labels=categories,
                                      autopct=lambda p: f'{p:.1f}% (${total_spent * p / 100:.2f})', startangle=140)
    ax.axis('equal')
    ax.set_title(title)

    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    close_button = ttk.Button(chart_window, text="Close Chart", command=chart_window.destroy)
    close_button.pack(pady=10)



def create_charts_tab(parent_window, data, tab_name, analyze_func_kwargs):
    charts_frame = ttk.Frame(parent_window, padding=10)

    # --- Month Selection ---
    available_months, _ = get_available_months_years(data)
    selected_month = tk.StringVar(charts_frame)
    selected_month.set(available_months[0] if available_months else "")

    month_label = ttk.Label(charts_frame, text="Select Month:")
    month_label.pack(pady=5)
    month_dropdown = ttk.Combobox(charts_frame, textvariable=selected_month, values=available_months, state="readonly")
    month_dropdown.pack(pady=5)

    def show_monthly_chart():
        if selected_month.get():
            year, month = map(int, selected_month.get().split('-'))
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            spending = analyze_spending(data, start_date, end_date, **analyze_func_kwargs)
            show_pie_chart(charts_frame, f"Monthly {tab_name} - {selected_month.get()}", spending)

    month_button = ttk.Button(charts_frame, text=f"Show Monthly {tab_name} Chart", command=show_monthly_chart)
    month_button.pack(pady=5)

    # --- Year Selection ---
    _, available_years = get_available_months_years(data)
    selected_year = tk.StringVar(charts_frame)
    selected_year.set(available_years[0] if available_years else "")

    year_label = ttk.Label(charts_frame, text="Select Year:")
    year_label.pack(pady=5)
    year_dropdown = ttk.Combobox(charts_frame, textvariable=selected_year, values=available_years, state="readonly")
    year_dropdown.pack(pady=5)

    def show_yearly_chart():
        if selected_year.get():
            year = int(selected_year.get())
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            spending = analyze_spending(data, start_date, end_date, **analyze_func_kwargs)
            show_pie_chart(charts_frame, f"Yearly {tab_name} - {selected_year.get()}", spending)

    year_button = ttk.Button(charts_frame, text=f"Show Yearly {tab_name} Chart", command=show_yearly_chart)
    year_button.pack(pady=5)

    # --- Week Selection ---
    available_weeks = get_available_weeks(data)
    selected_week = tk.StringVar(charts_frame)
    selected_week.set(available_weeks[0] if available_weeks else "")

    week_label = ttk.Label(charts_frame, text="Select Week:")
    week_label.pack(pady=5)
    week_dropdown = ttk.Combobox(charts_frame, textvariable=selected_week, values=available_weeks, state="readonly")
    week_dropdown.pack(pady=5)

    def show_weekly_chart():
        if selected_week.get():
            year_str, week_str = selected_week.get().split('-W')
            year = int(year_str)
            week = int(week_str)
            start_date = datetime.fromisocalendar(year, week, 1)
            end_date = start_date + timedelta(days=7)
            spending = analyze_spending(data, start_date, end_date, **analyze_func_kwargs)
            show_pie_chart(charts_frame, f"Weekly {tab_name} - {selected_week.get()}", spending)

    week_button = ttk.Button(charts_frame, text=f"Show Weekly {tab_name} Chart", command=show_weekly_chart)
    week_button.pack(pady=5)

    return charts_frame


def create_add_entry_tab(parent_window, expense_data, income_data, expense_file, income_file):
    add_frame = ttk.Frame(parent_window, padding=10)

    entry_type_label = ttk.Label(add_frame, text="Entry Type:")
    entry_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_type_var = tk.StringVar(add_frame)
    entry_type_var.set("Expense")  # Default value
    entry_type_dropdown = ttk.Combobox(add_frame, textvariable=entry_type_var, values=["Expense", "Income"],
                                       state="readonly")
    entry_type_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    category_label = ttk.Label(add_frame, text="Category:")
    category_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    category_var = tk.StringVar(add_frame)
    category_dropdown = ttk.Combobox(add_frame, textvariable=category_var, values=[], state="readonly")
    category_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    date_label = ttk.Label(add_frame, text="Date (MM/DD/YYYY):")
    date_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    date_entry = ttk.Entry(add_frame)
    date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    amount_label = ttk.Label(add_frame, text="Amount:")
    amount_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    amount_entry = ttk.Entry(add_frame)
    amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    necessity_label = ttk.Label(add_frame, text="Necessity:")
    necessity_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    necessity_var = tk.StringVar(add_frame)
    necessity_var.set("Yes")
    necessity_dropdown = ttk.Combobox(add_frame, textvariable=necessity_var, values=["Yes", "No"], state="readonly")
    necessity_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    def update_categories(*args):
        entry_type = entry_type_var.get()
        if entry_type == "Expense" and expense_data and len(expense_data) > 0:
            categories = sorted(list(set([row[expense_data[0].index("Category")] for row in expense_data[1:] if
                                          "Category" in expense_data[0]])))
            category_dropdown['values'] = categories
            if categories:
                category_var.set(categories[0])
            else:
                category_var.set("")
            necessity_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
            necessity_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        elif entry_type == "Income" and income_data and len(income_data) > 0:
            categories = ["Work","Misc", "Refund"]  # Set income categories
            category_dropdown['values'] = categories
            if categories:
                category_var.set(categories[0])
            else:
                category_var.set("")
            necessity_label.grid_forget()
            necessity_dropdown.grid_forget()
        else:
            category_dropdown['values'] = []
            category_var.set("")
            necessity_label.grid_forget()
            necessity_dropdown.grid_forget()

    entry_type_var.trace_add("write", update_categories)
    update_categories()  # Initial update

    def add_new_entry():
        entry_type = entry_type_var.get()
        category = category_var.get()
        date_str = date_entry.get()
        amount_str = amount_entry.get()
        necessity = necessity_var.get()

        try:
            datetime.strptime(date_str, '%m/%d/%Y')
            amount = float(amount_str.replace('$', '').replace(',', '').strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format (MM/DD/YYYY) or Amount.")
            return

        if not category:
            messagebox.showerror("Error", "Category cannot be empty.")
            return

        if entry_type == "Expense":
            # Read existing expense data
            existing_expense_data = read_csv_data_list(expense_file)
            headers = existing_expense_data[0] if existing_expense_data else ["Date", "Category", "Cost", "Necessity"]
            new_row = [date_str, category, amount, necessity]
            if not existing_expense_data:
                expense_data = [headers, new_row]
            else:
                expense_data = existing_expense_data + [new_row]  # Append the new row
            if write_csv_data(expense_file, expense_data):
                messagebox.showinfo("Success", "Expense added successfully.")
                # Clear the fields after successful addition
                date_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                update_categories()  # Reset the category dropdown
            else:
                messagebox.showerror("Error", "Failed to add expense.")

        elif entry_type == "Income":
            # Read existing income data
            existing_income_data = read_csv_data_list(income_file)
            headers = existing_income_data[0] if existing_income_data else ["Date", "Category", "Amount"]
            new_row = [date_str, category, amount]
            if not existing_income_data:
                income_data = [headers, new_row]
            else:
                income_data = existing_income_data + [new_row]  # Append new row
            if write_csv_data(income_file, income_data):
                messagebox.showinfo("Success", "Income added successfully.")
                date_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                update_categories()
            else:
                messagebox.showerror("Error", "Failed to add income.")
        return True

    add_button = ttk.Button(add_frame, text="Add Entry", command=add_new_entry)
    add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    for child in add_frame.winfo_children():
        child.grid_configure(sticky='ew')
    add_frame.columnconfigure(1, weight=1)

    return add_frame


def display_data_in_treeview(parent_window, data, title, has_filter_and_sort=False,edit_callback=None,delete_callback=None):
    # Use the parent_window provided, don't create a new Toplevel
    # window = tk.Toplevel(parent_window) # Removed this line
    parent_window.title(title)  # Use parent_window
    parent_window.geometry("800x600")

    # --- Frame for filter and sort controls ---
    if has_filter_and_sort:
        filter_sort_frame = ttk.Frame(parent_window) # Use parent_window
        filter_sort_frame.pack(pady=10, fill="x")

        tree_frame = ttk.Frame(parent_window)  # Frame for the Treeview # Use parent_window
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    else:
        tree_frame = ttk.Frame(parent_window) # Use parent_window
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    tree = ttk.Treeview(tree_frame)

    if data and data[0]:
        tree["columns"] = data[0]
        for col_index, col in enumerate(data[0]):
            tree.heading(col, text=col, anchor=tk.CENTER)

        # Calculate max width for each column based on header and data
        column_widths = [0] * len(data[0])
        for i, header_name in enumerate(data[0]):
            column_widths[i] = max(column_widths[i], len(header_name) * 8)  # 8 pixels per char

        for row in data[1:]:
            for i, cell_value in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(cell_value)) * 8)

        # Apply the calculated widths with a minimum width of 100
        for i, col in enumerate(data[0]):
            tree.column(col, width=max(100, column_widths[i]), anchor=tk.CENTER)
        tree.column("#0", width=0, stretch=tk.NO)

        for row in data[1:]:
            tree.insert("", tk.END, values=row)
    elif data is None:
        pass
    else:
        messagebox.showinfo("Info", f"No {title} data to display or the CSV file is empty.")

    tree.pack(fill="both", expand=True)
    if edit_callback or delete_callback:
        button_frame = ttk.Frame(parent_window)
        button_frame.pack(pady=10)

        if edit_callback:
            edit_button = ttk.Button(button_frame, text="Edit", command=lambda: edit_callback(tree))
            edit_button.pack(side=tk.LEFT, padx=10)
        if delete_callback:
            delete_button = ttk.Button(button_frame, text="Delete", command=lambda: delete_callback(tree))
            delete_button.pack(side=tk.LEFT, padx=10)

    if has_filter_and_sort:
        return tree, parent_window, filter_sort_frame # Return parent_window
    else:
        return tree, parent_window # Return parent_window



def open_expenses(parent, data=None): # added parent and data
    global expense_window, tree_expenses
    if not hasattr(globals(), 'expense_window') or not tk.Toplevel.winfo_exists(expense_window):
        expense_window = tk.Toplevel(parent)
        expense_window.title("Expenses")
        expense_window.geometry("800x600")
        expense_window.iconbitmap("ss.ico")
        if data is None:
            expense_data = read_csv_data_list(expense_file)
        else:
            expense_data = data
        sorted_expense_data = sort_data_by_date(expense_data) if expense_data else []
        tree_expenses, expense_window, expense_filter_sort_frame = display_data_in_treeview(expense_window,
                                                                                           sorted_expense_data,
                                                                                           "Expenses",
                                                                                           True,
                                                                                           edit_callback=edit_expense_entry,
                                                                                           delete_callback=delete_expense_entry)

        # --- Expense Category Filter ---
        expense_category_label = ttk.Label(expense_filter_sort_frame, text="Filter by Category:")
        expense_category_label.pack(pady=5)
        expense_categories = ["All"] + sorted(list(
            set([row[expense_data[0].index("Category")] for row in expense_data[1:] if
                 "Category" in expense_data[0]]))) if expense_data and len(expense_data) > 1 else ["All"]
        expense_category_var = tk.StringVar(expense_filter_sort_frame)
        expense_category_var.set("All")
        expense_category_dropdown = ttk.Combobox(expense_filter_sort_frame, textvariable=expense_category_var,
                                                 values=expense_categories, state="readonly")
        expense_category_dropdown.pack(pady=5)

        # --- Expense Sorting ---
        expense_sort_label = ttk.Label(expense_filter_sort_frame, text="Sort by:")
        expense_sort_label.pack(pady=5)
        expense_sort_var = tk.StringVar(expense_filter_sort_frame)
        expense_sort_var.set("Date: Most Recent to Least Recent")  # Default sort option
        expense_sort_options = [
            "Date: Most Recent to Least Recent",
            "Date: Least Recent to Most Recent",
            "Price: High to Low",
            "Price: Low to High"
        ]
        expense_sort_dropdown = ttk.Combobox(expense_filter_sort_frame, textvariable=expense_sort_var,
                                               values=expense_sort_options, state="readonly")
        expense_sort_dropdown.pack(pady=5)

        def update_expense_treeview():
            # Clear existing data in the Treeview
            for item in tree_expenses.get_children():
                tree_expenses.delete(item)

            # Read the updated data from the CSV files
            updated_expense_data = read_csv_data_list(expense_file) if data is None else data

            #Sort the data
            sorted_expense_data = sort_data_by_date(updated_expense_data) if updated_expense_data else []

            # --- Expense Sorting Logic ---
            selected_expense_sort = expense_sort_var.get()
            if selected_expense_sort == "Date: Most Recent to Least Recent":
                sorted_expense_data = sort_data_by_date(updated_expense_data) if updated_expense_data else []
            elif selected_expense_sort == "Date: Least Recent to Most Recent":
                sorted_expense_data = sort_data_by_date(updated_expense_data) if updated_expense_data else []
                if sorted_expense_data and len(sorted_expense_data) > 1:
                    sorted_expense_data = [sorted_expense_data[0]] + list(reversed(sorted_expense_data[1:]))
            elif selected_expense_sort == "Price: High to Low":
                if updated_expense_data and len(updated_expense_data) > 1:
                    try:
                        sorted_expense_data = [updated_expense_data[0]] + sorted(updated_expense_data[1:],
                                                                                 key=lambda x: float(str(x[
                                                                                                                            updated_expense_data[
                                                                                                                                0].index(
                                                                                                                                "Cost")]).replace(
                                                                                                    '$',
                                                                                                    '').replace(',',
                                                                                                                 '').strip()),
                                                                                 reverse=True)
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format. Please ensure 'Cost' is a valid number.")
                        sorted_expense_data = updated_expense_data
            elif selected_expense_sort == "Price: Low to High":
                if updated_expense_data and len(updated_expense_data) > 1:
                    try:
                        sorted_expense_data = [updated_expense_data[0]] + sorted(updated_expense_data[1:],
                                                                                 key=lambda x: float(str(x[
                                                                                                                            updated_expense_data[
                                                                                                                                0].index(
                                                                                                                                "Cost")]).replace(
                                                                                                    '$',
                                                                                                    '').replace(',',
                                                                                                                 '').strip()))
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format. Please ensure 'Cost' is a valid number.")
                        sorted_expense_data = updated_expense_data

            # Repopulate the Treeviews with the updated data
            if sorted_expense_data and sorted_expense_data[0]:
                tree_expenses["columns"] = sorted_expense_data[0]
                # Clear old headers
                for col in tree_expenses["columns"]:
                    tree_expenses.heading(col, text=col, anchor=tk.CENTER)

                # Calculate max width for each column based on header and data
                column_widths = [0] * len(sorted_expense_data[0])
                for i, header_name in enumerate(sorted_expense_data[0]):
                    column_widths[i] = max(column_widths[i], len(header_name) * 8)  # 8 pixels per char

                for row in sorted_expense_data[1:]:
                    for i, cell_value in enumerate(row):
                        column_widths[i] = max(column_widths[i], len(str(cell_value)) * 8)

                # Apply the calculated widths with a minimum width of 100
                for i, col in enumerate(sorted_expense_data[0]):
                    tree_expenses.column(col, width=max(100, column_widths[i]), anchor=tk.CENTER)
                tree_expenses.column("#0", width=0, stretch=tk.NO)

                filtered_expense_data = sorted_expense_data[1:]
                selected_expense_category = expense_category_var.get()  # Get the selected value.
                if selected_expense_category != "All":
                    filtered_expense_data = [row for row in filtered_expense_data if
                                             row[sorted_expense_data[0].index("Category")] == selected_expense_category]
                for row in filtered_expense_data:
                    tree_expenses.insert("", tk.END, values=row)
            expense_window.update()

        expense_category_var.trace_add("write", lambda *args: update_expense_treeview())
        expense_sort_var.trace_add("write", lambda *args: update_expense_treeview())
        return expense_window

    elif tk.Toplevel.winfo_exists(expense_window):
        expense_window.lift()
        return expense_window
    return expense_window


def open_income(parent, data=None): # added parent and data
    global income_window, tree_income
    if not hasattr(globals(), 'income_window') or not tk.Toplevel.winfo_exists(income_window):
        income_window = tk.Toplevel(parent)
        income_window.title("Income")
        income_window.geometry("800x600")
        income_window.iconbitmap("ss.ico")
        if data is None:
            income_data = read_csv_data_list(income_file)
        else:
            income_data = data
        sorted_income_data = sort_data_by_date(income_data) if income_data else []
        tree_income, income_window, income_filter_sort_frame = display_data_in_treeview(income_window, sorted_income_data,
                                                                                       "Income",
                                                                                       True,
                                                                                       edit_callback=edit_income_entry,
                                                                                       delete_callback=delete_income_entry)

        # --- Income Category Filter ---
        income_category_label = ttk.Label(income_filter_sort_frame, text="Filter by Category:")
        income_category_label.pack(pady=5)
        income_categories = ["All", "Work", "Misc", "Refund"]  # Set income categories for the dropdown
        income_category_var = tk.StringVar(income_filter_sort_frame)
        income_category_var.set("All")
        income_category_dropdown = ttk.Combobox(income_filter_sort_frame, textvariable=income_category_var,
                                                values=income_categories, state="readonly")
        income_category_dropdown.pack(pady=5)

        # --- Income Sorting ---
        income_sort_label = ttk.Label(income_filter_sort_frame, text="Sort by:")
        income_sort_label.pack(pady=5)
        income_sort_var = tk.StringVar(income_filter_sort_frame)
        income_sort_var.set("Date: Most Recent to Least Recent")  # Default sort option
        income_sort_options = [
            "Date: Most Recent to Least Recent",
            "Date: Least Recent to Most Recent",
            "Price: High to Low",
            "Price: Low to High"
        ]
        income_sort_dropdown = ttk.Combobox(income_filter_sort_frame, textvariable=income_sort_var,
                                            values=income_sort_options, state="readonly")
        income_sort_dropdown.pack(pady=5)

        def update_income_treeview():
            # Clear existing data in the Treeviews
            for item in tree_income.get_children():
                tree_income.delete(item)

            # Read the updated data from the CSV files
            updated_income_data = read_csv_data_list(income_file) if data is None else data

            # Sort the data
            sorted_income_data = sort_data_by_date(updated_income_data) if updated_income_data else []

            # --- Income Sorting Logic ---
            selected_income_sort = income_sort_var.get()
            if selected_income_sort == "Date: Most Recent to Least Recent":
                sorted_income_data = sort_data_by_date(updated_income_data) if updated_income_data else []
            elif selected_income_sort == "Date: Least Recent to Most Recent":
                sorted_income_data = sort_data_by_date(updated_income_data) if updated_income_data else []
                if sorted_income_data and len(sorted_income_data) > 1:
                    sorted_income_data = [sorted_income_data[0]] + list(reversed(sorted_income_data[1:]))
            elif selected_income_sort == "Price: High to Low":
                if updated_income_data and len(updated_income_data) > 1:
                    try:
                        sorted_income_data = [updated_income_data[0]] + sorted(updated_income_data[1:],
                                                                               key=lambda x: float(str(x[
                                                                                                                           updated_income_data[
                                                                                                                               0].index(
                                                                                                                               "Amount")]).replace(
                                                                                                  '$',
                                                                                                  '').replace(',',
                                                                                                               '').strip()),
                                                                               reverse=True)
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format.  Please ensure 'Amount' is a valid number.")
                        sorted_income_data = updated_income_data
            elif selected_income_sort == "Price: Low to High":
                if updated_income_data and len(updated_income_data) > 1:
                    try:
                        sorted_income_data = [updated_income_data[0]] + sorted(updated_income_data[1:],
                                                                               key=lambda x: float(str(x[
                                                                                                                           updated_income_data[
                                                                                                                               0].index(
                                                                                                                               "Amount")]).replace(
                                                                                                  '$',
                                                                                                  '').replace(',',
                                                                                                               '').strip()))
                    except ValueError:
                        messagebox.showerror("Error",
                                             "Invalid price format. Please ensure 'Amount' is a valid number.")
                        sorted_income_data = updated_income_data

            # Repopulate the Treeviews with the updated data
            if sorted_income_data and sorted_income_data[0]:
                tree_income["columns"] = sorted_income_data[0]
                for col in tree_income["columns"]:
                    tree_income.heading(col, text=col, anchor=tk.CENTER)

                # Calculate max width for each column
                column_widths = [0] * len(sorted_income_data[0])
                for i, header_name in enumerate(sorted_income_data[0]):
                    column_widths[i] = max(column_widths[i], len(header_name) * 8)  # 8 pixels per char

                for row in sorted_income_data[1:]:
                    for i, cell_value in enumerate(row):
                        column_widths[i] = max(column_widths[i], len(str(cell_value)) * 8)

                # Apply the calculated widths with a minimum width of 100
                for i, col in enumerate(sorted_income_data[0]):
                    tree_income.column(col, width=max(100, column_widths[i]), anchor=tk.CENTER)
                tree_income.column("#0", width=0, stretch=tk.NO)

                filtered_income_data = sorted_income_data[1:]
                selected_income_category = income_category_var.get()  # Get the selected value.
                if selected_income_category != "All":
                    filtered_income_data = [row for row in filtered_income_data if
                                            row[sorted_income_data[0].index("Category")] == selected_income_category]
                for row in filtered_income_data:
                    tree_income.insert("", tk.END, values=row)
            income_window.update()

        income_category_var.trace_add("write", lambda *args: update_income_treeview())
        income_sort_var.trace_add("write", lambda *args: update_income_treeview())
        return income_window
    elif tk.Toplevel.winfo_exists(income_window):
        income_window.lift()
        return income_window
    return income_window


def open_expenses_chart(parent, data=None): # added parent and data
    global expense_chart_window
    if not hasattr(globals(), 'expense_chart_window') or not tk.Toplevel.winfo_exists(expense_chart_window):
        expense_chart_window = tk.Toplevel(parent)
        expense_chart_window.title("Expense Charts")
        expense_chart_window.iconbitmap("ss.ico")
        if data is None:
            expense_data = read_csv_data_list(expense_file)
        else:
            expense_data = data
        expense_chart_frame = create_charts_tab(expense_chart_window, expense_data, "Expenses",
                                                {"category_col": "Category", "amount_col": "Cost",
                                                 "date_col": "Date"})
        expense_chart_frame.pack(fill="both", expand=True)
    elif tk.Toplevel.winfo_exists(expense_chart_window):
        expense_chart_window.lift()

def open_income_chart(parent, data=None): # added parent and data
    global income_chart_window
    if not hasattr(globals(), 'income_chart_window') or not tk.Toplevel.winfo_exists(income_chart_window):
        income_chart_window = tk.Toplevel(parent)
        income_chart_window.title("Income Charts")
        income_chart_window.iconbitmap("ss.ico")
        if data is None:
            income_data = read_csv_data_list(income_file)
        else:
            income_data = data
        income_chart_frame = create_charts_tab(income_chart_window, income_data, "Income",
                                                 {"category_col": "Category", "amount_col": "Amount",
                                                  "date_col": "Date"})
        income_chart_frame.pack(fill="both", expand=True)
    elif tk.Toplevel.winfo_exists(income_chart_window):
        income_chart_window.lift()

def open_entry(parent,e_file="DBs/expense_data.csv",i_file="DBs/income_data.csv"):
    global add_entry_window
    if not hasattr(globals(), 'add_entry_window') or not tk.Toplevel.winfo_exists(add_entry_window):
        add_entry_window = tk.Toplevel(parent)
        add_entry_window.title("Add Entry")
        add_entry_window.iconbitmap("ss.ico")
        expense_data = read_csv_data_list(e_file)
        income_data = read_csv_data_list(i_file)
        add_entry_frame = create_add_entry_tab(add_entry_window, expense_data, income_data, e_file, i_file)
        add_entry_frame.pack(fill="both", expand=True)
    elif tk.Toplevel.winfo_exists(add_entry_window):
        add_entry_window.lift()



def edit_expense_entry(tree):
    global expense_file
    expense_file = "DBs/expense_data.csv"
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to edit.")
        return

    values = tree.item(selected_item, 'values')
    if not values:
        messagebox.showerror("Error", "Selected item has no data.")
        return

    # Open a new window for editing
    edit_window = tk.Toplevel(tree)
    edit_window.title("Edit Expense Entry")
    edit_window.geometry("300x200")
    edit_window.iconbitmap("ss.ico")

    # Create labels and entry fields for each column
    labels = ["Date", "Category", "Cost"] # Removed "Necessity"
    entries = []
    for i, label in enumerate(labels):
        ttk.Label(edit_window, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(edit_window)
        entry.insert(0, values[i])
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entries.append(entry)

    def save_edited_entry():
        # Validate data
        try:
            datetime.strptime(entries[0].get(), '%m/%d/%Y')
            float(entries[2].get().replace('$', '').replace(',', '').strip())  # Check cost
        except ValueError:
            messagebox.showerror("Error", "Invalid Date or Cost format.")
            return

        # Update the treeview
        new_values = [entry.get() for entry in entries]
        tree.item(selected_item, values=new_values)

        # Update the data in the expense_data list
        global expense_data  #Added this line
        if 'expense_data' in globals(): # Added this check
            for i, row in enumerate(expense_data):
                if row == list(values):
                    expense_data[i] = new_values
                    break
        else:
             #Read the expense data and update it.
             expense_data = read_csv_data_list(expense_file)
             for i, row in enumerate(expense_data):
                if row == list(values):
                    expense_data[i] = new_values
                    break

        # Write the updated data to the CSV file
        if write_csv_data(expense_file, [expense_data[0]] + expense_data[1:]):
            messagebox.showinfo("Success", "Expense entry updated successfully.")
            edit_window.destroy()
        else:
            messagebox.showerror("Error", "Failed to update expense entry.")

    # Add a save button
    save_button = ttk.Button(edit_window, text="Save", command=save_edited_entry)
    save_button.grid(row=len(labels), column=0, columnspan=2, padx=5, pady=10, sticky="ew")



def delete_expense_entry(tree):
    global expense_file
    expense_file = "DBs/expense_data.csv"
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to delete.")
        return

    values = tree.item(selected_item, 'values')

    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?")
    if confirm:
        tree.delete(selected_item)

        # Remove the entry from the expense_data list
        global expense_data
        if 'expense_data' in globals(): # added this check
            for i, row in enumerate(expense_data):
                if row == list(values):
                    del expense_data[i]
                    break
        else:
            expense_data = read_csv_data_list(expense_file)
            for i, row in enumerate(expense_data):
                if row == list(values):
                    del expense_data[i]
                    break

        # Write the updated data to the CSV file
        if write_csv_data(expense_file, [expense_data[0]] + expense_data[1:]):
             messagebox.showinfo("Success", "Expense entry deleted successfully.")
        else:
            messagebox.showerror("Error", "Failed to delete expense entry.")




def edit_income_entry(tree):
    global income_file
    income_file = "DBs/income_data.csv"
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to edit.")
        return

    values = tree.item(selected_item, 'values')
    if not values:
        messagebox.showerror("Error", "Selected item has no data.")
        return

    # Open a new window for editing
    edit_window = tk.Toplevel(tree)
    edit_window.title("Edit Income Entry")
    edit_window.geometry("300x200")
    edit_window.iconbitmap("ss.ico")

    # Create labels and entry fields for each column
    labels = ["Date", "Category", "Amount"]
    entries = []
    for i, label in enumerate(labels):
        ttk.Label(edit_window, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(edit_window)
        entry.insert(0, values[i])
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entries.append(entry)

    def save_edited_entry():
        # Validate data
        try:
            datetime.strptime(entries[0].get(), '%m/%d/%Y')
            float(entries[2].get().replace('$', '').replace(',', '').strip())  # Check amount
        except ValueError:
            messagebox.showerror("Error", "Invalid Date or Amount format.")
            return

        # Update the treeview
        new_values = [entry.get() for entry in entries]
        tree.item(selected_item, values=new_values)

        # Update the data in the income_data list
        global income_data
        for i, row in enumerate(income_data):
            if row == list(values):
                income_data[i] = new_values
                break

        # Write the updated data to the CSV file
        if write_csv_data(income_file, [income_data[0]] + income_data[1:]):
            messagebox.showinfo("Success", "Income entry updated successfully.")
            edit_window.destroy()
        else:
            messagebox.showerror("Error", "Failed to update income entry.")

    # Add a save button
    save_button = ttk.Button(edit_window, text="Save", command=save_edited_entry)
    save_button.grid(row=len(labels), column=0, columnspan=2, padx=5, pady=10, sticky="ew")



def delete_income_entry(tree):
    global income_file
    income_file = "DBs/income_data.csv"
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to delete.")
        return
    values = tree.item(selected_item, 'values')
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?")
    if confirm:
        tree.delete(selected_item)

        # Remove the entry from the income_data list
        global income_data
        if 'income_data' in globals():
            for i, row in enumerate(income_data):
                if row == list(values):
                    del income_data[i]
                    break
        else:
            income_data = read_csv_data_list(income_file)
            for i, row in enumerate(income_data):
                if row == list(values):
                    del income_data[i]
                    break

        # Write the updated data to the CSV file
        if write_csv_data(income_file, [income_data[0]] + income_data[1:]):
            messagebox.showinfo("Success", "Income entry deleted successfully.")
        else:
            messagebox.showerror("Error", "Failed to delete income entry.")

def open_potentialsaving(parent, data=None):
    global potential_saving_window, tree_potential_saving
    if not hasattr(globals(), 'potential_saving_window') or not tk.Toplevel.winfo_exists(potential_saving_window):
        potential_saving_window = tk.Toplevel(parent)
        potential_saving_window.title("Potential Savings")
        potential_saving_window.geometry("700x1000")
        potential_saving_window.iconbitmap("ss.ico")

        if data is None:
            expense_data = read_csv_data_list(expense_file)
        else:
            expense_data = data

        tree_potential_saving, potential_saving_window, _ = display_data_in_treeview(potential_saving_window,
                                                                                     [["Date", "Category", "Cost", "Necessity"]],
                                                                                     "Potential Savings",
                                                                                     True)

        total_non_necessity = 0
        yearly_non_necessity = {}
        if expense_data:
            header = expense_data[0]
            necessity_index = -1
            cost_index = -1
            date_index = -1

            if "Necessity" in header:
                necessity_index = header.index("Necessity")
            elif "necessity" in header:
                necessity_index = header.index("necessity")

            if "Cost" in header:
                cost_index = header.index("Cost")
            elif "cost" in header:
                cost_index = header.index("cost")
            if "Date" in header:
                date_index = header.index("Date")
            elif "date" in header:
                date_index = header.index("date")

            if necessity_index != -1 and cost_index != -1 and date_index != -1:
                for row in expense_data[1:]:
                    try:
                        cost = float(str(row[cost_index]).replace('$', '').replace(',', '').strip())
                        is_not_necessity = row[necessity_index].lower() == "no"
                        if is_not_necessity:
                            total_non_necessity += cost
                        tree_potential_saving.insert("", tk.END,
                                                    values=[row[date_index], row[header.index("Category")], cost,
                                                            row[necessity_index]])
                        try:
                            year = datetime.strptime(row[date_index], '%m/%d/%Y').year
                            if year not in yearly_non_necessity:
                                yearly_non_necessity[year] = 0
                            if is_not_necessity:
                                yearly_non_necessity[year] += cost
                        except ValueError:
                            print(f"Warning: Could not parse date '{row[date_index]}'")
                    except ValueError:
                        print(f"Warning: Could not parse cost '{row[cost_index]}'")
            else:
                messagebox.showerror("Error", "Couldn't find 'Necessity' or 'Cost' column in the data.")

        # Display yearly potential savings
        yearly_savings_label_text = "Yearly Potential Savings:\n"
        for year, total in yearly_non_necessity.items():
            yearly_savings_label_text += f"  {year}: ${total:.2f}\n"
        yearly_savings_label = ttk.Label(potential_saving_window, text=yearly_savings_label_text)
        yearly_savings_label.pack(pady=5) # Reduced pady

        # --- Interest Rate Selection ---
        interest_rate = tk.StringVar(potential_saving_window)
        interest_rate.set("None")  # Default value
        interest_label = ttk.Label(potential_saving_window, text="Select Interest Rate:")
        interest_label.pack(pady=5) # Reduced pady
        interest_dropdown = ttk.Combobox(potential_saving_window, textvariable=interest_rate,
                                            values=["None", "Regular (0.01%)", "National Average (0.41%)", "High Yield (4%)"],
                                            state="readonly")
        interest_dropdown.pack(pady=5) # Reduced pady

        def calculate_and_show():
            selected_interest = interest_rate.get()
            yearly_savings_with_interest_text = "Yearly Potential Savings with Interest:\n"
            total_potential_savings = sum(yearly_non_necessity.values()) # Calculate total non-necessity across all years

            if selected_interest == "None":
                total_savings_with_interest = total_potential_savings
                for year, total in yearly_non_necessity.items():
                    yearly_savings_with_interest_text += f"  {year}: ${total:.2f}\n"
            elif selected_interest == "Regular (0.01%)":
                total_savings_with_interest = total_potential_savings * (1 + 0.0001)
                for year, total in yearly_non_necessity.items():
                    yearly_savings_with_interest_text += f"  {year}: ${total * (1 + 0.0001):.2f}\n"
            elif selected_interest == "National Average (0.41%)":
                total_savings_with_interest = total_potential_savings * (1 + 0.0041)
                for year, total in yearly_non_necessity.items():
                    yearly_savings_with_interest_text += f"  {year}: ${total * (1 + 0.0041):.2f}\n"
            elif selected_interest == "High Yield (4%)":
                total_savings_with_interest = total_potential_savings * (1 + 0.04)
                for year, total in yearly_non_necessity.items():
                    yearly_savings_with_interest_text += f"  {year}: ${total * (1 + 0.04):.2f}\n"
            else:
                total_savings_with_interest = total_potential_savings
                for year, total in yearly_non_necessity.items():
                    yearly_savings_with_interest_text += f"  {year}: ${total:.2f}\n"

            result_label.config(
                text=f"Total Potential Savings (All Years): ${total_potential_savings:.2f}\n"
                     f"{yearly_savings_with_interest_text}"
            )

        result_label = ttk.Label(potential_saving_window, text="")
        result_label.pack(pady=5) # Reduced pady

        calculate_button = ttk.Button(potential_saving_window, text="Calculate with Interest",
                                         command=calculate_and_show)
        calculate_button.pack(pady=5) # Reduced pady

        # --- Line Graph ---
        def show_month_selection():  # Month selection window
            month_window = tk.Toplevel(potential_saving_window)
            month_window.title("Select Month")
            month_window.geometry("300x150")

            available_months, _ = get_available_months_years(expense_data)
            selected_month = tk.StringVar(month_window)
            selected_month.set(available_months[0] if available_months else "")

            month_label = ttk.Label(month_window, text="Select Month:")
            month_label.pack(pady=5) # Reduced pady
            month_dropdown = ttk.Combobox(month_window, textvariable=selected_month,
                                                values=available_months, state="readonly")
            month_dropdown.pack(pady=5) # Reduced pady

            def show_graph():
                selected_month_value = selected_month.get()
                if selected_month_value:
                    show_savings_graph(selected_month_value, interest_rate.get())  # Pass selected month and interest

            graph_button = ttk.Button(month_window, text="Show Graph", command=show_graph)
            graph_button.pack(pady=5) # Reduced pady

        def show_savings_graph(selected_month_value, selected_interest):  # Graph window
            graph_window = tk.Toplevel(potential_saving_window)
            graph_window.title("Monthly Savings Projection")
            graph_window.geometry("600x550")

            year, month = map(int, selected_month_value.split('-'))
            start_date = datetime(year, month, 1)
            end_date = (datetime(year, month + 1, 1) if month < 12
                        else datetime(year + 1, 1, 1))
            monthly_non_necessity = 0
            if expense_data:
                header = expense_data[0]
                necessity_index = -1
                cost_index = -1
                date_index = -1

                if "Necessity" in header:
                    necessity_index = header.index("Necessity")
                elif "necessity" in header:
                    necessity_index = header.index("necessity")

                if "Cost" in header:
                    cost_index = header.index("Cost")
                elif "cost" in header:
                    cost_index = header.index("cost")
                if "Date" in header:
                    date_index = header.index("Date")
                elif "date" in header:
                    date_index = header.index("date")

                if necessity_index != -1 and cost_index != -1 and date_index != -1:
                    for row in expense_data[1:]:
                        try:
                            row_date = datetime.strptime(row[date_index], '%m/%d/%Y')
                            if start_date <= row_date < end_date:
                                if row[necessity_index].lower() == "no":
                                    try:
                                        cost = float(str(row[cost_index]).replace('$', '').replace(',', '').strip())
                                        monthly_non_necessity += cost
                                    except ValueError:
                                        print(
                                            f"Warning: Could not parse cost '{row[cost_index]}'")
                        except ValueError:
                            print(f"Warning: Could not parse date '{row[date_index]}'")

            months = [
                "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                "11", "12"
            ]
            savings = [monthly_non_necessity * i for i in range(1, 13)]
            total_savings = sum(savings)

            if selected_interest == "None":
                savings_with_interest = savings
                total_savings_with_interest = total_savings
            elif selected_interest == "Regular (0.01%)":
                savings_with_interest = [monthly_non_necessity * ((1 + 0.0001)**i - 1) / 0.0001 for i in range(1, 13)]
                total_savings_with_interest = monthly_non_necessity * ((1 + 0.0001)**12 - 1) / 0.0001
            elif selected_interest == "National Average (0.41%)":
                savings_with_interest = [monthly_non_necessity * ((1 + 0.0041)**i - 1) / 0.0041 for i in range(1, 13)]
                total_savings_with_interest = monthly_non_necessity * ((1 + 0.0041)**12 - 1) / 0.0041
            elif selected_interest == "High Yield (4%)":
                savings_with_interest = [monthly_non_necessity * ((1 + 0.04)**i - 1) / 0.04 for i in range(1, 13)]
                total_savings_with_interest = monthly_non_necessity * ((1 + 0.04)**12 - 1) / 0.04
            else:
                savings_with_interest = savings
                total_savings_with_interest = total_savings

            fig, ax = plt.subplots()
            ax.plot(months, savings, marker='o', label="Without Interest")
            ax.plot(months, savings_with_interest, marker='x', label=f"With {selected_interest} Interest")
            ax.set_xlabel("Month")
            ax.set_ylabel("Savings ($)")
            ax.set_title(f"Potential Savings Over 12 Months Starting {selected_month_value}")
            ax.grid(True)
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            canvas.draw()

            total_savings_label = ttk.Label(graph_window,
                                             text=f"Potential Savings Over 12 Months: ${total_savings:.2f}\n"
                                                  f"Potential Savings with Interest: ${total_savings_with_interest:.2f}")
            total_savings_label.pack(pady=10)

        graph_button = ttk.Button(potential_saving_window, text="Show Savings Graph",
                                             command=show_month_selection)
        graph_button.pack(pady=5) # Reduced pady
        return potential_saving_window
    elif tk.Toplevel.winfo_exists(potential_saving_window):
        potential_saving_window.lift()
        return potential_saving_window
    return potential_saving_window
















"""
def main():
    global root, expense_file, income_file
    root = tk.Tk()
    root.title("SmartSaver")
    default_height = 800
    default_width = int(default_height * 9 / 16) + 200
    root.geometry(f"{default_width}x{default_height}")
    root.resizable(False, False)  # Make the window non-resizable

    expense_file = "DBs/expense_data.csv"
    income_file = "DBs/income_data.csv"

    # --- Buttons to open windows ---
    open_expenses_button = ttk.Button(root, text="Open Expenses", command=lambda: open_expenses(root))
    open_expenses_button.pack(pady=10)
    open_income_button = ttk.Button(root, text="Open Income", command=lambda: open_income(root))
    open_income_chart_button = ttk.Button(root, text="Open Expenses Chart", command=lambda: open_expenses_chart(root))
    open_income_chart_button.pack(pady=10)
    open_expenses_chart_button = ttk.Button(root, text="Open Income Chart", command=lambda: open_income_chart(root))
    open_expenses_chart_button.pack(pady=10)
    open_entry_button = ttk.Button(root, text="Open Add Entry", command=lambda: open_entry(root))
    open_entry_button.pack(pady=10)

    root.mainloop()
"""

"""
if __name__ == "__main__":
    main()
"""