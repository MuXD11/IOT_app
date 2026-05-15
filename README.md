# LoRa-to-Cloud IoT Backend for Stratospheric Balloon Telemetry

Flask API and time-series storage layer for a real-time telemetry system I designed to track stratospheric balloons in flight. Receives data from a ground-station ESP32 over HTTP, writes it to InfluxDB, and exposes it to a Grafana dashboard for live monitoring.

This repository contains the **backend (cloud) component** of my bachelor's thesis project. The end-to-end system covers:

- An **onboard ESP32 + LoRa SX1276 + GPS NEO-6M** payload that samples sensors and broadcasts telemetry at 868 MHz.
- A **ground ESP32 receiver** that decodes LoRa packets and forwards them over Wi-Fi via HTTP POST.
- This **Flask API** deployed on Render, which validates and persists the data.
- An **InfluxDB Cloud** time-series database and a **Grafana** dashboard for visualization.

The full thesis (Spanish) covers the link budget, LoRa parameter selection (SF, BW, CR), the airborne GPS dynamic mode configuration, and the validation test campaign (long-duration run, reconnection recovery, integration test).

## Architecture

```
[Balloon ESP32] --LoRa 868 MHz--> [Ground ESP32] --HTTP POST--> [Flask API on Render] --> [InfluxDB] <-- [Grafana]
```

## API endpoints

| Method | Route                    | Purpose                                                                                                     |
| ------ | ------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `GET`  | `/`                      | Health check; returns the client's IP.                                                                      |
| `POST` | `/api/datos`             | Ingests a telemetry frame as a JSON array of `{sensor, valor}` objects, writes each as a point to InfluxDB. |
| `GET`  | `/api/datos/representar` | Debug view of recently ingested data (development only).                                                    |

### Example POST payload

```json
[
  { "sensor": "latitude", "valor": 40.123456 },
  { "sensor": "longitude", "valor": -3.654321 },
  { "sensor": "altitude", "valor": 1040.5 },
  { "sensor": "temperature", "valor": 23.5 }
]
```

## Local setup

```bash
git clone https://github.com/MuXD11/TFG-IOT-API.git
cd TFG-IOT-API
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then fill in your InfluxDB credentials
python iot_v1.py
```

The API will be available at `http://localhost:10000`.

## Deploying to Render

1. **Fork or push this repo to your own GitHub.**
2. In [render.com](https://render.com), select **New → Web Service** and connect your GitHub account.
3. Pick the repository and the `main` branch.
4. Configure the service:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
   - **Plan:** Free
5. Under **Environment**, add the variables listed in `.env.example` with your real InfluxDB Cloud values.
6. Click **Create Web Service**. Render assigns a public URL like `https://your-service.onrender.com`.
7. Point the receiver ESP32's HTTP client at `https://your-service.onrender.com/api/datos`.

## Environment variables

| Variable          | Description                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------- |
| `INFLUXDB_URL`    | URL of your InfluxDB Cloud region (e.g. `https://eu-central-1-1.aws.cloud2.influxdata.com`) |
| `INFLUXDB_TOKEN`  | API token with write access to the target bucket                                            |
| `INFLUXDB_ORG`    | Your InfluxDB organization name                                                             |
| `INFLUXDB_BUCKET` | The bucket where telemetry is written                                                       |

These are loaded at runtime via `os.environ`.

## Related repositories

- _(coming soon)_ `TFG-IOT-Flight` — firmware for the onboard ESP32 (LoRa TX, GPS, BME280, DS18B20).
- _(coming soon)_ `TFG-IOT-Ground` — firmware for the ground ESP32 (LoRa RX, Wi-Fi, HTTP client).

## Thesis

Full project report (Spanish): _Diseño e implementación de una infraestructura IoT con LoRa para la recopilación de datos en tiempo real en globos estratosféricos_ — Universidad de Alcalá, 2024/2025.

## License

MIT — see [LICENSE](LICENSE).
