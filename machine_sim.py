import argparse
import pandas as pd
from collections import Counter
import numpy as np
import os


max_consecutive_actions = 3
print_diag = False

def consecutive_actions_validator(df, print_diag=False):
    """
    Check if there are more than 3 consecutive "pick" and "place" actions in the strategy.

    Parameters:
    df (DataFrame): DataFrame containing the strategy
    print_diag (bool): Whether to print diagnostic messages

    Returns:
    bool: False if there are more than 3 consecutive "pick"/"place" actions, False otherwise
    """
    consecutive_picks = 0
    consecutive_places = 0
    for index, row in df.iterrows():
        action = row['Action']
        if action == 'pick':
            consecutive_picks += 1
            if consecutive_picks > max_consecutive_actions:
                print(f"Error: More than {max_consecutive_actions} consecutive picks found starting at row {index - max_consecutive_actions}")
                return False
        else:
            consecutive_picks = 0

        if action == 'place':
            consecutive_places += 1
            if consecutive_places > max_consecutive_actions:
                print(f"Error: More than {max_consecutive_actions} consecutive places found starting at row {index - max_consecutive_actions}")
                return False
        else:
            consecutive_places = 0

    if print_diag:
        print(f"Check: No more than {max_consecutive_actions} consecutive picks/places found.")
    return True

def stack_validator(df, print_diag=False):
    """
    Check if the stack is empty after all "pick" and "place" actions in the strategy.
    Also, check if the "place" action has a corresponding "pick" action in the stack.

    Parameters:
    df (DataFrame): DataFrame containing the strategy
    print_diag (bool): Whether to print diagnostic messages

    Returns:
    bool: False if there is an error in the stack, True otherwise
    """

    # Initialize a stack to keep track of picked components
    stack = []

    for index, row in df.iterrows():
        action = row['Action']
        component = row['Component']

        if action == 'pick':
            stack.append(component)
            if print_diag:
                print(f"Row {index}: Picked component {component}. Stack: {stack}")
        elif action == 'place':
            if stack:
                if component in stack:
                    stack.remove(component)
                    if print_diag:
                        print(f"Row {index}: Placed component {component}. Stack: {stack}")
                else:
                    print(f"Error: Component {component} not found in stack at row {index}. Current stack: {stack}")
                    return False
            else:
                print(f"Error: Stack underflow at row {index}. No components to place.")
                return False
    if print_diag:            
        print(f"Final stack: {stack}")
    return True

def naive_distance_calculator(df):
    """
    Calculate the total distance moved by the machine based on the strategy, without considering parrallel machines.

    Parameters:
    df (DataFrame): DataFrame containing the strategy

    Returns:
    float: Total distance moved by the machine
    """
    distance = 0
    last_x = 0
    last_y = 0

    for index, row in df.iterrows():
        # Access individual elements in the row
        x = row['X']
        y = row['Y']
        component = row['Component']
        action = row['Action']

        # Calculate the Euclidian distance moved
        if index > 0:
            distance += ((x - last_x)**2 + (y - last_y)**2)**0.5
        last_x = x
        last_y = y

    return distance

def read_equipment_file(equipment_file, print_diag=False):
    # Read the CSV file
    df = pd.read_csv(equipment_file, header=0)

    # Initialize a dictionary to store equipment and their components
    equipment_components = {}

    # Iterate over each row using iterrows()
    for index, row in df.iterrows():
        # Get the equipment name (first column)
        equipment = row[0]
        
        # Get the components (subsequent columns)
        components = row[1:].dropna().tolist()
        
        # Store the equipment and its components in the dictionary
        equipment_components[equipment] = components

    if print_diag:
        # Print the equipment and their components
        for equipment, components in equipment_components.items():
            print(f"Equipment {equipment}: Components {components}")

    return equipment_components

# Function to assign components to equipment
def assign_components_to_equipment(equipment_components):
    # Initialize a dictionary to store components and their supporting equipment
    component_to_equipments = {}
    
    # Iterate through the equipment_components dictionary
    for equipment, components in equipment_components.items():
        for component in components:
            if component not in component_to_equipments:
                component_to_equipments[component] = []
            component_to_equipments[component].append(equipment)
    
    return component_to_equipments

def get_before_place_states(df):
    """
    Get the states of the machine before each time "place" action sequances are about to start in the strategy.

    Parameters:
    df (DataFrame): DataFrame containing the strategy

    Returns:
    list: List of states of the machine before each "place" action sequance
    """
    states = []
    stack = []
    previous_action = None

    for index, row in df.iterrows():
        action = row['Action']
        component = row['Component']

        if action == 'pick':
            stack.append(component)
            previous_action = 'pick'
        elif action == 'place':
            if previous_action == 'pick':
                states.append(stack.copy())

            if stack:
                if component in stack:
                    stack.remove(component)
            previous_action = 'place'
            
    return states

