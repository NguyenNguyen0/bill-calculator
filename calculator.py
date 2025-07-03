import math
from models import Person

class BillsCalculator:
    @staticmethod
    def round_money(amount):
        if amount < 1000:
            return math.ceil(amount)
        return math.ceil(int(amount) / 100) * 100
    
    def calculate_bills(self, people, total_elec, total_water, total_days=30):
        """Calculate bills for each person based on their stay days"""
        # Calculate stay days for each person
        total_stay_days = 0
        for person in people:
            total_stay_days += person.stay_days
        
        # Calculate bills based on ratio of stay days
        for person in people:
            ratio = person.stay_days / total_stay_days if total_stay_days > 0 else 0
            person.elec = self.round_money(total_elec * ratio) if total_elec else 0
            person.water = self.round_money(total_water * ratio) if total_water else 0
        
        return people
    
    def parse_people_input(self, people_input):
        """Parse people input from command line"""
        result = []
        for item in people_input:
            if "=" in item:
                try:
                    name, days = item.split("=")
                    result.append(Person(name.strip(), stay_days=int(days)))
                except ValueError:
                    raise ValueError(f"Invalid format: {item}. Use name=days or just name.")
            else:
                result.append(Person(item.strip(), 0))
        
        return result