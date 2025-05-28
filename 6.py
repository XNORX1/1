from flask import Flask, render_template, jsonify, send_file
import RPi.GPIO as GPIO
import time
import sqlite3
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Configuración del botón
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 17
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Variables
count = 0
button_pressed = False

# Inicializar la base de datos
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

# Registrar ingreso
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

@app.route('/descargar_csv')
def descargar_csv():
    conn = sqlite3.connect('registro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personas")
    rows = cursor.fetchall()

    archivo_csv = 'personas.csv'
    with open(archivo_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'timestamp'])
        writer.writerows(rows)

    conn.close()
    return send_file(archivo_csv, as_attachment=True)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        GPIO.cleanup()



