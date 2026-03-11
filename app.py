import telebot
from flask import Flask, render_template, request, redirect, session, url_for
import os

# --- CONFIGURACIÓN ---
TOKEN = "8555813721:AAGUPCse67ekXW8QsT_xTP3kHJWOQ3zY1_s"
MI_CHAT_ID = "7501019675"
CLAVE_ADMIN = "151515vargas"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.secret_key = "asocitech_z_vargas"

# Base de datos temporal (Se reinicia al apagar el servidor)
estudiantes = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    datos = {
        'nombre': request.form['nombre'],
        'cedula': request.form['cedula'],
        'edad': int(request.form['edad']),
        'sexo': request.form['sexo'],
        'liceo': request.form['liceo'],
        'ano': request.form['ano'],
        'seccion': request.form['seccion'],
        'interes': request.form['interes'],
        'nivel': request.form['nivel'],
        'feria': request.form['feria'],
        'grupo': request.form['grupo'],
        'rep_nombre': request.form['rep_nombre'],
        'rep_tel': request.form['rep_tel']
    }
    estudiantes.append(datos)
    
    # Envío a Telegram
    reporte = f"🚀 *NUEVA INSCRIPCIÓN*\n👤 {datos['nombre']}\n🏫 {datos['liceo']}\n📑 {datos['ano']} - Secc: {datos['seccion']}\n🎂 Edad: {datos['edad']}\n📞 Rep: {datos['rep_tel']}"
    try:
        bot.send_message(MI_CHAT_ID, reporte, parse_mode="Markdown")
    except: pass
    
    return "✅ ¡Registro Exitoso! Bienvenido a ASOCITECH Montes."

@app.route('/vargas-admin')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    if request.form['clave'] == CLAVE_ADMIN:
        session['admin'] = True
        return redirect(url_for('panel'))
    return "❌ Clave Incorrecta"

@app.route('/vargas-admin/panel')
def panel():
    if not session.get('admin'): return redirect(url_for('login'))
    # ORGANIZACIÓN MAESTRA: Liceo -> Año -> Sección -> Edad
    lista = sorted(estudiantes, key=lambda x: (x['liceo'], x['ano'], x['seccion'], x['edad']))
    return render_template('admin.html', alumnos=lista)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
