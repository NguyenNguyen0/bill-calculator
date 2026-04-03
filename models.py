class Person:
    def __init__(self, name, stay_days=0):
        self.name = name
        self.stay_days = stay_days
        self.elec = 0
        self.water = 0
    
    @classmethod
    def from_dict(cls, data):
        person = cls(name=data["name"], stay_days=data["stay_days"])
        if "elec" in data:
            person.elec = data["elec"]
        if "water" in data:
            person.water = data["water"]
        return person

    def __repr__(self):
        return (
            f"Person(name={self.name!r}, stay_days={self.stay_days}, "
            f"elec={self.elec}, water={self.water})"
        )
    
    def to_dict(self):
        return {
            "name": self.name,
            "stay_days": self.stay_days,
            "elec": self.elec,
            "water": self.water
        }


class BillsData:
    def __init__(self, year=None, month=None, electricity=0, water=0, people=None, algorithm="ratio"):
        self.year = year
        self.month = month
        self.electricity = electricity
        self.water = water
        self.people = people if people else []
        self.algorithm = algorithm

    def to_dict(self):
        return {
            "year": self.year,
            "month": self.month,
            "electricity": self.electricity,
            "water": self.water,
            "algorithm": self.algorithm,
            "people": [person.to_dict() for person in self.people],
        }