# machinedream v1.1.1
# (c) 2024 PYTHAI BSD licence v3
# Concept: Gregory L. Magnusson

import os
import argparse
import sys
import random
import json
import time
import hashlib
import math
import statistics
from typing import List, Dict, Any, Tuple, Optional, Union, Deque
from collections import deque
from dotenv import load_dotenv

# --- Configuration ---
DEFAULT_MEMORY_FILE = "machine_dream_memory.json"
DEFAULT_MAX_MEMORY = 100
MIN_MEMORY_FOR_ASSESSMENT = 5
RECOMMENDATION_HISTORY_LENGTH = 3
DEFAULT_ABS_TUNING_STEP = 0.05
DEFAULT_TUNE_FACTOR_RANGE = (0.02, 0.04)
DEFAULT_AGE_PENALTY_FACTOR = 0.005
DEFAULT_OSCILLATION_DAMPING_FACTOR = 0.5
# Parameter Bounds
MIN_COMPLEXITY, MAX_COMPLEXITY = 1, 10
MIN_ABSTRACTION, MAX_ABSTRACTION = 0.0, 1.0
MIN_TUNING_LEVEL, MAX_TUNING_LEVEL = 0.1, 5.0
# Default Target ranges for normalization (heuristic)
DEFAULT_TARGET_RANGES = {
    "importance": (0.4, 0.85),
    "novelty": (0.3, 0.7),
    "diversity": (0.4, 0.8),
    "utility": (0.4, 0.9) # Added target range for utility
}
# Pruning Configuration
UTILITY_WEIGHT_IN_PRUNING = 0.3

# --- Symbolic Insight Simulation Elements ---
# (Templates and Keywords remain the same)
INSIGHT_TEMPLATES = {
    "synthesis_high": ["Emergent patterns reveal hidden coupling in {data_type}.", "Underlying structures unify {data_type} events.", "A shift in assumptions recontextualizes {data_type}.", "The essential truth of {data_type} transcends instances.", "Synthesizing {data_type} points to a novel principle."],
    "focus_low": ["Validate core behavior of {data_type} under stress.", "Isolate specific {data_type} action and consequence.", "The immediate cause-effect in {data_type} is paramount.", "Focus on the concrete {data_type} event.", "Refine {data_type} action based on direct observation."],
    "default": ["Re-evaluate the primary objective related to {data_type}.", "Consider alternative perspectives on the {data_type} event.", "The {data_type} action-outcome loop needs review.", "{data_type} data suggests a potential paradigm drift.", "Look for the signal within {data_type} noise."]
}
THEME_KEYWORDS = {
    "systemic": ["coupling", "integration", "holistic", "network", "interdependence", "emergence"],
    "simplification": ["core", "essence", "focus", "reduction", "clarity", "generalization"],
    "complexity": ["interaction", "edge_case", "friction", "cascade", "nuance", "anomaly"],
    "validation": ["component", "direct", "concrete", "observation", "stress_test", "isolation"],
    "re-evaluation": ["objective", "perspective", "relationship", "drift", "signal", "assumption"]
}

# --- Utility Functions ---
def normalize_value(value: Optional[float], min_val: float, max_val: float) -> Optional[float]:
    """ Normalizes a value to be between -1 (below min) and 1 (above max), 0 within range. Handles None input. """
    # (Implementation same as v1.1.0)
    if value is None: return None
    if value < min_val: range_below = min_val - max(0, min_val * 0.5); return max(-1.0, (value - min_val) / max(1e-6, range_below) ) if range_below > 0 else -1.0
    elif value > max_val: range_above = max(max_val * 1.5, max_val + 0.1) - max_val; return min(1.0, (value - max_val) / max(1e-6, range_above) ) if range_above > 0 else 1.0
    else: return 0.0

# --- MachineDream Class ---

