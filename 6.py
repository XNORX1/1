from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import time
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 17
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Variables globales
count = 0
button_pressed = False

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect('registro.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Función para registrar en la base de datos
def registrar_ingreso():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('registro.db')
    c = conn.cursor()
    c.execute("INSERT INTO personas (timestamp) VALUES (?)", (now,))
    conn.commit()
    conn.close()

# Callback del botón
def button_callback(channel):
    global count, button_pressed
    count += 1
    button_pressed = True
    registrar_ingreso()

GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_callback, bouncetime=300)

@app.route('/')
def index():
    return render_template('index.html', count=count, button_pressed=button_pressed)

@app.route('/get_count')
def get_count():
    return jsonify(count=count, button_pressed=button_pressed)

@app.route('/reset_button')
def reset_button():
    global button_pressed
    button_pressed = False
    return jsonify(button_pressed=button_pressed)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        GPIO.cleanup()
