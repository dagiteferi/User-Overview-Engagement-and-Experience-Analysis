import pandas as pd
import numpy as np #for numerical operations
import scipy.stats  #for statistical operations
from scipy.stats import zscore #for z-score calculation


def missing_values_table(df):
    # Total missing values
    mis_val = df.isnull().sum()

    # calculate percent of missing values in each col
    mis_val_percent = 100 * df.isnull().sum() / len(df)

    # dtype of missing values
    mis_val_dtype = df.dtypes

    # Make a table with the results
    mis_val_table = pd.concat([mis_val, mis_val_percent, mis_val_dtype], axis=1)

    # Rename the columns
    mis_val_table_ren_columns = mis_val_table.rename(
    columns={0: 'Missing Values', 1: '% of Total Values', 2: 'Dtype'})

    # Sort the table by percentage of missing descending
    mis_val_table_ren_columns = mis_val_table_ren_columns[
        mis_val_table_ren_columns.iloc[:, 1] != 0].sort_values(
        '% of Total Values', ascending=False).round(1)

    # Print some summary information
    print("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"
          "There are " + str(mis_val_table_ren_columns.shape[0]) +
          " columns that have missing values.")

    # Return the dataframe with missing information
    return mis_val_table_ren_columns

def convert_bytes_to_megabytes(x):
    return x / (1024 ** 2)

def convert_ms_to_seconds(ms):
    return ms / 1000


def handle_missing_values(df):
    df_filled = df.copy()  # Create a copy of the DataFrame for modifications
    
    for column in df_filled.columns:
        # If the column is numeric (float or int), replace missing values with the median
        if df_filled[column].dtype in ['float64', 'int64']:
            median_value = df_filled[column].median()
            df_filled[column] = df_filled[column].fillna(median_value)
        # If the column is categorical (object), replace missing values with the mode (most frequent value)
        elif df_filled[column].dtype == 'object':
            mode_value = df_filled[column].mode()[0]
            df_filled[column] = df_filled[column].fillna(mode_value)
    
    return df_filled

def handle_outliers_iqr(df):
    df_cleaned = df.copy()  # Create a copy of the DataFrame for modifications
    outlier_info = {}  # Dictionary to store information about outliers
    
    for column in df_cleaned.select_dtypes(include=['float64', 'int64']).columns:
        # Calculate Q1 (25th percentile) and Q3 (75th percentile)
        Q1 = df_cleaned[column].quantile(0.25)
        Q3 = df_cleaned[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Identify outliers
        outliers = df_cleaned[(df_cleaned[column] < lower_bound) | (df_cleaned[column] > upper_bound)]
        
        # Store the count of outliers
        outlier_info[column] = outliers.shape[0]
        
        # Replace outliers with median of the column
        median_value = df_cleaned[column].median()
        df_cleaned.loc[(df_cleaned[column] < lower_bound) | (df_cleaned[column] > upper_bound), column] = median_value
    
    return df_cleaned, outlier_info

def remove_duplicates(df):
    # Remove duplicate entries
    df_cleaned = df.drop_duplicates().reset_index(drop=True)
    
    # Convert data types to appropriate types
    for column in df_cleaned.columns:
        # If the column contains numeric data but is stored as an object, convert it to numeric
        if df_cleaned[column].dtype == 'object':
            try:
                df_cleaned[column] = pd.to_numeric(df_cleaned[column])
            except ValueError:
                # If conversion fails, it's likely a categorical column, so leave it as is
                pass
        
        # Convert datetime-like strings to actual datetime objects with a specific format if possible
        if df_cleaned[column].dtype == 'object':
            sample_value = df_cleaned[column].dropna().iloc[0]  # Take a sample value from the column
            try:
                # Check if the sample value looks like a date and if so, convert the entire column
                if isinstance(pd.to_datetime(sample_value, format='%Y-%m-%d', errors='raise'), pd.Timestamp):
                    df_cleaned[column] = pd.to_datetime(df_cleaned[column], format='%Y-%m-%d', errors='coerce')
                elif isinstance(pd.to_datetime(sample_value, format='%d/%m/%Y', errors='raise'), pd.Timestamp):
                    df_cleaned[column] = pd.to_datetime(df_cleaned[column], format='%d/%m/%Y', errors='coerce')
                # Add other date formats as needed
            except (ValueError, TypeError):
                # If conversion fails, leave the column as is
                pass
    
    return df_cleaned

def display_dataset_characteristics(df):
    print("### Dataset Characteristics ###\n")
    
    # Display the shape of the dataset
    print(f"Shape of the DataFrame: {df.shape}")
    
    # Display the column data types
    print("\nData Types of Each Column:")
    print(df.dtypes)
    
    # Display summary statistics for numeric columns
    print("\nSummary Statistics for Numeric Columns:")
    print(df.describe())
    
    # Display the count of missing values per column
    print("\nCount of Missing Values per Column:")
    print(df.isnull().sum())
    
    # Display the count of unique values per column
    print("\nCount of Unique Values per Column:")
    print(df.nunique())
    
    # Display the first few rows of the cleaned dataset
    print("\nFirst Few Rows of the DataFrame:")
    print(df.head())
