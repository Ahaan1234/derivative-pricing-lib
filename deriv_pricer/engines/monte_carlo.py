import math

import numpy as np

from deriv_pricer.models.black_scholes import BSModel


def price(
    option, model: BSModel, t: float, n_paths: int = 50_000, seed: int = 42
) -> float:
    """Monte Carlo price with antithetic variates for variance reduction."""
    rng = np.random.default_rng(seed)
    S, K = model.spot, option.strike
    r, q, sigma = model.rate, model.div_yield, model.sigma

    half = n_paths // 2
    Z = rng.standard_normal(half)
    drift = (r - q - 0.5 * sigma**2) * t
    diffusion = sigma * math.sqrt(t)

    S_T_pos = S * np.exp(drift + diffusion * Z)
    S_T_neg = S * np.exp(drift - diffusion * Z)

    is_call = str(option.option_type) == "call"
    if is_call:
        payoffs = np.concatenate(
            [np.maximum(S_T_pos - K, 0.0), np.maximum(S_T_neg - K, 0.0)]
        )
    else:
        payoffs = np.concatenate(
            [np.maximum(K - S_T_pos, 0.0), np.maximum(K - S_T_neg, 0.0)]
        )

    return math.exp(-r * t) * float(np.mean(payoffs))