def workload_penalty(states_A, states_B, states_C):
    """
    Calculate the workload penalty based on the number of "place" actions in each machine.

    Parameters:
    states_A (list): List of states of machine A before each "place" action sequance
    states_B (list): List of states of machine B before each "place" action sequance
    states_C (list): List of states of machine C before each "place" action sequance

    Returns:
    int: Workload penalty
    """
    workload_penalty = 0
    if not len(states_A) == len(states_B):
        workload_penalty += abs(len(states_A) - len(states_B))
        print("Penalty: Machine A and Machine B are not balanced. They have different number of pick/place actions.")
    
    if not len(states_A) == len(states_C):
        workload_penalty += abs(len(states_A) - len(states_C))
        print("Penalty: Machine A and Machine C are not balanced. They have different number of pick/place actions.")

    if not len(states_B) == len(states_C):
        workload_penalty += abs(len(states_B) - len(states_C))
        print("Penalty: Machine B and Machine C are not balanced. They have different number of pick/place actions.")

    return workload_penalty

def component_conflict_counter(components, component_support_count):
    # Count the occurrences of each component in the components
    component_count = Counter(components)
    # print(f"Component count: {component_count}")
    
    # Compare the counts with the component_support_count
    comparison_result = {}
    for component, available_equipment_count in component_support_count.items():
        actual_count = component_count.get(component, 0)
        if actual_count <= available_equipment_count or actual_count == 0:
            continue

        comparison_result[component] = {
            'actual_count': actual_count,
            'available_equipment_count': available_equipment_count
        }
    
    return comparison_result

def count_intra_machine_conflicts(state, component_support_count):
    count = 0
    comment = ""
    correct_state = []
    intraMachineConflict = component_conflict_counter(state, component_support_count)
    if intraMachineConflict:
        for component, conflict_results in intraMachineConflict.items():
            
            comment += f"Component {component} has {conflict_results['actual_count']} instances but only {conflict_results['available_equipment_count']} equipment can handle it. "
            count += conflict_results['actual_count'] - conflict_results['available_equipment_count']

            removed_components_number = 0
            for original_component in state:
                if original_component == component and removed_components_number < count:
                    removed_components_number += 1
                else:
                    correct_state.append(original_component)

    if count == 0:
        return {}
    return {'count': count, 'comment': comment, 'correct_state': correct_state}

def count_inter_machine_conflicts(corrected_state, states, component_support_count):
    count = 0
    comment = ""

    interMachineConflict = component_conflict_counter(corrected_state, component_support_count)
    if interMachineConflict:
        for component, conflict_results in interMachineConflict.items():
            conflicting_machines = [key for key, state in states.items() if component in state]
            comment += f"Component {component} is causing conflicts between machines: {', '.join(conflicting_machines)}. There is only {conflict_results['available_equipment_count']} equipment that can handle it. "

            for machine in conflicting_machines:
                count += states.get(machine, []).count(component)

            count -= conflict_results['available_equipment_count']
    if count == 0:
        return {}
    return {'count': count, 'comment': comment}

def enforce_column_format(df):
    # Ensure the first two columns are numeric
    df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
    df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce')
    
    # Ensure the third column is uppercase letters
    df.iloc[:, 2] = df.iloc[:, 2].astype(str).str.upper().replace('[^A-Z]', np.nan, regex=True)
    
    # Ensure the fourth column is lowercase words
    df.iloc[:, 3] = df.iloc[:, 3].astype(str).str.lower().replace('[^a-z]+', np.nan, regex=True)
    
    return df

def pcb_validator(df_A, df_B, df_C, df_pcb):
    """
    Validate if after all "pick" and "place" actions the PCB is complete.

    Parameters:
    df_A (DataFrame): DataFrame containing the strategy for Machine A
    df_B (DataFrame): DataFrame containing the strategy for Machine B
    df_C (DataFrame): DataFrame containing the strategy for Machine C
    df_pcb (DataFrame): DataFrame containing the PCB components
    """
    # Concat all the strategies
    df_str = pd.concat([df_A, df_B, df_C], ignore_index=True)

    # Merge the dataframes on the relevant columns and find the unmatched rows
    merged = pd.merge(df_pcb, df_str, on=['X', 'Y', 'Component', 'Action'], how='left', indicator=True)
    
    # Identify the rows in df_req that are not matched in df_str
    unmatched = merged[merged['_merge'] == 'left_only']
    
    return unmatched
    
