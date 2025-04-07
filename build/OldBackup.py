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
