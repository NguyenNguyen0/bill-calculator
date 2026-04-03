import typer
from typing import List, Optional
import importlib.metadata

from .core.models import BillsData
from .ui import BillsUI
from .core.calculator import BillsCalculator
from .data.storage import Storage
from .data.exporter import BillsExporter
from .data.history import BillsHistory

class BillsApp:
    def __init__(self):
        self.ui = BillsUI()
        self.calculator = BillsCalculator()
        self.storage = Storage()
        self.exporter = BillsExporter()
        self.history = BillsHistory()
        self.app = typer.Typer()
        self._setup_app()
    
    def _setup_app(self):
        @self.app.callback(invoke_without_command=True)
        def main(
            ctx: typer.Context,
            month: Optional[int] = typer.Option(None, "--month", "-m", help="Tháng tính tiền"),
            year: Optional[int] = typer.Option(None, "--year", "-y", help="Năm tính tiền"),
            electric_bill: Optional[float] = typer.Option(None, "--electric-bill", "-e", help="Tiền điện (VNĐ)"),
            water_bill: Optional[float] = typer.Option(None, "--water-bill", "-w", help="Tiền nước (VNĐ)"),
            people: Optional[List[str]] = typer.Option(None, "--people", "-p", help="Danh sách tên hoặc tên=ngày nghỉ"),
            load_file: Optional[str] = typer.Option(None, "--load-file", "-lf", help="Tải danh sách người từ file"),
            save_file: Optional[str] = typer.Option(None, "--save-file", "-sf", help="Lưu danh sách người vào file"),
            export_format: Optional[str] = typer.Option(None, "--export", "-x", help="Xuất kết quả ra txt hoặc csv"),
            no_history: bool = typer.Option(False, "--no-history", help="Không lưu lịch sử tính tiền"),
            algorithm: str = typer.Option("ratio", "--algorithm", "-a", help="Thuật toán tính tiền: 'ratio' (mặc định), 'stair' hoặc 'equal'"),
            tui: bool = typer.Option(False, "--tui", help="Chạy giao diện TUI (Textual)"),
            legacy_ui: bool = typer.Option(False, "--legacy-ui", help="Dùng giao diện interactive cũ"),
        ):
            try:
                version = importlib.metadata.version("bills-calculator")
                typer.echo(f"Bills Calculator v{version}")
            except importlib.metadata.PackageNotFoundError:
                typer.echo("Bills Calculator")
            
            if ctx.invoked_subcommand is None:
                has_cli_input = any(
                    [
                        month is not None,
                        year is not None,
                        electric_bill is not None,
                        water_bill is not None,
                        bool(people),
                        bool(load_file),
                        bool(save_file),
                        bool(export_format),
                        no_history,
                        algorithm != "ratio",
                    ]
                )

                if not legacy_ui and (tui or not has_cli_input):
                    try:
                        from .tui.app import BillsTextualApp
                    except ImportError:
                        self.ui.show_error(
                            "Không tìm thấy thư viện textual. Hãy cài dependency rồi thử lại."
                        )
                        return

                    BillsTextualApp().run()
                    return

                self._run_app(
                    month=month,
                    year=year,
                    electric_bill=electric_bill,
                    water_bill=water_bill,
                    people_input=people,
                    load_file=load_file,
                    save_file=save_file,
                    export_format=export_format,
                    no_history=no_history,
                    algorithm=algorithm
                )

        @self.app.command()
        def history(
            year: Optional[int] = typer.Option(None, "--year", "-y", help="Lọc theo năm"),
            month: Optional[int] = typer.Option(None, "--month", "-m", help="Lọc theo tháng"),
        ):
            if year is not None and month is not None:
                entries = self.history.get_by_month(year, month)
            else:
                entries = self.history.load_all()

            if not entries:
                self.ui.show_error("Chưa có lịch sử tính tiền.")
                return

            self._display_history(entries)
    
    def _run_app(
        self,
        month=None,
        year=None,
        electric_bill=0,
        water_bill=0,
        people_input=None,
        load_file=None,
        save_file=None,
        export_format=None,
        no_history=False,
        algorithm="ratio"
    ):
        bills_data = BillsData()
        people_list = []
        date_now = year is None and month is None
        current_year, current_month = self.ui.get_date_now()

        try:
            # Validate algorithm
            if algorithm not in ["ratio", "stair", "equal"]:
                self.ui.show_error(f"Thuật toán không hợp lệ: {algorithm}. Sử dụng 'ratio', 'stair' hoặc 'equal'.")
                return

            # Get bills data
            if electric_bill is None and water_bill is None:
                bills_data = self.ui.input_month_year_and_bills(date_now)
                # Ask for algorithm selection in interactive mode
                if not people_input and not load_file:
                    algorithm = self.ui.input_algorithm_selection()
            else:
                bills_data.year = year if year is not None else current_year
                bills_data.month = month if month is not None else current_month
                if bills_data.year < 2000 or bills_data.year > current_year + 1:
                    self.ui.show_error(f"Năm không hợp lệ: {bills_data.year}. Giá trị phải nằm trong khoảng 2000 - {current_year + 1}.")
                    return
                if bills_data.month < 1 or bills_data.month > 12:
                    self.ui.show_error(f"Tháng không hợp lệ: {bills_data.month}. Giá trị phải nằm trong khoảng 1 - 12.")
                    return
                bills_data.electricity = electric_bill if electric_bill is not None else 0
                bills_data.water = water_bill if water_bill is not None else 0
                if bills_data.electricity < 0:
                    self.ui.show_error("Tiền điện phải >= 0.")
                    return
                if bills_data.water < 0:
                    self.ui.show_error("Tiền nước phải >= 0.")
                    return

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
            algorithm_name = {
                "stair": "Thuật toán bậc thang",
                "equal": "Thuật toán bình quân",
                "ratio": "Thuật toán tỷ lệ",
            }.get(algorithm, "Thuật toán tỷ lệ")
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

            if save_file:
                self.storage.save_people_info(people_list, save_file)
                self.ui.show_success("Đã lưu danh sách người vào file!")
            elif not people_input and not load_file:
                if self.ui.confirm("Bạn có muốn lưu danh sách không?", default="n"):
                    self.storage.save_people_info(people_list)
                    self.ui.show_success("Đã lưu danh sách người vào file mặc định!")

            if export_format:
                export_format = export_format.lower()
                if export_format == "txt":
                    exported_file = self.exporter.export_txt(bills_data, "dist/exports/bills_result.txt")
                elif export_format == "csv":
                    exported_file = self.exporter.export_csv(bills_data, "dist/exports/bills_result.csv")
                else:
                    self.ui.show_error("Chỉ hỗ trợ export txt hoặc csv.")
                    return
                self.ui.show_success(f"Đã export kết quả ra file: {exported_file}")

            if not no_history:
                self.history.save(bills_data)

            if not people_input and not load_file:
                if self.ui.confirm("Copy kết quả vào clipboard?", default="n"):
                    self.ui.copy_text_to_clipboard(self.ui.format_result_text(bills_data))
                    self.ui.show_success("Đã copy kết quả vào clipboard!")
                
        except ValueError as exc:
            self.ui.show_error(str(exc))
        except KeyboardInterrupt:
            self.ui.show_error("Chương trình đã thoát!")

    def _display_history(self, entries):
        from rich.panel import Panel
        from rich.table import Table

        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Saved At", style="bold")
        table.add_column("Month", justify="center")
        table.add_column("Year", justify="center")
        table.add_column("Algorithm", justify="center")
        table.add_column("People", justify="right")
        table.add_column("Electricity", justify="right")
        table.add_column("Water", justify="right")

        for entry in entries:
            table.add_row(
                str(entry.get("saved_at", "")),
                str(entry.get("month", "")),
                str(entry.get("year", "")),
                str(entry.get("algorithm", "")),
                str(len(entry.get("people", []))),
                f"{entry.get('electricity', 0):,.0f} VNĐ",
                f"{entry.get('water', 0):,.0f} VNĐ",
            )

        self.ui.console.print(Panel(table, title="LỊCH SỬ TÍNH TIỀN", border_style="cyan"))
    
    def run(self):
        self.app()