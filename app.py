from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, session
from models import db, Proveedor, Cliente, Producto, Venta, DetalleVenta, Devolucion, DetalleDevolucion
from models import (
    RequisicionCompra, DetalleRequisicion, CotizacionCompra, DetalleCotizacionCompra,
    OrdenCompra, DetalleOrdenCompra, FacturaCompra, DetalleFacturaCompra,
    CotizacionVenta, DetalleCotizacionVenta, Remision, DetalleRemision,
    FacturaVenta, DetalleFacturaVenta, ConfiguracionSistema
)
from datetime import datetime
import os
import pandas as pd
from utils.import_utils import (
    importar_proveedores_desde_csv, 
    importar_clientes_desde_csv, 
    importar_productos_desde_csv,
    generar_ejemplo_csv
)
import io
from flask import send_file
from utils.pos_utils import (
    procesar_venta, 
    buscar_producto_por_codigo,
    obtener_resumen_ventas
)
import json
from facturacion_utils import generar_xml_cfdi, generar_qr_cfdi, generar_timbre_fiscal
from utils.corporativo_utils import generar_folio, convertir_documento, obtener_estados_siguientes, validar_conversion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_tienda_abarrotes_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda_abarrotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Context processor para agregar variables globales a todos los templates
@app.context_processor
def inject_global_vars():
    return {
        'now': datetime.now(),
        'current_year': datetime.now().year
    }

# Crear tablas al inicio
with app.app_context():
    db.create_all()

# ========== RUTAS PRINCIPALES ==========
@app.route('/')
def index():
    try:
        total_proveedores = Proveedor.query.count() or 0
        total_clientes = Cliente.query.count() or 0
        total_productos = Producto.query.count() or 0
        productos_bajo_stock = Producto.query.filter(Producto.stock <= Producto.stock_minimo).count() or 0
        
        return render_template('index.html',
                             total_proveedores=total_proveedores,
                             total_clientes=total_clientes,
                             total_productos=total_productos,
                             productos_bajo_stock=productos_bajo_stock)
    except Exception as e:
        return render_template('index.html',
                             total_proveedores=0,
                             total_clientes=0,
                             total_productos=0,
                             productos_bajo_stock=0)

