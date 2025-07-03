class Person:
    def __init__(self, name, stay_days=0):
        self.name = name
        self.stay_days = stay_days
        self.elec = 0
        self.water = 0
    
    @classmethod
    def from_dict(cls, data):
        person = cls(name=data["name"], stay_days=data["stay_days"])
        if "stay_days" in data:
            person.stay_days = data["stay_days"]
        if "elec" in data:
            person.elec = data["elec"]
        if "water" in data:
            person.water = data["water"]
        return person
    
    def to_dict(self):
        return {
            "name": self.name,
            "stay_days": self.stay_days,
            "elec": self.elec,
            "water": self.water
        }


class BillsData:
    def __init__(self, year=None, month=None, electricity=0, water=0, people=None):
        self.year = year
        self.month = month
        self.electricity = electricity
        self.water = water
        self.people = people if people else []