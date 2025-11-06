import math
from models import Person

class BillsCalculator:
    @staticmethod
    def round_money(amount):
        if amount < 1000:
            return math.ceil(amount)
        return math.ceil(int(amount) / 100) * 100
    
    def calculate_stair_algorithm(self, people, total_elec, total_water, total_days=30):
        """Calculate bills for each person based on tiered stay days"""
        if not people:
            return people

        # Find minimum stay days
        min_stay_days = min(person.stay_days for person in people)
        
        # Calculate base rate per day per person
        total_bill = total_elec + total_water
        person_count = len(people)
        base_rate_per_day = total_bill / (person_count * total_days) if total_days > 0 and person_count > 0 else 0
        
        # Calculate base amount for each person
        total_base_amount = 0
        for person in people:
            person.base_amount = min_stay_days * base_rate_per_day
            total_base_amount += person.base_amount
        
        # Calculate total days exceeding minimum stay
        total_excess_days = 0
        for person in people:
            person.excess_days = person.stay_days - min_stay_days
            total_excess_days += person.excess_days
        
        # Calculate excess amount per day
        remaining_bill = total_bill - total_base_amount
        excess_rate_per_day = remaining_bill / total_excess_days if total_excess_days > 0 else 0
        
        # Assign final bills to each person
        for person in people:
            excess_amount = person.excess_days * excess_rate_per_day
            total_amount = person.base_amount + excess_amount
            
            # Split into electricity and water proportionally
            ratio = total_amount / total_bill if total_bill > 0 else 0
            person.elec = self.round_money(total_elec * ratio) if total_elec else 0
            person.water = self.round_money(total_water * ratio) if total_water else 0
            
            # Clean up temporary attributes
            if hasattr(person, 'base_amount'):
                del person.base_amount
            if hasattr(person, 'excess_days'):
                del person.excess_days
        
        return people
    
    def calculate_ratio_algorithm(self, people, total_elec, total_water, total_days=30):
        """Calculate bills for each person based on their stay days ratio"""
        if not people:
            return people

        # Calculate total stay days
        total_stay_days = sum(person.stay_days for person in people)
        
        # Calculate bills based on ratio of stay days
        for person in people:
            ratio = person.stay_days / total_stay_days if total_stay_days > 0 else 0
            person.elec = self.round_money(total_elec * ratio) if total_elec else 0
            person.water = self.round_money(total_water * ratio) if total_water else 0
        
        return people

    def calculate_bills(self, people, total_elec, total_water, total_days=30, algorithm="ratio"):
        """Calculate bills for each person using the specified algorithm
        
        Args:
            people: List of Person objects
            total_elec: Total electricity bill
            total_water: Total water bill
            total_days: Total days in the period (default 30)
            algorithm: Algorithm to use - "ratio" (default) or "stair"
        """
        if algorithm == "stair":
            return self.calculate_stair_algorithm(people, total_elec, total_water, total_days)
        elif algorithm == "ratio":
            return self.calculate_ratio_algorithm(people, total_elec, total_water, total_days)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}. Use 'ratio' or 'stair'.")
    
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