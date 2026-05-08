import math

from scipy.stats import norm

from deriv_pricer.models.black_scholes import BSModel


def price(option, model: BSModel, t: float) -> float:
    """Black-Scholes-Merton closed-form price with continuous dividend yield."""
    if t <= 0:
        raise ValueError(f"t must be positive, got {t}")
    if model.sigma <= 0:
        raise ValueError(f"sigma must be positive, got {model.sigma}")

    S, K = model.spot, option.strike
    r, q, sigma = model.rate, model.div_yield, model.sigma

    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)

    if str(option.option_type) == "call":
        return S * math.exp(-q * t) * norm.cdf(d1) - K * math.exp(-r * t) * norm.cdf(d2)
    else:
        return K * math.exp(-r * t) * norm.cdf(-d2) - S * math.exp(-q * t) * norm.cdf(-d1)
