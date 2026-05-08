"""
mock_market.py
--------------
Tiny self-contained mock data source for a derivative pricing library.

Scenario: one fictional stock (ACME Corp, ticker "ACM") with a single
European call option expiring in 3 months.  Everything is hardcoded so
there are no external dependencies and no network calls.

Usage
-----
    from mock_market import get_spot, get_rate, get_vol_surface, get_instrument

    spot   = get_spot()           # float
    rate   = get_rate()           # flat continuously-compounded rate
    vols   = get_vol_surface()    # dict[(strike, maturity)] -> implied_vol
    option = get_instrument()     # dict describing the European call
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Tuple


# ---------------------------------------------------------------------------
# Market snapshot
# ---------------------------------------------------------------------------

VALUATION_DATE: date = date(2024, 1, 15)

# Spot price of ACME Corp
_SPOT: float = 100.0

# Flat, continuously-compounded risk-free rate (annual)
_RATE: float = 0.05

# Flat continuous dividend yield
_DIV_YIELD: float = 0.01


def get_spot() -> float:
    """Current spot price of ACM."""
    return _SPOT


def get_rate() -> float:
    """Flat continuously-compounded risk-free rate."""
    return _RATE


def get_div_yield() -> float:
    """Flat continuous dividend yield."""
    return _DIV_YIELD


# Vol surface  (strike x maturity -> implied vol)
# 3 strikes x 2 maturities — enough to test interpolation

# Key: (strike, time_to_expiry_years)
# Value: Black-Scholes implied volatility (annualised, decimal)
_VOL_SURFACE: Dict[Tuple[float, float], float] = {
    # 1-month slice  (T = 1/12)
    (90.0,  1/12): 0.24,   # ITM  — higher vol (skew)
    (100.0, 1/12): 0.20,   # ATM
    (110.0, 1/12): 0.18,   # OTM  — lower vol

    # 3-month slice  (T = 3/12)
    (90.0,  3/12): 0.23,
    (100.0, 3/12): 0.20,   # ATM 3M — the "main" contract lives here
    (110.0, 3/12): 0.18,
}


def get_vol_surface() -> Dict[Tuple[float, float], float]:
    """
    Returns the full vol surface as a dict.

    Keys are (strike: float, time_to_expiry_years: float).
    Values are annualised Black-Scholes implied vols.
    """
    return dict(_VOL_SURFACE)


def get_atm_vol(time_to_expiry: float = 3/12) -> float:
    """Convenience: ATM implied vol for a given maturity (nearest grid point)."""
    return _VOL_SURFACE[(100.0, time_to_expiry)]


# Instrument definition

@dataclass
class EuropeanOption:
    """A plain European call or put on a single underlying."""
    underlying:    str    # ticker
    option_type:   str    # "call" or "put"
    strike:        float
    expiry:        date
    notional:      float = 1.0      # number of contracts / shares

    # Derived at construction
    time_to_expiry: float = field(init=False)

    def __post_init__(self):
        delta = (self.expiry - VALUATION_DATE).days
        self.time_to_expiry = delta / 365.0

    def __repr__(self):
        return (
            f"EuropeanOption({self.option_type.upper()} "
            f"{self.underlying} K={self.strike} "
            f"T={self.time_to_expiry:.4f}y)"
        )


def get_instrument() -> EuropeanOption:
    """
    The one contract in our mock book:
    ACM European call, strike 100, expiry ~3 months from valuation date.
    """
    return EuropeanOption(
        underlying  = "ACM",
        option_type = "call",
        strike      = 100.0,
        expiry      = date(2024, 4, 15),   # exactly 91 days out
        notional    = 1.0,
    )


# Convenience bundle

@dataclass
class MarketSnapshot:
    """Everything a pricer needs, collected in one place."""
    valuation_date: date
    spot:           float
    rate:           float
    div_yield:      float
    vol_surface:    Dict[Tuple[float, float], float]
    instrument:     EuropeanOption


def get_market_snapshot() -> MarketSnapshot:
    """Return the full mock market state as a single object."""
    return MarketSnapshot(
        valuation_date = VALUATION_DATE,
        spot           = get_spot(),
        rate           = get_rate(),
        div_yield      = get_div_yield(),
        vol_surface    = get_vol_surface(),
        instrument     = get_instrument(),
    )


# Quick sanity check

if __name__ == "__main__":
    snap = get_market_snapshot()
    print(f"Valuation date : {snap.valuation_date}")
    print(f"Instrument     : {snap.instrument}")
    print(f"Spot           : {snap.spot}")
    print(f"Rate           : {snap.rate:.2%}")
    print(f"Div yield      : {snap.div_yield:.2%}")
    print(f"Time to expiry : {snap.instrument.time_to_expiry:.4f} years")
    print()
    print("Vol surface:")
    for (K, T), vol in sorted(snap.vol_surface.items()):
        print(f"  K={K:6.1f}  T={T:.4f}  IV={vol:.2%}")