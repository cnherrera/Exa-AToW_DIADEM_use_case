#
# python filtering_tool_doc.py data_from_database.csv --condition conditions.json#
#

import pandas as pd
import numpy as np
import argparse
import json
import os


# Global verbose flag
verbose = False

# Function to print messages if verbose is activated
def printv(*messages):
    """
    Print messages if the verbose flag is activated.

    Parameters:
    messages (tuple): A tuple of messages to print.
    """
    if verbose:
        for message in messages:
            print(message)

# Function to read the CSV file and return a dataframe
def read_csv_data(file_path):
    """
    Read the CSV file and return a pandas DataFrame.

    Parameters:
    file_path (str): Path to the CSV data file.

    Returns:
    pd.DataFrame: The DataFrame containing the CSV data.
    """
    try:
        data = pd.read_csv(file_path, engine='python', sep=None, skiprows=[0])
        print("CSV file read successfully.")
        return data
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None

# Function to convert conditions dictionary to query string
def dict_to_query(conditions):
    """
    Convert a dictionary of conditions to a query string for pandas DataFrame filtering.

    Parameters:
    conditions (dict): A dictionary where keys are column names and values are lists of conditions.

    Returns:
    str: The query string for pandas DataFrame filtering.
    """
    query_parts = []
    for column, condition_list in conditions.items():
        if isinstance(condition_list, list):
            condition_string = " & ".join([f"{column} {cond}" for cond in condition_list])
            query_parts.append(condition_string)
        else:
            query_parts.append(f"{column} {condition_list}")
    
    query_string = " & ".join(query_parts)
    printv(f"Query string: {query_string}")
    return query_string

# Function to filter data based on input conditions
def filter_data(data, conditions):
    """
    Apply conditions to filter data using pandas DataFrame query method.

    Parameters:
    data (pd.DataFrame): The DataFrame to filter.
    conditions (dict): A dictionary of conditions to apply to the DataFrame.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    printv("Filtering data based on provided conditions.")
    filtered_data = data.copy()
    
    while True:
        # Construct conditions query
        query_conditions = dict_to_query(conditions)
        printv("Conditions to be queried:")
        printv(query_conditions)
        
        printv("Data columns:")
        printv(data.columns)
        
        # Apply the filter
        filtered_data = data.query(query_conditions)
        printv("Data after filtering")
        printv(filtered_data)
        
        # Check the number of rows
        num_rows = len(filtered_data)
        print(f"Number of rows after filtering: {num_rows}")
        if num_rows == 1:
            printv("Filtering complete. Proceeding with the single entry.")
            printv(filtered_data)
            return filtered_data
        elif num_rows == 0:
            print("Warning: No elements left after filtering. Stopping the program.")
            return None
        else:
            # Prompt for additional filtering conditions
            printv(conditions)
            print("More than one entry found. Please provide additional filtering conditions.")
            field, operator, value = input("Enter additional conditions (field,operator,value): ").split(",")
            printv(field, operator, value)
            if field in conditions.keys():
                conditions[field].append(operator + value)
            else:
                conditions.update({field: [operator + value]})
            printv(conditions)

# Function to choose and extract attributes
def extract_attributes(data, attributes=None):
    """
    Choose and extract specific attributes for BigDFT simulation.

    Parameters:
    data (pd.DataFrame): The DataFrame containing the data.
    attributes (list, optional): A list of additional attributes to extract.

    Returns:
    dict: A dictionary containing the extracted attributes.
    """
    print("Choosing attributes and values")
    
    # Default attributes
    default_attributes = ['dft_dict', 'atomic_positions_x', 'atomic_positions_y', 'atomic_positions_z']
    print("Extracting default attributes...")
    dict_for_simu = {attr: data[attr].values.tolist() for attr in default_attributes}
    
    if attributes is not None:
        print("Extracting queried attributes")    
        for attr in attributes:
            if attr in data.columns:
                printv(attr)
                dict_for_simu[attr] = data[attr].values.tolist()
            else:
                print(f"{attr} not found in the dataset.")

    return dict_for_simu

# Process steps
def process_data(file_path, conditions, attributes=None, output_file=None):
    """
    Process the data by reading the CSV file, applying filtering conditions, and extracting attributes.

    Parameters:
    file_path (str): Path to the CSV data file.
    conditions (dict): A dictionary of filtering conditions.
    attributes (list, optional): A list of additional attributes to extract.
    output_file (str, optional): Path to the output JSON file.

    Returns:
    dict: A dictionary containing the extracted attributes.
    """
    # 1. Read CSV file
    data = read_csv_data(file_path)
    printv("Showing input data:")
    printv(data)
    
    # 2. Apply filtering
    analyzed_data = filter_data(data, conditions)
    
    # 3. Extract attributes
    attributes = extract_attributes(analyzed_data, attributes)

    # 4. Show chosen data
    if attributes is not None:
        printv("Chosen attributes for simulation")
        for key, value in attributes.items():
            printv(f"{key}: {value}")
        printv(f"Extracted attributes: {attributes}")
    else:
        printv("No attributes to display.")

        # Save the attributes to a JSON file
    if output_file:
        output_file_path = os.path.abspath(output_file)
        with open(output_file_path, 'w') as json_file:
            json.dump(attributes, json_file, indent=4)

        printv(f"Attributes saved to {output_file}")

    return attributes

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Process data based on input conditions and attributes.",
        epilog=(
            "Example:\n"
            "python your_script.py path_to_your_data.csv \\\n"
            '--conditions path_conditions.json \\\n'
            "--attributes A1 A2\\\n"
            "--output filename_attributes.json\\\n"
            "--verbose"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # Argument for the file path
    parser.add_argument('--file_path', type=str, help='Path to the CSV data file')

    # Argument for conditions (passed as a stringified dictionary)
    parser.add_argument('--conditions', type=str, help="Path to JSON file with filtering conditions (example: '{\"temperature\": \"> 300\", \"pressure\": \"<= 1\"}')", required=True)

    # Argument for attributes (list of column names)
    parser.add_argument('--attributes', type=str, nargs='*', help='List of attributes to include for next simulation')

    # Argument for output JSON file (optional)
    parser.add_argument('--output', type=str, help='Path to the output JSON file', default="attributes_for_simulation.json")

    # Argument for verbose mode
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    # Parse arguments
    args = parser.parse_args()
    # Set the global verbose flag
    verbose = args.verbose

    # Convert the conditions string to a dictionary
    with open(args.conditions, 'r') as file:
        conditions = json.load(file)
        printv(conditions)
    # Call the process_data function with parsed arguments
    print("Filtering process -> ")
    results = process_data(args.file_path, conditions, args.attributes,args.output)
