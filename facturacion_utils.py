import xml.etree.ElementTree as ET
from datetime import datetime
import uuid

def generar_xml_cfdi(venta, cliente, emisor_info):
    """
    Genera el XML para CFDI 4.0
    emisor_info: diccionario con datos fiscales del emisor
    """
    # Namespaces necesarios
    namespaces = {
        'cfdi': 'http://www.sat.gob.mx/cfd/4',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    # Crear elemento raíz
    comprobante = ET.Element('{http://www.sat.gob.mx/cfd/4}Comprobante')
    comprobante.set('Version', '4.0')
    comprobante.set('Serie', 'A')
    comprobante.set('Folio', venta.folio)
    comprobante.set('Fecha', datetime.now().isoformat()[:19])
    comprobante.set('FormaPago', '01')  # Efectivo
    comprobante.set('Moneda', 'MXN')
    comprobante.set('TipoCambio', '1')
    comprobante.set('Total', str(venta.total))
    comprobante.set('SubTotal', str(venta.total))
    comprobante.set('MetodoPago', 'PUE')  # Pago en una sola exhibición
    comprobante.set('LugarExpedicion', emisor_info['codigo_postal'])
    comprobante.set('Exportacion', '01')
    
    # Emisor
    emisor = ET.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Emisor')
    emisor.set('Rfc', emisor_info['rfc'])
    emisor.set('Nombre', emisor_info['razon_social'])
    emisor.set('RegimenFiscal', emisor_info['regimen_fiscal'])
    
    # Receptor
    receptor = ET.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Receptor')
    receptor.set('Rfc', cliente.rfc or 'XAXX010101000')
    receptor.set('Nombre', cliente.razon_social or f'{cliente.nombre} {cliente.apellido}')
    receptor.set('DomicilioFiscalReceptor', cliente.codigo_postal or '')
    receptor.set('RegimenFiscalReceptor', cliente.regimen_fiscal or '')
    receptor.set('UsoCFDI', cliente.uso_cfdi or 'G03')
    
    # Conceptos
    conceptos = ET.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Conceptos')
    
    for detalle in venta.detalles:
        concepto = ET.SubElement(conceptos, '{http://www.sat.gob.mx/cfd/4}Concepto')
        concepto.set('ClaveProdServ', '01010101')  # Código genérico
        concepto.set('NoIdentificacion', detalle.producto.codigo_barras or '')
        concepto.set('Cantidad', str(detalle.cantidad))
        concepto.set('ClaveUnidad', 'H87')  # Pieza
        concepto.set('Unidad', 'Pieza')
        concepto.set('Descripcion', detalle.producto.nombre)
        concepto.set('ValorUnitario', str(detalle.precio_unitario))
        concepto.set('Importe', str(detalle.subtotal))
        concepto.set('ObjetoImp', '01')  # No objeto de impuesto
        
        # Impuestos del concepto
        impuestos = ET.SubElement(concepto, '{http://www.sat.gob.mx/cfd/4}Impuestos')
        traslados = ET.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
        traslado = ET.SubElement(traslados, '{http://www.sat.gob.mx/cfd/4}Traslado')
        traslado.set('Base', str(detalle.subtotal))
        traslado.set('Impuesto', '002')  # IVA
        traslado.set('TipoFactor', 'Tasa')
        traslado.set('TasaOCuota', '0.160000')
        traslado.set('Importe', str(detalle.subtotal * 0.16))
    
    # Impuestos del comprobante
    impuestos = ET.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Impuestos')
    impuestos.set('TotalImpuestosTrasladados', str(venta.total * 0.16))
    
    traslados = ET.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
    traslado = ET.SubElement(traslados, '{http://www.sat.gob.mx/cfd/4}Traslado')
    traslado.set('Impuesto', '002')
    traslado.set('TipoFactor', 'Tasa')
    traslado.set('TasaOCuota', '0.160000')
    traslado.set('Importe', str(venta.total * 0.16))
    
    # Convertir a XML
    xml_str = ET.tostring(comprobante, encoding='unicode')
    
    # Agregar declaración XML
    xml_final = '<?xml version="1.0" encoding="UTF-8"?>' + xml_str
    
    return xml_final

def generar_qr_cfdi(xml_str, emisor_info):
    """Genera el código QR para el CFDI (implementación básica)"""
    # En una implementación real, esto generaría un código QR con los datos del CFDI
    return f"https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?{uuid.uuid4()}"