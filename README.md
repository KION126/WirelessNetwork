```
import time
import serial
from influxdb import InfluxDBClient as influxdb

# 시리얼 포트 설정
serial_port = '/dev/ttyACM0'  # 포트
baud_rate = 9600  # 보드레이트
ser = serial.Serial(serial_port, baud_rate)

# 물탱크 높이 설정
TANK_HEIGHT_CM = 20  # 물탱크 높이 (cm)

# 물탱크 수위 퍼센트 변환 함수
def get_tank_level_percent():
    # 물탱크 수위
    distance_to_water = read_ultrasonic_sensor()

    # 수위 퍼센트 변환
    if distance_to_water is not None:
        water_height = TANK_HEIGHT_CM - distance_to_water
        level_percent = max(0, min(100, (water_height / TANK_HEIGHT_CM) * 100))
        return level_percent

# 초음파 센서 값 읽기
def read_ultrasonic_sensor():
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            parts = line.split(',')
            distance = float(parts[1])  # 거리 값
            return distance
    except (ValueError, IndexError) as e:
        print("Invalid sensor reading:", e)
    return None

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
    try:
        client = influxdb('localhost', 'root', 'root', 'SmartPlantPot')
        client.write_points(data)
    except Exception as e:
        print("Error writing water tank level to InfluxDB:", e)
    finally:
        client.close()

# 1시간마다 물탱크 수위 기록
def monitor_water_tank_level():
    while True:
        level_percent = get_tank_level_percent()
        if level_percent is not None:
            log_water_tank_level(level_percent)
            print(f"Logged water tank level: {level_percent}%")
        time.sleep(3600)  # 1시간 대기

# 메인 실행
if __name__ == "__main__":
    try:
        monitor_water_tank_level()
    except KeyboardInterrupt:
        print("Water tank monitoring interrupted.")
    finally:
        ser.close()

```
```
import time
import RPi.GPIO as GPIO
import serial
from influxdb import InfluxDBClient as influxdb
from water_tank_monitor import log_water_tank_level, get_tank_level_percent

# GPIO 및 시리얼 설정
motor_pin = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

# 시리얼 포트 설정
serial_port = '/dev/ttyACM0'  # 포트
baud_rate = 9600  # 보드레이트
ser = serial.Serial(serial_port, baud_rate)

# 토양 습도 임계값
MOISTURE_THRESHOLD = 200

# 토양 습도 값 읽기
def read_soil_moisture_sensor():
    try:
        if ser.in_waiting > 0:
            # 시리얼 데이터 읽기
            line = ser.readline().decode('utf-8').rstrip()
            
            # 데이터 파싱
            parts = line.split(',')
            soil_moisture = float(parts[0])  # 토양 습도 값
            return int(soil_moisture)
            
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

        time.sleep(1)  # 10분 대기

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
