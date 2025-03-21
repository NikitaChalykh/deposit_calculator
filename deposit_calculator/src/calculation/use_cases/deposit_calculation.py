from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from collections import OrderedDict
from calendar import monthrange

from ..models import DepositCalculationRequestModel


class DepositCalculationCase:
    """
    Case api for calculating the deposit amount.
    """

    def __call__(self, payload: DepositCalculationRequestModel) -> dict:
        calc_amount: Decimal = payload.amount
        calc_date: date = payload.date
        calc_rate: Decimal = Decimal(payload.rate)

        result_deposit_calculation = OrderedDict()

        for _ in range(payload.periods):
            # рассчитываем сумму депозита за период
            calc_amount = calc_amount * (1 + calc_rate / (12 * 100))

            # сериализуем и сохраняем данные по сумме депозита за период
            self._add_deposit_calculation_data(
                calc_date=calc_date,
                calc_amount=calc_amount,
                result_deposit_calculation=result_deposit_calculation,
            )

            # обновляем дату для следующего расчетного периода
            calc_date = self._update_calc_date(calc_date)

        return result_deposit_calculation

    @staticmethod
    def _add_deposit_calculation_data(
        calc_date: date,
        calc_amount: Decimal,
        result_deposit_calculation: dict,
    ) -> None:
        """
        Append the serialized entry to the resulting dictionary.
        """

        form_calc_date = datetime.strftime(calc_date, "%d.%m.%Y")
        form_calc_amount = calc_amount.quantize(Decimal("1.00"), ROUND_HALF_UP)

        result_deposit_calculation.update({form_calc_date: form_calc_amount})

    @staticmethod
    def _update_calc_date(calc_date: date) -> date:
        """
        Updates the next period's settlement date.
        """

        calc_date_year = calc_date.year
        calc_date_month = calc_date.month + 1
        if calc_date_month > 12:
            calc_date_month = 1
            calc_date_year += 1

        _, days_in_month = monthrange(calc_date_year, calc_date_month)

        return calc_date + timedelta(days=days_in_month)
