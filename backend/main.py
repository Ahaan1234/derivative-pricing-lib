from fastapi import FastAPI
from datetime import date
from pydantic import BaseModel
from deriv_pricer.models.black_scholes import BSModel
from deriv_pricer.instruments.european import EuropeanOption, OptionType
from deriv_pricer.engines.analytic import price
from deriv_pricer.greeks import bump

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