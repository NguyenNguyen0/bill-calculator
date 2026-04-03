from __future__ import annotations

from bills_calculator.core.models import Person


class Storage:
    @staticmethod
    def save_people_info(people: list[Person], filename: str = "people_info.txt") -> None:
        with open(filename, "w", encoding="utf-8") as file_handle:
            for person in people:
                file_handle.write(f"{person.name}={person.stay_days}\n")

    @staticmethod
    def load_people_info(filename: str = "people_info.txt") -> list[Person]:
        people: list[Person] = []
        try:
            with open(filename, "r", encoding="utf-8") as file_handle:
                for line in file_handle:
                    line = line.strip()
                    if line and "=" in line:
                        name, stay_days = line.split("=", 1)
                        people.append(Person(name.strip(), int(stay_days)))
                    elif line:
                        people.append(Person(line.strip(), 0))
        except FileNotFoundError:
            return []

        return people
