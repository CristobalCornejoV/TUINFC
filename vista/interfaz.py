import tkinter as tk
from tkinter import ttk, messagebox

class NFCAppVista:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self.root.title("TUI NFC 1.0")
        self.root.geometry("640x480")
        self.root.minsize(480, 450)
        self.root.maxsize(840, 640)

        menubar = tk.Menu(root)
        root.config(menu=menubar)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Salir", command=root.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        acerca_menu = tk.Menu(menubar, tearoff=0)
        acerca_menu.add_command(label="Acerca de", command=lambda: messagebox.showinfo("Acerca de", "TUI NFC v1.0\n2025\nCristobal Cornejo"))
        menubar.add_cascade(label="Acerca de", menu=acerca_menu)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        self.tab_lector = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_lector, text="Lector")

        self.tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text="Historial")

        datos_frame = tk.LabelFrame(self.tab_lector, text="Datos recibidos", padx=10, pady=5)
        datos_frame.pack(padx=10, pady=(10, 10), fill="x")

        self.campos = {}
        campos_nombres = ["ID Tarjeta", "Nombre", "Fecha y Hora", "RUT"]
        for campo in campos_nombres:
            row = ttk.Frame(datos_frame)
            row.pack(fill="x", padx=5, pady=3)
            label = ttk.Label(row, text=campo, width=15)
            label.pack(side="left")
            entry = tk.Entry(row, bg="white", readonlybackground="white", state="readonly")
            entry.pack(side="left", fill="x", expand=True)
            self.campos[campo] = entry
            b = ttk.Button(row, text="Copiar", command=lambda e=entry: self.copiar_texto(e))
            b.pack(side="left", padx=5)

        historial_frame = tk.LabelFrame(self.tab_historial, text="Últimas 10 lecturas", padx=10, pady=5)
        historial_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.historial_items = [ttk.Label(historial_frame, text="") for _ in range(10)]
        for lbl in self.historial_items:
            lbl.pack(anchor="w", padx=5, pady=2)

        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(side="bottom", fill="x")
        self.label = ttk.Label(control_frame, text="Iniciando...", font=("Helvetica", 12, "bold"), foreground="orange")
        self.label.pack(side="left")
        self.toggle_button = ttk.Button(control_frame, text="Detener detección", command=self.controlador.toggle_reader)
        self.toggle_button.pack(side="right")
        self.limpiar_button = ttk.Button(control_frame, text="Limpiar datos", command=self.limpiar_datos)
        self.limpiar_button.pack(side="right", padx=(0,10))

    def copiar_texto(self, entry):
        self.root.clipboard_clear()
        self.root.clipboard_append(entry.get())
        self.root.update()

    def limpiar_datos(self):
        for entry in self.campos.values():
            entry.configure(state="normal")
            entry.delete(0, tk.END)
            entry.configure(state="readonly", bg="white")
