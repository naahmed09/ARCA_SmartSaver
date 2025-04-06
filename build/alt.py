import FE_FriendlyMain as backend
import tkinter as tk
import time

import Model_inference as ssai
run_model = True
if run_model:
    input_file = "DBs\expense_data.csv"
    output_file = ssai.predict_on_csv(input_file)
    print(f"Predictions saved to: {output_file}")
    time.sleep(1)


#open functions
"""
backend.open_expenses(root, data)
backend.open_income(root, data)
backend.open_expenses_chart(root, data)
backend.open_income_chart(root, data)
backend.open_entry(root, entry.csv, income.csv)
"""




root = tk.Tk()
root.iconbitmap("ss.ico")


expense_data = backend.read_csv_data_list("DBs/expense_data.csv")
income_data = backend.read_csv_data_list("DBs/income_data.csv")
potentsave = backend.read_csv_data_list("DBs/expenses_predictions.csv")

button = tk.Button(root, text="expense", command=lambda: backend.open_expenses(root, expense_data))
button.pack(padx=20, pady=20)
button2 = tk.Button(root, text="income", command=lambda: backend.open_income(root, income_data))
button2.pack(padx=20, pady=20)
button3 = tk.Button(root, text="expense charts", command=lambda: backend.open_expenses_chart(root, expense_data))
button3.pack(padx=20, pady=20)
button4 = tk.Button(root, text="income charts", command=lambda: backend.open_income_chart(root, income_data))
button4.pack(padx=20, pady=20)
button5 = tk.Button(root, text="POTENTSAV", command=lambda: backend.open_potentialsaving(root, potentsave))
button5.pack(padx=20, pady=20)


root.mainloop()
