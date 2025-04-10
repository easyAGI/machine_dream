# machinedream (c) 2024 PYTHAI BSD licence v3
import random
import json
import os
import time
import hashlib
import math # For ceiling division if needed, though integer division works fine here
from typing import List, Dict, Any, Optional

# --- Configuration Constants ---
DEFAULT_MEMORY_FILE = "machine_dream_memory.json"
DEFAULT_SVG_FILE = "memory_vector.svg"
VECTOR_DIMENSIONS = 768
SVG_COLS = 32

class MachineDream:
    """
    Simulates a machine 'dreaming' process with persistent memory
    and generates an SVG visualization of the memory state vector.

    Focuses on parsing simulation, stateful execution across runs,
    and deterministic visual representation of memory content.
    """
    def __init__(self, memory_file: str = DEFAULT_MEMORY_FILE):
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
        Parses raw text into a structured format (simple word splitting).

        Args:
            data (str): Raw data string to be parsed.

        Returns:
            Dict[str, List[str]]: Parsed data.
        """
        # Basic simulation remains unchanged
        parsed_data = {"knowledge": data.split()}
        return parsed_data

    def simulate_problem_solving(self, problem: str) -> Dict[str, Any]:
        """
        Simulates exploring potential solutions for a problem.

        Args:
            problem (str): The problem statement.

        Returns:
            Dict[str, Any]: Simulation results including chosen solution.
        """
        # Basic simulation remains unchanged
        solutions = [f"Solution_{random.randint(100, 999)}" for _ in range(3)]
        chosen_solution = random.choice(solutions) if solutions else None
        scenario = {
            "problem": problem,
            "potential_solutions": solutions,
            "chosen_simulated_solution": chosen_solution
        }
        return scenario

    def machine_dream(self, problem: str) -> Dict[str, Any]:
        """
        Performs one dream cycle: parse, simulate, store insight in memory.

        Args:
            problem (str): The problem statement to dream about.

        Returns:
            Dict[str, Any]: The insight generated from the dream.
        """
        parsed_problem = self.parse_information(problem)
        dream_simulation_result = self.simulate_problem_solving(problem)

        dream_insights = {
            "dream_id": f"{int(time.time())}_{random.randint(1000, 9999)}",
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
        This version does not implement persistent tuning state.
        """
        if self.memory:
            tuning_factor = random.uniform(0.9, 1.1)
            print(f"Auto-tuning simulation: Factor {tuning_factor:.6f} (effect not persistent)")
        else:
            print("No previous insights in memory to auto-tune from.")

    def save_memory(self) -> bool:
        """
        Saves the accumulated dream memory to the designated JSON file.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        try:
            # Use utf-8 encoding and set indent level
            with open(self.memory_file, 'w', encoding='utf-8') as file:
                json.dump(self.memory, file, indent=2, ensure_ascii=False)
            print(f"Memory saved to {self.memory_file} ({len(self.memory)} items)")
            return True
        except IOError as e:
            print(f"Error: Could not write memory file '{self.memory_file}': {e}")
            return False
        except TypeError as e:
            print(f"Error: Could not serialize memory to JSON: {e}")
            return False

    def load_memory(self) -> bool:
        """
        Loads dream memory from the JSON file if it exists.

        Returns:
            bool: True if loading succeeded or file was not found, False on error.
        """
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as file:
                loaded_memory = json.load(file)
            if isinstance(loaded_memory, list):
                self.memory = loaded_memory
                print(f"Memory loaded from {self.memory_file} ({len(self.memory)} items)")
                return True
            else:
                print(f"Error: Invalid format in '{self.memory_file}' (expected list). Starting fresh.")
                self.memory = []
                return False
        except FileNotFoundError:
            print(f"Memory file '{self.memory_file}' not found. Starting with empty memory.")
            self.memory = []
            return True # Not an error condition for starting
        except json.JSONDecodeError as e:
             print(f"Error decoding JSON from '{self.memory_file}': {e}. Starting fresh.")
             self.memory = []
             return False
        except IOError as e:
            print(f"Error reading memory file '{self.memory_file}': {e}. Starting fresh.")
            self.memory = []
            return False

    def _generate_vector_from_memory(self, dimensions: int = VECTOR_DIMENSIONS) -> Optional[List[float]]:
        """
        Generates a deterministic vector based on a hash of the current memory.
        Uses a separate RNG seeded by the hash to avoid affecting global state.

        Args:
            dimensions (int): The desired dimensionality of the vector.

        Returns:
            Optional[List[float]]: The generated vector, or None if memory is empty.
        """
        if not self.memory:
            return None

        try:
            # Ensure canonical representation: sort keys, no extra whitespace
            memory_str = json.dumps(self.memory, sort_keys=True, separators=(',', ':'))
        except TypeError as e:
            print(f"Warning: Could not serialize memory for hashing: {e}. Using fallback string representation.")
            memory_str = str(self.memory) # Less reliable for determinism if complex objects present

        # Create hash and seed
        hasher = hashlib.sha256(memory_str.encode('utf-8'))
        # Use first 8 bytes (64 bits) for better seed quality, though 4 is often enough
        seed = int.from_bytes(hasher.digest()[:8], 'big')

        # Use a dedicated Random instance
        rng = random.Random(seed)
        vector = [rng.random() for _ in range(dimensions)]
        return vector

    def generate_memory_vector_svg(self,
                                   filename: str = DEFAULT_SVG_FILE,
                                   dimensions: int = VECTOR_DIMENSIONS,
                                   cols: int = SVG_COLS,
                                   square_size: int = 5,
                                   padding: int = 1) -> bool:
        """
        Generates an SVG file visualizing the memory state as a grid of squares.

        Args:
            filename (str): The output SVG filename.
            dimensions (int): The dimensionality of the vector to simulate.
            cols (int): Number of columns in the SVG grid.
            square_size (int): Size of each square in pixels.
            padding (int): Padding between squares in pixels.

        Returns:
            bool: True if SVG generation was successful, False otherwise.
        """
        if cols <= 0:
            print("Error: SVG columns must be positive.")
            return False

        print(f"Generating SVG visualization ({dimensions}d) to '{filename}'...")
        vector = self._generate_vector_from_memory(dimensions)

        # Handle empty memory case
        if vector is None:
            print("Memory is empty. Generating placeholder SVG.")
            svg_content = f'<svg width="150" height="50" xmlns="http://www.w3.org/2000/svg">' \
                          f'<rect width="100%" height="100%" fill="#eee"/>' \
                          f'<text x="10" y="30" font-family="sans-serif" font-size="10" fill="#555">Memory Empty</text>' \
                          f'</svg>'
        else:
            # Ensure dimensions are compatible with grid, adjust if necessary
            if dimensions % cols != 0:
                exact_rows = dimensions / cols
                rows = math.ceil(exact_rows) # Use ceiling to ensure all data fits
                adjusted_dimensions = rows * cols
                print(f"Warning: Dimensions ({dimensions}) not perfectly divisible by cols ({cols}). "
                      f"Adjusting grid to {rows}x{cols}={adjusted_dimensions}. Padding vector.")
                # Pad vector with zeros if needed
                vector.extend([0.0] * (adjusted_dimensions - dimensions))
                dimensions = adjusted_dimensions
            else:
                rows = dimensions // cols

            # Calculate SVG canvas size
            svg_width = cols * (square_size + padding) + padding
            svg_height = rows * (square_size + padding) + padding

            # Build SVG content using a list for efficiency
            svg_elements = [
                f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
                f' <title>Memory State Vector ({VECTOR_DIMENSIONS}d Simulated)</title>', # Original requested dim
                f' <desc>Visualization of MachineDream memory state. Hash seeded from content.</desc>',
                f' <rect width="100%" height="100%" fill="#f0f0f0"/>' # Background
            ]

            # Create squares
            for i, value in enumerate(vector):
                row = i // cols
                col = i % cols
                x = padding + col * (square_size + padding)
                y = padding + row * (square_size + padding)

                # Map value (0.0 to 1.0) to grayscale
                gray_level = max(0, min(255, int(value * 255))) # Clamp just in case
                color = f"rgb({gray_level},{gray_level},{gray_level})"
                svg_elements.append(
                    f'  <rect x="{x}" y="{y}" width="{square_size}" height="{square_size}" fill="{color}"/>'
                )

            svg_elements.append('</svg>')
            svg_content = "\n".join(svg_elements)

        # Write SVG content to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"Memory vector SVG saved to '{filename}'")
            return True
        except IOError as e:
            print(f"Error: Could not write SVG file '{filename}': {e}")
            return False


# --- Example of Usage ---
if __name__ == "__main__":
    print("="*40)
    # Initialize (loads existing memory from default file)
    dream_machine = MachineDream() # Uses DEFAULT_MEMORY_FILE

    # Simulate a machine dream
    problem_statement = "Optimize neural network hyperparameters for image classification"
    dream_insights = dream_machine.machine_dream(problem_statement)
    if dream_insights: # Check if dream occurred (memory might be loaded)
        print("Latest Dream Insights Sample:", {k: v for i, (k, v) in enumerate(dream_insights.items()) if i < 3}) # Show sample

    # Auto fine-tune simulation (symbolic)
    dream_machine.auto_fine_tune()

    # Save the potentially updated memory
    dream_machine.save_memory()

    # Generate the SVG visualization of the current memory state
    # Use smaller squares for a denser look with 768 elements
    dream_machine.generate_memory_vector_svg(square_size=4, padding=1)
    print("="*40)
