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
    if not isinstance(data, list):
        data = [data]  # por si solo viene un objeto
    registros = []   # lista vacía
    for entrada in data:# Bucle para la lista de entrada
        if 'sensor' not in entrada or 'valor' not in entrada:
            continue
        sensor = entrada['sensor']
        valor = entrada['valor']
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] Sensor: {sensor} - Valor: {valor}")
        registros.append({
            'sensor': sensor,
            'valor': valor,
            'timestamp': timestamp
        })
    return jsonify({
        'mensaje': 'Datos recibidos correctamente',
        'registros': registros
    }), 200
# Estructura de datos y trama para hacer POST:
# curl -X POST https://iot-app-test1.onrender.com/api/datos -H "Content-Type: application/json" -d "[{\"sensor\":\"temperatura\",\"valor\":23.5}, {\"sensor\":\"presion\",\"valor\":1000}]"
# NOTAS: - Se utiliza \" dentro de la cadena para emular "
#        - el header es necesario para hacer un POST de un dato JSON: -H "Content-Type: application/json"
#        - respuesta esperada: [FECHA] "POST /api/datos HTTP/1.1" 200 xxx "-" "curl/8.7.1"   

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()