def main(strategy_folder):
    """
    Main function to simulate the machine based on the given strategy file.

    Parameters:
    strategy_folder (str): Path to the strategy folder containing the strategy files for Machine A, B and C
    """
    # print(f"Simulating machine based on the strategy files in: {strategy_folder}")

    current_file_path = os.path.abspath(__file__)
    code_path = os.path.dirname(current_file_path)
    strategy_file_A = f"{strategy_folder}/machineA.csv"
    strategy_file_B = f"{strategy_folder}/machineB.csv"
    strategy_file_C = f"{strategy_folder}/machineC.csv"

    # Read the strategy files
    df_A = enforce_column_format(pd.read_csv(strategy_file_A))
    df_B = enforce_column_format(pd.read_csv(strategy_file_B))
    df_C = enforce_column_format(pd.read_csv(strategy_file_C))

    if not consecutive_actions_validator(df_A) or not stack_validator(df_A, print_diag) or \
        not consecutive_actions_validator(df_B) or not stack_validator(df_B, print_diag) or \
        not consecutive_actions_validator(df_C) or not stack_validator(df_C, print_diag):
        return 1
    
    df_pcb = enforce_column_format(pd.read_csv(f"{code_path}/data.csv"))

    unmatched = pcb_validator(df_A, df_B, df_C, df_pcb)
    # If there are unmatched rows, validation fails
    if not unmatched.empty:
        print("Penalty: PCB is incomplete. The following required components are missing on the PCB:")
        print(unmatched[['X', 'Y', 'Component', 'Action']])
    else:
        print("All components are placed on the PCB.")

    # Calculate the total distance moved by each machine
    distance_A = naive_distance_calculator(df_A)
    print(f"Total naive distance moved by machine A: {round(distance_A, 2)}")

    distance_B = naive_distance_calculator(df_B)
    print(f"Total naive distance moved by machine B: {round(distance_B, 2)}")

    distance_C = naive_distance_calculator(df_C)
    print(f"Total naive distance moved by machine C: {round(distance_C, 2)}")

    total_distance = distance_A + distance_B + distance_C
    print(f"Total naive distance moved by all machines: {round(total_distance, 2)} \n")

    # Read the equipment file
    equipment_file = f"{code_path}/equipment_list.csv"
    equipment_components = read_equipment_file(equipment_file)
    # Assign components to equipment
    component_to_equipments = assign_components_to_equipment(equipment_components)
    component_support_count = {component: len(equipments) for component, equipments in component_to_equipments.items()}

    # print(component_support_count)
    states_A = get_before_place_states(df_A)
    states_B = get_before_place_states(df_B)
    states_C = get_before_place_states(df_C)
    # print(states_A)
    # print(states_B)
    # print(states_C)

    print("Workload penalties:")
    work_load_penalty = workload_penalty(states_A, states_B, states_C)
    if work_load_penalty == 0:
        print("No workload penalty.")
    
    print("\nInter and intra machine conflicts:")
    intra_machine_conflicts = 0
    inter_machine_conflicts = 0

    parallel_rounds = []
    while states_A or states_B or states_C:
        parallel_round = []
        if states_A:
            state_A = states_A.pop(0)
            # print(f"Processing sublist from state_A: {state_A}")

            machineA_intra_machine_conflict_report = count_intra_machine_conflicts(state_A, component_support_count)
            if machineA_intra_machine_conflict_report:
                print(f"Machine A has intra-machine conflicts in round {len(parallel_rounds)+1}")
                print(machineA_intra_machine_conflict_report['comment'])
                print(f"Machine A has following configuration on Head 1: {state_A[0] if len(state_A) > 0 else '-'}, Head 2: {state_A[1] if len(state_A) > 1 else '-'}, Head 3: {state_A[2] if len(state_A) > 2 else '-'} \n")

                intra_machine_conflicts += machineA_intra_machine_conflict_report['count']
                parallel_round.extend(machineA_intra_machine_conflict_report['correct_state'])
            else:
                parallel_round.extend(state_A)

        if states_B:
            state_B = states_B.pop(0)
            # print(f"Processing sublist from state_B: {state_B}")

            machineB_intra_machine_conflict_report = count_intra_machine_conflicts(state_B, component_support_count)
            if machineB_intra_machine_conflict_report:
                print(f"Machine B has intra-machine conflicts in round {len(parallel_rounds)+1}")
                print(machineB_intra_machine_conflict_report['comment'])
                print(f"Machine B has following configuration on Head 1: {state_B[0] if len(state_B) > 0 else '-'}, Head 2: {state_B[1] if len(state_B) > 1 else '-'}, Head 3: {state_B[2] if len(state_B) > 2 else '-'} \n")

                intra_machine_conflicts += machineB_intra_machine_conflict_report['count']
                parallel_round.extend(machineB_intra_machine_conflict_report['correct_state'])
            else:
                parallel_round.extend(state_B)
        
        if states_C:
            state_C = states_C.pop(0)
            # print(f"Processing sublist from state_C: {state_C}")

            machineC_intra_machine_conflict_report = count_intra_machine_conflicts(state_C, component_support_count)
            if machineC_intra_machine_conflict_report:
                print(f"Machine C has intra-machine conflicts in round {len(parallel_rounds)+1}")
                print(machineC_intra_machine_conflict_report['comment'])
                print(f"Machine C has following configuration on Head 1: {state_C[0] if len(state_C) > 0 else '-'}, Head 2: {state_C[1] if len(state_C) > 1 else '-'}, Head 3: {state_C[2] if len(state_C) > 2 else '-'} \n")

                intra_machine_conflicts += machineC_intra_machine_conflict_report['count']
                parallel_round.extend(machineC_intra_machine_conflict_report['correct_state'])
            else:
                parallel_round.extend(state_C)

        inter_machine_conflict_report = count_inter_machine_conflicts(parallel_round, {'A': state_A, 'B': state_B, 'C': state_C}, component_support_count)
        if inter_machine_conflict_report:
            print(f"Inter-machine conflicts in round {len(parallel_rounds)+1}")
            print(inter_machine_conflict_report['comment'])
            print(f"Machine A has following configuration on Head 1: {state_A[0] if len(state_A) > 0 else '-'}, Head 2: {state_A[1] if len(state_A) > 1 else '-'}, Head 3: {state_A[2] if len(state_A) > 2 else '-'}")
            print(f"Machine B has following configuration on Head 1: {state_B[0] if len(state_B) > 0 else '-'}, Head 2: {state_B[1] if len(state_B) > 1 else '-'}, Head 3: {state_B[2] if len(state_B) > 2 else '-'}")
            print(f"Machine C has following configuration on Head 1: {state_C[0] if len(state_C) > 0 else '-'}, Head 2: {state_C[1] if len(state_C) > 1 else '-'}, Head 3: {state_C[2] if len(state_C) > 2 else '-'} \n")

            inter_machine_conflicts += inter_machine_conflict_report['count']

        parallel_rounds.append(parallel_round)
        # print("\n")

    
    print(f"Total intra-machine conflicts: {intra_machine_conflicts}")
    print(f"Total inter-machine conflicts: {inter_machine_conflicts} \n")


    # 3 machines
    per_round_avg_machine_distance = total_distance / (len(parallel_rounds)*3)

    # *2 for making other machines with 3 heads wait
    total_workload_distance_penalty = work_load_penalty * per_round_avg_machine_distance * 2 * 3
    print(f"Total workload penalty: {round(total_workload_distance_penalty, 2)}")

    # *2 for going back and forth
    total_intra_machine_conflicts_penalty = intra_machine_conflicts * per_round_avg_machine_distance * 2
    print(f"Total intra-machine conflicts penalty: {round(total_intra_machine_conflicts_penalty, 2)}")

    # *2 for making other heads wait
    total_inter_machine_conflicts_penalty = inter_machine_conflicts * per_round_avg_machine_distance * 2
    print(f"Total inter-machine conflicts penalty: {round(total_inter_machine_conflicts_penalty, 2)}")

    # *2 for going back and forth for each missing component, *2 for other machines with 3 heads waiting + 1000 for QA machine check sendback
    missing_components_penalty = len(unmatched) * per_round_avg_machine_distance * 2 * 2 * 3
    missing_components_penalty += 1000 if not missing_components_penalty == 0 else 0
    print(f"Total missing components penalty: {round(missing_components_penalty, 2)} \n")

    total_score = total_workload_distance_penalty + total_intra_machine_conflicts_penalty +\
         + total_inter_machine_conflicts_penalty + missing_components_penalty + total_distance
    print(f"Total score: {round(total_score, 2)}")
    # print("Machine simulation completed.")

if __name__ == "__main__":
    current_file_path = os.path.abspath(__file__)
    solution_path = os.path.dirname(current_file_path)+"/solution"

    parser = argparse.ArgumentParser(description="Machine Simulation.")
    parser.add_argument('--strategy_folder', type=str, required=False, help='Path to the strategy csv file', default=solution_path)

    args = parser.parse_args()

    main(args.strategy_folder)
