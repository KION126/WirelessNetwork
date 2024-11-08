```
# soil_moisture_control.py
import time
import RPi.GPIO as GPIO
import serial
from influxdb import InfluxDBClient as influxdb
from water_tank_monitor import log_water_tank_level, get_tank_level_percent

# GPIO 및 시리얼 설정
motor_pin = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

serial_port = '/dev/ttyACM0'
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)

# 토양 습도 임계값
MOISTURE_THRESHOLD = 200

# 토양 습도 값 읽기
def read_soil_moisture_sensor():
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            parts = line.split(',')
            soil_moisture = float(parts[2])  # 토양 습도 값
            return soil_moisture
    except (ValueError, IndexError):
        print("Invalid sensor reading")
        return None

# 토양 습도 저장 함수
def log_soil_moisture(soil_moisture):
    data = [
        {
            "measurement": "soil_moisture",
            "fields": {
                "soil_moisture": soil_moisture
            }
        }
    ]
    try:
        client = influxdb('localhost', 'root', 'root', 'SmartPlantPot')
        client.write_points(data)
    except Exception as e:
        print("Error writing soil moisture to InfluxDB:", e)
    finally:
        client.close()

# 물 공급 함수
def activate_water_pump():
    GPIO.output(motor_pin, GPIO.LOW)  # 모터 ON
    time.sleep(2)  # 물 공급 시간
    GPIO.output(motor_pin, GPIO.HIGH)  # 모터 OFF
    log_water_tank_level(get_tank_level_percent())  # 물탱크 수위 기록

# 10분마다 토양 습도 확인 및 저장, 모터 제어
def monitor_and_control_soil_moisture():
    while True:
        # 토양 습도 값 읽기
        soil_moisture = read_soil_moisture_sensor()

        if soil_moisture is not None:
            # 토양 습도 기록
            log_soil_moisture(soil_moisture)

            # 임계값 비교 후 물 공급
            if soil_moisture < MOISTURE_THRESHOLD:
                print("토양 습도가 임계값보다 낮음, 모터 작동")
                activate_water_pump()

        time.sleep(600)  # 10분 대기

# 메인 실행
if __name__ == "__main__":
    try:
        monitor_and_control_soil_moisture()
    except KeyboardInterrupt:
        print("Soil moisture monitoring interrupted.")
    finally:
        GPIO.cleanup()
        ser.close()

```
