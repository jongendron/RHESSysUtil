# __init__.py

from pathlib import Path
print(f"mod1.py: {Path(__file__).absolute()}")

from . import a
from . import b
from . import c
# from ..mod2 import d