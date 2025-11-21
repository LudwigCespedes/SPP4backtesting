"""
Setup script para instalar SPP4backtesting como paquete.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="spp4backtesting",
    version="1.0.0",
    author="Ludwig Cespedes",
    description="Sistema de backtesting para estrategias de trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "backtesting>=0.3.3",
        "yfinance>=0.2.0",
        "TA-Lib>=0.4.0",
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "matplotlib>=3.6.0",
    ],
)
