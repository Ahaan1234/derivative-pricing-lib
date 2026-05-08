from dataclasses import dataclass


@dataclass
class BSModel:
    """Black-Scholes-Merton model parameters."""

    spot: float
    rate: float
    div_yield: float
    sigma: float
