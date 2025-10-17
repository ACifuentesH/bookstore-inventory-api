# 📚 Bookstore Inventory API

API REST desarrollada en Django que permite gestionar el inventario de libros de una librería, calcular precios de venta con margen del 40% y convertir monedas usando tasas de cambio reales. El sistema está optimizado para Bolívares Venezolanos (VES) como moneda principal.

## 📋 Requisitos Previos

### Lenguaje y Versión
- **Python**: 3.8 o superior
- **Django**: 5.2
- **Sistema Operativo**: Windows, Linux o macOS

### Dependencias Principales
- Django 5.2
- Django REST Framework
- django-cors-headers
- python-decouple
- django-filter
- requests
- psycopg2-binary (para PostgreSQL)

### Entorno de Desarrollo
- **Editor de código**: VS Code
- **Cliente API**: Postman 
- **Base de datos**: SQLite (incluida) o PostgreSQL (opcional)

## 🚀 Instalación y Ejecución

### Paso 1: Clonar el Repositorio
```bash
git clone <repository-url>
cd bookstore-inventory-api
```

### Paso 2: Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### Paso 5: Ejecutar el Servidor
```bash
python manage.py runserver
```

### Paso 6: Verificar Instalación
Abrir el navegador en: `http://localhost:8000/api/books/`

**Respuesta esperada:**
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

### Alternativa: Ejecutar con Docker

```bash
# Ejecutar con Docker Compose
docker-compose up --build

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario (opcional)
docker-compose exec web python manage.py createsuperuser
```

## 🌐 API Endpoints

### CRUD Básico
- `POST /api/books/` - Crear libro
- `GET /api/books/` - Listar libros (con paginación)
- `GET /api/books/{id}/` - Obtener libro por ID
- `PUT /api/books/{id}/` - Actualizar libro
- `DELETE /api/books/{id}/` - Eliminar libro

### Endpoints Especializados
- `POST /api/books/{id}/calculate-price/` - **Calcular precio con integración externa**
- `GET /api/books/search/?category={category}` - Buscar por categoría
- `GET /api/books/low-stock/?threshold=10` - Libros con stock bajo
- `GET /api/books/{id}/price-history/` - Historial de precios
- `GET /api/exchange-rates/` - Información de tasas de cambio

## 💰 Ejemplos de Uso de los Endpoints

### 1. Crear un Libro
```bash
POST http://localhost:8000/api/books/
Content-Type: application/json

{
  "title": "Cien Años de Soledad",
  "author": "Gabriel García Márquez",
  "isbn": "978-84-376-0494-8",
  "cost_usd": 12.99,
  "stock_quantity": 15,
  "category": "Literatura Latinoamericana",
  "supplier_country": "CO",
  "local_currency": "VES"
}
```

**Respuesta:**
```json
{
  "id": 1,
  "title": "Cien Años de Soledad",
  "author": "Gabriel García Márquez",
  "isbn": "978-84-376-0494-8",
  "cost_usd": "12.99",
  "selling_price_local": "3705.22",
  "local_currency": "VES",
  "stock_quantity": 15,
  "category": "Literatura Latinoamericana",
  "supplier_country": "CO",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### 2. Calcular Precio de Venta (Endpoint Principal)
```bash
POST http://localhost:8000/api/books/1/calculate-price/
Content-Type: application/json

{
  "currency": "VES"
}
```

**Respuesta:**
```json
{
  "book_id": 1,
  "cost_usd": 12.99,
  "exchange_rate": 205.68,
  "cost_local": 2671.78,
  "margin_percentage": 40,
  "selling_price_local": 3740.50,
  "currency": "VES",
  "calculation_timestamp": "2025-01-15T10:30:00Z"
}
```

### 3. Listar Todos los Libros
```bash
GET http://localhost:8000/api/books/
```

### 4. Buscar Libros por Categoría
```bash
GET http://localhost:8000/api/books/search/?category=Literatura
```

### 5. Ver Libros con Stock Bajo
```bash
GET http://localhost:8000/api/books/low-stock/?threshold=10
```

### 6. Ver Tasas de Cambio Actuales
```bash
GET http://localhost:8000/api/exchange-rates/
```

**Respuesta:**
```json
{
  "base_currency": "USD",
  "date": "2025-01-15",
  "rates": {
    "VES": 205.68
  }
}
```

## 🧪 Pruebas con Postman

### Importar Colección
1. Abrir Postman
2. Importar `Bookstore_Inventory_API.postman_collection.json`
3. Importar `Bookstore_Inventory_Environment.postman_environment.json`
4. Configurar variable `base_url` = `http://localhost:8000`

### Orden de Pruebas Recomendado
1. `GET /api/books/` - Verificar que la API funciona
2. `POST /api/books/` - Crear un libro
3. `POST /api/books/{id}/calculate-price/` - Calcular precio
4. `GET /api/books/{id}/` - Obtener libro específico
5. `PUT /api/books/{id}/` - Actualizar libro
6. `GET /api/books/search/` - Buscar por categoría
7. `GET /api/books/low-stock/` - Ver stock bajo
8. `GET /api/exchange-rates/` - Ver tasas de cambio

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)
```bash
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
DB_NAME=bookstore_inventory
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
EXCHANGE_RATE_API_KEY=tu_api_key_opcional
```


## 📊 Estructura del Proyecto

```
bookstore-inventory-api/
├── inventory_project/          # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── books/                      # Aplicación principal
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── admin.py
├── requirements.txt
├── manage.py
├── db.sqlite3                  # Base de datos SQLite
└── README.md
```

## 🛡️ Validaciones de Negocio

- **ISBN**: Debe tener 10 o 13 dígitos
- **Costo USD**: Debe ser mayor a 0
- **Stock**: No puede ser negativo
- **ISBN Único**: No se permiten duplicados

## 🛡️ Manejo de Errores

### Códigos HTTP
- `200` - Éxito
- `400` - Error de validación
- `404` - Recurso no encontrado
- `500` - Error interno del servidor
- `503` - Servicio no disponible (API externa)

### Respaldo de Emergencia
- Si la API de tasas de cambio falla → Tasa 1:1
- Logs de advertencia para debugging
- Validaciones de modelo integradas

---

