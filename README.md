# WirelessNetwork

```
import serial
import time
import datetime import datetime
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient as influxdb

# 수중 모터 핀 설정
motor_pin = 14  # GPIO 핀 번호

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

# 시리얼 포트 설정
serial_port = '/dev/ttyACM0' 	# 포트
baud_rate = 9600  		# 보드레이트
ser = serial.Serial(serial_port, baud_rate)

# 토양 습도 임계값 설정
moisture_threshold = 200 

# InfluxDB 설정
def influxDB_insert(soil_moisture, distance):
    data = [
        {
            "measurement": "soil_moisture",
            "fields": {
                "soil_moisture": soil_moisture,
            }
        },
        {
            "measurement": "water_tank_level",
            "fields": {
                "water_tank_level": distance
            }
        }
    ]
    
    # InfluxDB 연결 및 데이터 전송
    client = None
    try:
        client = influxdb('localhost', 'root', 'root', 'SmartPlantPot')
    except Exception as e:
        print("smwtM.InfluxDB Exception: " + str(e))
    
    if client is not None:
        try:
            client.write_points(data)
        except Exception as e:
            print("smwtM.InfluxDB Exception write: " + str(e))
        finally:
            client.close()
       
# 수중 모터 작동
def activate_water_pump:
    PIO.output(motor_pin, GPIO.LOW)  # 모터 ON
    
def control_water_pump:
    try:
        if ser.in_waiting > 0:
            # 시리얼 데이터 읽기
            line = ser.readline().decode('utf-8').rstrip() 
            
            # 데이터 파싱
            parts = line.split(' ')
            soil_moisture = int(parts[1])  # 토양 습도 값
            distance = float(parts[3])  	# 거리 값
            
            # InfluxDB에 데이터 저장
            influxDB_insert(soil_moisture, distance)
            
            # 토양 습도 값에 따라 모터 작동
            if soil_moisture < moisture_threshold:
                activate_water_pump  # 모터 ON
            else:
                GPIO.output(motor_pin, GPIO.HIGH)  # 모터 OFF
            
    except ValueError:
        print("smwtM.Invalid senter reading")
    
def main():
    print("Starting soil_moisture_water_tank_moniter.py...")
    
    try:
        while True:
            control_water_pump()
            time.sleep(1)   # 간격
    
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        
if name == "main":
    main()
    
finally:
    GPIO.cleanup()
    ser.close()


```
