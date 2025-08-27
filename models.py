from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal
db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    tipo_cliente = db.Column(db.String(20), default='mostrador')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos fiscales para CFDI 4.0
    razon_social = db.Column(db.String(200))
    rfc = db.Column(db.String(13))
    regimen_fiscal = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(5))
    uso_cfdi = db.Column(db.String(50))  # Uso del CFDI: G01, G03, etc.
    
    def __repr__(self):
        return f'<Cliente {self.nombre} {self.apellido}>'

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos fiscales para CFDI 4.0
    razon_social = db.Column(db.String(200))
    rfc = db.Column(db.String(13))
    regimen_fiscal = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(5))
    
    productos = db.relationship('Producto', backref='proveedor_rel', lazy=True)
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=True)  # Cambiado de codigo_barras a codigo
    codigo_barras = db.Column(db.String(50), unique=True, nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_compra = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    categoria = db.Column(db.String(50))
    
    # Campos fiscales
    clave_producto_sat = db.Column(db.String(50))  # Clave SAT
    unidad_medida_sat = db.Column(db.String(20), default='H87')  # H87 = Pieza
    clave_unidad_sat = db.Column(db.String(3), default='E48')  # E48 = Servicio
    objeto_impuesto_sat = db.Column(db.String(2), default='02')  # 02 = Sí causa IVA
    
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    imagen_url = db.Column(db.String(200), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
    
    def necesita_reabastecimiento(self):
        return self.stock <= self.stock_minimo


class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    total = db.Column(db.Numeric(10, 2), nullable=False)
    efectivo = db.Column(db.Numeric(10, 2))
    cambio = db.Column(db.Numeric(10, 2))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='completada')  # completada, cancelada, devolucion
    
    cliente = db.relationship('Cliente', backref='ventas')
    detalles = db.relationship('DetalleVenta', backref='venta', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Venta {self.folio}>'

class DetalleVenta(db.Model):
    __tablename__ = 'detalles_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    producto = db.relationship('Producto', backref='ventas_detalles')
    
    def __repr__(self):
        return f'<DetalleVenta {self.id}>'

class Devolucion(db.Model):
    __tablename__ = 'devoluciones'
    
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    motivo = db.Column(db.Text)
    total_devolucion = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    venta = db.relationship('Venta', backref='devoluciones')
    detalles = db.relationship('DetalleDevolucion', backref='devolucion', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Devolucion {self.id}>'

class DetalleDevolucion(db.Model):
    __tablename__ = 'detalles_devolucion'
    
    id = db.Column(db.Integer, primary_key=True)
    devolucion_id = db.Column(db.Integer, db.ForeignKey('devoluciones.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    producto = db.relationship('Producto', backref='devoluciones_detalles')
    
    def __repr__(self):
        return f'<DetalleDevolucion {self.id}>'
    
    # ... (modelos existentes)

# Modelos para módulo de Compras
class RequisicionCompra(db.Model):
    __tablename__ = 'requisiciones_compra'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    solicitante = db.Column(db.String(100))
    departamento = db.Column(db.String(100))
    justificacion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aprobada, rechazada
    total_estimado = db.Column(db.Float, default=0.0)
    
    detalles = db.relationship('DetalleRequisicion', backref='requisicion', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RequisicionCompra {self.folio}>'

class DetalleRequisicion(db.Model):
    __tablename__ = 'detalles_requisicion'
    
    id = db.Column(db.Integer, primary_key=True)
    requisicion_id = db.Column(db.Integer, db.ForeignKey('requisiciones_compra.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    unidad_medida = db.Column(db.String(20))
    precio_estimado = db.Column(db.Float, default=0.0)
    
    producto = db.relationship('Producto', backref='requisiciones_detalles')
    
    def __repr__(self):
        return f'<DetalleRequisicion {self.id}>'

class CotizacionCompra(db.Model):
    __tablename__ = 'cotizaciones_compra'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    requisicion_id = db.Column(db.Integer, db.ForeignKey('requisiciones_compra.id'))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    validez = db.Column(db.Integer, default=30)  # días de validez
    condiciones_pago = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aceptada, rechazada
    total = db.Column(db.Float, default=0.0)
    
    requisicion = db.relationship('RequisicionCompra', backref='cotizaciones')
    proveedor = db.relationship('Proveedor', backref='cotizaciones')
    detalles = db.relationship('DetalleCotizacionCompra', backref='cotizacion', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CotizacionCompra {self.folio}>'

class DetalleCotizacionCompra(db.Model):
    __tablename__ = 'detalles_cotizacion_compra'
    
    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizaciones_compra.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Producto', backref='cotizaciones_compra_detalles')
    
    def __repr__(self):
        return f'<DetalleCotizacionCompra {self.id}>'

class OrdenCompra(db.Model):
    __tablename__ = 'ordenes_compra'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizaciones_compra.id'))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_esperada_entrega = db.Column(db.DateTime)
    condiciones_pago = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, parcial, completada, cancelada
    total = db.Column(db.Float, default=0.0)
    
    cotizacion = db.relationship('CotizacionCompra', backref='ordenes_compra')
    proveedor = db.relationship('Proveedor', backref='ordenes_compra')
    detalles = db.relationship('DetalleOrdenCompra', backref='orden_compra', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<OrdenCompra {self.folio}>'

class DetalleOrdenCompra(db.Model):
    __tablename__ = 'detalles_orden_compra'
    
    id = db.Column(db.Integer, primary_key=True)
    orden_compra_id = db.Column(db.Integer, db.ForeignKey('ordenes_compra.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Producto', backref='ordenes_compra_detalles')
    
    def __repr__(self):
        return f'<DetalleOrdenCompra {self.id}>'

class FacturaCompra(db.Model):
    __tablename__ = 'facturas_compra'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    orden_compra_id = db.Column(db.Integer, db.ForeignKey('ordenes_compra.id'))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_factura = db.Column(db.DateTime)
    uuid = db.Column(db.String(50))  # UUID del CFDI
    total = db.Column(db.Float, default=0.0)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagada, cancelada
    
    orden_compra = db.relationship('OrdenCompra', backref='facturas')
    proveedor = db.relationship('Proveedor', backref='facturas_compra')
    detalles = db.relationship('DetalleFacturaCompra', backref='factura', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FacturaCompra {self.folio}>'

class DetalleFacturaCompra(db.Model):
    __tablename__ = 'detalles_factura_compra'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas_compra.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Producto', backref='facturas_compra_detalles')
    
    def __repr__(self):
        return f'<DetalleFacturaCompra {self.id}>'

# Modelos para módulo de Ventas Corporativas
class CotizacionVenta(db.Model):
    __tablename__ = 'cotizaciones_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    validez = db.Column(db.Integer, default=30)  # días de validez
    condiciones_pago = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aceptada, rechazada
    total = db.Column(db.Float, default=0.0)
    
    cliente = db.relationship('Cliente', backref='cotizaciones_venta')
    detalles = db.relationship('DetalleCotizacionVenta', backref='cotizacion', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CotizacionVenta {self.folio}>'

class DetalleCotizacionVenta(db.Model):
    __tablename__ = 'detalles_cotizacion_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizaciones_venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Producto', backref='cotizaciones_venta_detalles')
    
    def __repr__(self):
        return f'<DetalleCotizacionVenta {self.id}>'

class Remision(db.Model):
    __tablename__ = 'remisiones'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizaciones_venta.id'))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, entregada, cancelada
    total = db.Column(db.Float, default=0.0)
    
    cotizacion = db.relationship('CotizacionVenta', backref='remisiones')
    cliente = db.relationship('Cliente', backref='remisiones')
    detalles = db.relationship('DetalleRemision', backref='remision', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Remision {self.folio}>'

class DetalleRemision(db.Model):
    __tablename__ = 'detalles_remision'
    
    id = db.Column(db.Integer, primary_key=True)
    remision_id = db.Column(db.Integer, db.ForeignKey('remisiones.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Producto', backref='remisiones_detalles')
    
    def __repr__(self):
        return f'<DetalleRemision {self.id}>'

class FacturaVenta(db.Model):
    __tablename__ = 'facturas_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True)
    remision_id = db.Column(db.Integer, db.ForeignKey('remisiones.id'))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_factura = db.Column(db.DateTime)
    uuid = db.Column(db.String(50))  # UUID del CFDI
    total = db.Column(db.Float, default=0.0)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagada, cancelada
    
    remision = db.relationship('Remision', backref='facturas')
    cliente = db.relationship('Cliente', backref='facturas_venta')
    detalles = db.relationship('DetalleFacturaVenta', backref='factura', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FacturaVenta {self.folio}>'

class DetalleFacturaVenta(db.Model):
    __tablename__ = 'detalles_factura_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas_venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    importe = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Producto', backref='facturas_venta_detalles')
    
    def __repr__(self):
        return f'<DetalleFacturaVenta {self.id}>'

# Modelo para configuración del sistema
class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuracion_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text)
    tipo = db.Column(db.String(20))  # string, integer, boolean, json
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(20))  # general, facturacion, apariencia, etc.
    
    def __repr__(self):
        return f'<ConfiguracionSistema {self.clave}>'