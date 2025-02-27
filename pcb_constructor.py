import pandas as pd

# Read the input CSV file
input_csv = './data.csv'
data = pd.read_csv(input_csv)

# Determine the size of the grid
max_x = data['x'].max()
max_y = data['y'].max()

# Initialize an empty grid
grid = [['' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

# Fill the second column with letters A to J starting from y=2
for i in range(2, min(12, max_y + 1)):  # Ensure we don't go out of bounds
    grid[0][i] = chr(65 + i - 2)  # ASCII value of 'A' is 65

# Place components in the grid
for index, row in data.iterrows():
    x = row['x']
    y = row['y']
    component = row['component']
    grid[y][x] = component

# Convert grid to DataFrame
grid_df = pd.DataFrame(grid)

# Save the grid DataFrame to a new CSV file
output_csv = '/Users/gevorg/my_documents/work/Soton/2023_24_academic_year/MATH6119/code/pcb_grid.csv'
grid_df.to_csv(output_csv, index=False, header=False)

print(f"Output CSV has been saved to {output_csv}")
