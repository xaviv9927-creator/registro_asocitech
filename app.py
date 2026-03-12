import telebot
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import os
import re
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = "8555813721:AAGUPCse67ekXW8QsT_xTP3kHJWOQ3zY1_s"
MI_CHAT_ID = "7501019675"
CLAVE_ADMIN = "151515vargas"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.secret_key = "asocitech_vargas_2026"
app.config['SESSION_COOKIE_NAME'] = 'admin_session'

# Base de datos temporal (en producción usarías una BD real)
estudiantes = []

# --- FUNCIONES DE VALIDACIÓN ---
def validar_cedula(cedula):
    """Venezuelan ID: 7-8 digits, optional letters for foreigners"""
    cedula = cedula.strip().upper()
    return bool(re.match(r'^[VEJPG]?[0-9]{6,9}$', cedula))

def validar_telefono(telefono):
    """Venezuelan phone: 0412-1234567 or 584121234567"""
    telefono = telefono.strip()
    # Quitar espacios y guiones
    telefono = re.sub(r'[\s-]', '', telefono)
    # Formato venezolano: 04121234567 o 584121234567
    if re.match(r'^0(412|414|416|424|426|212|412|414|416)[0-9]{7}$', telefono):
        return True
    if re.match(r'^58(412|414|416|424|426|212)[0-9]{7}$', telefono):
        return True
    return False

def validar_edad(edad):
    try:
        edad_int = int(edad)
        return 4 <= edad_int <= 20  # Rango típico para estudiantes
    except:
        return False

# --- REGISTRO PÚBLICO ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    errores = []
    
    # Validar todos los campos
    nombre = request.form.get('nombre', '').strip().upper()
    if len(nombre) < 5 or len(nombre) > 100:
        errores.append("Nombre inválido (debe tener entre 5 y 100 caracteres)")
    
    cedula = request.form.get('cedula', '').strip()
    if not validar_cedula(cedula):
        errores.append("Cédula inválida (debe tener 6-9 dígitos)")
    
    edad = request.form.get('edad', '')
    if not validar_edad(edad):
        errores.append("Edad inválida (debe ser entre 4 y 20 años)")
    
    telefono = request.form.get('rep_tel', '').strip()
    if not validar_telefono(telefono):
        errores.append("Teléfono inválido (formato: 04121234567 o 584121234567)")
    
    # Campos obligatorios
    campos_requeridos = ['sexo', 'liceo', 'ano', 'seccion', 'interes', 'nivel', 'feria', 'rep_nombre']
    for campo in campos_requeridos:
        if not request.form.get(campo, '').strip():
            errores.append(f"El campo {campo} es obligatorio")
    
    if errores:
        return render_template('error.html', errores=errores), 400
    
    # Si todo está bien, guardar
    datos = {
        'id': len(estudiantes) + 1,
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'nombre': nombre,
        'cedula': cedula,
        'edad': int(edad),
        'sexo': request.form['sexo'],
        'liceo': request.form['liceo'].strip().upper(),
        'ano': request.form['ano'].strip(),
        'seccion': request.form['seccion'].strip().upper(),
        'interes': request.form['interes'].strip(),
        'nivel': request.form['nivel'],
        'feria': request.form['feria'],
        'grupo': request.form.get('grupo', '').strip().upper() or 'SIN GRUPO',
        'rep_nombre': request.form['rep_nombre'].strip().upper(),
        'rep_tel': telefono
    }
    estudiantes.append(datos)
    
    # Reporte a Telegram con más detalles
    reporte = (
        f"🚀 *NUEVA INSCRIPCIÓN #{len(estudiantes)}*\n"
        f"📅 {datos['fecha']}\n"
        f"👤 *Estudiante:* {datos['nombre']}\n"
        f"🆔 Cédula: {datos['cedula']}\n"
        f"🎂 Edad: {datos['edad']} años\n"
        f"🏫 *Liceo:* {datos['liceo']}\n"
        f"📚 {datos['ano']} - Sección {datos['seccion']}\n"
        f"🔬 Nivel: {datos['nivel']}\n"
        f"📞 *Representante:* {datos['rep_nombre']}\n"
        f"📱 Tel: {datos['rep_tel']}"
    )
    try:
        bot.send_message(MI_CHAT_ID, reporte, parse_mode="Markdown")
    except Exception as e:
        print(f"Error Telegram: {e}")
    
    return render_template('exito.html', datos=datos)

# --- PANEL ADMIN MEJORADO ---
@app.route('/vargas-admin')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    if request.form.get('clave') == CLAVE_ADMIN:
        session['admin'] = True
        session['admin_login_time'] = datetime.now().isoformat()
        return redirect(url_for('panel'))
    return render_template('login.html', error="Clave incorrecta")

@app.route('/vargas-admin/panel')
def panel():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    # Obtener parámetros de ordenamiento
    orden = request.args.get('orden', 'liceo')
    direccion = request.args.get('dir', 'asc')
    
    # Función de ordenamiento dinámico
    def key_func(x):
        if orden == 'liceo':
            return (x['liceo'], x['ano'], x['seccion'], x['edad'])
        elif orden == 'fecha':
            return x.get('fecha', '')
        elif orden == 'edad':
            return x['edad']
        elif orden == 'nombre':
            return x['nombre']
        else:
            return x[orden]
    
    alumnos_ordenados = sorted(estudiantes, key=key_func, reverse=(direccion == 'desc'))
    
    # Estadísticas
    stats = {
        'total': len(estudiantes),
        'liceos': len(set(e['liceo'] for e in estudiantes)),
        'por_nivel': {
            'Principiante': sum(1 for e in estudiantes if e['nivel'] == 'Principiante'),
            'Intermedio': sum(1 for e in estudiantes if e['nivel'] == 'Intermedio'),
            'Avanzado': sum(1 for e in estudiantes if e['nivel'] == 'Avanzado')
        }
    }
    
    return render_template('admin.html', alumnos=alumnos_ordenados, stats=stats, orden_actual=orden)

@app.route('/vargas-admin/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- API PARA DATOS (si quieres funcionalidad AJAX) ---
@app.route('/api/estudiantes')
def api_estudiantes():
    if not session.get('admin'):
        return jsonify({'error': 'No autorizado'}), 401
    return jsonify(estudiantes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
