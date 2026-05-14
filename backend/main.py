from fastapi import FastAPI
from datetime import date
from pydantic import BaseModel
from deriv_pricer.models.black_scholes import BSModel
from deriv_pricer.instruments.european import EuropeanOption, OptionType
from deriv_pricer.engines.analytic import price
from deriv_pricer.greeks import bump
from deriv_pricer.analysis.scenario import price_scenarios
from deriv_pricer.analysis.sensitivity import sensitivity

app = FastAPI()

class PriceRequest(BaseModel):
    underlying: str
    option_type: str
    strike: float
    expiry: date
    spot: float
    rate: float
    div_yield: float
    sigma: float


def build_from_request(req: PriceRequest):
    option = EuropeanOption(
        underlying=req.underlying,
        option_type=OptionType.CALL if req.option_type == "call" else OptionType.PUT,
        strike=req.strike,
        expiry=req.expiry,
    )
    model = BSModel(req.spot, req.rate, req.div_yield, req.sigma)
    time = (req.expiry - date.today()).days / 365
    return option, model, time


@app.post("/price_option")
def price_option(req: PriceRequest):
    option, model, time = build_from_request(req)
    return {"price": price(option, model, time), "time": time}


@app.post("/compute_greeks")
def compute_greeks(req: PriceRequest):
    option, model, time = build_from_request(req)
    return {
        "delta": bump.delta(option, model, time),
        "gamma": bump.gamma(option, model, time),
        "vega":  bump.vega(option, model, time),
        "theta": bump.theta(option, model, time),
        "rho":   bump.rho(option, model, time),
    }


class ScenarioRequest(BaseModel):
    underlying: str
    option_type: str
    strike: float
    expiry: date
    spot: float
    rate: float
    div_yield: float
    sigma: float
    scenarios: list[dict]


class SensitivityRequest(BaseModel):
    underlying: str
    option_type: str
    strike: float
    expiry: date
    spot: float
    rate: float
    div_yield: float
    sigma: float
    parameter: str
    range_min: float
    range_max: float
    steps: int


@app.post("/price_scenario")
def price_scenario(req: ScenarioRequest):
    option, model, time = build_from_request(req)
    prices = price_scenarios(option, model, time, req.scenarios)
    return {"scenarios": [{"scenario": s, "price": p} for s, p in zip(req.scenarios, prices)]}


@app.post("/sensitivity")
def sensitivity_endpoint(req: SensitivityRequest):
    option, model, time = build_from_request(req)
    series = sensitivity(option, model, time, req.parameter, req.range_min, req.range_max, req.steps)
    return {"parameter": req.parameter, "series": series}