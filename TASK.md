# TASK.md — Đại tu & Build .exe cho Bills Calculator

> Tài liệu này liệt kê toàn bộ công việc cần thực hiện theo thứ tự ưu tiên.
> Mỗi task có checklist cụ thể để Copilot có thể thực hiện tuần tự.

---

## PHASE 1 — Sửa bug & hạ tầng cơ bản (ưu tiên cao nhất)

### TASK-01: Fix bug `storage.py` — sai tên thuộc tính

**File:** `storage.py`

- [ ] Dòng 8: đổi `person.days_off` → `person.stay_days`
- [ ] Kiểm tra toàn bộ file `storage.py`, đảm bảo không còn tham chiếu `days_off`

```python
# TRƯỚC (sai)
f.write(f"{person.name}={person.days_off}\n")

# SAU (đúng)
f.write(f"{person.name}={person.stay_days}\n")
```

---

### TASK-02: Tạo file `__main__.py` đúng chuẩn

**File cần tạo:** `__main__.py`

- [ ] Tạo file `__main__.py` tại root project với nội dung:

```python
from app import BillsApp

def main():
    app = BillsApp()
    app.run()

if __name__ == "__main__":
    main()
```

---

### TASK-03: Fix `setup.py` — entry point sai cú pháp

**File:** `setup.py`

- [ ] Sửa entry point từ `bills-calculator=app:BillsApp.run` thành trỏ vào hàm wrapper `main` trong `__main__.py`:

```python
entry_points={
    "console_scripts": [
        "bills-calculator=__main__:main",
    ],
},
```

---

### TASK-04: Fix `models.py` — code thừa trong `from_dict()`

**File:** `models.py`

- [ ] Xóa dòng gán `stay_days` thừa (dòng 12, gán lại sau khi đã gán trong constructor)
- [ ] Thêm `__repr__` vào class `Person` để debug dễ hơn:

```python
def __repr__(self):
    return f"Person(name={self.name!r}, stay_days={self.stay_days}, elec={self.elec}, water={self.water})"
```

---


## PHASE 2 — Chuyển pip sang uv

### TASK-05: Tạo `requirements.txt` (tạm thời, làm nguồn cho uv)

**Lý do:** File này được README đề cập nhưng không tồn tại trong project.

- [ ] Tạo file `requirements.txt` tại root với nội dung:

```
rich
pyfiglet
typer[all]
```

---

### TASK-06: Migrate sang uv — khởi tạo project

> uv thay thế pip + venv bằng một công cụ duy nhất, nhanh hơn và reproducible hơn.

- [ ] Cài uv nếu chưa có: `pip install uv` hoặc `winget install astral-sh.uv`
- [ ] Tại thư mục project, khởi tạo uv project:

```bash
uv init --no-workspace
```

Lệnh này tạo file `pyproject.toml` chuẩn PEP 517/518.

---

### TASK-07: Migrate dependencies vào `pyproject.toml`

- [ ] Thêm dependencies vào `pyproject.toml` (uv tạo ra):

```toml
[project]
name = "bills-calculator"
version = "1.0.0"
description = "A Python-based application to calculate electricity and water bills for shared accommodations."
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "rich",
    "pyfiglet",
    "typer[all]",
    "pyinstaller",
]

[project.scripts]
bills-calculator = "__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] Chạy lệnh để tạo `uv.lock` và cài dependencies:

```bash
uv sync
```

---

### TASK-08: Xóa / archive các file pip cũ

- [ ] Xóa `requirements.txt` (đã migrate vào `pyproject.toml`) hoặc giữ lại comment "legacy"
- [ ] Xóa `setup.py` (thay bằng `pyproject.toml`)
- [ ] Cập nhật `.gitignore` để ignore thư mục `.venv` do uv tạo:

```gitignore
.venv/
uv.lock  # tuỳ chọn: có thể commit lock file để reproducible
```

- [ ] Cập nhật README — thay hướng dẫn cài đặt:

```markdown
## Cài đặt

```bash
# Cài uv (nếu chưa có)
pip install uv

# Clone và cài dependencies
git clone https://github.com/NguyenNguyen0/calculate_electricity_bill.git
cd calculate_electricity_bill
uv sync

# Chạy ứng dụng
uv run python -m bills_calculator
```
```

---


## PHASE 3 — Chuẩn bị build .exe với PyInstaller

### TASK-09: Cập nhật `bills_calculator.spec`

**File:** `bills_calculator.spec`

- [ ] Sửa entry point từ `['__main__.py']` → `['__main__.py']` (đúng sau khi TASK-02 hoàn thành)
- [ ] Thêm `datas` để đóng gói pyfiglet fonts (bắt buộc, thiếu fonts sẽ crash khi chạy .exe):

```python
import pyfiglet
import os

pyfiglet_path = os.path.dirname(pyfiglet.__file__)

