```
import serial
import time
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient as influxdb

# 시리얼 포트 설정
serial_port = '/dev/ttyACM0'  # 포트
baud_rate = 9600  # 보드레이트
ser = serial.Serial(serial_port, baud_rate)

# 물탱크 높이 설정
TANK_HEIGHT_CM = 20  # 물탱크 높이 (cm)

# 물탱크 수위 퍼센트 변환 함수
def get_tank_level_percent():
    # 초음파 센서 값
    distance_to_water = read_ultrasonic_sensor()

    # 물 높이 계산
    water_height = TANK_HEIGHT_CM - distance_to_water

    # 퍼센트 변환
    level_percent = max(0, min(100, (water_height / TANK_HEIGHT_CM) * 100))
    return level_percent

# 초음파 센서 값 읽기
def read_ultrasonic_sensor():
    try:
        if ser.in_waiting > 0:
            # 시리얼 데이터 읽기
            line = ser.readline().decode('utf-8').rstrip()
            
            # 데이터 파싱
            parts = line.split(',')
            distance = float(parts[1])  # 거리 값
            
            return distance
    
    except ValueError:
        print("Invalid sensor reading")
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
        print("Error writing water tank to InfluxDB:", e)
    finally:
        client.close()

# 1시간마다 물탱크 수위 기록
def monitor_water_tank_level():
    while True:
        level_percent = get_tank_level_percent()
        log_water_tank_level(level_percent)
        print(f"Logged water tank level: {level_percent}%")
        time.sleep(3600)  # 1시간 대기

# 메인 실행
if __name__ == "__main__":
    try:
        monitor_water_tank_level()
        GPIO.cleanup()
        ser.close()
    except KeyboardInterrupt:
        print("Water tank monitoring interrupted.")

```
