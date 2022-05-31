from cocol.cocol import Cocol

import os
import tkinter as tk
from tkinter import filedialog


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    filepath = filedialog.askopenfilename(title='Seleccione el archivo .atg',
                                          defaultextension='.atg',
                                          filetypes=[('cocol', '.atg')],
                                          initialdir=os.getcwd())

    cocol = Cocol(filepath)

    print('Archivo scaner' + cocol.cocol_reader.compiler_name + '.py y parser' + cocol.cocol_reader.compiler_name + ' generado correctamente.')
