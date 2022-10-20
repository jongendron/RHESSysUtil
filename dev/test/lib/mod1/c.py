# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 12:14:22 2022

@author: jonge
"""

from pathlib import Path
print(f"c.py: {Path(__file__).absolute()}")

def fnc(s: str) -> None:
    print(s)