import random
import string
from datetime import datetime
from models import Venta, DetalleVenta, Producto

def generar_folio():
    """Genera un folio único para la venta"""
    fecha = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{fecha}-{random_str}"

def procesar_venta(carrito, cliente_id=None, efectivo=0):
    """Procesa una venta y actualiza el inventario"""
    from models import db
    
    try:
        # Calcular total
        total = sum(item['subtotal'] for item in carrito)
        
        # Calcular cambio
        cambio = max(0, efectivo - total) if efectivo else 0
        
        # Crear venta
        venta = Venta(
            folio=generar_folio(),
            cliente_id=cliente_id,
            total=total,
            efectivo=efectivo,
            cambio=cambio,
            fecha_creacion=datetime.utcnow()
        )
        
        db.session.add(venta)
        
        # Crear detalles de venta y actualizar inventario
        for item in carrito:
            producto = Producto.query.get(item['producto_id'])
            
            # Verificar stock suficiente
            if producto.stock < item['cantidad']:
                raise Exception(f"Stock insuficiente para {producto.nombre}")
            
            # Actualizar stock
            producto.stock -= item['cantidad']
            
            # Crear detalle de venta
            detalle = DetalleVenta(
                venta=venta,
                producto_id=item['producto_id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
                subtotal=item['subtotal']
            )
            
            db.session.add(detalle)
        
        db.session.commit()
        return venta, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def buscar_producto_por_codigo(codigo):
    """Busca un producto por código de barras"""
    return Producto.query.filter(
        (Producto.codigo_barras == codigo) | (Producto.id == codigo)
    ).first()

def obtener_resumen_ventas(fecha_inicio=None, fecha_fin=None):
    """Obtiene un resumen de ventas para el día o rango de fechas"""
    from models import db
    
    query = db.session.query(
        db.func.count(Venta.id).label('total_ventas'),
        db.func.sum(Venta.total).label('total_ingresos')
    ).filter(Venta.estado == 'completada')
    
    if fecha_inicio:
        query = query.filter(Venta.fecha_creacion >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Venta.fecha_creacion <= fecha_fin)
    
    return query.first()