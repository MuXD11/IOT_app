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

    if not data:
        return '❌ No se recibieron datos o el formato es incorrecto\n', 400

    # Aceptar objeto único o lista
    if not isinstance(data, list):
        data = [data]

    salida = ['Datos recibidos correctamente ✅\n']
    timestamp = datetime.utcnow().isoformat()

    for entrada in data:
        if 'sensor' not in entrada or 'valor' not in entrada:
            salida.append("❌ Entrada inválida (falta sensor o valor)\n")
            continue

        sensor = entrada['sensor']
        valor = entrada['valor']

        # Imprimir en logs (Render)
        print(f"[{timestamp}] Sensor: {sensor} - Valor: {valor}")

        # Agregar al texto de respuesta
        salida.append(f"[{timestamp}] Sensor: {sensor} - Valor: {valor}\n")

    return ''.join(salida), 200
# Estructura de datos y trama para hacer POST:
# curl -X POST https://iot-app-test1.onrender.com/api/datos -H "Content-Type: application/json" -d "[{\"sensor\":\"temperatura\",\"valor\":23.5}, {\"sensor\":\"presion\",\"valor\":1000}]"
# NOTAS: - Se utiliza \" dentro de la cadena para emular "
#        - el header es necesario para hacer un POST de un dato JSON: -H "Content-Type: application/json"
#        - respuesta esperada: [FECHA] "POST /api/datos HTTP/1.1" 200 xxx "-" "curl/8.7.1"   

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()
