from fastapi import FastAPI
from datetime import date
from pydantic import BaseModel
from deriv_pricer.models.black_scholes import BSModel
from deriv_pricer.instruments.european import EuropeanOption, OptionType
from deriv_pricer.engines.analytic import price

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


@app.post("/price_option")
def price_option(req: PriceRequest):
    option = EuropeanOption(
        underlying=req.underlying,
        option_type=OptionType.CALL if req.option_type == "call" else OptionType.PUT,
        strike=req.strike,
        expiry=req.expiry,
    )

    model = BSModel(req.spot, req.rate, req.div_yield, req.sigma)
    t = (req.expiry - date.today()).days/365
    result = price(option, model, t)
    return {"price: ": result, "t": t}