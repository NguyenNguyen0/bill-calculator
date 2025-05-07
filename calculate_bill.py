from tabulate import tabulate
import calendar
import math
from colorama import Fore, init


init(autoreset=True)


def round_money(amount):
    return math.ceil(int(amount) / 100) * 100


def print_result(results, electricity_bill=0, water_bill=0, month=0, year=0):
    padding = "=" * 21
    print(f"\n\n{Fore.BLUE} {padding} THÁNG {month} NĂM {year} {padding} {Fore.RESET}")
    print(f"{"TIỀN ĐIỆN:":<25} {Fore.RED} {electricity_bill:>30,} {Fore.RESET} VNĐ")
    print(f"{"TỔNG TIỀN ĐIỆN THU:":<25} {Fore.RED} {sum([float(result[1][:-4].replace(',', '')) for result in results]):>30,.0f} {Fore.RESET} VNĐ")
    print(f"{"TIỀN NƯỚC:":<25} {Fore.RED} {water_bill:>30,} {Fore.RESET} VNĐ")
    print(f"{"TỔNG TIỀN NƯỚC THU:":<25} {Fore.RED} {sum([float(result[2][:-4].replace(',', '')) for result in results]):>30,.0f} {Fore.RESET} VNĐ")
    print(f"{Fore.BLUE} {"=" * 60}")
    print(
        tabulate(
            results,
            headers=["Người", "Tiền Điện ⚡", "Tiền Nước 💦", "Số Ngày Ở 🕛"],
            tablefmt="grid",
        )
    )


def calculate_bill():
    electricity_bill = 1_788_407
    water_bill = 0

    # Nhập số ngày không sử dụng điện của từng người
    unusage_days = {
        "Nguyên": 15,
        "Vĩ": 9,
        "Vũ": 15,
        "Tấn": 9,
        "Xuân": 15,
        "Ninh": 12,
        "Đạt": 13,
        "Tú": 9,
        "Thương": 15,
        "Dũng": 13,
        "Tấn Anh": 9,
    }

    month = 2
    year = calendar.datetime.datetime.now().year
    days_in_month = calendar.monthrange(year, month=month)[1]

    # Tính tổng số ngày sử dụng điện của tất cả mọi người
    total_usage_days = sum(
        [days_in_month - unusage_days[person] for person in unusage_days]
    )

    # Tính số tiền điện của từng người
    results = []
    for person in unusage_days:
        usage_days = days_in_month - unusage_days[person]
        person_water_bill = round_money((usage_days / total_usage_days) * water_bill)
        person_electricity_bill = round_money(
            (usage_days / total_usage_days) * electricity_bill
        )
        results.append(
            [
                person,
                f"{person_electricity_bill:,.2f} VNĐ",
                f"{person_water_bill:,.2f} VNĐ",
                usage_days,
            ]
        )

    print_result(results=results, electricity_bill=electricity_bill, water_bill=water_bill, month=month, year=year)

calculate_bill()
