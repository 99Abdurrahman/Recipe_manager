# setup.py
from cx_Freeze import setup, Executable # type: ignore
import sys

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["tkinter", "sqlite3", "pandas", "datetime", "os", "openpyxl"],
    "excludes": ["streamlit", "matplotlib", "numpy.random._pickle", "test", "unittest"],
    "include_files": [],
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
    "optimize": 2
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="RecipeManager",
    version="1.0",
    description="Arin Resort Hotel Recipe Management System",
    author="Your Name",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "recipe_manager.py", 
            base=base, 
            icon=None,
            target_name="RecipeManager.exe"
        )
    ]
)