class MachineDream:
    """
    Simulates an internal knowledge refinement engine ('Machine Dream').
    Aggregates experiences into symbolic insights, assesses insight quality/utility/variance,
    detects and dampens parameter oscillation, generates detailed tuning data, applies tuning,
    allows manual control, and manages memory via utility/age-weighted importance pruning.

    Emphasizes emergent, symbolic messages suitable for autotuning feedback.
    v1.1.1
    """
    def __init__(self,
                 memory_file: str = DEFAULT_MEMORY_FILE,
                 initial_tuning_level: float = 1.0,
                 initial_dream_complexity: int = 5,
                 initial_abstraction_level: float = 0.6,
                 max_memory_size: int = DEFAULT_MAX_MEMORY,
                 abs_tuning_step: float = DEFAULT_ABS_TUNING_STEP,
                 tune_factor_range: Tuple[float, float] = DEFAULT_TUNE_FACTOR_RANGE,
                 age_penalty_factor: float = DEFAULT_AGE_PENALTY_FACTOR,
                 oscillation_damping_factor: float = DEFAULT_OSCILLATION_DAMPING_FACTOR, # Added damping factor
                 target_ranges: Dict[str, Tuple[float, float]] = DEFAULT_TARGET_RANGES):
        """ Initializes the MachineDream instance loads memory sets parameters """
        self.memory_file = memory_file
        self.memory: List[Dict[str, Any]] = []
        # Core State
        self.tuning_level: float = max(MIN_TUNING_LEVEL, min(MAX_TUNING_LEVEL, initial_tuning_level))
        # Dream Control Parameters
        self.dream_complexity: int = max(MIN_COMPLEXITY, min(MAX_COMPLEXITY, initial_dream_complexity))
        self.abstraction_level: float = max(MIN_ABSTRACTION, min(MAX_ABSTRACTION, initial_abstraction_level))
        # Memory Management
        self.max_memory_size: int = max(10, max_memory_size)
        # Tuning Control
        self.base_abs_tuning_step: float = max(0.01, abs_tuning_step)
        self.abs_tuning_step: float = self.base_abs_tuning_step
        self.tune_factor_min: float = max(0.0, tune_factor_range[0])
        self.tune_factor_max: float = max(self.tune_factor_min, tune_factor_range[1])
        self.age_penalty_factor: float = max(0.0, age_penalty_factor)
        self.oscillation_damping_factor: float = max(0.0, min(0.9, oscillation_damping_factor)) # Clamp 0-0.9
        self.target_ranges: Dict[str, Tuple[float, float]] = target_ranges
        # Internal State
        self._last_assessment_data: Optional[Dict[str, Any]] = None
        self._recommendation_history: Dict[str, Deque[str]] = { "complexity_adj": deque(maxlen=RECOMMENDATION_HISTORY_LENGTH), "abs_adj": deque(maxlen=RECOMMENDATION_HISTORY_LENGTH)}
        self._is_complexity_damped: bool = False; self._is_abstraction_damped: bool = False

        self.load_memory()

    # --- Core Simulation Methods ---

    def _simulate_data_preprocessing(self, input_data_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """ Simulates preprocessing input data based on metadata and abstraction level """
        # (Implementation same as v1.1.0)
        raw_size = input_data_metadata.get('raw_size', 1000); complexity = input_data_metadata.get('complexity', 0.5)
        abstraction_effect = self.abstraction_level * (1.2 - complexity); processed_size = max(10, int(raw_size * (1.0 - abstraction_effect)))
        retained_ratio = processed_size / raw_size if raw_size > 0 else 0
        processed_data = {"input_metadata": input_data_metadata, "processed_size": processed_size, "retained_ratio": round(retained_ratio, 3), "preprocessing_abstraction_level": self.abstraction_level}
        return processed_data

    def _simulate_symbolic_aggregation(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Simulates the core 'dream' process: generating a symbolic insight """
        # (Implementation same as v1.1.0)
        input_metadata = processed_data.get('input_metadata', {}); data_complexity = input_metadata.get('complexity', 0.5); data_type = input_metadata.get('type', 'data')
        if self.abstraction_level > 0.7 or self.dream_complexity > 7: template_category = "synthesis_high"
        elif self.abstraction_level < 0.3 or self.dream_complexity < 3: template_category = "focus_low"
        else: template_category = "default"
        template_list = INSIGHT_TEMPLATES.get(template_category, INSIGHT_TEMPLATES["default"]); symbolic_insight = random.choice(template_list).format(data_type=data_type)
        theme_category_map = { "synthesis_high": "systemic", "focus_low": "validation", "default": "re-evaluation"}
        if template_category == "default":
             if self.abstraction_level > 0.6: theme_cat = "simplification"
             elif self.dream_complexity > 5: theme_cat = "complexity"
             else: theme_cat = theme_category_map.get(template_category)
        else: theme_cat = theme_category_map.get(template_category)
        possible_themes = THEME_KEYWORDS.get(theme_cat, []); num_themes = random.randint(1, min(3, len(possible_themes)))
        key_themes = random.sample(possible_themes, num_themes) if possible_themes else []
        synthesis_level = (self.abstraction_level * 0.6) + (self.dream_complexity / 15.0) + (self.tuning_level / 18.0); synthesis_level = max(0.1, min(1.0, synthesis_level + random.uniform(-0.1, 0.1)))
        aggregation_outcome = {"symbolic_insight": symbolic_insight, "key_themes": key_themes, "template_category_used": template_category, "estimated_synthesis_level": round(synthesis_level, 3), "dream_complexity_used": self.dream_complexity, "dream_abstraction_level": self.abstraction_level}
        return aggregation_outcome

    def _calculate_theme_novelty(self, current_themes: List[str], history_length: int = 5) -> float:
        """ Calculates novelty based on Jaccard distance from recent themes """
        # (Implementation same as v1.1.0)
        if not current_themes or len(self.memory) < 1: return 1.0; recent_dreams = self.memory[-min(len(self.memory), history_length):]
        recent_themes_sets = [set(d.get('dream_result', {}).get('key_themes', [])) for d in recent_dreams]; current_theme_set = set(current_themes); max_similarity = 0.0
        for recent_set in recent_themes_sets:
            intersection = len(current_theme_set.intersection(recent_set)); union = len(current_theme_set.union(recent_set)); similarity = intersection / union if union > 0 else 1.0
            max_similarity = max(max_similarity, similarity)
        novelty = 1.0 - max_similarity; return round(novelty, 3)

    def _calculate_importance_score(self, dream_result: Dict[str, Any], recent_theme_diversity: float, theme_novelty: float) -> float:
         """ Calculates simulated importance including synthesis novelty and breakthrough chance """
         # (Implementation same as v1.1.0)
         synthesis = dream_result.get('estimated_synthesis_level', 0); num_themes = len(dream_result.get('key_themes', [])); theme_factor = min(1.0, num_themes / 3.0); base_score = (synthesis * 0.65) + (theme_factor * 0.15)
         novelty_bonus = theme_novelty * 0.20; score = base_score + novelty_bonus
         if dream_result.get('template_category_used') == "synthesis_high": score += 0.05
         breakthrough_chance = 0.03; stagnant_threshold = 0.3
         if recent_theme_diversity < stagnant_threshold: breakthrough_chance += 0.05
         if theme_novelty > 0.8: breakthrough_chance += 0.02
         is_breakthrough = random.random() < breakthrough_chance
         if is_breakthrough: print("!!! Breakthrough Insight Generated !!!"); score = max(score, 0.9) + random.uniform(0.1, 0.3)
         score += random.uniform(-0.01, 0.01); final_score = max(0, min(1.5, score))
         return final_score

    def run_dream_cycle(self, input_data_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ Runs a full dream cycle: assess, preprocess, aggregate, score, store, tune, prune, save. """
        # (Implementation same as v1.1.0)
        cycle_start_time = time.time()
        try:
            data_id = input_data_metadata.get('id', f'batch_{int(cycle_start_time)}')
            print(f"\nInitiating Dream Cycle for data: '{data_id}' (Type: {input_data_metadata.get('type','N/A')})...")
            print(f"Params: Complexity={self.dream_complexity}, Abstraction={self.abstraction_level:.3f}, Tuning={self.tuning_level:.3f}, Mem={len(self.memory)}/{self.max_memory_size}")
            tuning_data = self.assess_state(); self._last_assessment_data = tuning_data
            processed_data = self._simulate_data_preprocessing(input_data_metadata)
            aggregation_result = self._simulate_symbolic_aggregation(processed_data)
            current_themes = aggregation_result.get('key_themes', [])
            theme_novelty = self._calculate_theme_novelty(current_themes)
            recent_diversity = tuning_data.get('metrics', {}).get('theme_diversity', 0.5)
            importance_score = self._calculate_importance_score(aggregation_result, recent_diversity, theme_novelty)
            dream_insights = {"dream_id": f"DREAM_{int(cycle_start_time)}_{random.randint(100, 999)}", "timestamp": cycle_start_time, "importance_score": round(importance_score, 4), "theme_novelty": theme_novelty, "data_context": processed_data, "dream_result": aggregation_result, "state_at_dream": {"tuning_level": self.tuning_level, "dream_complexity": self.dream_complexity, "abstraction_level": self.abstraction_level }, "utility_score": None }
            self.memory.append(dream_insights)
            print(f"Completed dream {dream_insights['dream_id']} -> Insight: \"{aggregation_result['symbolic_insight']}\" (Importance: {importance_score:.3f}, Novelty: {theme_novelty:.3f}). Mem Size: {len(self.memory)}")
            self.apply_tuning(tuning_data)
            self.prune_memory()
            self.save_memory()
            return dream_insights
        except Exception as e: print(f"Error during dream cycle for data '{input_data_metadata.get('id', 'unknown')}': {e}", file=sys.stderr); return None

    # --- Assessment, Tuning, Pruning Methods ---

    def prune_memory(self) -> int:
        """ Prunes memories using score combining age-weighted importance and utility """
        # (Implementation same as v1.1.0)
        pruned_count = 0; current_time = time.time()
        if len(self.memory) > self.max_memory_size:
            num_to_prune = len(self.memory) - self.max_memory_size
            print(f"--- Pruning Memory: Exceeded max size ({self.max_memory_size}). Identifying {num_to_prune} lowest combined score.")
            memory_with_scores = []
            timestamps = [item.get('timestamp', current_time) for item in self.memory]; max_age = (current_time - min(timestamps)) if len(timestamps) > 1 else 0
            for index, item in enumerate(self.memory):
                 base_importance = item.get('importance_score', 0); timestamp = item.get('timestamp', current_time); age = current_time - timestamp
                 normalized_age = age / max_age if max_age > 0 else 0; age_weight = max(0.0, 1.0 - (normalized_age * self.age_penalty_factor))
                 age_weighted_importance = base_importance * age_weight; utility = item.get('utility_score', 0.5) # Default neutral utility
                 utility_factor = 1.0 + (utility - 0.5) * UTILITY_WEIGHT_IN_PRUNING; combined_score = age_weighted_importance * utility_factor
                 memory_with_scores.append({"index": index, "score": combined_score})
            memory_with_scores.sort(key=lambda item: item["score"])
            indices_to_remove = {item["index"] for item in memory_with_scores[:num_to_prune]}
            if indices_to_remove:
                 original_size = len(self.memory); self.memory = [item for index, item in enumerate(self.memory) if index not in indices_to_remove]
                 pruned_count = original_size - len(self.memory)
                 print(f"--- Pruning Complete. Removed {pruned_count} items (Combined Score). Memory size now: {len(self.memory)}")
            else: print("--- Pruning Aborted: Could not identify items to prune.")
        return pruned_count

    def _detect_oscillation(self, history: Deque[str], current_recommendation: str) -> bool:
        """ Checks if the last N recommendations show consistent alternation """
        # (Implementation same as v1.0.8)
        if len(history) < RECOMMENDATION_HISTORY_LENGTH -1 or current_recommendation == 'maintain': return False
        alternating = True; last_rec = current_recommendation
        for i in range(len(history) -1, -1, -1):
            prev_rec = history[i]
            if prev_rec == 'maintain' or last_rec == 'maintain' or prev_rec == last_rec: alternating = False; break
            last_rec = prev_rec
        if alternating and len(history) == history.maxlen:
             print(f"--- Oscillation detected in recommendation history: {list(history)} + {current_recommendation} ---")
             return True
        return False


    def assess_state(self) -> Dict[str, Any]:
        """ Assesses state, generates tuning data, including utility metrics. """
        print("\n--- Assessing Internal State (v1.1.1 Assessment Logic) ---")
        assessment_time = time.time()
        status = "stable"; system_mode = "Stable"
        recommendations = {'complexity_adj': 'maintain', 'abs_adj': 'maintain', 'tune_adj': 'maintain'}
        # Added utility metrics
        metrics = { 'avg_importance': None, 'stdev_importance': None, 'norm_importance': None,
                    'theme_diversity': None, 'norm_diversity': None,
                    'avg_novelty': None, 'stdev_novelty': None, 'norm_novelty': None,
                    'avg_utility': None, 'stdev_utility': None, 'norm_utility': None, # Added Utility
                    'complexity_oscillation': False, 'abstraction_oscillation': False,
                    'memory_pressure': round(len(self.memory) / max(1, self.max_memory_size), 2)}
        suggested_adjustments = {'complexity_delta': 0, 'abstraction_delta': 0.0, 'tuning_factor': 1.0}
        needs_tuning = False; oscillating = False; damping_active = False

        if len(self.memory) < MIN_MEMORY_FOR_ASSESSMENT: status = "insufficient_history"; system_mode="Initializing"; print(f"Insufficient history ({len(self.memory)}/{MIN_MEMORY_FOR_ASSESSMENT}).")
        else:
            recent_dreams = self.memory[-MIN_MEMORY_FOR_ASSESSMENT:]
            try: # Calculate Raw & Normalized Metrics
                 importances = [d.get('importance_score', 0) for d in recent_dreams]
                 novelties = [d.get('theme_novelty', 0) for d in recent_dreams]
                 # Get utility scores, using 0.5 for None (neutral default for assessment)
                 utilities = [d.get('utility_score') if d.get('utility_score') is not None else 0.5 for d in recent_dreams]
                 all_themes = [theme for d in recent_dreams for theme in d.get('dream_result', {}).get('key_themes', [])]; unique_themes = set(all_themes)

                 metrics['avg_importance'] = round(statistics.mean(importances), 3); metrics['stdev_importance'] = round(statistics.stdev(importances) if len(importances) > 1 else 0.0, 3)
                 metrics['theme_diversity'] = round(len(unique_themes) / max(1, len(all_themes)), 2) if all_themes else 0.0
                 metrics['avg_novelty'] = round(statistics.mean(novelties), 3); metrics['stdev_novelty'] = round(statistics.stdev(novelties) if len(novelties) > 1 else 0.0, 3)
                 metrics['avg_utility'] = round(statistics.mean(utilities), 3); metrics['stdev_utility'] = round(statistics.stdev(utilities) if len(utilities) > 1 else 0.0, 3) # Added Utility metrics

                 # Normalize metrics using target ranges
                 metrics['norm_importance'] = round(normalize_value(metrics['avg_importance'], self.target_ranges['importance'][0], self.target_ranges['importance'][1]), 3)
                 metrics['norm_diversity'] = round(normalize_value(metrics['theme_diversity'], self.target_ranges['diversity'][0], self.target_ranges['diversity'][1]), 3)
                 metrics['norm_novelty'] = round(normalize_value(metrics['avg_novelty'], self.target_ranges['novelty'][0], self.target_ranges['novelty'][1]), 3)
                 metrics['norm_utility'] = round(normalize_value(metrics['avg_utility'], self.target_ranges['utility'][0], self.target_ranges['utility'][1]), 3) # Added Utility normalization

            except Exception as e: print(f"Warning: Error calculating metrics: {e}"); status = "error_calculating_metrics"; system_mode="Error"; avg_importance = None
            else: avg_importance = metrics['avg_importance']

            if status not in ["insufficient_history", "error_calculating_metrics"] and avg_importance is not None:
                norm_imp = metrics['norm_importance']; norm_div = metrics['norm_diversity']; norm_nov = metrics['norm_novelty']; norm_util = metrics['norm_utility']

                # --- Generate Recommendations Based on Normalized Metrics ---
                # Rule 0: Critically low utility -> major parameter shake-up
                if norm_util < -0.75: # Heuristic: Consistently producing unhelpful insights
                     status="Needs Improvement"; system_mode="Reconfiguring"; needs_tuning = True
                     recommendations['complexity_adj'] = random.choice(['increase', 'decrease']) # Drastic change
                     recommendations['abs_adj'] = random.choice(['increase', 'decrease'])      # Drastic change
                     recommendations['tune_adj'] = 'increase' # Try boosting overall effort
                     print("Feedback: Critically low average utility. Suggesting major parameter adjustments.")
                # Rule 1: Low Importance primary issue
                elif norm_imp < -0.5:
                     if metrics['stdev_importance'] > 0.25: status="Unstable"; system_mode="Stabilizing"; recommendations['complexity_adj']='decrease'; recommendations['tune_adj']='decrease'
                     else: status="Needs Improvement"; system_mode="Boosting"; recommendations['complexity_adj']='increase'; recommendations['tune_adj']='increase'
                     needs_tuning = True
                # Rule 2: Stagnation (low diversity or novelty) primary
                elif (norm_div < -0.5 or norm_nov < -0.5) and abs(norm_imp or 0) < 0.6 : # Check stagnation is significant and imp not critically low
                     status="Stagnant"; system_mode="Exploring"; needs_tuning = True
                     if norm_nov < -0.5: recommendations['abs_adj'] = random.choice(['increase', 'decrease']) # Low novelty -> adjust abstraction
                     if norm_div < -0.5: recommendations['complexity_adj'] = random.choice(['increase','decrease']) # Low diversity -> adjust complexity
                     recommendations['tune_adj'] = 'increase' # Encourage exploration
                # Rule 3: Memory pressure
                elif metrics['memory_pressure'] > 0.9 and self.abstraction_level < MAX_ABSTRACTION * 0.9:
                     status="Needs Tuning"; system_mode="Consolidating"; recommendations['abs_adj']='increase'; needs_tuning = True
                # Rule 4: High performance stable -> relax tuning
                elif norm_imp > 0.5 and metrics['stdev_importance'] < 0.1 and norm_util > -0.2: # Add check for non-terrible utility
                     status="Stable"; system_mode="Exploiting"; recommendations['tune_adj']='decrease'

                # --- Check for Oscillation (Overrides some recommendations) ---
                metrics['complexity_oscillation'] = self._detect_oscillation(self._recommendation_history["complexity_adj"], recommendations['complexity_adj'])
                metrics['abstraction_oscillation'] = self._detect_oscillation(self._recommendation_history["abs_adj"], recommendations['abs_adj'])
                oscillating = metrics['complexity_oscillation'] or metrics['abstraction_oscillation']
                if oscillating:
                     status="Oscillating"; system_mode="Stabilizing"; needs_tuning = True; damping_active = True
                     if metrics['complexity_oscillation']: recommendations['complexity_adj'] = 'maintain'
                     if metrics['abstraction_oscillation']: recommendations['abs_adj'] = 'maintain'
                     recommendations['tune_adj'] = 'decrease'; print("Feedback: Oscillation detected! Dampening applied.")

                # --- Set Final Status & Random Tune ---
                if status == "stable" and needs_tuning: status = "needs_tuning" # Ensure status reflects need
                if status == "stable" and system_mode == "Stable": print("Feedback: System appears stable and within target ranges.")
                elif needs_tuning and recommendations['tune_adj'] == 'maintain' and not oscillating: # Random tune only if needed and not oscillating
                     recommendations['tune_adj'] = random.choice(['increase', 'decrease'])

                # --- Generate Final Suggested Adjustments ---
                # ... (Logic to set suggested_adjustments based on final recommendations) ...
                if recommendations['complexity_adj'] == 'increase': suggested_adjustments['complexity_delta'] = +1
                elif recommendations['complexity_adj'] == 'decrease': suggested_adjustments['complexity_delta'] = -1
                else: suggested_adjustments['complexity_delta'] = 0
                if recommendations['abs_adj'] == 'increase': suggested_adjustments['abstraction_delta'] = +self.base_abs_tuning_step
                elif recommendations['abs_adj'] == 'decrease': suggested_adjustments['abstraction_delta'] = -self.base_abs_tuning_step
                else: suggested_adjustments['abstraction_delta'] = 0.0
                if recommendations['tune_adj'] == 'increase': suggested_adjustments['tuning_factor'] = 1.0 + random.uniform(self.tune_factor_min, self.tune_factor_max)
                elif recommendations['tune_adj'] == 'decrease': suggested_adjustments['tuning_factor'] = 1.0 - random.uniform(self.tune_factor_min, self.tune_factor_max)
                else: suggested_adjustments['tuning_factor'] = 1.0

                # --- Update History ---
                self._recommendation_history["complexity_adj"].append(recommendations['complexity_adj'])
                self._recommendation_history["abs_adj"].append(recommendations['abs_adj'])

                # Print assessment summary
                print(f"Assessment Metrics: AvgImp={metrics['avg_importance']:.3f}({metrics['norm_importance']:.2f}), StdImp={metrics['stdev_importance']:.3f}, Div={metrics['theme_diversity']:.2f}({metrics['norm_diversity']:.2f}), AvgNov={metrics['avg_novelty']:.3f}({metrics['norm_novelty']:.2f}), StdNov={metrics['stdev_novelty']:.3f}, AvgUtil={metrics['avg_utility']:.3f}({metrics['norm_utility']:.2f}), MemP={metrics['memory_pressure']:.2f}, Osc(C/A):{metrics['complexity_oscillation']}/{metrics['abstraction_oscillation']}")
                print(f"Assessment State: {status} / System Mode: {system_mode}")
                print(f"Tuning Recs (Adj): Cmplx_d={suggested_adjustments['complexity_delta']}, Abs_d={suggested_adjustments['abstraction_delta']:.3f}, Tune_f={suggested_adjustments['tuning_factor']:.4f}")
            else: print("Skipping recommendation generation.")

        tuning_data = { "assessment_timestamp": assessment_time, "status": status, "system_mode": system_mode, "metrics": metrics, "recommendations": recommendations, "suggested_adjustments": suggested_adjustments, "current_params": { "tuning_level": self.tuning_level, "dream_complexity": self.dream_complexity, "abstraction_level": self.abstraction_level, "memory_size": len(self.memory), "max_memory": self.max_memory_size}}
        return tuning_data

    def apply_tuning(self, tuning_data: Dict[str, Any]):
        """ Applies tuning using suggested adjustments, damping step sizes if oscillating. """
        # (Implementation same as v1.0.9)
        adjustments = tuning_data.get('suggested_adjustments', {}); status = tuning_data.get('status', 'error'); metrics = tuning_data.get('metrics', {})
        if status in ['stable', 'needs_tuning', 'oscillating', 'Stagnant', 'Unstable', 'Needs Improvement', 'Reconfiguring']: # Added Reconfiguring
             print("\n--- Applying Tuning Adjustments ---"); changed = False
             current_abs_step = self.base_abs_tuning_step
             if metrics.get('abstraction_oscillation', False):
                  if not self._is_abstraction_damped: self.abs_tuning_step *= self.oscillation_damping_factor; self._is_abstraction_damped = True; print(f"Damping abstraction step size to: {self.abs_tuning_step:.4f}")
                  current_abs_step = self.abs_tuning_step
             elif self._is_abstraction_damped:
                  self.abs_tuning_step = min(self.base_abs_tuning_step, self.abs_tuning_step / (1.0 - self.oscillation_damping_factor * 0.1))
                  if self.abs_tuning_step >= self.base_abs_tuning_step: self.abs_tuning_step = self.base_abs_tuning_step; self._is_abstraction_damped = False; print("Abstraction damping removed.")
                  current_abs_step = self.abs_tuning_step
             comp_delta = adjustments.get('complexity_delta', 0)
             if comp_delta != 0:
                  new_comp = max(MIN_COMPLEXITY, min(MAX_COMPLEXITY, self.dream_complexity + comp_delta))
                  if new_comp != self.dream_complexity: self.dream_complexity = new_comp; changed = True; print(f"Applied: Set dream_complexity to {self.dream_complexity}")
             abs_delta = adjustments.get('abstraction_delta', 0.0)
             if abs_delta == 0.0 and tuning_data.get('recommendations',{}).get('abs_adj') != 'maintain': abs_dir = tuning_data['recommendations']['abs_adj']; abs_delta = +current_abs_step if abs_dir == 'increase' else -current_abs_step
             if abs_delta != 0.0:
                  new_abs = max(MIN_ABSTRACTION, min(MAX_ABSTRACTION, self.abstraction_level + abs_delta))
                  if abs(new_abs - self.abstraction_level) > 1e-9: applied_delta = new_abs - self.abstraction_level; self.abstraction_level = new_abs; changed = True; print(f"Applied: Adjusted abstraction_level by {applied_delta:.3f} to {self.abstraction_level:.3f} (using step ~{current_abs_step:.3f})")
             tuning_factor = adjustments.get('tuning_factor', 1.0)
             if abs(tuning_factor - 1.0) > 1e-9:
                  new_tune = max(MIN_TUNING_LEVEL, min(MAX_TUNING_LEVEL, self.tuning_level * tuning_factor))
                  if abs(new_tune - self.tuning_level) > 1e-9: self.tuning_level = new_tune; changed = True; print(f"Applied: Set tuning_level to {self.tuning_level:.3f} (factor {tuning_factor:.4f})")
             if not changed: print("No tuning parameters were changed.")
        else: print(f"\n--- Tuning Application Skipped (Status: {status}) ---")


    # --- Getters, Persistence, Visualization, Manual Control ---

    def get_latest_insight(self, min_importance: float = 0.6) -> Optional[Dict[str, Any]]:
         """ Retrieves the symbolic insight dict from the most recent important dream. """
         # (Implementation same as v1.0.9)
         if not self.memory: return None; sorted_memory = sorted(self.memory, key=lambda d: d.get('timestamp', 0), reverse=True)
         for dream in sorted_memory:
             importance = dream.get('importance_score', 0)
             if importance >= min_importance: return dream.get('dream_result')
         return None

    def save_memory(self) -> bool:
        """ Saves the dream memory and current parameters to JSON file. """
        # (Implementation same as v1.0.9)
        memory_to_save = {"metadata": {"save_timestamp": time.time(), "version": "1.1.1", "last_tuning_level": self.tuning_level, "last_dream_complexity": self.dream_complexity, "last_abstraction_level": self.abstraction_level, "max_memory_size": self.max_memory_size, "total_dreams_in_file": len(self.memory), "last_assessment_data": self._last_assessment_data, "recommendation_history": {k: list(v) for k, v in self._recommendation_history.items()} }, "dreams": self.memory }
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as file: json.dump(memory_to_save, file, indent=2, ensure_ascii=False)
            return True
        except (IOError, TypeError) as e: print(f"Error saving Machine Dream memory to {self.memory_file}: {e}", file=sys.stderr); return False

    def load_memory(self) -> bool:
        """ Loads dream memory and parameters including recommendation history. """
        # (Implementation same as v1.0.9)
        try:
            if not os.path.exists(self.memory_file): raise FileNotFoundError
            with open(self.memory_file, 'r', encoding='utf-8') as file: loaded_data = json.load(file)
            if isinstance(loaded_data, dict) and "dreams" in loaded_data and "metadata" in loaded_data:
                self.memory = loaded_data["dreams"]; metadata = loaded_data["metadata"]; file_version = metadata.get("version", "unknown")
                print(f"\nLoading Machine Dream Memory (Format Version: {file_version}) from {self.memory_file}.")
                self.tuning_level = metadata.get("last_tuning_level", self.tuning_level); self.dream_complexity = metadata.get("last_dream_complexity", metadata.get("last_refinement_depth", metadata.get("last_dream_depth", self.dream_complexity))); self.abstraction_level = metadata.get("last_abstraction_level", self.abstraction_level); self.max_memory_size = metadata.get("max_memory_size", self.max_memory_size); self._last_assessment_data = metadata.get("last_assessment_data", self._last_assessment_data)
                history_loaded = metadata.get("recommendation_history", {})
                for key in self._recommendation_history: self._recommendation_history[key] = deque(history_loaded.get(key, []), maxlen=RECOMMENDATION_HISTORY_LENGTH)
                print(f"Restored state: Dreams={len(self.memory)}, Tuning={self.tuning_level:.3f}, Complexity={self.dream_complexity}, Abstraction={self.abstraction_level:.3f}, MaxMem={self.max_memory_size}")
                return True
            elif isinstance(loaded_data, list): self.memory = loaded_data; print(f"Memory loaded from {self.memory_file} (legacy list format). State not restored."); return True
            else: print(f"Error: Unexpected data structure in {self.memory_file}.", file=sys.stderr); return False
        except FileNotFoundError: print(f"\nMachine Dream Memory file {self.memory_file} not found. Starting fresh."); self.memory = []; return True
        except (json.JSONDecodeError, IOError) as e: print(f"Error loading Machine Dream memory from {self.memory_file}: {e}", file=sys.stderr); return False

    def set_parameter(self, param_name: str, value: Union[int, float]) -> bool:
        """ Manually sets a dream parameter with validation/clamping using defined bounds. """
        # (Implementation same as v1.0.9)
        print(f"\n--- Manual Parameter Update ---"); try:
            if param_name == "complexity": new_val = max(MIN_COMPLEXITY, min(MAX_COMPLEXITY, int(value))); print(f"Setting dream_complexity from {self.dream_complexity} to {new_val}"); self.dream_complexity = new_val
            elif param_name == "abstraction": new_val = max(MIN_ABSTRACTION, min(MAX_ABSTRACTION, float(value))); print(f"Setting abstraction_level from {self.abstraction_level:.3f} to {new_val:.3f}"); self.abstraction_level = new_val
            elif param_name == "tuning": new_val = max(MIN_TUNING_LEVEL, min(MAX_TUNING_LEVEL, float(value))); print(f"Setting tuning_level from {self.tuning_level:.3f} to {new_val:.3f}"); self.tuning_level = new_val
            else: print(f"Error: Unknown parameter '{param_name}'."); return False
            return True
        except ValueError: print(f"Error: Invalid value '{value}'."); return False

    def clear_memory_and_state(self):
        """ Clears memory and resets tuning history. Keeps current parameters. """
        # (Implementation same as v1.0.9)
        print("\n--- Clearing Memory and Assessment State ---"); self.memory = []; self._last_assessment_data = None
        for key in self._recommendation_history: self._recommendation_history[key].clear()
        print("Memory cleared."); self.save_memory()

    # --- SVG Visualization (Optional artifact) ---
    # (SVG methods unchanged)
    def _generate_vector_from_memory(self, dimensions: int = 768) -> Optional[List[float]]:
        if not self.memory: return None; try: memory_str = json.dumps(self.memory, sort_keys=True, separators=(',', ':'))
        except TypeError: memory_str = str(self.memory); hasher = hashlib.sha256(memory_str.encode('utf-8')); seed = int.from_bytes(hasher.digest()[:8], 'big'); rng = random.Random(seed); return [rng.random() for _ in range(dimensions)]
    def generate_memory_vector_svg(self, filename: str = "memory_vector_symbolic.svg", dimensions: int = 768, cols: int = 32, square_size: int = 4, padding: int = 1) -> bool:
        if cols <= 0: print("Error: SVG columns must be positive.", file=sys.stderr); return False; vector = self._generate_vector_from_memory(dimensions)
        if vector is None: svg_content = f'<svg width="150" height="50" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#eee"/><text x="10" y="30" font-family="sans-serif" font-size="10" fill="#555">Memory Empty</text></svg>'
        else:
            if dimensions % cols != 0: rows = math.ceil(dimensions / cols); adjusted_dimensions = rows * cols; vector.extend([0.0] * (adjusted_dimensions - dimensions)); dimensions = adjusted_dimensions
            else: rows = dimensions // cols; svg_width = cols * (square_size + padding) + padding; svg_height = rows * (square_size + padding) + padding
            svg_elements = [f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">', f' <title>Memory State Vector ({VECTOR_DIMENSIONS}d Simulated)</title>', f' <desc>Visualization of MachineDream memory state. Hash seeded from content.</desc>', f' <rect width="100%" height="100%" fill="#f0f0f0"/>']
            for i, value in enumerate(vector):
                row = i // cols; col = i % cols; x = padding + col * (square_size + padding); y = padding + row * (square_size + padding); gray_level = max(0, min(255, int(value * 255))); color = f"rgb({gray_level},{gray_level},{gray_level})"
                svg_elements.append(f'  <rect x="{x}" y="{y}" width="{square_size}" height="{square_size}" fill="{color}"/>')
            svg_elements.append('</svg>'); svg_content = "\n".join(svg_elements)
        try: with open(filename, 'w', encoding='utf-8') as f: f.write(svg_content); print(f"Memory vector SVG saved to '{filename}'"); return True
        except IOError as e: print(f"Error writing SVG file '{filename}': {e}", file=sys.stderr); return False

    # --- Utility Feedback ---
    def record_insight_utility(self, dream_id: str, utility_score: float):
        """ Records a simulated utility score (0-1) for a specific dream insight. """
        # (Implementation same as v1.0.9)
        found = False; short_id = dream_id.split('_')[-1] if '_' in dream_id else dream_id
        for dream in self.memory:
             current_dream_id = dream.get("dream_id", "")
             if current_dream_id == dream_id or current_dream_id.endswith(f"_{short_id}"):
                  clamped_utility = round(max(0.0, min(1.0, utility_score)), 3)
                  dream["utility_score"] = clamped_utility
                  print(f"Recorded utility score {clamped_utility} for dream ending in '{short_id}' (ID: {current_dream_id})")
                  found = True; break
        if not found: print(f"Warning: Dream ID like '{dream_id}' not found to record utility.")


# --- Placeholder for External API Interaction ---
def call_external_multimodal_model(prompt: str, latest_insight: Optional[Dict[str, Any]] = None) -> Tuple[str, Optional[str]]:
    """ Placeholder function representing a call to an external model (e.g., Gemini). """
    # (Implementation same as v1.0.9)
    print("\n--- Calling External Multimodal Model (Placeholder) ---"); print(f"Prompt Received: {prompt[:100]}...")
    context_added = False; full_prompt = f"Task: {prompt}"; used_dream_id = None
    if latest_insight:
        symbolic_msg = latest_insight.get('symbolic_insight'); themes = latest_insight.get('key_themes', [])
        for dream in reversed(global_dream_machine.memory): # Use global instance
            if dream.get('dream_result') == latest_insight: used_dream_id = dream.get('dream_id'); break
        if symbolic_msg: full_prompt = f"Contextual Insight: \"{symbolic_msg}\" (Themes: {', '.join(themes)})\n\nTask: {prompt}"; context_added = True; print(f"Symbolic Insight Provided: \"{symbolic_msg}\" (From Dream: {used_dream_id})")
        else: print("No symbolic insight text found in provided context.")
    if not context_added: print("No specific insight context provided or applicable.")
    time.sleep(0.1); mock_response = f"Simulated response for '{prompt[:30]}...'. Context Used: {context_added}"
    print("--- External Model Response (Simulated) ---")
    simulated_utility = random.uniform(0.3, 0.9) if context_added else random.uniform(0.2, 0.6)
    print(f"(Simulated utility feedback for dream {used_dream_id}: {simulated_utility:.3f})")
    if used_dream_id: global_dream_machine.record_insight_utility(used_dream_id, simulated_utility)
    return mock_response, used_dream_id


# --- Command Line Interface for MachineDream Management ---

def run_interactive_loop(dream_machine: MachineDream, num_loops: int):
    """ Handles the interactive command-line loop for managing MachineDream. """
    # (Implementation mostly same as v1.0.9, added display of avg utility)
    loop_range = range(1, num_loops + 1) if num_loops > 0 else iter(int, 1)
    loop_desc = f"{num_loops} cycle(s)" if num_loops > 0 else "indefinitely"
    print(f"Running MachineDream interactively for {loop_desc}.")
    print("Commands: dream [id] [sz] [comp], status, insight [id], assess, tune_data, api [prompt], set <param> <value>, clear, exit")

    for i in loop_range:
        counter = i if num_loops > 0 else None
        prefix = f"[{counter}] " if counter is not None else ""
        try:
            command = input(f"\n{prefix}MachineDream> ").strip()
            parts = command.split(); action = parts[0].lower() if parts else ""
            if action == "exit": break
            elif action == "dream":
                data_id = parts[1] if len(parts) > 1 else f"interactive_{int(time.time())}"; size = int(parts[2]) if len(parts) > 2 else random.randint(500, 2500); comp = float(parts[3]) if len(parts) > 3 else round(random.uniform(0.3, 0.8), 1)
                metadata = {'id': data_id, 'type': 'interactive_input', 'raw_size': size, 'complexity': comp}; dream_machine.run_dream_cycle(metadata)
            elif action == "status":
                print("\n--- MachineDream Status ---"); print(f"  Memory Size: {len(dream_machine.memory)} / {dream_machine.max_memory_size}"); print(f"  Tuning Level: {dream_machine.tuning_level:.3f}"); print(f"  Dream Complexity: {dream_machine.dream_complexity}"); print(f"  Abstraction Level: {dream_machine.abstraction_level:.3f}")
                print(f"  Abs Tuning Step: {dream_machine.abs_tuning_step:.4f} (Base: {dream_machine.base_abs_tuning_step:.4f}) {'[DAMPED]' if dream_machine._is_abstraction_damped else ''}")
                if dream_machine._last_assessment_data:
                     metrics = dream_machine._last_assessment_data.get('metrics', {}); status = dream_machine._last_assessment_data.get('status', 'N/A'); mode = dream_machine._last_assessment_data.get('system_mode', 'N/A')
                     print(f"  Last Assessment Status: {status} / Mode: {mode}")
                     print(f"  Last Metrics: Imp={metrics.get('avg_importance', 'N/A')}(+/-{metrics.get('stdev_importance', 'N/A')}), Div={metrics.get('theme_diversity', 'N/A')}, Nov={metrics.get('avg_novelty', 'N/A')}(+/-{metrics.get('stdev_novelty', 'N/A')}), Util={metrics.get('avg_utility', 'N/A')}(+/-{metrics.get('stdev_utility', 'N/A')}), Osc(C/A):{metrics.get('complexity_oscillation', False)}/{metrics.get('abstraction_oscillation', False)}") # Added utility display
                else: print("  Last Assessment Status: Not available")
                print(f"  Rec History (Cmplx): {list(dream_machine._recommendation_history['complexity_adj'])}"); print(f"  Rec History (Abs):   {list(dream_machine._recommendation_history['abs_adj'])}")
            elif action == "insight":
                 if len(parts) > 1:
                     dream_id_to_find = parts[1]; found_insight = None; found_dream = None
                     for dream in reversed(dream_machine.memory):
                          current_dream_id = dream.get("dream_id", "");
                          if current_dream_id == dream_id_to_find or current_dream_id.endswith(f"_{dream_id_to_find}"): found_insight = dream.get("dream_result"); found_dream = dream; break
                     insight_result = found_insight;
                     if found_dream: print(f"\n--- Insight for Dream ID ending in '{dream_id_to_find}' (Score: {found_dream.get('importance_score', 'N/A'):.3f}, Utility: {found_dream.get('utility_score', 'N/A')}) ---")
                 else: print("\n--- Latest High-Importance Insight ---"); insight_result = dream_machine.get_latest_insight(min_importance=0.7)
                 if insight_result: print(f"  Symbolic Insight: \"{insight_result.get('symbolic_insight', 'N/A')}\"\n  Key Themes: {insight_result.get('key_themes', [])}\n  Synthesis Level: {insight_result.get('estimated_synthesis_level', 'N/A')}")
                 else: print("Insight not found or no recent high-importance insight (threshold 0.7).")
            elif action == "assess": print("\n--- Running Manual Assessment ---"); assessment_data = dream_machine.assess_state(); print("\n--- Assessment Data ---"); print(json.dumps(assessment_data, indent=2))
            elif action == "tune_data": print("\n--- Last Generated Tuning Data ---"); print(json.dumps(dream_machine._last_assessment_data, indent=2)) if dream_machine._last_assessment_data else print("No assessment data generated yet.")
            elif action == "api":
                 test_prompt = " ".join(parts[1:]) if len(parts) > 1 else "Generate plan based on recent insights."; latest_insight_data = dream_machine.get_latest_insight(min_importance=0.5)
                 response, _ = call_external_multimodal_model(test_prompt, latest_insight=latest_insight_data); print(f"\nAPI Response (Simulated):\n{response}")
            elif action == "set":
                 if len(parts) == 3:
                      param_name = parts[1].lower(); value_str = parts[2]
                      try:
                          if param_name == "complexity": value = int(value_str)
                          elif param_name in ["abstraction", "tuning"]: value = float(value_str)
                          else: raise ValueError("Unknown parameter")
                          dream_machine.set_parameter(param_name, value)
                      except ValueError: print(f"Error: Invalid parameter name or value format.")
                 else: print("Usage: set <complexity|abstraction|tuning> <value>")
            elif action == "clear":
                 confirm = input("Clear ALL dream memory and assessment history? (yes/no): ").lower()
                 if confirm == 'yes': dream_machine.clear_memory_and_state()
                 else: print("Clear cancelled.")
            elif not action: continue
            else: print(f"Unknown command: '{action}'.")

        except (EOFError, KeyboardInterrupt): print("\nExiting interactive mode."); break
        except Exception as e: print(f"Error during interactive command: {e}", file=sys.stderr)

    if num_loops > 0: print(f"\nFinished {num_loops} cycle(s).")


def main():
    """ Main execution handler focused on MachineDream simulation v1.1.1 """
    parser = argparse.ArgumentParser(description="MachineDream Engine v1.1.1. Simulates insight generation with utility feedback.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-n", "--num_loops", type=int, default=0, help="Number of automated dream cycles. (Default 0: interactive).")
    parser.add_argument("--max-memory", type=int, default=DEFAULT_MAX_MEMORY, help=f"Set max dream memory size (Default: {DEFAULT_MAX_MEMORY}).")
    parser.add_argument("--memory-file", type=str, default=DEFAULT_MEMORY_FILE, help=f"Specify memory file path (Default: {DEFAULT_MEMORY_FILE}).")
    parser.add_argument("--svg", action="store_true", help="Generate memory vector SVG visualization on exit (optional).")
    parser.add_argument("--init-complexity", type=int, help="Override initial dream complexity.")
    parser.add_argument("--init-abstraction", type=float, help="Override initial abstraction level (0.0-1.0).")
    parser.add_argument("--init-tuning", type=float, help="Override initial tuning level.")
    parser.add_argument("--abs-step", type=float, default=DEFAULT_ABS_TUNING_STEP, help=f"Base step size for abstraction tuning (Default: {DEFAULT_ABS_TUNING_STEP}).")
    parser.add_argument("--age-penalty", type=float, default=DEFAULT_AGE_PENALTY_FACTOR, help=f"Age penalty factor for pruning (Default: {DEFAULT_AGE_PENALTY_FACTOR}).")
    parser.add_argument("--damping-factor", type=float, default=DEFAULT_OSCILLATION_DAMPING_FACTOR, help=f"Factor to reduce step size on oscillation (Default: {DEFAULT_OSCILLATION_DAMPING_FACTOR}).")
    # Argument to override target ranges (parsing slightly complex)
    parser.add_argument("--target-ranges", type=str, default=None, help='Override target ranges as JSON string. Ex: \'{"importance": [0.4,0.8], "novelty": [0.2,0.6]}\'')

    args = parser.parse_args()

    # --- Initialize MachineDream ---
    init_kwargs = {"memory_file": args.memory_file, "max_memory_size": args.max_memory, "abs_tuning_step": args.abs_step, "age_penalty_factor": args.age_penalty, "oscillation_damping_factor": args.damping_factor}
    if args.init_complexity is not None: init_kwargs["initial_dream_complexity"] = args.init_complexity
    if args.init_abstraction is not None: init_kwargs["initial_abstraction_level"] = args.init_abstraction
    if args.init_tuning is not None: init_kwargs["initial_tuning_level"] = args.init_tuning
    # Parse target ranges if provided
    if args.target_ranges:
        try:
            custom_ranges = json.loads(args.target_ranges)
            # Validate format (basic check)
            if isinstance(custom_ranges, dict) and all(isinstance(v, list) and len(v) == 2 for v in custom_ranges.values()):
                # Merge with defaults (custom overrides default)
                merged_ranges = DEFAULT_TARGET_RANGES.copy()
                merged_ranges.update(custom_ranges)
                init_kwargs["target_ranges"] = merged_ranges
                print(f"Using custom target ranges: {init_kwargs['target_ranges']}")
            else: print("Warning: Invalid format for --target-ranges. Using defaults.", file=sys.stderr)
        except json.JSONDecodeError as e: print(f"Warning: Could not parse --target-ranges JSON: {e}. Using defaults.", file=sys.stderr)

    global global_dream_machine # Make instance global
    global_dream_machine = MachineDream(**init_kwargs)

    exit_code = 0
    try:
        if args.num_loops > 0:
            # Automated Mode
            print(f"--- MachineDream Automated Mode v1.1.1: Running {args.num_loops} cycles ---")
            for i in range(args.num_loops):
                print(f"\n--- Automated Cycle {i+1}/{args.num_loops} ---")
                base_comp = 0.6; comp_adj = (global_dream_machine.dream_complexity - 5) * 0.05; comp = round(max(0.1, min(1.0, base_comp + comp_adj + random.uniform(-0.1, 0.1))), 1)
                size = random.randint(800, 3000); dtype = random.choice(['logs', 'sim_results', 'feedback', 'sensors', 'images', 'text_corpus', 'code_changes', 'user_queries'])
                metadata = {'id': f"auto_cycle_{i+1}", 'type': dtype, 'raw_size': size, 'complexity': comp}
                result = global_dream_machine.run_dream_cycle(metadata)
                if result is None: print(f"Error occurred in cycle {i+1}. Stopping.", file=sys.stderr); exit_code = 1; break
                time.sleep(0.05)
            print(f"\n--- Finished {args.num_loops} automated cycles ---")
        else:
            # Interactive Mode
            print("--- MachineDream Interactive Mode v1.1.1 ---")
            run_interactive_loop(global_dream_machine, 0)

    finally:
        if args.svg: print("\n--- Post-execution SVG Generation ---"); global_dream_machine.generate_memory_vector_svg()
        print("\nSaving final Machine Dream state...")
        global_dream_machine.save_memory()
        print("MachineDream session ended.")
        sys.exit(exit_code)

if __name__ == "__main__":
    load_dotenv()
    main()
