# -*- coding: utf-8 -*-
"""
Created on Fri May 23 12:56:22 2025

@author: Fiona
"""

# app.py
from factory import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

