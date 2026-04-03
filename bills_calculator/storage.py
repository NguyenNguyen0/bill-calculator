from .models import Person

class Storage:
    @staticmethod
    def save_people_info(people, filename="people_info.txt"):
        """Save people information to a file"""
        with open(filename, "w", encoding="utf-8") as f:
            for person in people:
                f.write(f"{person.name}={person.stay_days}\n")
    
    @staticmethod
    def load_people_info(filename="people_info.txt"):
        """Load people information from a file"""
        people = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and "=" in line:
                        name, stay_days = line.split("=", 1)
                        people.append(Person(name.strip(), int(stay_days)))
                    elif line:
                        people.append(Person(line.strip(), 0))
        except FileNotFoundError:
            return []
        
        return people