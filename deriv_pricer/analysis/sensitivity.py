import dataclasses

import numpy as np

from deriv_pricer.engines import analytic
from deriv_pricer.models.black_scholes import BSModel

_VALID = {"spot", "rate", "div_yield", "sigma"}


def sensitivity(
    opt,
    model: BSModel,
    t: float,
    parameter: str,
    range_min: float,
    range_max: float,
    steps: int,
) -> list[dict]:
    """Return price series over evenly-spaced values of one BSModel parameter."""
    if parameter not in _VALID:
        raise ValueError(f"parameter must be one of {_VALID}, got {parameter!r}")
    return [
        {"parameter_value": float(v), "price": analytic.price(opt, dataclasses.replace(model, **{parameter: float(v)}), t)}
        for v in np.linspace(range_min, range_max, steps)
    ]