# ========== MÓDULO DE PROVEEDORES ==========
@app.route('/proveedores')
def lista_proveedores():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('proveedores/lista.html', proveedores=proveedores)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    if request.method == 'POST':
        try:
            proveedor = Proveedor(
                nombre=request.form['nombre'],
                contacto=request.form.get('contacto', ''),
                telefono=request.form.get('telefono', ''),
                email=request.form.get('email', ''),
                direccion=request.form.get('direccion', ''),
                razon_social=request.form.get('razon_social', ''),
                rfc=request.form.get('rfc', ''),
                regimen_fiscal=request.form.get('regimen_fiscal', ''),
                codigo_postal=request.form.get('codigo_postal', ''),
                calle=request.form.get('calle', ''),
                numero_exterior=request.form.get('numero_exterior', ''),
                numero_interior=request.form.get('numero_interior', ''),
                colonia=request.form.get('colonia', ''),
                municipio=request.form.get('municipio', ''),
                estado=request.form.get('estado', ''),
                pais=request.form.get('pais', 'México')
            )
            db.session.add(proveedor)
            db.session.commit()
            flash('✅ Proveedor creado exitosamente', 'success')
            return redirect(url_for('lista_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear proveedor: {str(e)}', 'danger')
    
    return render_template('proveedores/nuevo.html')

@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            proveedor.nombre = request.form['nombre']
            proveedor.contacto = request.form.get('contacto', '')
            proveedor.telefono = request.form.get('telefono', '')
            proveedor.email = request.form.get('email', '')
            proveedor.direccion = request.form.get('direccion', '')
            proveedor.razon_social = request.form.get('razon_social', '')
            proveedor.rfc = request.form.get('rfc', '')
            proveedor.regimen_fiscal = request.form.get('regimen_fiscal', '')
            proveedor.codigo_postal = request.form.get('codigo_postal', '')
            proveedor.calle = request.form.get('calle', '')
            proveedor.numero_exterior = request.form.get('numero_exterior', '')
            proveedor.numero_interior = request.form.get('numero_interior', '')
            proveedor.colonia = request.form.get('colonia', '')
            proveedor.municipio = request.form.get('municipio', '')
            proveedor.estado = request.form.get('estado', '')
            proveedor.pais = request.form.get('pais', 'México')
            
            db.session.commit()
            flash('✅ Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('lista_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar proveedor: {str(e)}', 'danger')
    
    return render_template('proveedores/editar.html', proveedor=proveedor)

@app.route('/proveedores/eliminar/<int:id>')
def eliminar_proveedor(id):
    try:
        proveedor = Proveedor.query.get_or_404(id)
        
        if proveedor.productos:
            flash('❌ No se puede eliminar el proveedor porque tiene productos asociados', 'danger')
            return redirect(url_for('lista_proveedores'))
            
        db.session.delete(proveedor)
        db.session.commit()
        flash('✅ Proveedor eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al eliminar proveedor: {str(e)}', 'danger')
    
    return redirect(url_for('lista_proveedores'))

# ========== MÓDULO DE CLIENTES ==========
@app.route('/clientes')
def lista_clientes():
    tipo = request.args.get('tipo', 'all')
    
    if tipo == 'mostrador':
        clientes = Cliente.query.filter_by(tipo_cliente='mostrador').order_by(Cliente.nombre).all()
    elif tipo == 'registrado':
        clientes = Cliente.query.filter_by(tipo_cliente='registrado').order_by(Cliente.nombre).all()
    else:
        clientes = Cliente.query.order_by(Cliente.nombre).all()
    
    return render_template('clientes/lista.html', clientes=clientes, tipo_seleccionado=tipo)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        try:
            cliente = Cliente(
                nombre=request.form['nombre'],
                apellido=request.form.get('apellido', ''),
                telefono=request.form.get('telefono', ''),
                email=request.form.get('email', ''),
                direccion=request.form.get('direccion', ''),
                tipo_cliente=request.form.get('tipo_cliente', 'mostrador'),
                razon_social=request.form.get('razon_social', ''),
                rfc=request.form.get('rfc', ''),
                regimen_fiscal=request.form.get('regimen_fiscal', ''),
                codigo_postal=request.form.get('codigo_postal', ''),
                calle=request.form.get('calle', ''),
                numero_exterior=request.form.get('numero_exterior', ''),
                numero_interior=request.form.get('numero_interior', ''),
                colonia=request.form.get('colonia', ''),
                municipio=request.form.get('municipio', ''),
                estado=request.form.get('estado', ''),
                pais=request.form.get('pais', 'México'),
                uso_cfdi=request.form.get('uso_cfdi', 'G03')
            )
            db.session.add(cliente)
            db.session.commit()
            flash('✅ Cliente creado exitosamente', 'success')
            return redirect(url_for('lista_clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear cliente: {str(e)}', 'danger')
    
    return render_template('clientes/nuevo.html')

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            cliente.nombre = request.form['nombre']
            cliente.apellido = request.form.get('apellido', '')
            cliente.telefono = request.form.get('telefono', '')
            cliente.email = request.form.get('email', '')
            cliente.direccion = request.form.get('direccion', '')
            cliente.tipo_cliente = request.form.get('tipo_cliente', 'mostrador')
            cliente.razon_social = request.form.get('razon_social', '')
            cliente.rfc = request.form.get('rfc', '')
            cliente.regimen_fiscal = request.form.get('regimen_fiscal', '')
            cliente.codigo_postal = request.form.get('codigo_postal', '')
            cliente.calle = request.form.get('calle', '')
            cliente.numero_exterior = request.form.get('numero_exterior', '')
            cliente.numero_interior = request.form.get('numero_interior', '')
            cliente.colonia = request.form.get('colonia', '')
            cliente.municipio = request.form.get('municipio', '')
            cliente.estado = request.form.get('estado', '')
            cliente.pais = request.form.get('pais', 'México')
            cliente.uso_cfdi = request.form.get('uso_cfdi', 'G03')
            
            db.session.commit()
            flash('✅ Cliente actualizado exitosamente', 'success')
            return redirect(url_for('lista_clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar cliente: {str(e)}', 'danger')
    
    return render_template('clientes/editar.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        db.session.delete(cliente)
        db.session.commit()
        flash('✅ Cliente eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al eliminar cliente: {str(e)}', 'danger')
    
    return redirect(url_for('lista_clientes'))

# ========== MÓDULO DE PRODUCTOS ==========
@app.route('/productos')
def lista_productos():
    categoria = request.args.get('categoria', 'all')
    stock = request.args.get('stock', 'all')
    
    query = Producto.query
    
    if categoria != 'all':
        query = query.filter_by(categoria=categoria)
    
    if stock == 'bajo':
        query = query.filter(Producto.stock <= Producto.stock_minimo)
    elif stock == 'sin':
        query = query.filter(Producto.stock == 0)
    
    productos = query.order_by(Producto.nombre).all()
    categorias = db.session.query(Producto.categoria).distinct().all()
    categorias = [cat[0] for cat in categorias if cat[0]]
    
    return render_template('productos/lista.html', 
                         productos=productos, 
                         categorias=categorias,
                         categoria_seleccionada=categoria,
                         stock_seleccionado=stock)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    
    if request.method == 'POST':
        try:
            # Validaciones
            codigo = request.form.get('codigo', '')
            if codigo:
                existe_codigo = Producto.query.filter_by(codigo=codigo).first()
                if existe_codigo:
                    flash('❌ El código del producto ya existe', 'danger')
                    return render_template('productos/nuevo.html', proveedores=proveedores)
            
            codigo_barras = request.form.get('codigo_barras', '')
            if codigo_barras:
                existe_codigo_barras = Producto.query.filter_by(codigo_barras=codigo_barras).first()
                if existe_codigo_barras:
                    flash('❌ El código de barras del producto ya existe', 'danger')
                    return render_template('productos/nuevo.html', proveedores=proveedores)
            
            nombre = request.form['nombre']
            existe_nombre = Producto.query.filter_by(nombre=nombre).first()
            if existe_nombre:
                flash('❌ El nombre del producto ya existe', 'danger')
                return render_template('productos/nuevo.html', proveedores=proveedores)
            
            # Crear producto
            producto = Producto(
                codigo=codigo,
                codigo_barras=codigo_barras,
                nombre=nombre,
                descripcion=request.form.get('descripcion', ''),
                precio_compra=float(request.form['precio_compra']),
                precio_venta=float(request.form['precio_venta']),
                stock=int(request.form.get('stock', 0)),
                stock_minimo=int(request.form.get('stock_minimo', 5)),
                categoria=request.form.get('categoria', ''),
                clave_producto_sat=request.form.get('clave_producto_sat', ''),
                unidad_medida_sat=request.form.get('unidad_medida_sat', 'H87'),
                clave_unidad_sat=request.form.get('clave_unidad_sat', 'E48'),
                objeto_impuesto_sat=request.form.get('objeto_impuesto_sat', '02'),
                proveedor_id=int(request.form['proveedor_id'])
            )
            
            db.session.add(producto)
            db.session.commit()
            flash('✅ Producto creado exitosamente', 'success')
            return redirect(url_for('lista_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear producto: {str(e)}', 'danger')
    
    return render_template('productos/nuevo.html', proveedores=proveedores)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    
    if request.method == 'POST':
        try:
            # Validaciones
            codigo = request.form.get('codigo', '')
            if codigo and codigo != producto.codigo:
                existe_codigo = Producto.query.filter(Producto.codigo == codigo, Producto.id != id).first()
                if existe_codigo:
                    flash('❌ El código del producto ya existe', 'danger')
                    return render_template('productos/editar.html', producto=producto, proveedores=proveedores)
            
            codigo_barras = request.form.get('codigo_barras', '')
            if codigo_barras and codigo_barras != producto.codigo_barras:
                existe_codigo_barras = Producto.query.filter(Producto.codigo_barras == codigo_barras, Producto.id != id).first()
                if existe_codigo_barras:
                    flash('❌ El código de barras del producto ya existe', 'danger')
                    return render_template('productos/editar.html', producto=producto, proveedores=proveedores)
            
            nombre = request.form['nombre']
            if nombre != producto.nombre:
                existe_nombre = Producto.query.filter(Producto.nombre == nombre, Producto.id != id).first()
                if existe_nombre:
                    flash('❌ El nombre del producto ya existe', 'danger')
                    return render_template('productos/editar.html', producto=producto, proveedores=proveedores)
            
            # Actualizar producto
            producto.codigo = codigo
            producto.codigo_barras = codigo_barras
            producto.nombre = nombre
            producto.descripcion = request.form.get('descripcion', '')
            producto.precio_compra = float(request.form['precio_compra'])
            producto.precio_venta = float(request.form['precio_venta'])
            producto.stock = int(request.form.get('stock', 0))
            producto.stock_minimo = int(request.form.get('stock_minimo', 5))
            producto.categoria = request.form.get('categoria', '')
            producto.clave_producto_sat = request.form.get('clave_producto_sat', '')
            producto.unidad_medida_sat = request.form.get('unidad_medida_sat', 'H87')
            producto.clave_unidad_sat = request.form.get('clave_unidad_sat', 'E48')
            producto.objeto_impuesto_sat = request.form.get('objeto_impuesto_sat', '02')
            producto.proveedor_id = int(request.form['proveedor_id'])
            
            db.session.commit()
            flash('✅ Producto actualizado exitosamente', 'success')
            return redirect(url_for('lista_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar producto: {str(e)}', 'danger')
    
    return render_template('productos/editar.html', producto=producto, proveedores=proveedores)

@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):
    try:
        producto = Producto.query.get_or_404(id)
        db.session.delete(producto)
        db.session.commit()
        flash('✅ Producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al eliminar producto: {str(e)}', 'danger')
    
    return redirect(url_for('lista_productos'))

# ========== MÓDULO POS (EXISTENTE) ==========
@app.route('/pos')
def punto_venta():
    if 'carrito' not in session:
        session['carrito'] = []
    
    productos = Producto.query.filter_by(activo=True).all()
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    
    hoy = datetime.now().date()
    resumen = obtener_resumen_ventas(hoy, hoy)
    
    return render_template('pos/pos.html', 
                         productos=productos, 
                         clientes=clientes,
                         resumen=resumen)

# ... (resto de las rutas POS existentes)

# ========== MÓDULO DE COMPRAS CORPORATIVAS ==========
@app.route('/compras/requisiciones')
def lista_requisiciones():
    estado = request.args.get('estado', 'todos')
    
    if estado == 'pendientes':
        requisiciones = RequisicionCompra.query.filter_by(estado='pendiente').order_by(RequisicionCompra.fecha_creacion.desc()).all()
    elif estado == 'aprobadas':
        requisiciones = RequisicionCompra.query.filter_by(estado='aprobada').order_by(RequisicionCompra.fecha_creacion.desc()).all()
    elif estado == 'rechazadas':
        requisiciones = RequisicionCompra.query.filter_by(estado='rechazada').order_by(RequisicionCompra.fecha_creacion.desc()).all()
    else:
        requisiciones = RequisicionCompra.query.order_by(RequisicionCompra.fecha_creacion.desc()).all()
    
    return render_template('compras/requisiciones/lista.html', requisiciones=requisiciones, estado_seleccionado=estado)

@app.route('/compras/requisiciones/nueva', methods=['GET', 'POST'])
def nueva_requisicion():
    if request.method == 'POST':
        try:
            requisicion = RequisicionCompra(
                folio=generar_folio('REQ'),
                solicitante=request.form['solicitante'],
                departamento=request.form['departamento'],
                justificacion=request.form['justificacion'],
                estado='pendiente',
                total_estimado=0.0
            )
            db.session.add(requisicion)
            db.session.commit()
            flash('✅ Requisición creada exitosamente', 'success')
            return redirect(url_for('editar_requisicion', id=requisicion.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear requisición: {str(e)}', 'danger')
    
    return render_template('compras/requisiciones/nueva.html')

@app.route('/compras/requisiciones/<int:id>/editar', methods=['GET', 'POST'])
def editar_requisicion(id):
    requisicion = RequisicionCompra.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            requisicion.solicitante = request.form['solicitante']
            requisicion.departamento = request.form['departamento']
            requisicion.justificacion = request.form['justificacion']
            
            # Procesar detalles
            detalles_data = request.get_json().get('detalles', [])
            total_estimado = 0
            
            # Eliminar detalles existentes
            DetalleRequisicion.query.filter_by(requisicion_id=id).delete()
            
            for detalle in detalles_data:
                nuevo_detalle = DetalleRequisicion(
                    requisicion_id=id,
                    producto_id=detalle.get('producto_id'),
                    descripcion=detalle['descripcion'],
                    cantidad=detalle['cantidad'],
                    unidad_medida=detalle.get('unidad_medida', ''),
                    precio_estimado=detalle.get('precio_estimado', 0)
                )
                db.session.add(nuevo_detalle)
                total_estimado += detalle['cantidad'] * detalle.get('precio_estimado', 0)
            
            requisicion.total_estimado = total_estimado
            db.session.commit()
            
            return jsonify({'success': True, 'total_estimado': total_estimado})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    return render_template('compras/requisiciones/editar.html', requisicion=requisicion)

@app.route('/compras/requisiciones/<int:id>/aprobar')
def aprobar_requisicion(id):
    requisicion = RequisicionCompra.query.get_or_404(id)
    
    if requisicion.estado != 'pendiente':
        flash('❌ Solo se pueden aprobar requisiciones pendientes', 'danger')
        return redirect(url_for('detalle_requisicion', id=id))
    
    try:
        requisicion.estado = 'aprobada'
        db.session.commit()
        flash('✅ Requisición aprobada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al aprobar requisición: {str(e)}', 'danger')
    
    return redirect(url_for('detalle_requisicion', id=id))

@app.route('/compras/requisiciones/<int:id>/rechazar')
def rechazar_requisicion(id):
    requisicion = RequisicionCompra.query.get_or_404(id)
    
    if requisicion.estado != 'pendiente':
        flash('❌ Solo se pueden rechazar requisiciones pendientes', 'danger')
        return redirect(url_for('detalle_requisicion', id=id))
    
    try:
        requisicion.estado = 'rechazada'
        db.session.commit()
        flash('✅ Requisición rechazada', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al rechazar requisición: {str(e)}', 'danger')
    
    return redirect(url_for('detalle_requisicion', id=id))

@app.route('/compras/requisiciones/<int:id>/convertir/cotizacion')
def convertir_requisicion_cotizacion(id):
    requisicion = RequisicionCompra.query.get_or_404(id)
    
    if requisicion.estado != 'aprobada':
        flash('❌ Solo se pueden convertir requisiciones aprobadas', 'danger')
        return redirect(url_for('detalle_requisicion', id=id))
    
    try:
        cotizacion = CotizacionCompra(
            folio=generar_folio('COT'),
            requisicion_id=requisicion.id,
            estado='pendiente',
            total=0.0
        )
        db.session.add(cotizacion)
        db.session.flush()
        
        # Copiar detalles
        for detalle in requisicion.detalles:
            nuevo_detalle = DetalleCotizacionCompra(
                cotizacion_id=cotizacion.id,
                producto_id=detalle.producto_id,
                descripcion=detalle.descripcion,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_estimado or 0,
                importe=detalle.cantidad * (detalle.precio_estimado or 0)
            )
            db.session.add(nuevo_detalle)
            cotizacion.total += nuevo_detalle.importe
        
        db.session.commit()
        flash('✅ Cotización creada a partir de la requisición', 'success')
        return redirect(url_for('editar_cotizacion_compra', id=cotizacion.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al crear cotización: {str(e)}', 'danger')
        return redirect(url_for('detalle_requisicion', id=id))

# ... (rutas similares para cotizaciones, órdenes de compra, facturas de compra)

# ========== MÓDULO DE VENTAS CORPORATIVAS ==========
@app.route('/ventas/cotizaciones')
def lista_cotizaciones_venta():
    estado = request.args.get('estado', 'todos')
    
    if estado == 'pendientes':
        cotizaciones = CotizacionVenta.query.filter_by(estado='pendiente').order_by(CotizacionVenta.fecha_creacion.desc()).all()
    elif estado == 'aceptadas':
        cotizaciones = CotizacionVenta.query.filter_by(estado='aceptada').order_by(CotizacionVenta.fecha_creacion.desc()).all()
    elif estado == 'rechazadas':
        cotizaciones = CotizacionVenta.query.filter_by(estado='rechazada').order_by(CotizacionVenta.fecha_creacion.desc()).all()
    else:
        cotizaciones = CotizacionVenta.query.order_by(CotizacionVenta.fecha_creacion.desc()).all()
    
    return render_template('ventas/cotizaciones/lista.html', cotizaciones=cotizaciones, estado_seleccionado=estado)

@app.route('/ventas/cotizaciones/nueva', methods=['GET', 'POST'])
def nueva_cotizacion_venta():
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    productos = Producto.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        try:
            cotizacion = CotizacionVenta(
                folio=generar_folio('COTV'),
                cliente_id=int(request.form['cliente_id']),
                validez=int(request.form.get('validez', 30)),
                condiciones_pago=request.form.get('condiciones_pago', ''),
                observaciones=request.form.get('observaciones', ''),
                estado='pendiente',
                total=0.0
            )
            db.session.add(cotizacion)
            db.session.commit()
            flash('✅ Cotización de venta creada exitosamente', 'success')
            return redirect(url_for('editar_cotizacion_venta', id=cotizacion.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear cotización: {str(e)}', 'danger')
    
    return render_template('ventas/cotizaciones/nueva.html', clientes=clientes, productos=productos)

# ... (rutas similares para remisiones y facturas de venta)

# ========== MÓDULO DE CONFIGURACIÓN ==========
@app.route('/configuracion')
def configuracion():
    return render_template('configuracion/general.html')

@app.route('/configuracion/general', methods=['GET', 'POST'])
def configuracion_general():
    if request.method == 'POST':
        try:
            # Guardar configuración general
            configuraciones = {
                'nombre_tienda': request.form.get('nombre_tienda', ''),
                'rfc_tienda': request.form.get('rfc_tienda', ''),
                'telefono_tienda': request.form.get('telefono_tienda', ''),
                'email_tienda': request.form.get('email_tienda', ''),
                'direccion_tienda': request.form.get('direccion_tienda', ''),
                'moneda': request.form.get('moneda', 'MXN'),
                'formato_fecha': request.form.get('formato_fecha', 'dd/mm/yyyy'),
                'zona_horaria': request.form.get('zona_horaria', 'America/Mexico_City')
            }
            
            for clave, valor in configuraciones.items():
                config = ConfiguracionSistema.query.filter_by(clave=clave).first()
                if config:
                    config.valor = valor
                else:
                    config = ConfiguracionSistema(
                        clave=clave,
                        valor=valor,
                        tipo='string',
                        descripcion=f'Configuración de {clave}',
                        categoria='general'
                    )
                    db.session.add(config)
            
            db.session.commit()
            flash('✅ Configuración general guardada exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al guardar configuración: {str(e)}', 'danger')
    
    # Obtener configuraciones actuales
    configs = ConfiguracionSistema.query.filter_by(categoria='general').all()
    configuracion = {config.clave: config.valor for config in configs}
    
    return render_template('configuracion/general.html', configuracion=configuracion)

@app.route('/configuracion/facturacion', methods=['GET', 'POST'])
def configuracion_facturacion():
    if request.method == 'POST':
        try:
            configuraciones = {
                'modo_prueba_facturacion': request.form.get('modo_prueba_facturacion', 'false'),
                'rfc_emisor': request.form.get('rfc_emisor', ''),
                'razon_social_emisor': request.form.get('razon_social_emisor', ''),
                'regimen_fiscal_emisor': request.form.get('regimen_fiscal_emisor', ''),
                'codigo_postal_emisor': request.form.get('codigo_postal_emisor', ''),
                'certificado_pac': request.form.get('certificado_pac', ''),
                'llave_privada_pac': request.form.get('llave_privada_pac', '')
            }
            
            for clave, valor in configuraciones.items():
                config = ConfiguracionSistema.query.filter_by(clave=clave).first()
                if config:
                    config.valor = valor
                else:
                    config = ConfiguracionSistema(
                        clave=clave,
                        valor=valor,
                        tipo='string' if clave != 'modo_prueba_facturacion' else 'boolean',
                        descripcion=f'Configuración de {clave}',
                        categoria='facturacion'
                    )
                    db.session.add(config)
            
            db.session.commit()
            flash('✅ Configuración de facturación guardada exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al guardar configuración: {str(e)}', 'danger')
    
    configs = ConfiguracionSistema.query.filter_by(categoria='facturacion').all()
    configuracion = {config.clave: config.valor for config in configs}
    
    return render_template('configuracion/facturacion.html', configuracion=configuracion)

@app.route('/configuracion/apariencia', methods=['GET', 'POST'])
def configuracion_apariencia():
    if request.method == 'POST':
        try:
            configuraciones = {
                'tema': request.form.get('tema', 'default'),
                'color_primario': request.form.get('color_primario', '#007bff'),
                'color_secundario': request.form.get('color_secundario', '#6c757d'),
                'logo_url': request.form.get('logo_url', ''),
                'favicon_url': request.form.get('favicon_url', '')
            }
            
            for clave, valor in configuraciones.items():
                config = ConfiguracionSistema.query.filter_by(clave=clave).first()
                if config:
                    config.valor = valor
                else:
                    config = ConfiguracionSistema(
                        clave=clave,
                        valor=valor,
                        tipo='string',
                        descripcion=f'Configuración de {clave}',
                        categoria='apariencia'
                    )
                    db.session.add(config)
            
            db.session.commit()
            flash('✅ Configuración de apariencia guardada exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al guardar configuración: {str(e)}', 'danger')
    
    configs = ConfiguracionSistema.query.filter_by(categoria='apariencia').all()
    configuracion = {config.clave: config.valor for config in configs}
    
    return render_template('configuracion/apariencia.html', configuracion=configuracion)

@app.route('/configuracion/usuarios', methods=['GET', 'POST'])
def configuracion_usuarios():
    # Esta función manejaría la configuración de usuarios y permisos
    return render_template('configuracion/usuarios.html')

# ========== RUTAS DE IMPORTACIÓN ==========
@app.route('/proveedores/importar', methods=['GET', 'POST'])
def importar_proveedores():
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)
        
        if archivo and archivo.filename.endswith('.csv'):
            try:
                registros, errores = importar_proveedores_desde_csv(archivo)
                
                if registros > 0:
                    flash(f'✅ Se importaron {registros} proveedores correctamente', 'success')
                
                if errores:
                    for error in errores:
                        flash(f'❌ {error}', 'warning')
                
                return redirect(url_for('lista_proveedores'))
                
            except Exception as e:
                flash(f'❌ Error al importar proveedores: {str(e)}', 'danger')
        
        else:
            flash('❌ Formato de archivo no válido. Solo se aceptan archivos CSV.', 'danger')
    
    return render_template('proveedores/importar.html')

@app.route('/proveedores/descargar-ejemplo')
def descargar_ejemplo_proveedores():
    csv_data = generar_ejemplo_csv('proveedores')
    return send_file(
        io.BytesIO(csv_data.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='ejemplo_proveedores.csv'
    )

# ... (rutas de importación para clientes y productos)

# ========== API PARA BÚSQUEDA RÁPIDA ==========
@app.route('/api/productos/buscar')
def buscar_productos():
    termino = request.args.get('q', '')
    productos = Producto.query.filter(
        (Producto.nombre.ilike(f'%{termino}%')) | 
        (Producto.codigo.ilike(f'%{termino}%')) |
        (Producto.codigo_barras.ilike(f'%{termino}%'))
    ).limit(10).all()
    
    resultados = [{
        'id': p.id,
        'nombre': p.nombre,
        'codigo': p.codigo,
        'codigo_barras': p.codigo_barras,
        'precio_venta': p.precio_venta,
        'stock': p.stock
    } for p in productos]
    
    return jsonify(resultados)

# ========== RUTAS DE FACTURACIÓN ==========
@app.route('/facturar/<int:venta_id>')
def facturar_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    cliente = venta.cliente
    
    emisor_info = {
        'rfc': 'ABC123456789',
        'razon_social': 'Mi Tienda de Abarrotes SA de CV',
        'regimen_fiscal': '601',
        'codigo_postal': '01000'
    }
    
    xml_cfdi = generar_xml_cfdi(venta, cliente, emisor_info)
    qr_url = generar_qr_cfdi(xml_cfdi, emisor_info)
    timbre = generar_timbre_fiscal(xml_cfdi)
    
    return render_template('facturacion/factura.html', 
                         venta=venta,
                         xml_cfdi=xml_cfdi,
                         qr_url=qr_url,
                         uuid=timbre['uuid'],
                         fecha_timbrado=timbre['fecha_timbrado'],
                         no_certificado_sat=timbre['no_certificado_sat'])

@app.route('/descargar-factura/<int:venta_id>')
def descargar_factura(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    cliente = venta.cliente
    emisor_info = {
        'rfc': 'ABC123456789',
        'razon_social': 'Mi Tienda de Abarrotes SA de CV',
        'regimen_fiscal': '601',
        'codigo_postal': '01000'
    }
    
    xml_cfdi = generar_xml_cfdi(venta, cliente, emisor_info)
    
    return Response(
        xml_cfdi,
        mimetype='application/xml',
        headers={'Content-Disposition': f'attachment;filename=factura_{venta.folio}.xml'}
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)