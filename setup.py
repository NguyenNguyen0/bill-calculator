from setuptools import setup, find_packages

setup(
    name="bills-calculator",
    version="1.0.0",
    description="A Python-based application to calculate electricity and water bills for shared accommodations.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Nguyen Nguyen",
    url="https://github.com/nguyenguyen0/calculate_electricity_bill",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "rich",
        "pyfiglet",
        "typer[all]"
    ],
    entry_points={
        "console_scripts": [
            "bills-calculator=app:BillsApp.run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
)
