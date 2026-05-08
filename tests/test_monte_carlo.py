import pytest

from mock_market import get_market_snapshot
from deriv_pricer.engines.analytic import price as analytic_price
from deriv_pricer.engines.monte_carlo import price as mc_price
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


def test_mc_converges_to_analytic(setup):
    opt, model, t = setup
    bs = analytic_price(opt, model, t)
    mc = mc_price(opt, model, t, n_paths=200_000)
    assert abs(mc - bs) / bs < 0.01


def test_mc_convergence_improves_with_more_paths(setup):
    opt, model, t = setup
    bs = analytic_price(opt, model, t)
    err_low = abs(mc_price(opt, model, t, n_paths=10_000) - bs)
    err_high = abs(mc_price(opt, model, t, n_paths=100_000) - bs)
    assert err_high < err_low
