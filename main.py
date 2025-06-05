import tkinter as tk
from controlador.app_controlador import NFCAppControlador

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from controlador.app_controlador import resource_path
        icon_path = resource_path("resources/icono.png")
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
    except Exception:
        pass
    app = NFCAppControlador(root)
    root.mainloop()
