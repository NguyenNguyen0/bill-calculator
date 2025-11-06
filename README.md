# ⚡ Electricity Bill Calculator 🪟💡

> A Python-based application to calculate electricity and water bills for shared accommodations. The app distributes costs based on individual stay durations using configurable calculation algorithms.

![App demo](./calculating-cli.gif "App demo")

## ✨ Features

- 🧮 **Multiple Calculation Algorithms**: Choose between ratio-based or stair-step algorithms for fair cost distribution.
- 📊 **Ratio Algorithm** (default): Distributes costs proportionally based on each person's stay days.
- 📈 **Stair Algorithm**: Ensures everyone pays a base amount for minimum stay days, then distributes remaining costs based on extra days.
- 📝 Support for manual or file-based input of residents and their days off.
- 💾 Save and load resident data for reuse.
- 🎨 Interactive command-line interface with rich text formatting and algorithm selection.
- ⚡ Real-time algorithm information and calculation status.

## 🚀 Installation

1. 📥 Clone the repository:
   ```bash
   git clone https://github.com/NguyenNguyen0/calculate_electricity_bill.git
   cd calculate_electricity_bill
   ```

2. 📦 Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### Method 1: 🐍 Direct Python execution
```bash
python main.py
```

### Method 2: 📦 After installation
If you've installed the package (using `pip install .`), you can run:
```bash
bills-calculator
```

### ⚙️ Command-Line Options

- 🔌 `--electric-bill` or `-e`: Specify the total electricity bill (VNĐ).
- 💧 `--water-bill` or `-w`: Specify the total water bill (VNĐ).
- 👥 `--people` or `-p`: Provide a list of residents in the format `name=stay_days` or just `name`.
- 🧮 `--algorithm` or `-a`: Choose calculation algorithm: `ratio` (default) or `stair`.
- 📂 `--load-file` or `-lf`: Load resident data from a file.
- 💾 `--save-file` or `-sf`: Save resident data to a file.
- 📅 `--month` or `-m`: Specify the billing month.
- 🗓️ `--year` or `-y`: Specify the billing year.

## 🧮 Calculation Algorithms

### 📊 Ratio Algorithm (Default)
Distributes bills proportionally based on stay days:
- Each person pays: `(their_stay_days / total_stay_days) * total_bill`
- Simple and straightforward proportional distribution

### 📈 Stair Algorithm
Ensures fairness with a base rate for everyone:
- Everyone pays the same base amount for minimum stay days
- Remaining bill is distributed among those who stayed extra days
- More equitable for people with similar stay durations

## 🔧 Examples

**🎯 Interactive mode (no arguments):**
```bash
python main.py
```

**⚡ With command-line arguments using ratio algorithm (default):**
```bash
python main.py --electric-bill 500000 --water-bill 200000 --people "Alice=25" "Bob=28"
```

**📈 Using stair algorithm for more equitable distribution:**
```bash
python main.py --electric-bill 500000 --water-bill 200000 --people "Alice=25" "Bob=28" --algorithm stair
```

**📂 Load people from file with specific algorithm:**
```bash
python main.py --electric-bill 500000 --water-bill 200000 --load-file people.txt --algorithm ratio
```

**💾 Save people to file (use Ctrl+C to trigger save):**
```bash
python main.py --electric-bill 500000 --water-bill 200000 --people "Alice=25" "Bob=28" --save-file people.txt
```

**🔍 Compare algorithms with same data:**
```bash
# Ratio algorithm
python main.py -e 1000000 -w 500000 -p "Alice=25" -p "Bob=30" -a ratio

# Stair algorithm  
python main.py -e 1000000 -w 500000 -p "Alice=25" -p "Bob=30" -a stair
```

## 📁 File Structure

- 📊 `models.py`: Contains data models for residents and bills.
- 🧮 `calculator.py`: Handles bill calculations.
- 💾 `storage.py`: Manages saving and loading resident data.
- 🎨 `ui.py`: Provides a rich-text user interface.
- 🏠 `app.py`: Main application logic.
- 🚀 `__main__.py`: Entry point for the application.

## 📋 Requirements

- 🐍 Python 3.10+
- 📦 Dependencies listed in `requirements.txt`

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
