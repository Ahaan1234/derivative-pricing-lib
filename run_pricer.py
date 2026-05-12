from datetime import date
from deriv_pricer.instruments.european import EuropeanOption, OptionType
from deriv_pricer.models.black_scholes import BSModel
from deriv_pricer.engines.analytic import price

opt = EuropeanOption(
    underlying="ACM",
    option_type=OptionType.CALL,
    strike=100.0,
    expiry=date(2024, 4, 15),
)
model = BSModel(spot=100.0, rate=0.05, div_yield=0.01, sigma=0.20)
t = 91 / 365

print(price(opt, model, t))

# observations: 
#   `t` should be computed, not passed by the agent. 
#       It's (expiry - today) / 365 — deterministic given the expiry date. 
#       Your API endpoint should compute it internally so the LLM never has to reason about it. 
#   `underlying` looks like it's just a label right now. 
#       In the real system it'll likely need to resolve to a live spot price. 
#       That's where your market data tool comes in later, but for now hardcoding spot as is fine.
#   The `OptionType` enum is the first schema decision. 
#       In the tool definition, this becomes "enum": ["call", "put"] 
#       and you map it to OptionType.CALL / OptionType.PUT inside the endpoint. 
#       The LLM never sees the Python enum.

