import time
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient as influxdb
from water_tank_monitor import log_water_tank_level, get_tank_level_percent

# GPIO 설정
motor_pin = 14  # 수중 모터 핀(우측위에서 3번째)
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
        client = influxdb()
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
    log_water_tank_level(get_tank_level_percent())    # 물탱크 수위 최신화

# 토양 습도 제어
def monitor_and_control_soil_moisture(queue):
    while True:
        if not queue.empty():            
            # 큐에서 토양 습도 데이터 받기
            data_type, value = queue.get()
            if data_type == 'soil_moisture_value':
                soil_moisture = value
            print(soil_moisture)

            # 토양 습도 기록
            log_soil_moisture(soil_moisture)

            # 임계값 비교 후 물 공급
            if soil_moisture < MOISTURE_THRESHOLD:
                print("토양 습도 임계값보다 낮음, 모터 작동")
                activate_water_pump()

        time.sleep(1)  # 대기(테스트)
        #time.sleep(600)  # 대기(10분)
