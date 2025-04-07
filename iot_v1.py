from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Ruta principal de prueba (GET)
@app.route('/')
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return f'API Flask funcionando correctamente ✅\nTu IP es: {ip}'

# Ruta para recibir datos del ESP32 (POST)
@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    data = request.get_json()

    if not data or 'sensor' not in data or 'valor' not in data:
        return jsonify({'error': 'Faltan campos requeridos (sensor, valor)'}), 400

    sensor = data['sensor']
    valor = data['valor']
    timestamp = datetime.utcnow().isoformat()

    # Mostrar en consola para debug
    print(f"[{timestamp}] Sensor: {sensor} - Valor: {valor}")

    # Respuesta a quien haya enviado el dato
    return jsonify({
        'mensaje': 'Datos recibidos correctamente',
        'sensor': sensor,
        'valor': valor,
        'timestamp': timestamp
    }), 200

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()
