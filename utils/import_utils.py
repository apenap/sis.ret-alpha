import pandas as pd
from models import Proveedor, Cliente, Producto, db
from datetime import datetime
import io

def importar_proveedores_desde_csv(archivo):
    """
    Importa proveedores desde un archivo CSV con campos fiscales
    """
    try:
        # Leer el archivo CSV
        df = pd.read_csv(archivo)
        
        proveedores_importados = 0
        errores = []
        
        for index, row in df.iterrows():
            try:
                # Verificar si el proveedor ya existe
                existe = Proveedor.query.filter(
                    (Proveedor.nombre == row['nombre']) | 
                    (Proveedor.rfc == row.get('rfc', ''))
                ).first()
                
                if existe:
                    errores.append(f"Fila {index+1}: Proveedor '{row['nombre']}' ya existe")
                    continue
                
                # Crear nuevo proveedor con campos fiscales
                proveedor = Proveedor(
                    nombre=row['nombre'],
                    contacto=row.get('contacto', ''),
                    telefono=row.get('telefono', ''),
                    email=row.get('email', ''),
                    direccion=row.get('direccion', ''),
                    # Campos fiscales
                    razon_social=row.get('razon_social', row['nombre']),
                    rfc=row.get('rfc', ''),
                    regimen_fiscal=row.get('regimen_fiscal', ''),
                    codigo_postal=row.get('codigo_postal', ''),
                    calle=row.get('calle', ''),
                    numero_exterior=row.get('numero_exterior', ''),
                    numero_interior=row.get('numero_interior', ''),
                    colonia=row.get('colonia', ''),
                    municipio=row.get('municipio', ''),
                    estado=row.get('estado', ''),
                    pais=row.get('pais', 'México'),
                    fecha_creacion=datetime.utcnow()
                )
                
                db.session.add(proveedor)
                proveedores_importados += 1
                
            except Exception as e:
                errores.append(f"Fila {index+1}: Error - {str(e)}")
        
        db.session.commit()
        return proveedores_importados, errores
        
    except Exception as e:
        return 0, [f"Error al procesar el archivo: {str(e)}"]

def importar_clientes_desde_csv(archivo):
    """
    Importa clientes desde un archivo CSV con campos fiscales
    """
    try:
        # Leer el archivo CSV
        df = pd.read_csv(archivo)
        
        clientes_importados = 0
        errores = []
        
        for index, row in df.iterrows():
            try:
                # Verificar si el cliente ya existe (por email, teléfono o RFC)
                existe_email = Cliente.query.filter_by(email=row.get('email', '')).first() if row.get('email') else None
                existe_telefono = Cliente.query.filter_by(telefono=row.get('telefono', '')).first() if row.get('telefono') else None
                existe_rfc = Cliente.query.filter_by(rfc=row.get('rfc', '')).first() if row.get('rfc') else None
                
                if existe_email or existe_telefono or existe_rfc:
                    errores.append(f"Fila {index+1}: Cliente con email, teléfono o RFC ya existe")
                    continue
                
                # Crear nuevo cliente con campos fiscales
                cliente = Cliente(
                    nombre=row['nombre'],
                    apellido=row.get('apellido', ''),
                    telefono=row.get('telefono', ''),
                    email=row.get('email', ''),
                    direccion=row.get('direccion', ''),
                    tipo_cliente=row.get('tipo_cliente', 'mostrador'),
                    # Campos fiscales
                    razon_social=row.get('razon_social', f"{row['nombre']} {row.get('apellido', '')}"),
                    rfc=row.get('rfc', ''),
                    regimen_fiscal=row.get('regimen_fiscal', ''),
                    codigo_postal=row.get('codigo_postal', ''),
                    calle=row.get('calle', ''),
                    numero_exterior=row.get('numero_exterior', ''),
                    numero_interior=row.get('numero_interior', ''),
                    colonia=row.get('colonia', ''),
                    municipio=row.get('municipio', ''),
                    estado=row.get('estado', ''),
                    pais=row.get('pais', 'México'),
                    uso_cfdi=row.get('uso_cfdi', 'G03'),
                    fecha_registro=datetime.utcnow()
                )
                
                db.session.add(cliente)
                clientes_importados += 1
                
            except Exception as e:
                errores.append(f"Fila {index+1}: Error - {str(e)}")
        
        db.session.commit()
        return clientes_importados, errores
        
    except Exception as e:
        return 0, [f"Error al procesar el archivo: {str(e)}"]

