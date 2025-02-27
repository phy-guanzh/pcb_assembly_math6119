# Machine Simulation Project

This project simulates the operation of machines based on given strategies. The simulation includes validation of actions, calculation of distances moved by machines, and identification of conflicts and penalties.

## Project Structure

- **pcb_constructor.py**: Constructs a PCB grid from a CSV file.
- **data.csv**: Contains the coordinates and components to be placed on the PCB.
- **pcb_grid.csv**: Output file containing the constructed PCB grid.
- **xlsx_to_csv.py**: Converts `.xlsx` files to `.csv` format.
- **equipment_list.csv**: Lists the equipment and the components they can handle.
- **run.sh**: Bash script to run simulations for multiple groups.
- **machine_sim.py**: Main simulation script that validates actions, calculates distances, and identifies conflicts.
- **readme.md**: This file, providing an overview of the project.

## Usage

### Running the Simulation

To run the simulation for all groups, execute the `run.sh` script:

```sh
bash run.sh
```

### Simulation Script

The `machine_sim.py` script performs the following tasks:

1. **Validation**:
    - Checks for consecutive "pick" and "place" actions.
    - Validates the stack of picked and placed components.
    - Ensures the PCB is complete after all actions.

2. **Distance Calculation**:
    - Calculates the total distance moved by each machine.

3. **Conflict Identification**:
    - Identifies intra-machine and inter-machine conflicts.
    - Calculates penalties for workload imbalance and missing components.

### Example Output

The results of the simulation are saved in `results.txt` files within each group's solution folder. An example output is shown below:

```
All components are placed on the PCB.
Total naive distance moved by machine A: 504.28
Total naive distance moved by machine B: 579.55
Total naive distance moved by machine C: 590.95
Total naive distance moved by all machines: 1674.79 

Workload penalties:
Penalty: Machine A and Machine B are not balanced. They have different number of pick/place actions.
Penalty: Machine A and Machine C are not balanced. They have different number of pick/place actions.
Penalty: Machine B and Machine C are not balanced. They have different number of pick/place actions.

Inter and intra machine conflicts:
Inter-machine conflicts in round 17
Component J is causing conflicts between machines: B, C. There is only 1 equipment that can handle it. 
Machine A has following configuration on Head 1: A, Head 2: -, Head 3: -
Machine B has following configuration on Head 1: J, Head 2: -, Head 3: -
Machine C has following configuration on Head 1: J, Head 2: -, Head 3: - 

Total intra-machine conflicts: 0
Total inter-machine conflicts: 1 

Total workload penalty: 1717.73
Total intra-machine conflicts penalty: 0.0
Total inter-machine conflicts penalty: 28.63
Total missing components penalty: 0.0 

Total score: 3421.15
```

## Dependencies

- Python 3.x
- pandas
- numpy

## Installation

Install the required Python packages using pip:

```sh
pip install pandas numpy
```

## License

This project is licensed under the MIT License.