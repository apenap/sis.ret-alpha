from app import app, db

def migrate_final():
    with app.app_context():
        try:
            # Crear todas las tablas corporativas
            db.engine.execute('''
                CREATE TABLE IF NOT EXISTS requisiciones_compra (
                    id INTEGER PRIMARY KEY,
                    folio VARCHAR(20) UNIQUE,
                    fecha_creacion DATETIME,
                    solicitante VARCHAR(100),
                    departamento VARCHAR(100),
                    justificacion TEXT,
                    estado VARCHAR(20),
                    total_estimado FLOAT
                )
            ''')
            
            # ... (crear el resto de las tablas)
            
            # Tabla de configuración
            db.engine.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_sistema (
                    id INTEGER PRIMARY KEY,
                    clave VARCHAR(50) UNIQUE,
                    valor TEXT,
                    tipo VARCHAR(20),
                    descripcion TEXT,
                    categoria VARCHAR(20)
                )
            ''')
            
            print("✅ Migración completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error en migración: {str(e)}")

if __name__ == '__main__':
    migrate_final()