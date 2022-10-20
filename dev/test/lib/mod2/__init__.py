# __init__.py

from pathlib import Path
print(f"mod2.py: {Path(__file__).absolute()}")

from . import d
from . import e
from . import f