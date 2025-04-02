from dataclasses import dataclass
from ..config import (
    SIM_TIME,
    CHECKIN_DESKS,
    SECURITY_LANES,
    PASSPORT_BOOTHS,
    PASSPORT_EGATES,
    ONLINE_CHECKIN_RATE,
    CARRYON_ONLY_RATE,
    EGATE_ELIGIBLE_RATE,
)


@dataclass
class SimulationParameters:
    """Stores and validates simulation parameters"""

    def __init__(self, **kwargs):
        self.params = {
            "sim_duration": SIM_TIME,
            "num_checkin_desks": CHECKIN_DESKS,
            "num_security_lanes": SECURITY_LANES,
            "num_passport_booths": PASSPORT_BOOTHS,
            "num_egates": PASSPORT_EGATES,
            "online_checkin_rate": ONLINE_CHECKIN_RATE,
            "carryon_only_rate": CARRYON_ONLY_RATE,
            "egate_eligible_rate": EGATE_ELIGIBLE_RATE,
        }
        # Update with provided parameters
        self.params.update(kwargs)

    @property
    def sim_duration(self):
        """Get simulation duration"""
        return self.params["sim_duration"]

    def __getitem__(self, key):
        return self.params[key]

    def update(self, **kwargs):
        """Update parameters"""
        self.params.update(kwargs)
        self.validate()

    def validate(self):
        """Validate parameter values"""
        assert self.params["sim_duration"] > 0, "Simulation duration must be positive"
        assert (
            self.params["num_checkin_desks"] > 0
        ), "Number of check-in desks must be positive"
        assert (
            self.params["num_security_lanes"] > 0
        ), "Number of security lanes must be positive"
        assert (
            self.params["num_passport_booths"] > 0
        ), "Number of passport booths must be positive"
        assert (
            0 <= self.params["online_checkin_rate"] <= 1
        ), "Online check-in rate must be between 0 and 1"
        assert (
            0 <= self.params["carryon_only_rate"] <= 1
        ), "Carry-on only rate must be between 0 and 1"
        assert (
            0 <= self.params["egate_eligible_rate"] <= 1
        ), "E-gate eligible rate must be between 0 and 1"
