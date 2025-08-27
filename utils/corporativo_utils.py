import random
import string
from datetime import datetime

def generar_folio(prefix):
    """Genera un folio único con prefijo y fecha"""
    fecha = datetime.now().strftime('%y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{fecha}-{random_str}"

def convertir_documento(documento_actual, nuevo_tipo, datos_adicionales=None):
    """
    Convierte un documento a otro tipo en el flujo secuencial
    """
    # Esta función se implementará según el tipo de conversión
    pass

def obtener_estados_siguientes(tipo_documento, estado_actual):
    """
    Devuelve los estados posibles a los que puede avanzar un documento
    """
    flujos = {
        'requisicion': {
            'pendiente': ['aprobada', 'rechazada'],
            'aprobada': ['convertida_cotizacion'],
            'rechazada': []
        },
        'cotizacion_compra': {
            'pendiente': ['aceptada', 'rechazada'],
            'aceptada': ['convertida_orden'],
            'rechazada': []
        },
        # ... más flujos
    }
    
    return flujos.get(tipo_documento, {}).get(estado_actual, [])

def validar_conversion(tipo_origen, tipo_destino, estado_actual):
    """
    Valida si un documento puede convertirse a otro tipo
    """
    conversiones_permitidas = {
        'requisicion': ['cotizacion_compra'],
        'cotizacion_compra': ['orden_compra'],
        'orden_compra': ['factura_compra'],
        'cotizacion_venta': ['remision'],
        'remision': ['factura_venta']
    }
    
    return (tipo_destino in conversiones_permitidas.get(tipo_origen, []) and 
            estado_actual in ['aprobada', 'aceptada', 'entregada'])