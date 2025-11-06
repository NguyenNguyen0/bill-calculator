import typer
from typing import List, Optional
import importlib.metadata

from models import BillsData
from ui import BillsUI
from calculator import BillsCalculator
from storage import Storage

class BillsApp:
    def __init__(self):
        self.ui = BillsUI()
        self.calculator = BillsCalculator()
        self.storage = Storage()
        self.app = typer.Typer()
        self._setup_app()
    
    def _setup_app(self):
        @self.app.callback(invoke_without_command=True)
        def main(
            ctx: typer.Context,
            month: Optional[int] = typer.Option(None, "--month", "-m", help="Tháng tính tiền"),
            year: Optional[int] = typer.Option(None, "--year", "-y", help="Năm tính tiền"),
            electric_bill: float = typer.Option(0, "--electric-bill", "-e", help="Tiền điện (VNĐ)"),
            water_bill: float = typer.Option(0, "--water-bill", "-w", help="Tiền nước (VNĐ)"),
            people: Optional[List[str]] = typer.Option(None, "--people", "-p", help="Danh sách tên hoặc tên=ngày nghỉ"),
            load_file: Optional[str] = typer.Option(None, "--load-file", "-lf", help="Tải danh sách người từ file"),
            save_file: Optional[str] = typer.Option(None, "--save-file", "-sf", help="Lưu danh sách người vào file"),
            algorithm: str = typer.Option("ratio", "--algorithm", "-a", help="Thuật toán tính tiền: 'ratio' (mặc định) hoặc 'stair'"),
        ):
            try:
                version = importlib.metadata.version("bills-calculator")
                typer.echo(f"Bills Calculator v{version}")
            except importlib.metadata.PackageNotFoundError:
                typer.echo("Bills Calculator")
            
            if ctx.invoked_subcommand is None:
                self._run_app(
                    month=month,
                    year=year,
                    electric_bill=electric_bill,
                    water_bill=water_bill,
                    people_input=people,
                    load_file=load_file,
                    save_file=save_file,
                    algorithm=algorithm
                )
    
    def _run_app(
        self,
        month=None,
        year=None,
        electric_bill=0,
        water_bill=0,
        people_input=None,
        load_file=None,
        save_file=None,
        algorithm="ratio"
    ):
        bills_data = BillsData()
        people_list = []
        date_now = year is None and month is None

        try:
            # Validate algorithm
            if algorithm not in ["ratio", "stair"]:
                self.ui.show_error(f"Thuật toán không hợp lệ: {algorithm}. Sử dụng 'ratio' hoặc 'stair'.")
                return

            # Get bills data
            if not electric_bill and not water_bill:
                bills_data = self.ui.input_month_year_and_bills(date_now)
                # Ask for algorithm selection in interactive mode
                if not people_input and not load_file:
                    algorithm = self.ui.input_algorithm_selection()
            else:
                if date_now:
                    year, month = self.ui.get_date_now()
                bills_data.year = year
                bills_data.month = month 
                bills_data.electricity = electric_bill
                bills_data.water = water_bill

            # Get people data
            if load_file:
                people_list = self.storage.load_people_info(load_file)
                if not people_list:
                    self.ui.show_error("Không có người nào được tải từ file.")
                    return
            elif not people_input:
                people_list = self.ui.input_people_info()
            else:
                people_list = self.calculator.parse_people_input(people_input)

            # Show algorithm info
            algorithm_name = "Thuật toán bậc thang" if algorithm == "stair" else "Thuật toán tỷ lệ"
            self.ui.show_algorithm_info(algorithm, algorithm_name)

            # Calculate bills
            def calculate():
                return self.calculator.calculate_bills(
                    people_list, bills_data.electricity, bills_data.water, algorithm=algorithm
                )
            
            people_list = self.ui.show_status(f"Calculating bills using {algorithm_name}...", calculate)
            
            # Update bills data with calculated people and algorithm
            bills_data.people = people_list
            bills_data.algorithm = algorithm
            
            # Display result
            self.ui.display_result(bills_data)
                
        except KeyboardInterrupt:
            if save_file:
                self.storage.save_people_info(people_list, save_file)
                self.ui.show_success("Đã lưu danh sách người vào file!")
            
            self.ui.show_error("Chương trình đã thoát!")
    
    def run(self):
        self.app()