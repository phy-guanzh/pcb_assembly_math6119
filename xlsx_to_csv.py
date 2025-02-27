import argparse
import os
import pandas as pd

def find_xlsx_files(folder_path):
    """
    Finds all .xlsx files in the given folder and its subdirectories.

    Parameters:
    folder_path (str): Path to the folder

    Returns:
    list: List of paths to .xlsx files
    """
    xlsx_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xlsx'):
                xlsx_files.append(os.path.join(root, file))
    return xlsx_files

def convert_xlsx_to_csv(xlsx_file):
    """
    Converts an .xlsx file to .csv and saves it in the same directory.

    Parameters:
    xlsx_file (str): Path to the .xlsx file
    """
    csv_file = xlsx_file.replace('.xlsx', '.csv')
    try:
        data = pd.read_excel(xlsx_file)
        data.to_csv(csv_file, index=False)
        print(f"Converted {xlsx_file} to {csv_file}")
    except Exception as e:
        print(f"Failed to convert {xlsx_file}: {e}")

def main(folder_path):
    """
    Main function to process the folder path and print .xlsx file paths.

    Parameters:
    folder_path (str): Path to the folder
    """
    xlsx_files = find_xlsx_files(folder_path)
    if xlsx_files:
        print("Found the following .xlsx files:")
        for file_path in xlsx_files:
            print(file_path)
            convert_xlsx_to_csv(file_path)
    else:
        print("No .xlsx files found in the specified folder.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find .xlsx files in a specified folder.")
    parser.add_argument('folder_path', type=str, help='Path to the folder')

    args = parser.parse_args()

    main(args.folder_path)