import dataclasses

from deriv_pricer.engines import analytic
from deriv_pricer.models.black_scholes import BSModel


def delta(option, model: BSModel, t: float, h: float = 0.01) -> float:
    """Central-difference delta: dP/dS."""
    up = analytic.price(option, dataclasses.replace(model, spot=model.spot + h), t)
    dn = analytic.price(option, dataclasses.replace(model, spot=model.spot - h), t)
    return (up - dn) / (2 * h)


def gamma(option, model: BSModel, t: float, h: float = 0.01) -> float:
    """Central-difference gamma: d²P/dS²."""
    mid = analytic.price(option, model, t)
    up = analytic.price(option, dataclasses.replace(model, spot=model.spot + h), t)
    dn = analytic.price(option, dataclasses.replace(model, spot=model.spot - h), t)
    return (up - 2 * mid + dn) / h**2


def vega(option, model: BSModel, t: float, h: float = 0.0001) -> float:
    """Central-difference vega per 1 vol point (divide by 100)."""
    up = analytic.price(option, dataclasses.replace(model, sigma=model.sigma + h), t)
    dn = analytic.price(option, dataclasses.replace(model, sigma=model.sigma - h), t)
    return (up - dn) / (2 * h) / 100


def theta(option, model: BSModel, t: float, h: float = 1 / 365) -> float:
    """Backward-difference theta per calendar day."""
    return (analytic.price(option, model, t - h) - analytic.price(option, model, t)) / h


def rho(option, model: BSModel, t: float, h: float = 0.0001) -> float:
    """Central-difference rho per 1 basis point (divide by 10000)."""
    up = analytic.price(option, dataclasses.replace(model, rate=model.rate + h), t)
    dn = analytic.price(option, dataclasses.replace(model, rate=model.rate - h), t)
    return (up - dn) / (2 * h) / 10000