a = Analysis(
    ['__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(pyfiglet_path, 'fonts'), 'pyfiglet/fonts'),
    ],
    hiddenimports=['pyfiglet.fonts'],
    ...
)
```

- [ ] Thêm `icon` nếu có file `.ico`:

```python
exe = EXE(
    ...
    name='bills_calculator',
    icon='assets/icon.ico',  # tạo file này nếu muốn có icon
    console=True,
    ...
)
```

---

### TASK-10: Build và kiểm tra .exe

- [ ] Cài PyInstaller vào uv environment:

```bash
uv add pyinstaller --dev
```

- [ ] Build bằng spec file:

```bash
uv run pyinstaller bills_calculator.spec
```

- [ ] Kiểm tra file output tại `dist/bills_calculator.exe`
- [ ] Test chạy thử:

```bash
.\dist\bills_calculator.exe
.\dist\bills_calculator.exe -e 500000 -w 200000 -p "Alice=25" "Bob=30"
```

- [ ] Xác nhận pyfiglet font load đúng (title BILLS-CALCULATOR hiển thị ASCII art)

---

## PHASE 4 — Cải thiện UX & validation

### TASK-11: Thêm validation đầu vào

**File:** `ui.py`, `app.py`

- [ ] Validate `month`: phải trong khoảng 1–12, hiển thị lỗi nếu sai
- [ ] Validate `year`: phải >= 2000 và <= năm hiện tại + 1
- [ ] Validate `stay_days`: phải >= 0
- [ ] Validate `electricity` và `water`: phải >= 0
- [ ] Dùng try/except + `self.ui.show_error()` để hiện thông báo rõ ràng thay vì crash

---

### TASK-12: Thêm cột "Tổng tiền" trong bảng kết quả

**File:** `ui.py` — hàm `display_result()`

- [ ] Thêm cột "Tổng cộng 💰" vào bảng kết quả
- [ ] Giá trị = `p.elec + p.water` cho từng người
- [ ] Hiển thị bold hoặc màu nổi bật để dễ đọc

---

### TASK-13: Lưu file rõ ràng (không phụ thuộc Ctrl+C)

**File:** `app.py`

- [ ] Sau khi hiển thị kết quả, nếu `--save-file` được truyền vào thì lưu luôn (không cần Ctrl+C)
- [ ] Trong interactive mode: hỏi người dùng "Bạn có muốn lưu danh sách không? (y/n)" trước khi thoát

---

## PHASE 5 — Tính năng mới

### TASK-14: Thêm thuật toán "bình quân đầu người" (equal split)

**File:** `calculator.py`, `ui.py`, `app.py`

- [ ] Thêm method `calculate_equal_algorithm()` trong `BillsCalculator`:
  - Chia đều tổng tiền cho số người, không quan tâm số ngày
- [ ] Thêm option `"equal"` vào `--algorithm` / `-a`
- [ ] Cập nhật `input_algorithm_selection()` trong `ui.py` thêm lựa chọn số 3
- [ ] Cập nhật README với mô tả thuật toán mới

---

### TASK-15: Export kết quả ra file text/CSV

**File mới:** `exporter.py`

- [ ] Tạo class `BillsExporter` với các method:
  - `export_txt(bills_data, filename)` — xuất bảng dạng plain text
  - `export_csv(bills_data, filename)` — xuất CSV (name, stay_days, elec, water, total)
- [ ] Thêm option `--export` hoặc `-x` vào CLI: `--export txt` hoặc `--export csv`
- [ ] Hiển thị thông báo sau khi export thành công

---

### TASK-16: Lưu lịch sử tính tiền

**File mới:** `history.py`, thêm thư mục `data/`

- [ ] Tạo class `BillsHistory`:
  - `save(bills_data)` — lưu kết quả vào `data/history.json` (append)
  - `load_all()` — đọc toàn bộ lịch sử
  - `get_by_month(year, month)` — lọc theo tháng/năm
- [ ] Tự động lưu mỗi lần tính xong (opt-out với flag `--no-history`)
- [ ] Thêm subcommand `history` để xem lại: `bills-calculator history`

---

### TASK-17: Copy kết quả vào clipboard

**File:** `ui.py` hoặc `exporter.py`

- [ ] Thêm dependency `pyperclip` vào `pyproject.toml`
- [ ] Sau khi hiển thị kết quả, hỏi "Copy kết quả vào clipboard? (y/n)"
- [ ] Format copy: text thuần, dễ paste vào Zalo/Messenger

---

## Thứ tự thực hiện đề xuất

```
PHASE 1 (bugs)     → TASK-01, 02, 03, 04
PHASE 2 (uv)       → TASK-05, 06, 07, 08
PHASE 3 (exe)      → TASK-09, 10
PHASE 4 (UX)       → TASK-11, 12, 13
PHASE 5 (features) → TASK-14, 15, 16, 17
```

> Sau PHASE 1 + 2 + 3: project có thể build được .exe hoạt động đúng.
> PHASE 4 + 5: nâng cấp trải nghiệm và tính năng.
