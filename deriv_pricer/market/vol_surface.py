import bisect
from typing import Dict, Tuple


class VolSurface:
    """Bilinear interpolation over a (strike, time_to_expiry) vol grid."""

    def __init__(self, grid: Dict[Tuple[float, float], float], spot: float = 100.0):
        """Initialise from a {(strike, tte): implied_vol} dict."""
        self._grid = grid
        self._spot = spot
        self._strikes = sorted({k for k, _ in grid})
        self._maturities = sorted({t for _, t in grid})

    def get_vol(self, strike: float, time_to_expiry: float) -> float:
        """Bilinear interpolation; clamps to grid boundaries."""
        K = max(self._strikes[0], min(self._strikes[-1], strike))
        T = max(self._maturities[0], min(self._maturities[-1], time_to_expiry))

        ki = bisect.bisect_right(self._strikes, K)
        ki = max(1, min(ki, len(self._strikes) - 1))
        k0, k1 = self._strikes[ki - 1], self._strikes[ki]

        ti = bisect.bisect_right(self._maturities, T)
        ti = max(1, min(ti, len(self._maturities) - 1))
        t0, t1 = self._maturities[ti - 1], self._maturities[ti]

        wk = (K - k0) / (k1 - k0) if k1 != k0 else 0.0
        wt = (T - t0) / (t1 - t0) if t1 != t0 else 0.0

        v00 = self._grid[(k0, t0)]
        v10 = self._grid[(k1, t0)]
        v01 = self._grid[(k0, t1)]
        v11 = self._grid[(k1, t1)]

        return (
            (1 - wk) * (1 - wt) * v00
            + wk * (1 - wt) * v10
            + (1 - wk) * wt * v01
            + wk * wt * v11
        )

    def atm_vol(self, time_to_expiry: float) -> float:
        """Convenience wrapper: vol at spot strike."""
        return self.get_vol(self._spot, time_to_expiry)
