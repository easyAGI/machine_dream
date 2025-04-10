# machinedream (c) 2024 PYTHAI BSD licence v3
import random
import json
import time # For timestamps
from typing import List, Dict, Any, Tuple, Optional # Added Optional

class MachineDream:
    # Simulates a machine dreaming process for knowledge consolidation
    # abstraction problem exploration incorporating self healing
    # feedback for auto tuning the dreaming process and memory pruning

    # This class conceptualizes how a system might use simulated scenarios
    # dreams to generate insights manage memory adapt its internal
    # processing dreaming based on self assessment healing and prune old data
    def __init__(self, initial_tuning_level: float = 1.0,
                 initial_dream_depth: int = 3, # initial exploration depth # improve this logic maybe link to initial memory state
                 initial_abstraction_level: float = 0.5, # initial abstraction 0 detailed 1 abstract # improve this logic perhaps link to task complexity
                 max_memory_size: int = 50): # maximum number of dreams before pruning # add configuration option
        # Initializes the MachineDream instance

        # Args:
        #     initial_tuning_level float General parameter reflecting overall state
        #     initial_dream_depth int Parameter controlling simulated depth effort
        #     initial_abstraction_level float Parameter conceptually representing abstraction
        #     max_memory_size int Threshold for triggering memory pruning
        self.memory: List[Dict[str, Any]] = []
        # --- Core State Parameters ---
        self.tuning_level: float = initial_tuning_level # General system state performance factor

        # --- Dreaming Control Parameters ---
        self.dream_depth: int = max(1, initial_dream_depth) # Min depth is one
        self.abstraction_level: float = max(0.0, min(1.0, initial_abstraction_level)) # Clamp between zero and one

        # --- Memory Management Parameters ---
        self.max_memory_size: int = max(10, max_memory_size) # Ensure reasonable minimum memory size

        # --- Internal State ---
        self._last_healing_feedback: Optional[Dict[str, str]] = None # Store last feedback for reference

    def parse_information(self, data: str) -> Dict[str, Any]:
        # Parses raw textual data into a structured format influenced by abstraction

        # Args:
        #     data str Raw data string to be parsed

        # Returns:
        #     Dict str Any Parsed data reflecting abstraction level

        # Basic text splitting # improve this logic consider NLP techniques if complexity increases
        units = data.lower().split()
        original_length = len(units)
        # Abstraction level determines percentage of units kept higher level means fewer units # revised abstraction simulation # improve this logic maybe keep keywords instead of random sample
        percentage_to_keep = 1.0 - self.abstraction_level
        num_units_to_keep = max(1, int(original_length * percentage_to_keep)) # ensure at least one unit
        # Keep the first N percent units simple simulation of retaining core info # improved logic less random than sampling
        knowledge_units = units[:num_units_to_keep]

        parsed_data = {
            "original_length": original_length,
            "retained_length": len(knowledge_units),
            "knowledge_units": knowledge_units,
            "parsing_abstraction_level": self.abstraction_level
            }
        return parsed_data

    def simulate_problem_solving(self, problem: str) -> Dict[str, Any]:
        # Simulates exploring potential solutions influenced by dream_depth

        # Args:
        #     problem str The problem statement to simulate solutions for

        # Returns:
        #     Dict str Any Simulation results including potential solutions

        solutions = []
        # Dream depth influences the number or complexity of solutions explored # revised simulation range # improve this logic complexity could scale differently
        min_solutions = max(1, self.dream_depth - 1)
        max_solutions = self.dream_depth + 1 # Simpler range based on depth
        num_solutions = random.randint(min_solutions, max_solutions)

        for i in range(num_solutions):
            # generate slightly more varied placeholder solutions # placeholder generation # improve this logic actual solutions would differ
            simulated_solution = f"Approach_{self.dream_depth}_{i+1}_{random.randint(100, 999)}"
            solutions.append(simulated_solution)

        chosen_solution = random.choice(solutions) if solutions else None # random choice simulation # improve this logic choice could be based on simulated evaluation
        scenario = {
            "problem_statement": problem,
            "solutions_explored_count": len(solutions),
            "potential_solutions": solutions,
            "chosen_simulated_solution": chosen_solution,
            "simulation_dream_depth": self.dream_depth
        }
        return scenario

    def machine_dream(self, problem: str) -> Dict[str, Any]:
        # Performs a machine dream cycle involving parsing simulation and storage

        # Args:
        #     problem str The problem statement to dream about

        # Returns:
        #     Dict str Any The insights gained from the dream
        print(f"\nInitiating dream for: '{problem[:60]}...'") # standard log message
        print(f"Current params: Depth={self.dream_depth}, Abstraction={self.abstraction_level:.2f}, Tuning={self.tuning_level:.2f}, Mem={len(self.memory)}/{self.max_memory_size}") # added memory status

        # 1 Parse influenced by abstraction_level
        parsed_problem = self.parse_information(problem)

        # 2 Simulate influenced by dream_depth
        dream_simulation_result = self.simulate_problem_solving(problem)

        # 3 Generate insights including state snapshot
        dream_insights = {
            "dream_id": f"DREAM_{int(time.time())}_{random.randint(100, 999)}", # time based id # improve this logic consider UUIDs
            "timestamp": time.time(), # Use real timestamp
            "problem_context": parsed_problem,
            "simulation_outcome": dream_simulation_result,
            "state_at_dream": { # Snapshot of state during dream
                 "tuning_level": self.tuning_level,
                 "dream_depth": self.dream_depth,
                 "abstraction_level": self.abstraction_level
            }
            # could add a simulated importance score here later # future improvement
        }

        # 4 Store insights
        self.memory.append(dream_insights)
        print(f"Completed dream {dream_insights['dream_id']}. Memory size now: {len(self.memory)}")
        return dream_insights

    def prune_memory(self) -> int:
        # Prunes the oldest memories if the memory size exceeds the maximum threshold

        # Returns:
        #     int Number of memories pruned
        pruned_count = 0
        if len(self.memory) > self.max_memory_size:
            # Calculate how many items to remove to get back to max size simple strategy # prune strategy # improve this logic maybe prune based on importance score or keep percentage
            num_to_prune = len(self.memory) - self.max_memory_size
            print(f"--- Pruning Memory: Exceeded max size ({self.max_memory_size}). Removing {num_to_prune} oldest entries.")
            # Remove the oldest entries from the beginning of the list
            self.memory = self.memory[num_to_prune:]
            pruned_count = num_to_prune
            print(f"--- Pruning Complete. Memory size now: {len(self.memory)}")
        return pruned_count

    def simulate_self_healing(self) -> Dict[str, str]:
        # Simulates self assessment evaluating system health and dream effectiveness
        # Generates feedback signals based on simulated heuristics

        # Returns:
        #     Dict str str Feedback signals for auto tuning

        print("\n--- Simulating Self-Healing Assessment ---")
        feedback = {'depth_adjustment': 'maintain', 'abstraction_adjustment': 'maintain', 'general_tuning_adjustment': 'maintain'} # Default to maintain
        needs_adjustment = False # Track if any parameter needs changing

        if not self.memory:
            print("No dream memory available for assessment.")
            return {'status': 'no_memory'}

        # --- Sample Assessment Heuristics --- # simulation heuristics # improve this logic base on real metrics if available

        # 1 Assess exploration depth
        recent_dreams_count = min(len(self.memory), 5) # look at last N dreams # config parameter possible
        recent_dreams = self.memory[-recent_dreams_count:]
        avg_solutions = sum(d['simulation_outcome']['solutions_explored_count'] for d in recent_dreams) / recent_dreams_count # simple average
        # Check if average exploration deviates significantly from target depth # deviation thresholds # improve this logic thresholds could adapt
        if avg_solutions < self.dream_depth * 0.8: # Significantly below target
             feedback['depth_adjustment'] = 'increase'
             print("Feedback: Exploration depth seems low Suggest increasing.")
             needs_adjustment = True
        elif avg_solutions > self.dream_depth * 1.2 + 1: # Significantly above target
             feedback['depth_adjustment'] = 'decrease'
             print("Feedback: Exploration depth seems high Suggest decreasing for efficiency.")
             needs_adjustment = True

        # 2 Assess abstraction level based on memory pressure # memory pressure heuristic # improve this logic correlate with performance metrics if possible
        memory_usage_ratio = len(self.memory) / self.max_memory_size
        if memory_usage_ratio > 0.9 and self.abstraction_level < 0.8: # High memory usage suggest increasing abstraction
            feedback['abstraction_adjustment'] = 'increase'
            print("Feedback: High memory pressure Suggest increasing abstraction.")
            needs_adjustment = True
        elif memory_usage_ratio < 0.3 and self.abstraction_level > 0.2: # Low memory usage maybe too abstract
             feedback['abstraction_adjustment'] = 'decrease'
             print("Feedback: Low memory usage Suggest decreasing abstraction for more detail.")
             needs_adjustment = True

        # 3 Adjust general tuning slightly if other parameters are being changed indicating adaptation need # revised tuning logic # improve this logic link to external performance
        if needs_adjustment:
             # Small random adjustment if the system is actively adapting other parameters
             feedback['general_tuning_adjustment'] = random.choice(['increase', 'decrease'])
             print(f"Feedback: System adapting Suggest small '{feedback['general_tuning_adjustment']}' to general tuning.")
        else:
             feedback['general_tuning_adjustment'] = 'maintain'
             print("Feedback: System appears stable No major adjustments suggested.")


        print(f"Healing Assessment Complete Feedback: {feedback}")
        self._last_healing_feedback = feedback # Store for reference
        return feedback

    def auto_fine_tune(self) -> None:
        # Auto tunes dreaming parameters based on self healing feedback and prunes memory

        print("\n--- Auto Fine-Tuning and Memory Check ---")
        feedback = self.simulate_self_healing()

        if not feedback or feedback.get('status') == 'no_memory':
            print("Auto-Tuning skipped: No feedback available.")
            return

        # Apply adjustments based on feedback # parameter update logic # improve this logic could use smoother updates or learning rates
        # Depth Adjustment
        depth_adj = feedback.get('depth_adjustment', 'maintain')
        if depth_adj == 'increase':
            self.dream_depth = min(10, self.dream_depth + 1) # simple increment with cap # config parameter for step cap
            print(f"Increased dream_depth to {self.dream_depth}")
        elif depth_adj == 'decrease':
            self.dream_depth = max(1, self.dream_depth - 1) # simple decrement min 1
            print(f"Decreased dream_depth to {self.dream_depth}")

        # Abstraction Adjustment
        abs_adj = feedback.get('abstraction_adjustment', 'maintain')
        abs_step = 0.05 # smaller step size # config parameter
        if abs_adj == 'increase':
            self.abstraction_level = min(1.0, self.abstraction_level + abs_step) # increment with cap
            print(f"Increased abstraction_level to {self.abstraction_level:.2f}")
        elif abs_adj == 'decrease':
            self.abstraction_level = max(0.0, self.abstraction_level - abs_step) # decrement with cap
            print(f"Decreased abstraction_level to {self.abstraction_level:.2f}")

        # General Tuning Level Adjustment
        tune_adj = feedback.get('general_tuning_adjustment', 'maintain')
        tuning_factor = 1.0
        if tune_adj == 'increase':
            tuning_factor = random.uniform(1.0, 1.03) # smaller random increase factor # config parameter range
            self.tuning_level *= tuning_factor
            print(f"Increased general tuning_level by factor {tuning_factor:.3f} to {self.tuning_level:.2f}")
        elif tune_adj == 'decrease':
            tuning_factor = random.uniform(0.97, 1.0) # smaller random decrease factor # config parameter range
            self.tuning_level *= tuning_factor
            print(f"Decreased general tuning_level by factor {tuning_factor:.3f} to {self.tuning_level:.2f}")

        # Clamp tuning level # simple bounds check # improve this logic bounds could adapt
        self.tuning_level = max(0.1, min(self.tuning_level, 5.0)) # reduced upper bound

        print("Parameter Tuning Complete.")

        # --- Memory Pruning Step --- # memory management integrated
        self.prune_memory()


    def save_memory(self, filename: str = "machine_dream_memory.json") -> bool:
        # Saves the accumulated dream memory and metadata to a JSON file
        memory_to_save = {
            "metadata": {
                "save_timestamp": time.time(),
                "last_tuning_level": self.tuning_level,
                "last_dream_depth": self.dream_depth,
                "last_abstraction_level": self.abstraction_level,
                "max_memory_size": self.max_memory_size, # save max memory size
                "total_dreams_in_file": len(self.memory), # number of dreams being saved
                "last_healing_feedback": self._last_healing_feedback
            },
            "dreams": self.memory
        }
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(memory_to_save, file, indent=2, ensure_ascii=False) # reduced indent for smaller file # config parameter indent
            print(f"\nMemory successfully saved to {filename}")
            return True
        except IOError as e:
            print(f"Error saving memory to {filename}: {e}") # standard error logging # improve this logic add more detailed logging
            return False
        except TypeError as e:
            print(f"Error serializing memory to JSON: {e}") # standard error logging # improve this logic handle specific serialization issues
            return False

    def load_memory(self, filename: str = "machine_dream_memory.json") -> bool:
        # Loads dream memory and metadata restoring state

        # Returns:
        #     bool True if loading was successful False otherwise
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                loaded_data = json.load(file)

            if isinstance(loaded_data, dict) and "dreams" in loaded_data and "metadata" in loaded_data:
                self.memory = loaded_data["dreams"]
                metadata = loaded_data["metadata"]
                # Restore state from metadata # state restoration logic # improve this logic add version checks
                self.tuning_level = metadata.get("last_tuning_level", self.tuning_level)
                self.dream_depth = metadata.get("last_dream_depth", self.dream_depth)
                self.abstraction_level = metadata.get("last_abstraction_level", self.abstraction_level)
                self.max_memory_size = metadata.get("max_memory_size", self.max_memory_size) # load max memory size
                self._last_healing_feedback = metadata.get("last_healing_feedback", self._last_healing_feedback)

                print(f"\nMemory successfully loaded from {filename}.")
                print(f"Restored state: Dreams={len(self.memory)}, Tuning={self.tuning_level:.2f}, Depth={self.dream_depth}, Abstraction={self.abstraction_level:.2f}, MaxMem={self.max_memory_size}")
                return True
            else:
                 # Try loading old format just a list # backward compatibility # consider removing eventually
                 if isinstance(loaded_data, list):
                     self.memory = loaded_data
                     print(f"Memory loaded from {filename} (old format) Found {len(self.memory)} records State not restored")
                     return True
                 else:
                    print(f"Error: Unexpected data structure in {filename}") # data structure error # improve this logic provide more detail
                    return False

        except FileNotFoundError:
            print(f"\nMemory file {filename} not found Starting with empty memory") # standard info message
            self.memory = [] # Ensure memory is empty
            return False
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading memory from {filename}: {e}") # standard error logging # improve this logic handle corrupt files
            return False


