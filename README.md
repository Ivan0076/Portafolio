# Portfolio Personal — Diseñador Digital de Medios Interactivos

Aplicación web de portafolio profesional construida con **Flask + Jinja2 + Bootstrap 5 + CSS3**.

---

## Estructura del proyecto

```
portfolio/
├── app.py                  ← Aplicación Flask principal
├── requirements.txt
├── instance/
│   └── data.json           ← Base de datos JSON (auto-generada)
├── static/
│   ├── css/style.css       ← Estilos personalizados
│   ├── js/main.js          ← JavaScript (cursor, animaciones)
│   └── uploads/            ← Imágenes subidas
└── templates/
    ├── base.html           ← Layout base
    ├── index.html          ← Página de inicio
    ├── portfolio.html      ← Galería con filtros
    ├── project_detail.html ← Vista detalle de proyecto
    ├── login.html          ← Inicio de sesión (solo admin)
    ├── dashboard.html      ← Panel de administración
    ├── project_form.html   ← Crear/editar proyecto
    ├── profile_form.html   ← Editar perfil
    └── 404.html
```

---

## Instalación y uso

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar credenciales de admin

Edita `app.py` y cambia:
```python
OWNER_USERNAME = 'admin'                            # ← tu usuario
OWNER_PASSWORD_HASH = generate_password_hash('portfolio2024!')  # ← tu contraseña
```

Para cambiar la contraseña, ejecuta en Python:
```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('TU_NUEVA_CONTRASEÑA'))
```
Copia el resultado y pégalo como valor de `OWNER_PASSWORD_HASH`.

### 3. Ejecutar en desarrollo

```bash
python app.py
```

Visita: http://localhost:5000

### 4. Producción (con Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## Acceso al panel de administración

- URL: `/admin/login`
- El enlace de candado (🔒) aparece discretamente en el footer
- Solo el admin puede subir/editar/eliminar proyectos
- Los visitantes normales solo pueden ver el portafolio

---

## Categorías de proyectos

- **3D Models** — Modelos tridimensionales
- **2D Animations** — Animaciones en dos dimensiones
- **3D Animations** — Animaciones en tres dimensiones
- **Illustrations** — Dibujos e ilustraciones digitales

---
