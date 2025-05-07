class Person:
    def __init__(self, name, days_off=0):
        self.name = name
        self.days_off = days_off
        self.stay_days = 0
        self.elec = 0
        self.water = 0
    
    def calculate_stay_days(self, total_days=30):
        self.stay_days = total_days - self.days_off
        return self.stay_days
    
    @classmethod
    def from_dict(cls, data):
        person = cls(name=data["name"], days_off=data["days_off"])
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
            "days_off": self.days_off,
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