def importar_productos_desde_csv(archivo):
    """
    Importa productos desde un archivo CSV con campos fiscales
    """
    try:
        # Leer el archivo CSV
        df = pd.read_csv(archivo)
        
        productos_importados = 0
        errores = []
        
        for index, row in df.iterrows():
            try:
                # Verificar si el producto ya existe (por código, código_barras o nombre)
                existe_codigo = Producto.query.filter_by(codigo=row.get('codigo', '')).first() if row.get('codigo') else None
                existe_codigo_barras = Producto.query.filter_by(codigo_barras=row.get('codigo_barras', '')).first() if row.get('codigo_barras') else None
                existe_nombre = Producto.query.filter_by(nombre=row['nombre']).first()
                
                if existe_codigo or existe_codigo_barras or existe_nombre:
                    errores.append(f"Fila {index+1}: Producto con código, código de barras o nombre ya existe")
                    continue
                
                # Verificar que el proveedor existe
                proveedor_id = row.get('proveedor_id')
                if proveedor_id:
                    proveedor = Proveedor.query.get(int(proveedor_id))
                    if not proveedor:
                        errores.append(f"Fila {index+1}: Proveedor con ID {proveedor_id} no existe")
                        continue
                
                # Crear nuevo producto con campos fiscales
                producto = Producto(
                    codigo=row.get('codigo', ''),
                    codigo_barras=row.get('codigo_barras', ''),
                    nombre=row['nombre'],
                    descripcion=row.get('descripcion', ''),
                    precio_compra=float(row['precio_compra']),
                    precio_venta=float(row['precio_venta']),
                    stock=int(row.get('stock', 0)),
                    stock_minimo=int(row.get('stock_minimo', 5)),
                    categoria=row.get('categoria', ''),
                    # Campos fiscales
                    clave_producto_sat=row.get('clave_producto_sat', ''),
                    unidad_medida_sat=row.get('unidad_medida_sat', 'H87'),
                    clave_unidad_sat=row.get('clave_unidad_sat', 'E48'),
                    objeto_impuesto_sat=row.get('objeto_impuesto_sat', '02'),
                    proveedor_id=int(row['proveedor_id']),
                    fecha_creacion=datetime.utcnow(),
                    activo=row.get('activo', True)
                )
                
                db.session.add(producto)
                productos_importados += 1
                
            except Exception as e:
                errores.append(f"Fila {index+1}: Error - {str(e)}")
        
        db.session.commit()
        return productos_importados, errores
        
    except Exception as e:
        return 0, [f"Error al procesar el archivo: {str(e)}"]

def generar_ejemplo_csv(tipo):
    """
    Genera un ejemplo de CSV según el tipo con campos fiscales
    """
    if tipo == 'proveedores':
        data = {
            'nombre': ['Proveedor Ejemplo 1', 'Proveedor Ejemplo 2'],
            'contacto': ['Juan Pérez', 'María García'],
            'telefono': ['555-1234', '555-5678'],
            'email': ['juan@proveedor.com', 'maria@proveedor.com'],
            'direccion': ['Calle Falsa 123', 'Avenida Real 456'],
            # Campos fiscales
            'razon_social': ['Proveedor Ejemplo 1 SA de CV', 'Proveedor Ejemplo 2 SA de CV'],
            'rfc': ['PJE123456789', 'PJE987654321'],
            'regimen_fiscal': ['601', '601'],
            'codigo_postal': ['01000', '02000'],
            'calle': ['Calle Falsa', 'Avenida Real'],
            'numero_exterior': ['123', '456'],
            'colonia': ['Centro', 'Juárez'],
            'municipio': ['Ciudad de México', 'Guadalajara'],
            'estado': ['Ciudad de México', 'Jalisco'],
            'pais': ['México', 'México']
        }
    elif tipo == 'clientes':
        data = {
            'nombre': ['Cliente Ejemplo 1', 'Cliente Ejemplo 2'],
            'apellido': ['González', 'López'],
            'telefono': ['555-1111', '555-2222'],
            'email': ['cliente1@email.com', 'cliente2@email.com'],
            'direccion': ['Dirección 1', 'Dirección 2'],
            'tipo_cliente': ['mostrador', 'registrado'],
            # Campos fiscales
            'razon_social': ['Cliente Ejemplo 1', 'Cliente Ejemplo 2'],
            'rfc': ['CLE123456789', 'CLE987654321'],
            'regimen_fiscal': ['601', '601'],
            'codigo_postal': ['01000', '02000'],
            'calle': ['Calle Cliente 1', 'Calle Cliente 2'],
            'numero_exterior': ['123', '456'],
            'colonia': ['Centro', 'Juárez'],
            'municipio': ['Ciudad de México', 'Guadalajara'],
            'estado': ['Ciudad de México', 'Jalisco'],
            'pais': ['México', 'México'],
            'uso_cfdi': ['G03', 'G01']
        }
    elif tipo == 'productos':
        data = {
            'codigo': ['PROD001', 'PROD002'],
            'codigo_barras': ['7501000000001', '7501000000002'],
            'nombre': ['Arroz 1kg', 'Aceite 1L'],
            'descripcion': ['Arroz integral de primera', 'Aceite de oliva extra virgen'],
            'precio_compra': [15.50, 25.00],
            'precio_venta': [20.00, 35.00],
            'stock': [100, 50],
            'stock_minimo': [10, 5],
            'categoria': ['Abarrotes', 'Aceites'],
            'proveedor_id': [1, 1],
            'activo': [True, True],
            # Campos fiscales
            'clave_producto_sat': ['01010101', '01010102'],
            'unidad_medida_sat': ['H87', 'H87'],
            'clave_unidad_sat': ['E48', 'E48'],
            'objeto_impuesto_sat': ['02', '02']
        }
    else:
        return None
    
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()