# machinedream (c) 2024 PYTHAI BSD licence v3
import random
import json
import os
import time # Added for timestamp in dream ID
import hashlib # Added for deterministic seeding
from typing import List, Dict, Any, Optional # Updated typing imports

class MachineDream:
    """
    Simulates a machine 'dreaming' process focusing on parsing,
    simulated problem solving, persistent memory, and generating
    a visual representation of the memory state as an SVG vector.
    """
    def __init__(self, memory_file: str = "machine_dream_memory.json"):
        """
        Initializes the MachineDream instance and loads previous memory.

        Args:
            memory_file (str): Path to the JSON file for storing/loading memory.
        """
        self.memory_file = memory_file
        self.memory: List[Dict[str, Any]] = []
        self.load_memory() # Load memory on initialization

    def parse_information(self, data: str) -> Dict[str, List[str]]:
        """
        Parses raw textual data into a structured format (simple splitting).

        Args:
            data (str): Raw data string to be parsed.

        Returns:
            Dict[str, List[str]]: Parsed data (split into words).
        """
        # Basic simulation: split text into words.
        parsed_data = {"knowledge": data.split()}
        return parsed_data

    def simulate_problem_solving(self, problem: str) -> Dict[str, Any]:
        """
        Simulates exploring potential solutions for a given problem.

        Args:
            problem (str): The problem statement to simulate solutions for.

        Returns:
            Dict[str, Any]: Simulation results including potential solutions.
        """
        # Simulate by generating random placeholder solutions
        solutions = []
        num_solutions = 3 # Fixed number for simplicity
        for _ in range(num_solutions):
            simulated_solution = f"Solution_{random.randint(100, 999)}"
            solutions.append(simulated_solution)

        chosen_solution = random.choice(solutions) if solutions else None
        scenario = {
            "problem": problem,
            "potential_solutions": solutions,
            "chosen_simulated_solution": chosen_solution
        }
        return scenario

    def machine_dream(self, problem: str) -> Dict[str, Any]:
        """
        Performs a 'machine dream' cycle for a given problem.

        Parses problem, simulates solutions, generates insights, appends to memory.

        Args:
            problem (str): The problem statement to dream about.

        Returns:
            Dict[str, Any]: The insights gained from the dream.
        """
        parsed_problem = self.parse_information(problem)
        dream_simulation_result = self.simulate_problem_solving(problem)

        dream_insights = {
            "dream_id": f"{int(time.time())}_{random.randint(1000, 9999)}", # Use timestamp + random
            "timestamp": time.time(),
            "problem_parsed": parsed_problem,
            "solution_chosen": dream_simulation_result['chosen_simulated_solution']
        }

        self.memory.append(dream_insights)
        print(f"Insight {dream_insights['dream_id']} added. Memory size: {len(self.memory)}")
        return dream_insights

    def auto_fine_tune(self) -> None:
        """
        Simulates auto-tuning based on memory existence (ephemeral effect).
        """
        if self.memory:
            tuning_factor = random.uniform(0.9, 1.1)
            print(f"Auto-tuning simulation: Factor {tuning_factor:.6f} (effect not persistent)")
        else:
            print("No previous insights in memory to auto-tune from.")

    def save_memory(self) -> bool:
        """ Saves the accumulated dream memory to the JSON file. """
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as file:
                json.dump(self.memory, file, indent=2, ensure_ascii=False) # Use indent=2
            print(f"Memory saved to {self.memory_file} ({len(self.memory)} items)")
            return True
        except (IOError, TypeError) as e:
            print(f"Error saving memory to {self.memory_file}: {e}")
            return False

    def load_memory(self) -> bool:
        """ Loads dream memory from the JSON file if it exists. """
        if not os.path.exists(self.memory_file):
            print("Memory file not found. Starting with empty memory.")
            self.memory = []
            return True

        try:
            with open(self.memory_file, 'r', encoding='utf-8') as file:
                loaded_memory = json.load(file)
            if isinstance(loaded_memory, list):
                self.memory = loaded_memory
                print(f"Memory loaded from {self.memory_file} ({len(self.memory)} items)")
                return True
            else:
                print(f"Error: Invalid format in {self.memory_file}. Starting fresh.")
                self.memory = []
                return False
        except (json.JSONDecodeError, IOError) as e:
             print(f"Error loading memory from {self.memory_file}: {e}. Starting fresh.")
             self.memory = []
             return False

    def _generate_deterministic_vector(self, dimensions: int = 768) -> Optional[List[float]]:
        """
        Generates a vector of floats based on a hash of the current memory.
        Returns None if memory is empty.
        """
        if not self.memory:
            return None

        # 1. Get a deterministic representation of the memory
        try:
            # Sort keys to ensure consistent JSON string for the same logical content
            memory_str = json.dumps(self.memory, sort_keys=True, separators=(',', ':'))
        except TypeError:
            # Fallback if complex objects are somehow in memory (shouldn't happen here)
            memory_str = str(self.memory)

        # 2. Create a hash of the memory string
        hasher = hashlib.sha256()
        hasher.update(memory_str.encode('utf-8'))
        # Use the first 4 bytes of the hash as the seed (int)
        seed = int.from_bytes(hasher.digest()[:4], 'big')

        # 3. Seed the random number generator
        rng = random.Random(seed)

        # 4. Generate the vector
        vector = [rng.random() for _ in range(dimensions)]
        return vector

    def generate_memory_vector_svg(self, filename: str = "memory_vector.svg",
                                   dimensions: int = 768,
                                   cols: int = 32) -> bool:
        """
        Generates an SVG file visualizing the memory state as a grid.

        Args:
            filename (str): The output SVG filename.
            dimensions (int): The dimensionality of the vector to simulate.
            cols (int): The number of columns in the SVG grid visualization.

        Returns:
            bool: True if SVG generation was successful, False otherwise.
        """
        print(f"Generating SVG visualization ({dimensions}d)...")
        vector = self._generate_deterministic_vector(dimensions)

        if vector is None:
            print("Cannot generate SVG: Memory is empty.")
            # Optionally create a blank/indicator SVG
            try:
                 with open(filename, 'w', encoding='utf-8') as f:
                      f.write('<svg width="100" height="50" xmlns="http://www.w3.org/2000/svg"><text x="10" y="30" font-family="sans-serif" font-size="10">Memory Empty</text></svg>')
                 print(f"Generated empty placeholder SVG: {filename}")
                 return True
            except IOError as e:
                 print(f"Error writing placeholder SVG {filename}: {e}")
                 return False

        # Calculate grid parameters
        if dimensions % cols != 0:
            print(f"Warning: Dimensions ({dimensions}) not perfectly divisible by cols ({cols}). Truncating vector.")
            dimensions = (dimensions // cols) * cols
            vector = vector[:dimensions]

        rows = dimensions // cols
        square_size = 10 # Size of each square in pixels
        padding = 1    # Padding between squares
        svg_width = cols * (square_size + padding) + padding
        svg_height = rows * (square_size + padding) + padding

        # Start SVG string
        svg_elements = [
            f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
            f' <title>Memory State Vector ({dimensions}d)</title>',
            f' <desc>Visualization of MachineDream memory state. Seed hash derived from memory content.</desc>',
            ' <rect width="100%" height="100%" fill="#f0f0f0"/>' # Background
        ]

        # Create squares
        for i, value in enumerate(vector):
            row = i // cols
            col = i % cols
            x = padding + col * (square_size + padding)
            y = padding + row * (square_size + padding)

            # Map value (0.0 to 1.0) to grayscale (black to white)
            gray_level = int(value * 255)
            color = f"rgb({gray_level},{gray_level},{gray_level})"

            svg_elements.append(
                f'  <rect x="{x}" y="{y}" width="{square_size}" height="{square_size}" fill="{color}"/>'
            )

        svg_elements.append('</svg>')
        svg_content = "\n".join(svg_elements)

        # Write to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"Memory vector SVG saved to {filename}")
            return True
        except IOError as e:
            print(f"Error saving SVG to {filename}: {e}")
            return False


# Example of Usage (demonstrates persistence and SVG generation)
if __name__ == "__main__":
    print("="*30)
    # Initialize (loads existing memory)
    dream_machine = MachineDream(memory_file="machine_dream_memory.json")

    # Simulate a machine dream
    problem_statement = "Optimize neural network hyperparameters for image classification"
    dream_insights = dream_machine.machine_dream(problem_statement)
    print("Latest Dream Insights:", dream_insights)

    # Auto fine-tune simulation
    dream_machine.auto_fine_tune()

    # Save the updated memory
    dream_machine.save_memory()

    # Generate the SVG visualization of the *current* memory state
    dream_machine.generate_memory_vector_svg(filename="memory_vector.svg")
    print("="*30)
