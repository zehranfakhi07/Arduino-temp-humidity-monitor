### HealthShare Platform

- Backend: FastAPI with JWT auth, field encryption, and role/scoped access
- Mobile: Expo React Native client for patients/providers

Quick start:

```bash
# Backend
cd backend
pip3 install --break-system-packages -r requirements.txt
PYTHONPATH=$(pwd) python3 -c "from app.main import init_db; init_db()"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

```bash
# Mobile
cd mobile
npm install
# Set EXPO_PUBLIC_API_BASE in mobile/.env to your backend URL
npm run start
```

Security features:
- AES-GCM field encryption for test results, records, prescriptions
- Argon2 password hashing
- JWT access tokens
- Patient-controlled provider access grants with scopes and expiry
- Audit logging for key actions

---

# Arduino-temp-humidity-monitor
This Arduino project shows the current temperature and humidity on an LCD screen using a DHT11 sensor. It's easy to build and perfect for beginners learning about sensors and displays.
Arduino Temperature and Humidity Monitor
This is a basic project I made using an Arduino Uno, DHT11 sensor, and a 16x2 LCD (without
I2C). It reads the temperature and humidity and shows it on the LCD screen. It’s a simple offline
project no Wi-Fi or internet needed.
Components I Used
- Arduino Uno
- DHT11 Temperature & Humidity Sensor
- 16x2 LCD Display (non-I2C)
- 10k Potentiometer
- Breadboard and jumper wires
- USB Cable
  
  Connections
DHT11:
- VCC → 5V
- GND → GND
- DATA → Pin 7
LCD (non-I2C):
- RS → Pin 12
- EN → Pin 11
- D4 → Pin 5
- D5 → Pin 4
- D6 → Pin 3
- D7 → Pin 2
- VSS → GND
- VDD → 5V
- VO → Middle pin of potentiometer
- RW → GND
Code
I’ve uploaded the Arduino code in this repo as “TempMonitor.ino”. It reads the sensor values and
displays them on the LCD.
# Output
The LCD shows:
