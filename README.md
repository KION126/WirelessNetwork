# WirelessNetwork

```
# water_tank_monitor.py
import time
from influxdb import InfluxDBClient as influxdb

# 물탱크 높이 설정 (수정 가능)
TANK_HEIGHT_CM = 20  # 물탱크 높이 (cm)

# 물탱크 수위 퍼센트 조회 함수
def get_tank_level_percent():
    # 초음파 센서로 뚜껑부터 물까지의 거리를 측정하는 예시 값 (실제 센서 값으로 교체 필요)
    distance_to_water = read_ultrasonic_sensor()  # 초음파 센서 값 읽기 함수 (아래에 정의)
    
    # 물 높이 계산
    water_height = TANK_HEIGHT_CM - distance_to_water

    # 퍼센트 계산
    level_percent = max(0, min(100, (water_height / TANK_HEIGHT_CM) * 100))
    return level_percent

# 초음파 센서 값 읽기 (가상의 함수로 예시)
def read_ultrasonic_sensor():
    # 여기서 실제 초음파 센서 값을 반환하도록 구현합니다.
    # 예를 들어 5cm 깊이만큼 물이 있을 때 15cm가 남았다고 가정
    return 15  # 예시 거리 값 (cm)

# 물탱크 수위 퍼센트 기록 함수
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
        print("Error writing to InfluxDB:", e)
    finally:
        client.close()

# 1시간마다 물탱크 수위 퍼센트 기록
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
    except KeyboardInterrupt:
        print("Water tank monitoring interrupted.")

```


```
# soil_moisture_control.py
import time
import RPi.GPIO as GPIO
import serial
from water_tank_monitor import log_water_tank_level, get_tank_level_percent

# GPIO 설정
motor_pin = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

# 시리얼 포트 설정
serial_port = '/dev/ttyACM0'
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)
moisture_threshold = 200

# 물 공급 함수
def activate_water_pump():
    GPIO.output(motor_pin, GPIO.LOW)  # 모터 ON
    time.sleep(2)  # 물을 공급할 시간
    GPIO.output(motor_pin, GPIO.HIGH)  # 모터 OFF

# 일정 시간마다 습도 재확인 및 기록
def check_soil_moisture_until_threshold():
    while True:
        time.sleep(600)  # 10분 대기
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            parts = line.split(' ')
            soil_moisture = int(parts[1])

            # 토양습도를 DB에 저장 (임포트된 함수 사용)
            log_soil_moisture(soil_moisture)

            # 임계값 도달 시 루프 종료
            if soil_moisture >= moisture_threshold:
                print("Soil moisture threshold reached, stopping pump.")
                break
            else:
                print("Soil moisture still below threshold, reactivating water pump.")
                activate_water_pump()
                log_water_tank_level(get_tank_level_percent())  # 물탱크 수위 기록

# 토양습도 확인 및 물 공급
def control_soil_moisture():
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            parts = line.split(' ')
            soil_moisture = int(parts[1])

            # 물 공급 및 수위 저장
            if soil_moisture < moisture_threshold:
                print("Soil moisture below threshold, activating water pump.")
                activate_water_pump()
                log_water_tank_level(get_tank_level_percent())
                
                # 10분 대기 후 다시 확인
                check_soil_moisture_until_threshold()
            else:
                GPIO.output(motor_pin, GPIO.HIGH)  # 모터 OFF
    except ValueError:
        print("Invalid sensor reading")

# 메인 실행
if __name__ == "__main__":
    try:
        while True:
            control_soil_moisture()
            time.sleep(1)  # 1초 간격으로 습도 확인
    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        GPIO.cleanup()
        ser.close()

```
