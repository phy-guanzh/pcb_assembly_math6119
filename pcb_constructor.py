import pandas as pd
import os

# Read the input CSV file
file_dir = os.path.dirname(os.path.abspath(__file__))

input_csv = file_dir + '/data.csv'
data = pd.read_csv(input_csv)

# Determine the size of the grid
max_x = data['X'].max()
max_y = data['Y'].max()

# Initialize an empty grid
grid = [['' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

# Fill the second column with letters A to J starting from y=2
for i in range(2, min(12, max_y + 1)):  # Ensure we don't go out of bounds
    grid[0][i] = chr(65 + i - 2)  # ASCII value of 'A' is 65

# Place components in the grid
for index, row in data.iterrows():
    x = row['X']
    y = row['Y']
    component = row['Component']
    grid[y][x] = component

# Convert grid to DataFrame
grid_df = pd.DataFrame(grid)

# Save the grid DataFrame to a new CSV file
output_csv = file_dir + '/pcb_grid.csv'
grid_df.to_csv(output_csv, index=False, header=False)

print(f"Output CSV has been saved to {output_csv}")
