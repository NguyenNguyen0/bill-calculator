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
            date_now: bool = typer.Option(False, "--date-now", "-dn", help="Sử dụng ngày hiện tại"),
            month: Optional[int] = typer.Option(None, "--month", "-m", help="Tháng tính tiền"),
            year: Optional[int] = typer.Option(None, "--year", "-y", help="Năm tính tiền"),
            electric_bill: float = typer.Option(0, "--electric-bill", "-e", help="Tiền điện (VNĐ)"),
            water_bill: float = typer.Option(0, "--water-bill", "-w", help="Tiền nước (VNĐ)"),
            people: Optional[List[str]] = typer.Option(None, "--people", "-p", help="Danh sách tên hoặc tên=ngày nghỉ"),
            load_file: Optional[str] = typer.Option(None, "--load-file", "-lf", help="Tải danh sách người từ file"),
            save_file: Optional[str] = typer.Option(None, "--save-file", "-sf", help="Lưu danh sách người vào file"),
        ):
            try:
                version = importlib.metadata.version("bills-calculator")
                typer.echo(f"Bills Calculator v{version}")
            except importlib.metadata.PackageNotFoundError:
                typer.echo("Bills Calculator")
            
            if ctx.invoked_subcommand is None:
                self._run_app(
                    date_now=date_now,
                    month=month,
                    year=year,
                    electric_bill=electric_bill,
                    water_bill=water_bill,
                    people_input=people,
                    load_file=load_file,
                    save_file=save_file
                )
    
    def _run_app(
        self,
        date_now=False,
        month=None,
        year=None,
        electric_bill=0,
        water_bill=0,
        people_input=None,
        load_file=None,
        save_file=None
    ):
        bills_data = BillsData()
        people_list = []
        
        try:
            # Get bills data
            if not electric_bill and not water_bill:
                bills_data = self.ui.input_month_year_and_bills(date_now)
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

            # Calculate bills
            def calculate():
                return self.calculator.calculate_bills(
                    people_list, bills_data.electricity, bills_data.water
                )
            
            people_list = self.ui.show_status("Calculating bills...", calculate)
            
            # Update bills data with calculated people
            bills_data.people = people_list
            
            # Display result
            self.ui.display_result(bills_data)
                
        except KeyboardInterrupt:
            if save_file:
                self.storage.save_people_info(people_list, save_file)
                self.ui.show_success("Đã lưu danh sách người vào file!")
            
            self.ui.show_error("Chương trình đã thoát!")
    
    def run(self):
        self.app()