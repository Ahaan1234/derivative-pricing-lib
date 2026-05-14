import dataclasses

from deriv_pricer.engines import analytic
from deriv_pricer.models.black_scholes import BSModel


def price_scenarios(opt, model: BSModel, t: float, scenarios: list[dict]) -> list[float]:
    """Price opt under each scenario, where each scenario is a partial BSModel override."""
    return [analytic.price(opt, dataclasses.replace(model, **s), t) for s in scenarios]
