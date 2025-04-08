from flask import Flask, request, jsonify
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = Flask(__name__)

# Variable global de datosrecibidos  del ESP32. Se guarda en la RAM del servidor y se borra a los 15 minutos
# Cuidado!: Investigar para guardado persistente.
datos_recibidos = [] 
 
 # Configuración de InfluxDB
INFLUXDB_URL = "https://eu-central-1-1.aws.cloud2.influxdata.com" 
INFLUXDB_TOKEN = "KNHuhH5zKfNE6c6il4Jrqt-d-J9BaKPxmK4fpceYQiLbhGdyCNCk2p-z5mR6UYWZNOgoe-JAZo9f_GB-_3RNaw=="
INFLUXDB_ORG = "I_SOFTW"
INFLUXDB_BUCKET = "IOT_BUCKET"
 
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

@app.route('/api/datos/representar', methods=['GET'] )
def representar_datos():
    return generar_html_datos(datos_recibidos)
 


       
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


if __name__ == '__main__':
    #app.run(debug=True)
    app.run()



# Estructura de datos y trama para hacer POST:
# curl -X POST https://iot-app-test1.onrender.com/api/datos -H "Content-Type: application/json" -d "[{\"sensor\":\"temperatura\",\"valor\":23.5}, {\"sensor\":\"presion\",\"valor\":1000}]"
# NOTAS: - Se utiliza \" dentro de la cadena para emular "
#        - el header es necesario para hacer un POST de un dato JSON: -H "Content-Type: application/json"
#        - respuesta esperada: [FECHA] "POST /api/datos HTTP/1.1" 200 xxx "-" "curl/8.7.1"   
# "Point" es la unidad básica de datos en InfluxDB


# NOTA IMPORTANTE: Cada vez que se instale una nueva librería, es obligatorio hacer: pip freeze > requirements.txt