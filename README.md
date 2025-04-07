# ARCA SmartSaver

A comprehensive personal finance application for tracking expenses, income, and generating insights to help you save money.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Machine Learning Features](#machine-learning-features)
- [Contributing](#contributing)

## Overview

ARCA SmartSaver is a data-driven application designed to help users track their financial activities, visualize spending patterns, and identify potential savings opportunities through AI-powered expense analysis.

## Features

- **User Authentication**
  - Secure login system to protect your financial data

- **Expense & Income Tracking**
  - Add, view, edit, and delete expense and income entries
  - Categorize entries (Expenses: Food, Groceries, Entertainment, Transportation, Bills)
  - Categorize income (Work, Misc, Refund)
  - Date-based record keeping

- **Financial Overview**
  - View past expenses and income in an organized layout
  - Real-time balance calculation displayed in the interface
  - Data visualization using Seaborn graphs

- **AI-Powered Savings Analysis**
  - Machine learning model to identify potentially unnecessary expenses
  - Calculate total potential savings based on spending habits
  - Investment projection calculator with different interest rates

- **Data Visualization**
  - Generate visual reports for different time periods (week, month, year)
  - Interactive graphs for better financial insights

## Installation

```bash
# Clone the repository
git clone https://github.com/naahmed09/SmartSaverV2.git

# Run the application
python main.py
```

## Usage

1. **Login** - Enter your credentials on the login page
2. **Home Page** - Central hub for accessing all features
3. **Add Transactions** - Record new expenses or income with dates and categories
4. **View History** - See all your past financial transactions
5. **Generate Reports** - Visualize your financial data over different time periods
6. **Analyze Savings** - Get AI-powered recommendations for potential savings
7. **Project Investments** - See how your savings could grow with different interest rates

## Dependencies

The application relies on the following Python libraries:
- matplotlib: Data visualization and graphing
- joblib: Model serialization for the AI component
- pandas: Data manipulation and CSV handling
- scikit-learn: Machine learning for expense analysis
- numpy: Numerical operations and data processing


## Machine Learning Features

The application uses a custom machine learning model to identify potentially unnecessary expenses. The model is trained to recognize patterns in spending that might indicate areas where users can save money.

Key ML components:
- Feature extraction from expense data
- Classification of expenses as necessary or potentially unnecessary
- Regular model updates based on user feedback and spending patterns

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
