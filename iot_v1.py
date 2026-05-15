from flask import Flask, request, jsonify
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from threading import Lock
import os
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)

# Variable global de datosrecibidos  del ESP32. Se guarda en la RAM del servidor y se borra a los 15 minutos
# Cuidado!: Investigar para guardado persistente.
datos_recibidos = [] 

# Variable global para los TCs  pendientes. Se guarda en la RAM del servidor y se borra a los 15 minutos

comandos_pendientes = [] 

# Variable global para conteo de TCs pendientes

tc_count = 0

pending_cmd = None

lock = Lock()


 # Configuración de InfluxDB
INFLUXDB_URL    = os.environ["INFLUXDB_URL"]
INFLUXDB_TOKEN  = os.environ["INFLUXDB_TOKEN"]
INFLUXDB_ORG    = os.environ["INFLUXDB_ORG"]
INFLUXDB_BUCKET = os.environ["INFLUXDB_BUCKET"]
 
client_IDB = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client_IDB.write_api(write_options=SYNCHRONOUS)


####### Ruta principal de prueba (GET)
@app.route('/')
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return f'API Flask funcionando correctamente ✅\nTu IP es: {ip}'


####### Ruta para recibir datos del ESP32 (POST)
@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    global datos_recibidos
    data = request.get_json()

    if not data:
        return ' No se recibieron datos o el formato es incorrecto\n', 400

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

        #Guardado de datos en variable global
        datos_recibidos.append({
            'sensor': sensor,
            'valor': valor,
            'timestamp': timestamp
        })
        # Escribir en la variable para envíar a InfluxDB 
        point = (
        Point("lecturas")                    
        .tag("sensor", sensor)               
        .field("valor", float(valor))        
        .time(datetime.now(timezone.utc))             
        )
 
        # Escribir en el BUCKET InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)    

        # Imprimir en logs (Render)
        print(f"[{timestamp}] Sensor: {sensor} - Valor: {valor}")

        # Agregar al texto de respuesta
        salida.append(f"[{timestamp}] Sensor: {sensor} - Valor: {valor}\n")

    return ''.join(salida), 200


####### Ruta para representar datos recibidos desde un navegador (GET)
@app.route('/api/datos/representar', methods=['GET'] )
def representar_datos():
    return generar_html_datos(datos_recibidos)


####### Ruta para envíar nuevos comandos al receptor desde cualquier terminal (POST)
@app.route('/api/comando', methods=['POST'])
def set_cmd():
    global pending_cmd
    if not request.is_json:
        return '❌ Usa "Content-Type: application/json"\n', 415

    data = request.get_json(silent=True)
    if data is None:
        return "❌ JSON malformado\n", 400

    try:
        tc = validate_tc(data)
    except ValueError as e:
        return f"❌ {e}\n", 400

    with lock:
        pending_cmd = tc  # sobrescribe el anterior

    return jsonify({"status": "ok", **tc}), 200


####### Ruta para recibir desde el ESP32 los comandos subidos al servidor (GET)
@app.route('/api/comando', methods=['GET'])
def get_cmd():
    global pending_cmd
    with lock:
        if pending_cmd is None:
            # No hay TC pendiente → 204 No Content (lo que maneja tu ESP32)
            return ("", 204)
        tc = pending_cmd
        pending_cmd = None  # lo entregamos y borramos (buzón vacío)
    return jsonify(tc), 200


@app.route('/api/comando/health', methods=['GET'])
def health():
    with lock:
        has = pending_cmd is not None
    return jsonify({"ok": True, "pending": has}), 200








def generar_html_datos(arg):        #Función global para imprimir datos por pantalla. Devuelve un html
    print("Ejecutando función global de muestra de datos")

    html = """
    <html>
    <head>
        <title>Datos Recibidos</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 8px 0; }
        </style>
    </head>
    <body>
        <h2>Datos recibidos</h2>
    """

    if not arg:
        html += "<p>No se han recibido datos aún.</p>"
    else:
        html += "<ul>"                   #<ul> = unordered list
        for item in arg:
            sensor = item.get('sensor', 'N/A')
            valor = item.get('valor', 'N/A')
            html += f"<li><strong>{sensor}</strong>: {valor}</li>"
        html += "</ul>" 

    html += """     
        <script>
            setTimeout(() => {
                window.location.reload();
            }, 5000);  
        </script>
    </body>
    </html>
    """
    # Script que recarga cada 5 segundos el navegador
    return html

def validate_tc(obj):
    if not isinstance(obj, dict):
        raise ValueError("Debe ser un objeto JSON")
    for k in ("Type_of_message", "TC_Action_ID", "TC_Payload"):
        if k not in obj:
            raise ValueError(f'Falta la clave "{k}"')

    # Casts + rangos
    t = int(obj["Type_of_message"])
    a = int(obj["TC_Action_ID"])
    p = int(obj["TC_Payload"])

    if not (0 <= t <= 255):
        raise ValueError('"Type_of_message" debe estar en 0..255')
    if not (0 <= a <= 255):
        raise ValueError('"TC_Action_ID" debe estar en 0..255')
    if not (0 <= p <= 1000):
        raise ValueError("TC_Payload fuera de rango int32")

    return {"Type_of_message": t, "TC_Action_ID": a, "TC_Payload": p}


if __name__ == '__main__':
    #app.run(debug=True)
    app.run()


# NOTA IMPORTANTE: Cada vez que se instale una nueva librería, es obligatorio hacer: pip freeze > requirements.txt
# Estructura de datos y trama para POST:



# curl -X POST https://iot-app-test1.onrender.com/api/datos -H "Content-Type: application/json" -d "[{\"sensor\":\"temperatura\",\"valor\":23.5}, {\"sensor\":\"presion\",\"valor\":1000}]"
# NOTAS: - Se utiliza \" dentro de la cadena para emular "
#        - el header es necesario para hacer un POST de un dato JSON: -H "Content-Type: application/json"
#        - respuesta esperada: [FECHA] "POST /api/datos HTTP/1.1" 200 xxx "-" "curl/8.7.1"   
# "Point" es la unidad básica de datos en InfluxDB

# curl -X POST https://iot-app-test1.onrender.com/api/comando \
# -H "Content-Type: application/json" \
# -d "{\"comando\": \"SET_MODO\", \"valor\": 3}"