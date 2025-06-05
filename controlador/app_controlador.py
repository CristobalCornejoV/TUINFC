import tkinter as tk
from modelo.lector_nfc import (
    obtener_uid_tarjeta,
    obtener_datos_tarjeta,
    parsear_respuesta,
    lector_conectado
)
from vista.interfaz import NFCAppVista

class NFCAppControlador:
    def __init__(self, root):
        self.vista = NFCAppVista(root, self)
        self.historial = []
        self.ultimo_uid = None
        self.manual_pause = False
        self.reader_was_disconnected = False
        self.reader_active = True
        self.iniciar_monitor_lector()
        self.actualizar_estado_lector_periodico()

    def manejar_tarjeta_detectada(self, card):
        try:
            connection = card.createConnection()
            uid = obtener_uid_tarjeta(connection)
            if uid:
                self.vista.root.after(0, lambda: self.procesar_tarjeta(uid))
        except:
            pass

    def procesar_tarjeta(self, tarjeta_id):
        try:
            texto_respuesta = obtener_datos_tarjeta(tarjeta_id)
            resultado = parsear_respuesta(texto_respuesta)
            self.mostrar_respuesta(resultado, tarjeta_id=tarjeta_id)
        except Exception as e:
            self.mostrar_respuesta({"NOMBRE": "Error", "FECHA Y HORA": "", "RUT": str(e)}, tarjeta_id=tarjeta_id)

    def mostrar_respuesta(self, datos, tarjeta_id=""):
        self.vista.limpiar_datos()
        for entry in self.vista.campos.values():
            entry.configure(bg="#ffffcc", state="normal")

        def colocar_datos():
            for key in ["ID Tarjeta", "Nombre", "Fecha y Hora", "RUT"]:
                texto = datos.get(key.upper(), "") if key != "ID Tarjeta" else tarjeta_id
                self.vista.campos[key].delete(0, tk.END)
                self.vista.campos[key].insert(0, texto)
                self.vista.campos[key].configure(state="readonly", bg="white")
            entrada = f"{datos.get('FECHA Y HORA', '')} - {datos.get('RUT', '')} - {datos.get('NOMBRE', '')}"
            self.historial.insert(0, entrada)
            self.historial = self.historial[:10]
            for i, item in enumerate(self.vista.historial_items):
                item.config(text=self.historial[i] if i < len(self.historial) else "")

        self.vista.root.after(150, colocar_datos)

    def toggle_reader(self):
        if self.reader_active:
            self.reader_active = False
            self.manual_pause = True
            self.detener_monitor_lector()
            self.vista.label.config(text="Detección detenida", foreground="red")
            self.vista.toggle_button.config(text="Iniciar detección")
        else:
            self.manual_pause = False
            self.reader_active = True
            self.iniciar_monitor_lector()
            self.vista.label.config(text="Detectando...", foreground="green")
            self.vista.toggle_button.config(text="Detener detección")

    def iniciar_monitor_lector(self):
        from smartcard.CardMonitoring import CardMonitor, CardObserver
        if not hasattr(self, 'card_monitor') or self.card_monitor is None:
            self.card_monitor = CardMonitor()
        if not hasattr(self, 'card_observer') or self.card_observer is None:
            class CardObserverImpl(CardObserver):
                def __init__(self, callback):
                    self.callback = callback
                def update(self, observable, actions):
                    added_cards, _ = actions
                    for card in added_cards:
                        self.callback(card)
            self.card_observer = CardObserverImpl(self.manejar_tarjeta_detectada)
            self.card_monitor.addObserver(self.card_observer)

    def detener_monitor_lector(self):
        if hasattr(self, 'card_monitor') and self.card_monitor and hasattr(self, 'card_observer') and self.card_observer:
            self.card_monitor.deleteObserver(self.card_observer)
            self.card_observer = None

    def actualizar_estado_lector_periodico(self):
        conectado = lector_conectado()
        if not conectado:
            if self.reader_active:
                self.vista.label.config(text="Lector NFC desconectado", foreground="red")
                self.vista.toggle_button.config(text="Iniciar detección")
                self.reader_active = False
                self.detener_monitor_lector()
            self.reader_was_disconnected = True
        else:
            if self.reader_was_disconnected:
                self.reader_was_disconnected = False
                self.manual_pause = False
                self.reader_active = True
                self.iniciar_monitor_lector()
                self.vista.label.config(text="Detectando...", foreground="green")
                self.vista.toggle_button.config(text="Detener detección")
            else:
                if self.reader_active:
                    self.vista.label.config(text="Detectando...", foreground="green")
                    self.vista.toggle_button.config(text="Detener detección")
                else:
                    self.vista.label.config(text="Detección detenida", foreground="red")
                    self.vista.toggle_button.config(text="Iniciar detección")
        self.vista.root.after(1000, self.actualizar_estado_lector_periodico)
