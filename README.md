메인
```
import threading
import time
import serial
from queue import Queue
from soil_moisture_control import monitor_and_control_soil_moisture
from water_tank_monitor import monitor_and_log_water_tank_level

# 시리얼 포트 설정
serial_port = '/dev/ttyACM0'  # 아두이노 시리얼 포트
baud_rate = 9600  # 보드레이트

# 시리얼 포트를 하나의 스레드에서 읽고, 다른 스레드에 전달하는 큐 설정
queue = Queue()

def serial_reader():
    """시리얼 데이터를 읽어서 큐에 전달하는 스레드"""
    ser = serial.Serial(serial_port, baud_rate)
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            parts = line.split(',')
            soil_moisture = float(parts[0])  # 첫 번째 값: 토양 습도
            water_distance = float(parts[1])  # 두 번째 값: 물탱크 거리

            # 큐에 데이터 넣기
            queue.put((soil_moisture, water_distance))
        time.sleep(0.1)  # 시리얼 데이터를 읽는 주기

def start_threads():
    """멀티스레드 실행"""
    # 시리얼 읽기 스레드
    serial_thread = threading.Thread(target=serial_reader, daemon=True)

    # 토양 습도 제어 스레드
    soil_moisture_thread = threading.Thread(target=monitor_and_control_soil_moisture, args=(queue,), daemon=True)

    # 물탱크 수위 기록 스레드
    water_tank_thread = threading.Thread(target=monitor_and_log_water_tank_level, args=(queue,), daemon=True)

    # 스레드 시작
    serial_thread.start()
    soil_moisture_thread.start()
    water_tank_thread.start()

    # 메인 스레드는 계속 실행되어야 함
    serial_thread.join()
    soil_moisture_thread.join()
    water_tank_thread.join()

if __name__ == "__main__":
    try:
        start_threads()
    except KeyboardInterrupt:
        print("Program interrupted.")
```
토양
```
import time
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient as influxdb

# GPIO 설정
motor_pin = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

# 토양 습도 임계값
MOISTURE_THRESHOLD = 200

# 토양 습도 값 기록 함수
def log_soil_moisture(soil_moisture):
    data = [
        {
            "measurement": "soil_moisture",
            "fields": {
                "soil_moisture": soil_moisture
            }
        }
    ]
    client = None
    try:
        client = influxdb('localhost', 8086, 'root', 'root', 'SmartPlantPot')
        client.write_points(data)
    except Exception as e:
        print("Error writing soil moisture to InfluxDB:", e)
    finally:
        if client is not None:
            client.close()

# 물 공급 함수
def activate_water_pump():
    GPIO.output(motor_pin, GPIO.LOW)  # 모터 ON
    time.sleep(2)  # 물 공급 시간
    GPIO.output(motor_pin, GPIO.HIGH)  # 모터 OFF

# 토양 습도 제어
def monitor_and_control_soil_moisture(queue):
    while True:
        if not queue.empty():
            soil_moisture, _ = queue.get()  # 큐에서 토양 습도 데이터 받기
            print(f"Received soil moisture: {soil_moisture}")

            # 토양 습도 기록
            log_soil_moisture(soil_moisture)

            # 임계값 비교 후 물 공급
            if soil_moisture < MOISTURE_THRESHOLD:
                print("Soil moisture is low, activating pump.")
                activate_water_pump()

        time.sleep(1)  # 대기
```
물탱크
```
import time
from influxdb import InfluxDBClient as influxdb

# 물탱크 높이 설정
TANK_HEIGHT_CM = 20  # 물탱크 높이 (cm)

# 물탱크 수위 퍼센트 변환 함수
def get_tank_level_percent(distance_to_water):
    water_height = TANK_HEIGHT_CM - distance_to_water
    level_percent = max(0, min(100, (water_height / TANK_HEIGHT_CM) * 100))
    return level_percent

# 물탱크 수위 기록 함수
def log_water_tank_level(level_percent):
    data = [
        {
            "measurement": "water_tank_level",
            "fields": {
                "level_percent": level_percent
            }
        }
    ]
    client = None
    try:
        client = influxdb('localhost', 8086, 'root', 'root', 'SmartPlantPot')
        client.write_points(data)
    except Exception as e:
        print("Error writing water tank level to InfluxDB:", e)
    finally:
        if client is not None:
            client.close()

# 물탱크 수위 확인 및 기록
def monitor_and_log_water_tank_level(queue):
    while True:
        if not queue.empty():
            _, distance_to_water = queue.get()  # 큐에서 물탱크 거리 값 받기
            print(f"Received water distance: {distance_to_water} cm")

            # 물탱크 수위 계산
            level_percent = get_tank_level_percent(distance_to_water)

            # 물탱크 수위 기록
            log_water_tank_level(level_percent)

        time.sleep(1)  # 대기

```
