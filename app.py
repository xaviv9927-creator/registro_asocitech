import telebot
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import os
import re
from datetime import datetime

# === CONFIGURACIÓN ===
TOKEN = "8555813721:AAGUPCse67ekXW8QsT_xTP3kHJWOQ3zY1_s"
MI_CHAT_ID = "7501019675"
CLAVE_ADMIN = "151515vargas"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.secret_key = "asocitech_vargas_2026"
app.config['SESSION_COOKIE_NAME'] = 'admin_session'

# === BASE DE DATOS TEMPORAL ===
estudiantes = []

# === FUNCIONES DE VALIDACIÓN ===
def validar_cedula(cedula):
    cedula = cedula.strip().upper()
    return bool(re.match(r'^[VEJPG]?[0-9]{6,9}$', cedula))

def validar_telefono(telefono):
    telefono = re.sub(r'[\s-]', '', telefono)
    return bool(re.match(r'^(0|58)(412|414|416|424|426|212)[0-9]{7}$', telefono))

def validar_edad(edad):
    try:
        return 4 <= int(edad) <= 20
    except:
        return False

# === RUTA PRINCIPAL - FORMULARIO ===
@app.route('/')
def index():
    return render_template('index.html')

# === PROCESAR REGISTRO ===
@app.route('/registrar', methods=['POST'])
def registrar():
    errores = []
    
    # Validar todos los campos
    nombre = request.form.get('nombre', '').strip().upper()
    if len(nombre) < 5:
        errores.append("Nombre inválido (mínimo 5 caracteres)")
    
    cedula = request.form.get('cedula', '').strip()
    if not validar_cedula(cedula):
        errores.append("Cédula inválida (debe tener 6-9 dígitos)")
    
    telefono_est = request.form.get('telefono_est', '').strip()
    if not validar_telefono(telefono_est):
        errores.append("Teléfono del estudiante inválido (ej: 04121234567)")
    
    edad = request.form.get('edad', '')
    if not validar_edad(edad):
        errores.append("Edad inválida (debe ser entre 4 y 20 años)")
    
    telefono_rep = request.form.get('rep_tel', '').strip()
    if not validar_telefono(telefono_rep):
        errores.append("Teléfono del representante inválido (ej: 04121234567)")
    
    if errores:
        return render_template('error.html', errores=errores), 400
    
    # Guardar datos
    datos = {
        'id': len(estudiantes) + 1,
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'nombre': nombre,
        'cedula': cedula,
        'telefono_est': telefono_est,
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
        'rep_tel': telefono_rep
    }
    estudiantes.append(datos)
    
    # Reporte a Telegram
    reporte = (
        f"🚀 *NUEVA INSCRIPCIÓN #{len(estudiantes)}*\n"
        f"📅 {datos['fecha']}\n"
        f"👤 *Estudiante:* {datos['nombre']}\n"
        f"🆔 Cédula: {datos['cedula']}\n"
        f"📱 Tel Est: {datos['telefono_est']}\n"
        f"🎂 Edad: {datos['edad']} años\n"
        f"🏫 *Liceo:* {datos['liceo']}\n"
        f"📚 {datos['ano']} - Sección {datos['seccion']}\n"
        f"🔬 Nivel: {datos['nivel']}\n"
        f"📞 *Representante:* {datos['rep_nombre']}\n"
        f"📱 Tel Rep: {datos['rep_tel']}"
    )
    try:
        bot.send_message(MI_CHAT_ID, reporte, parse_mode="Markdown")
    except:
        pass
    
    return render_template('exito.html', datos=datos)

# === LOGIN ADMIN ===
@app.route('/vargas-admin')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    if request.form.get('clave') == CLAVE_ADMIN:
        session['admin'] = True
        return redirect(url_for('panel'))
    return render_template('login.html', error="Clave incorrecta")

# === PANEL PRINCIPAL ADMIN ===
@app.route('/vargas-admin/panel')
def panel():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    # Obtener parámetro de orden
    orden = request.args.get('orden', 'liceo')
    
    # Agrupar por liceo
    liceos = {}
    for e in estudiantes:
        if e['liceo'] not in liceos:
            liceos[e['liceo']] = []
        liceos[e['liceo']].append(e)
    
    # Ordenar cada liceo por año y sección
    for liceo in liceos:
        liceos[liceo].sort(key=lambda x: (x['ano'], x['seccion'], x['edad']))
    
    # Estadísticas
    stats = {
        'total': len(estudiantes),
        'liceos': len(liceos),
        'por_nivel': {
            'Principiante': sum(1 for e in estudiantes if e['nivel'] == 'Principiante'),
            'Intermedio': sum(1 for e in estudiantes if e['nivel'] == 'Intermedio'),
            'Avanzado': sum(1 for e in estudiantes if e['nivel'] == 'Avanzado')
        }
    }
    
    return render_template('admin.html', liceos=liceos, stats=stats, orden_actual=orden)

# === VER DETALLE DE ESTUDIANTE ===
@app.route('/vargas-admin/estudiante/<int:id>')
def ver_estudiante(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    estudiante = next((e for e in estudiantes if e['id'] == id), None)
    if not estudiante:
        return "Estudiante no encontrado", 404
    
    return render_template('detalle.html', e=estudiante)

# === CERRAR SESIÓN ===
@app.route('/vargas-admin/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# === INICIAR SERVIDOR ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
