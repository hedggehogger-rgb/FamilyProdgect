from decimal import Decimal
import re
from typing import Dict
import httpx
from app.core.config import settings
from app.domain.interfaces import IExchangeRateProvider
from app.domain.models import Currency


class ApiExchangeRateProvider(IExchangeRateProvider):

    def __init__(self, endpoint_url: str = settings.EXCHANGE_RATE_API_URL):
        self._endpoint_url = endpoint_url

    def get_rates_to_usd(self) -> Dict[Currency, Decimal]:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(self._endpoint_url)
                if response.status_code == 200:
                    return self._parse_rates(response.text)
        except Exception:
            pass
        return self._fallback_rates()

    def _parse_rates(self, text: str) -> Dict[Currency, Decimal]:
        rates: Dict[Currency, Decimal] = {Currency.USD: Decimal("1.00")}
        for currency in Currency:
            if currency != Currency.USD:
                pattern = rf'"{currency.value}"\s*:\s*([0-9.]+)'
                match = re.search(pattern, text)
                if match:
                    rates[currency] = Decimal(match.group(1))
        return rates

    def _fallback_rates(self) -> Dict[Currency, Decimal]:
        return {
            Currency.USD: Decimal("1.00"),
            Currency.RUB: Decimal("92.00"),
            Currency.AMD: Decimal("390.00"),
        }