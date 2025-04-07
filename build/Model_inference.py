import pandas as pd
import joblib
import numpy as np
import sys
import os


def predict_on_csv(input_csv_path, output_csv_path=None):
    
    #Load a CSV file, make necessity predictions, and save results
    
    #Args:
        #input_csv_path (str): Path to input CSV with Date, Category, Cost columns
        #output_csv_path (str): Path to save results. If None, will modify input filename
    
    #Returns:
        #str: Path to the saved CSV file with predictions
    
    # Load the model and encoders
    model = joblib.load('expense_necessity_model.joblib')
    le_category = joblib.load('category_encoder.joblib')
    le_necessity = joblib.load('necessity_encoder.joblib')
    
    # Read the input CSV
    df = pd.read_csv(input_csv_path)
    
    # Convert date to day of week
    df['DayOfWeek'] = pd.to_datetime(df['Date']).dt.dayofweek
    
    # Encode categories
    df['Category_encoded'] = le_category.transform(df['Category'])
    
    # Prepare features for prediction
    X = df[['DayOfWeek', 'Category_encoded', 'Cost']].values
    
    # Make predictions
    predictions = model.predict(X)
    
    # Convert predictions back to Yes/No
    df['Necessity'] = le_necessity.inverse_transform(predictions)
    
    # Remove temporary column
    df = df.drop('Category_encoded', axis=1)
    
    # Determine output path
    if output_csv_path is None:
        output_csv_path = input_csv_path.replace('_data.csv', 's_predictions.csv')
    
    # Save results
    df.to_csv(output_csv_path, index=False)
    return output_csv_path



"""if __name__ == "__main__":
    # Example usage
    if len(sys.argv) != 2:
        print("Usage: python3 Model_inference2.py <input_csv_path>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = predict_on_csv(input_file)
    print(f"Predictions saved to: {output_file}")"""

"""input_file = "DBs\expense_data.csv"
output_file = predict_on_csv(input_file)
print(f"Predictions saved to: {output_file}")"""

