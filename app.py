import telebot
import re
from datetime import datetime

# === CONFIGURACIÓN ===
TOKEN = "8555813721:AAGUPCse67ekXW8QsT_xTP3kHJWOQ3zY1_s"
MI_CHAT_ID = "7501019675"

bot = telebot.TeleBot(TOKEN)

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

# === COMANDO START ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    texto = (
        "🚀 *BIENVENIDO A ASOCITECH MONTES*\n\n"
        "Te haré algunas preguntas para tu registro científico.\n\n"
        "📌 *Responde una por una:*\n"
        "1️⃣ Nombre completo del estudiante:\n"
        "2️⃣ Cédula:\n"
        "3️⃣ Edad:\n"
        "4️⃣ Sexo (M/F):\n"
        "5️⃣ Liceo o escuela:\n"
        "6️⃣ Año (Ej: 4to, 5to):\n"
        "7️⃣ Sección:\n"
        "8️⃣ ¿Qué te gusta de la ciencia?:\n"
        "9️⃣ Nivel (Principiante/Intermedio/Avanzado):\n"
        "🔟 ¿Has participado en ferias? (Si/No):\n"
        "1️⃣1️⃣ Grupo (opcional, escribe 'Ninguno' si no tienes):\n"
        "1️⃣2️⃣ Nombre del representante:\n"
        "1️⃣3️⃣ Teléfono del representante (Ej: 04121234567):"
    )
    bot.send_message(message.chat.id, texto, parse_mode="Markdown")
    bot.register_next_step_handler(message, procesar_registro)

# === PROCESAR RESPUESTAS ===
def procesar_registro(message):
    respuestas = message.text.split('\n')
    
    # Verificar que haya 13 respuestas
    if len(respuestas) < 13:
        bot.send_message(message.chat.id, "❌ Debes responder las 13 preguntas separadas por saltos de línea. Usa /start para intentar de nuevo.")
        return
    
    # Validar datos importantes
    errores = []
    
    if not validar_edad(respuestas[2].strip()):
        errores.append("Edad inválida (debe ser 4-20 años)")
    
    if not validar_cedula(respuestas[1].strip()):
        errores.append("Cédula inválida (debe tener 6-9 dígitos)")
    
    if not validar_telefono(respuestas[12].strip()):
        errores.append("Teléfono inválido (formato: 04121234567)")
    
    if errores:
        bot.send_message(message.chat.id, "❌ Errores:\n" + "\n".join(errores) + "\n\nUsa /start para intentar de nuevo.")
        return
    
    # Si todo está bien, enviar a MI_CHAT_ID
    reporte = (
        f"🚀 *NUEVO REGISTRO CIENTÍFICO*\n"
        f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"👤 *Usuario:* {message.from_user.first_name} (@{message.from_user.username})\n"
        f"🆔 ID: {message.from_user.id}\n\n"
        f"📋 *DATOS DEL ESTUDIANTE:*\n"
        f"1️⃣ Nombre: {respuestas[0].strip()}\n"
        f"2️⃣ Cédula: {respuestas[1].strip()}\n"
        f"3️⃣ Edad: {respuestas[2].strip()}\n"
        f"4️⃣ Sexo: {respuestas[3].strip()}\n"
        f"5️⃣ Liceo: {respuestas[4].strip()}\n"
        f"6️⃣ Año: {respuestas[5].strip()}\n"
        f"7️⃣ Sección: {respuestas[6].strip()}\n"
        f"8️⃣ Interés: {respuestas[7].strip()}\n"
        f"9️⃣ Nivel: {respuestas[8].strip()}\n"
        f"🔟 Ferias: {respuestas[9].strip()}\n"
        f"1️⃣1️⃣ Grupo: {respuestas[10].strip()}\n"
        f"1️⃣2️⃣ Representante: {respuestas[11].strip()}\n"
        f"1️⃣3️⃣ Teléfono: {respuestas[12].strip()}"
    )
    
    # Enviar a ti (el admin)
    bot.send_message(MI_CHAT_ID, reporte, parse_mode="Markdown")
    
    # Confirmar al usuario
    bot.send_message(
        message.chat.id, 
        "✅ *¡REGISTRO EXITOSO!*\n\nGracias por formar parte de ASOCITECH Montes. Te contactaremos pronto por WhatsApp para los detalles de los talleres científicos.\n\n🔬 *La ciencia te necesita*",
        parse_mode="Markdown"
    )

# === RESPUESTA A CUALQUIER OTRO MENSAJE ===
@bot.message_handler(func=lambda m: True)
def mensaje_generico(message):
    bot.send_message(message.chat.id, "🤖 Usa /start para registrarte en ASOCITECH")

# === INICIAR BOT ===
print("✅ BOT DE ASOCITECH ACTIVADO - Esperando registros...")
bot.infinity_polling()
