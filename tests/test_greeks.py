import pytest

from mock_market import get_market_snapshot
from deriv_pricer.greeks.bump import delta, gamma, vega, theta, rho
from deriv_pricer.market.vol_surface import VolSurface
from deriv_pricer.models.black_scholes import BSModel


@pytest.fixture
def setup():
    snap = get_market_snapshot()
    opt = snap.instrument
    surf = VolSurface(snap.vol_surface, snap.spot)
    t = opt.time_to_expiry
    sigma = surf.get_vol(opt.strike, t)
    model = BSModel(snap.spot, snap.rate, snap.div_yield, sigma)
    return opt, model, t


def test_delta_in_unit_interval(setup):
    opt, model, t = setup
    d = delta(opt, model, t)
    assert 0 < d < 1


def test_gamma_positive(setup):
    opt, model, t = setup
    assert gamma(opt, model, t) > 0


def test_vega_positive(setup):
    opt, model, t = setup
    assert vega(opt, model, t) > 0


def test_theta_negative(setup):
    opt, model, t = setup
    assert theta(opt, model, t) < 0
