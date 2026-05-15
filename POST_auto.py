import requests
import random
import time
import json

URL = "https://iot-app-test1.onrender.com/api/datos"
HEADERS = {"Content-Type": "application/json"}

def generar_datos():
    temperatura = round(random.uniform(10.0, 30.0), 2)  # entre 10.00 y 30.00
    presion = random.randint(4000, 8000)  # entre 4000 y 8000
    return [
        {"sensor": "temperatura", "valor": temperatura},
        {"sensor": "presion", "valor": presion}
    ]

while True:
    datos = generar_datos()
    try:
        respuesta = requests.post(URL, headers=HEADERS, data=json.dumps(datos))
        print("📤 Enviando:", datos)
        print("✅ Respuesta:", respuesta.status_code, respuesta.text)
    except Exception as e:
        print("❌ Error al enviar:", e)
    
    time.sleep(5)  # Espera 5 segundos


# POST MANUAL:   -X POST https://iot-app-test1.onrender.com/api/datos -H "Content-Type: application/json" -d "[{\"sensor\":\"temperatura\",\"valor\":15}, {\"sensor\":\"presion\",\"valor\":5000}]"