from decimal import Decimal
import logging
import re
from typing import Dict
import httpx
from app.core.config import settings
from app.domain.interfaces import IExchangeRateProvider
from app.domain.models import Currency

logger = logging.getLogger(__name__)


class ApiExchangeRateProvider(IExchangeRateProvider):

    def __init__(self, endpoint_url: str = settings.EXCHANGE_RATE_API_URL):
        self._endpoint_url = endpoint_url

    def get_rates_to_usd(self) -> Dict[Currency, Decimal]:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(self._endpoint_url)
                if response.status_code == 200:
                    data = response.json()
                    rates_dict = data.get("rates", {})
                    if rates_dict:
                        return {
                            cur: Decimal(str(rates_dict.get(cur.value, "1.0")))
                            for cur in Currency
                        }
                    return self._parse_rates_fallback(response.text)
        except Exception as exc:
            logger.warning(
                "Не удалось получить курсы валют из внешнего API: %s. Используются резервные.",
                exc,
            )
        return self._fallback_rates()

    def _parse_rates_fallback(self, text: str) -> Dict[Currency, Decimal]:
        rates: Dict[Currency, Decimal] = {Currency.USD: Decimal("1.00")}
        for currency in Currency:
            if currency != Currency.USD:
                pattern = rf'"{currency.value}"\s*:\s*([0-9.]+)'
                match = re.search(pattern, text)
                if match:
                    rates[currency] = Decimal(match.group(1))
        return rates

    @staticmethod
    def _fallback_rates() -> Dict[Currency, Decimal]:
        return {
            Currency.USD: Decimal("1.00"),
            Currency.RUB: Decimal("92.00"),
            Currency.AMD: Decimal("390.00"),
        }