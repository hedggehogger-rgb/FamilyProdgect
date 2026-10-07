from decimal import Decimal, ROUND_HALF_UP
from typing import Dict
from app.domain.interfaces import IExchangeRateProvider
from app.domain.models import Currency


class CurrencyConverter:

    def __init__(self, provider: IExchangeRateProvider):
        self._provider = provider
        self._rates_to_usd: Dict[Currency, Decimal] = {}
        self.refresh_rates()

    def refresh_rates(self) -> None:
        self._rates_to_usd = self._provider.get_rates_to_usd()

    def convert(
        self, amount: Decimal, from_cur: Currency, to_cur: Currency
    ) -> Decimal:
        if from_cur == to_cur:
            return amount

        rate_from = self._rates_to_usd.get(from_cur, Decimal("1.00"))
        rate_to = self._rates_to_usd.get(to_cur, Decimal("1.00"))

        converted = (amount / rate_from) * rate_to
        return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)