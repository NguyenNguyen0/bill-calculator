from __future__ import annotations

import math
from typing import Sequence

from .constants import DEFAULT_ALGORITHM, SUPPORTED_ALGORITHMS
from .models import Person


class BillsCalculator:
    @staticmethod
    def round_money(amount: float) -> float:
        if amount < 1000:
            return math.ceil(amount)
        return math.ceil(int(amount) / 100) * 100

    def calculate_stair_algorithm(
        self,
        people: Sequence[Person],
        total_elec: float,
        total_water: float,
        total_days: int = 30,
    ) -> list[Person]:
        if not people:
            return list(people)

        min_stay_days = min(person.stay_days for person in people)
        total_bill = total_elec + total_water
        person_count = len(people)
        base_rate_per_day = total_bill / (person_count * total_days) if total_days > 0 and person_count > 0 else 0

        total_base_amount = 0.0
        for person in people:
            person.base_amount = min_stay_days * base_rate_per_day
            total_base_amount += person.base_amount

        total_excess_days = 0
        for person in people:
            person.excess_days = person.stay_days - min_stay_days
            total_excess_days += person.excess_days

        remaining_bill = total_bill - total_base_amount
        excess_rate_per_day = remaining_bill / total_excess_days if total_excess_days > 0 else 0

        for person in people:
            excess_amount = person.excess_days * excess_rate_per_day
            total_amount = person.base_amount + excess_amount

            ratio = total_amount / total_bill if total_bill > 0 else 0
            person.elec = self.round_money(total_elec * ratio) if total_elec else 0
            person.water = self.round_money(total_water * ratio) if total_water else 0

            if hasattr(person, "base_amount"):
                del person.base_amount
            if hasattr(person, "excess_days"):
                del person.excess_days

        return list(people)

    def calculate_ratio_algorithm(
        self,
        people: Sequence[Person],
        total_elec: float,
        total_water: float,
        total_days: int = 30,
    ) -> list[Person]:
        if not people:
            return list(people)

        total_stay_days = sum(person.stay_days for person in people)

        for person in people:
            ratio = person.stay_days / total_stay_days if total_stay_days > 0 else 0
            person.elec = self.round_money(total_elec * ratio) if total_elec else 0
            person.water = self.round_money(total_water * ratio) if total_water else 0

        return list(people)

    def calculate_equal_algorithm(
        self,
        people: Sequence[Person],
        total_elec: float,
        total_water: float,
        total_days: int = 30,
    ) -> list[Person]:
        if not people:
            return list(people)

        person_count = len(people)
        for person in people:
            person.elec = self.round_money(total_elec / person_count) if total_elec else 0
            person.water = self.round_money(total_water / person_count) if total_water else 0

        return list(people)

    def calculate_bills(
        self,
        people: Sequence[Person],
        total_elec: float,
        total_water: float,
        total_days: int = 30,
        algorithm: str = DEFAULT_ALGORITHM,
    ) -> list[Person]:
        if algorithm == "stair":
            return self.calculate_stair_algorithm(people, total_elec, total_water, total_days)
        if algorithm == "ratio":
            return self.calculate_ratio_algorithm(people, total_elec, total_water, total_days)
        if algorithm == "equal":
            return self.calculate_equal_algorithm(people, total_elec, total_water, total_days)
        raise ValueError(f"Unknown algorithm: {algorithm}. Use {', '.join(sorted(SUPPORTED_ALGORITHMS))}.")

    def parse_people_input(self, people_input: Sequence[str]) -> list[Person]:
        result: list[Person] = []
        for item in people_input:
            if "=" in item:
                try:
                    name, days = item.split("=")
                    result.append(Person(name.strip(), stay_days=int(days)))
                except ValueError as exc:
                    raise ValueError(f"Invalid format: {item}. Use name=days or just name.") from exc
            else:
                result.append(Person(item.strip(), 0))

        return result
