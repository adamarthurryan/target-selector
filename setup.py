"""Setup configuration for target-selector."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="target-selector",
    version="0.1.0",
    author="Adam Arthur Ryan",
    description="Astronomical observation planning tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/target-selector",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "astropy>=5.0",
        "astroquery>=0.4.6",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "target-selector=target_selector.cli:main",
        ],
    },
)
