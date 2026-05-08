import math

import pytest

from mock_market import get_market_snapshot
from deriv_pricer.engines.analytic import price
from deriv_pricer.market.vol_surface import VolSurface
from deriv_pricer.models.black_scholes import BSModel


@pytest.fixture
def snap():
    return get_market_snapshot()


@pytest.fixture
def setup(snap):
    opt = snap.instrument
    surf = VolSurface(snap.vol_surface, snap.spot)
    t = opt.time_to_expiry
    sigma = surf.get_vol(opt.strike, t)
    model = BSModel(snap.spot, snap.rate, snap.div_yield, sigma)
    return opt, model, t


def test_call_price_near_known_value(setup):
    opt, model, t = setup
    call_price = price(opt, model, t)
    # S=100, K=100, T≈0.249, r=0.05, q=0.01, σ=0.20 → ~4.47
    assert abs(call_price - 4.47) < 0.01


def test_put_call_parity(setup):
    opt, model, t = setup
    import dataclasses
    from deriv_pricer.instruments.european import EuropeanOption, OptionType

    put_opt = EuropeanOption(
        underlying=opt.underlying,
        option_type=OptionType.PUT,
        strike=opt.strike,
        expiry=opt.expiry,
    )
    C = price(opt, model, t)
    P = price(put_opt, model, t)
    S, K, r, q = model.spot, opt.strike, model.rate, model.div_yield
    parity = S * math.exp(-q * t) - K * math.exp(-r * t)
    assert abs((C - P) - parity) < 1e-10
