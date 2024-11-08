```
# water_tank_monitor.py
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
    distance_to_water = read_ultrasonic_sensor()

    if distance_to_water is not None:
        water_height = TANK_HEIGHT_CM - distance_to_water
        level_percent = max(0, min(100, (water_height / TANK_HEIGHT_CM) * 100))
        return level_percent
    else:
        print("Failed to read distance; skipping water level logging.")
        return None

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
