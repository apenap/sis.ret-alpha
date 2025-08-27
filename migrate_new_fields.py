from app import app, db

def migrate_new_fields():
    with app.app_context():
        try:
            # Agregar campos faltantes a productos
            db.engine.execute('ALTER TABLE productos ADD COLUMN codigo VARCHAR(50)')
            db.engine.execute('ALTER TABLE productos ADD COLUMN clave_producto_sat VARCHAR(50)')
            db.engine.execute('ALTER TABLE productos ADD COLUMN unidad_medida_sat VARCHAR(20) DEFAULT "H87"')
            db.engine.execute('ALTER TABLE productos ADD COLUMN clave_unidad_sat VARCHAR(3) DEFAULT "E48"')
            db.engine.execute('ALTER TABLE productos ADD COLUMN objeto_impuesto_sat VARCHAR(2) DEFAULT "02"')
            
            print("✅ Campos de productos migrados exitosamente")
            
        except Exception as e:
            print(f"⚠️ Error en migración de productos: {str(e)}")
            
        try:
            # Agregar campos faltantes a proveedores
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN razon_social VARCHAR(200)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN rfc VARCHAR(13)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN regimen_fiscal VARCHAR(10)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN codigo_postal VARCHAR(5)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN calle VARCHAR(200)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN numero_exterior VARCHAR(20)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN numero_interior VARCHAR(20)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN colonia VARCHAR(100)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN municipio VARCHAR(100)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN estado VARCHAR(50)')
            db.engine.execute('ALTER TABLE proveedores ADD COLUMN pais VARCHAR(50) DEFAULT "México"')
            
            print("✅ Campos de proveedores migrados exitosamente")
            
        except Exception as e:
            print(f"⚠️ Error en migración de proveedores: {str(e)}")
            
        try:
            # Agregar campos faltantes a clientes
            db.engine.execute('ALTER TABLE clientes ADD COLUMN razon_social VARCHAR(200)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN rfc VARCHAR(13)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN regimen_fiscal VARCHAR(10)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN codigo_postal VARCHAR(5)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN calle VARCHAR(200)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN numero_exterior VARCHAR(20)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN numero_interior VARCHAR(20)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN colonia VARCHAR(100)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN municipio VARCHAR(100)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN estado VARCHAR(50)')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN pais VARCHAR(50) DEFAULT "México"')
            db.engine.execute('ALTER TABLE clientes ADD COLUMN uso_cfdi VARCHAR(3) DEFAULT "G03"')
            
            print("✅ Campos de clientes migrados exitosamente")
            
        except Exception as e:
            print(f"⚠️ Error en migración de clientes: {str(e)}")

if __name__ == '__main__':
    migrate_new_fields()