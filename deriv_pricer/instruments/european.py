from dataclasses import dataclass
from datetime import date
from enum import Enum


class OptionType(str, Enum):
    """Call or put option type."""

    CALL = "call"
    PUT = "put"


@dataclass
class EuropeanOption:
    """European vanilla option."""

    underlying: str
    option_type: OptionType
    strike: float
    expiry: date
    notional: float = 1.0

    def time_to_expiry(self, valuation_date: date) -> float:
        """Returns (expiry - valuation_date).days / 365.0."""
        return (self.expiry - valuation_date).days / 365.0

    def payoff(self, spot_at_expiry: float) -> float:
        """Intrinsic payoff at expiry."""
        if self.option_type == OptionType.CALL:
            return max(spot_at_expiry - self.strike, 0.0)
        return max(self.strike - spot_at_expiry, 0.0)
