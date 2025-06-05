import requests
import re
from smartcard.System import readers
from smartcard.CardMonitoring import CardMonitor, CardObserver

API_BASE_URL = "https://ejemplo.com/api/WEB"

def obtener_uid_tarjeta(cardconnection):
    try:
        cardconnection.connect()
        get_uid_command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = cardconnection.transmit(get_uid_command)
        if sw1 == 0x90:
            data_le = data[::-1]
            uid_decimal_le = 0
            for b in data_le:
                uid_decimal_le = (uid_decimal_le << 8) + b
            return str(uid_decimal_le)
    except:
        pass
    return None

def lector_conectado():
    try:
        return len(readers()) > 0
    except:
        return False

def obtener_datos_tarjeta(tarjeta_id):
    url = f"{API_BASE_URL}?ntarjeta={tarjeta_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise e

def formatear_rut(rut_crudo):
    rut = ''.join(filter(lambda x: x.isdigit() or x.upper() == 'K', rut_crudo.upper().strip()))
    if len(rut) < 2:
        return rut
    cuerpo, dv = rut[:-1], rut[-1]
    cuerpo_formateado = ""
    while len(cuerpo) > 3:
        cuerpo_formateado = "." + cuerpo[-3:] + cuerpo_formateado
        cuerpo = cuerpo[:-3]
    cuerpo_formateado = cuerpo + cuerpo_formateado
    return f"{cuerpo_formateado}-{dv}"

def parsear_respuesta(respuesta_texto):
    texto = respuesta_texto.replace("\n", " ").strip()
    rut_match = re.search(r'(\d{7,8}[0-9Kk])$', texto.replace(" ", ""))
    rut_crudo = rut_match.group(1) if rut_match else ""
    fecha_hora_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2}:\d{2})?', texto)
    fecha = fecha_hora_match.group(1) if fecha_hora_match else ""
    hora = fecha_hora_match.group(2) if fecha_hora_match and fecha_hora_match.group(2) else ""
    fecha_hora = f"{fecha} {hora}".strip()
    palabras = texto.split()
    index_funcionario = next((i for i, p in enumerate(palabras) if "funcionario" in p.lower()), -1)
    nombre_completo = palabras[2:6] if index_funcionario == -1 and len(palabras) >= 6 else palabras[index_funcionario + 1:index_funcionario + 5]
    apellido = next((nombre_completo.pop(i).upper() for i, p in enumerate(nombre_completo) if any(c.islower() for c in p)), None)
    nombre_completo = [apellido] + [w.upper() for w in nombre_completo] if apellido else [w.upper() for w in nombre_completo]
    return {
        "NOMBRE": ' '.join(nombre_completo),
        "FECHA Y HORA": fecha_hora,
        "RUT": formatear_rut(rut_crudo) if rut_crudo else ""
    }