# --- Example of Usage ---
if __name__ == "__main__":
    print("="*50) # separator style # improve this logic use logging framework
    print("Initializing MachineDream")
    # Set a smaller max memory to demonstrate pruning more easily
    dream_machine = MachineDream(initial_tuning_level=1.0, initial_dream_depth=3, initial_abstraction_level=0.4, max_memory_size=15) # test pruning # config parameters

    # Try loading previous state
    dream_machine.load_memory()
    print("="*50) # separator style

    problems = [ # example problem set # improve this logic use dynamic problem generation or external source
        "Optimize neural network hyperparameters for image classification",
        "Develop a strategy for reducing latency in distributed systems",
        "How to handle conflicting information from multiple sensors?",
        "Improve energy efficiency in mobile computing devices",
        "Generate novel protein structures with specific binding properties",
        "Predict stock market fluctuations based on news sentiment",
        "Design a more effective spam filtering algorithm",
        "Create a chatbot with realistic emotional responses",
        "Summarize long technical documents accurately",
        "Detect anomalies in network traffic patterns"
    ]

    # Simulate more cycles to potentially trigger pruning
    num_cycles = 20 # increased cycles to observe pruning # config parameter
    for i in range(num_cycles):
        print(f"\n{'='*20} CYCLE {i+1}/{num_cycles} {'='*20}") # cycle logging
        # Select a problem
        current_problem = random.choice(problems) # random selection # improve this logic use curriculum learning

        # --- Dream Phase ---
        insights = dream_machine.machine_dream(current_problem)

        # --- Heal & Tune Phase includes pruning ---
        dream_machine.auto_fine_tune() # pruning happens inside here now

        # Optional Add a small delay to simulate time passing
        # time sleep zero point one # shorter delay
        if i % 5 == 0: time.sleep(0.1) # delay occasionally


    print(f"\n{'='*50}") # separator style
    print("Simulation Complete.")
    print(f"Final State: Tuning={dream_machine.tuning_level:.2f}, Depth={dream_machine.dream_depth}, Abstraction={self.abstraction_level:.2f}, Mem={len(dream_machine.memory)}/{dream_machine.max_memory_size}")
    print(f"Total dreams generated across run (approx): {num_cycles}") # Note this isn't total *stored*

    # Save the final state and memory
    dream_machine.save_memory()
    print("="*50) # separator style
