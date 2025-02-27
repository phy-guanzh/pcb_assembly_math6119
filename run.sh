#!/bin/bash

# Iterate through group 1 to group 18
for i in {1..18}; do
  group_folder="../reports/group ${i}/solution"
  
  # Check if the solutions directory exists
  if [ -d "$group_folder" ]; then
    # echo "Running simulation for ${group_folder}"

    # Find all subdirectories within the solutions directory
    find "$group_folder" -mindepth 1 -type d | while read -r subfolder; do
      echo "Running simulation for ${subfolder}"
      # Run the Python script and save the output to results.txt in the same subfolder
      python3 ./machine_sim.py --strategy_folder "${subfolder}" > "${subfolder}/results.txt"
    done
    
    # If no subdirectories, run the script in the solutions directory itself
    if [ "$(find "$group_folder" -mindepth 1 -type d | wc -l)" -eq 0 ]; then
      echo "Running simulation for ${group_folder}"
      # Run the Python script and save the output to results.txt in the solutions directory
      python3 ./machine_sim.py --strategy_folder "${group_folder}" > "${group_folder}/results_group_${i}.txt"
    fi
  else
    echo "Directory $group_folder does not exist."
  fi
done
