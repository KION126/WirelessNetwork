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
from influxdb import InfluxDBClient as influxdb
from water_tank_monitor import log_water_tank_level, get_tank_level_percent

# GPIO 및 시리얼 설정
motor_pin = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

serial_port = '/dev/ttyACM0'
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)
moisture_threshold = 200

# InfluxDB에 토양 습도 저장 함수
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
    time.sleep(2)  # 물을 공급하는 시간
    GPIO.output(motor_pin, GPIO.HIGH)  # 모터 OFF
    log_water_tank_level(get_tank_level_percent())  # 물탱크 수위 기록

# 10분마다 토양 습도 확인 및 제어
def monitor_and_control_soil_moisture():
    while True:
        try:
            if ser.in_waiting > 0:
                # 시리얼 데이터 읽기
                line = ser.readline().decode('utf-8').rstrip()
                parts = line.split(' ')
                soil_moisture = int(parts[1])

                # DB에 토양 습도 기록
                log_soil_moisture(soil_moisture)
                print(f"Logged soil moisture: {soil_moisture}")

                # 임계값 비교 후 물 공급
                if soil_moisture < moisture_threshold:
                    print("Soil moisture below threshold, activating water pump.")
                    activate_water_pump()

            time.sleep(600)  # 10분 대기
        except ValueError:
            print("Invalid sensor reading")
        except KeyboardInterrupt:
            print("Soil moisture monitoring interrupted.")
            break
    GPIO.cleanup()
    ser.close()

# 메인 실행
if __name__ == "__main__":



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
def read_soil_mosture_sensor():
    try:
        if ser.in_waiting > 0:
            # 시리얼 데이터 읽기
            line = ser.readline().decode('utf-8').rstrip()
            
            # 데이터 파싱
            parts = line.split(',')
            distance = float(parts[2])  # 습도 값
            
            return distance
    
    except ValueError:
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
    time.sleep(2)  # 물을 공급하는 시간
    GPIO.output(motor_pin, GPIO.HIGH)  # 모터 OFF
    log_water_tank_level(get_tank_level_percent())  # 물탱크 수위 기록

# 10분마다 토양 습도 확인 및 저장, 모터 제어
def monitor_and_control_soil_moisture():
    while True:
        # 토양 습도 값
        soil_moisture = read_soil_mosture_sensor()

        # 토양 습도 기록
        log_soil_moisture(soil_moisture)

        # 임계값 비교 후 물 공급
        if soil_moisture < moisture_threshold:
            print("토양 습도가 임계값 보다 낮음, 모터 작동")
            activate_water_pump()

        time.sleep(600)  # 10분 대기

# 메인 실행
if __name__ == "__main__":
    try:
        monitor_and_control_soil_moisture()
        GPIO.cleanup()
        ser.close()
    except KeyboardInterrupt:
        print("Soil moisture monitoring interrupted.")


```
    monitor_and_control_soil_moisture()


```
