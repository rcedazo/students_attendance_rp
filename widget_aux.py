#!/usr/bin/python
"""widget_aux.py: Clases de widget auxiliares para la interfaz gráfica"""
__author__ = "Ana María Manso Rodríguez"
__credits__ = ["Ana María Manso Rodríguez"]
__version__ = "1.0"
__status__ = "Development"

from tkinter import ttk
import tkinter as tk


class Desplegable(ttk.Frame):

    def __init__(self, valores, parent):
        super().__init__(parent)
        
        self.combo = ttk.Combobox(self, width=60)
        self.combo.grid(row=2, column=1)
        self.combo["values"] = valores
        self.combo.bind("<<ComboboxSelected>>")
