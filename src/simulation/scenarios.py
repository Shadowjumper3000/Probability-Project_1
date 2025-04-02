from copy import deepcopy
from ..utils.sim_params import SimulationParameters
from ..utils.logger import setup_logger


class ScenarioManager:
    """Manages different simulation scenarios"""

    def __init__(self):
        self.logger = setup_logger("scenario_manager")
        self.base_params = SimulationParameters()
        self.results = {}

    def run_scenario(self, name, sim_class, **param_changes):
        """Run a simulation scenario with modified parameters"""
        self.logger.info(f"Running scenario: {name}")

        # Create scenario parameters
        scenario_params = deepcopy(self.base_params)
        scenario_params.update(**param_changes)
        scenario_params.validate()

        # Run simulation
        sim = sim_class(scenario_params)
        results = sim.run()

        # Store results
        self.results[name] = {"params": scenario_params.params, "results": results}

        return results
