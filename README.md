# WirelessNetwork

```
import serial
import time
import RPi.GPIO as GPIO

# 수중 모터를 연결한 핀 번호 설정
motor_pin = 17  # GPIO 핀 번호 (적절한 핀 번호로 변경)

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

# 아두이노가 연결된 시리얼 포트 설정 (포트 경로를 확인 후 변경)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # 연결 안정화를 위해 대기

try:
    while True:
        if ser.in_waiting > 0:  # 데이터가 수신된 경우
            data = ser.readline().decode('utf-8').strip()
            print(data)  # 거리와 습도 값을 출력
            
            # 데이터 파싱
            parts = data.split(", ")
            soil_moisture_value = int(parts[1].split(": ")[1])  # 토양 습도 값 추출
            
            # 토양 습도 값이 기준 이하일 때 모터 작동
            if soil_moisture_value < 300:  # 기준 값 이하로 설정
                print("수중 모터 작동")
                GPIO.output(motor_pin, GPIO.HIGH)  # 모터 ON
            else:
                print("수중 모터 멈춤")
                GPIO.output(motor_pin, GPIO.LOW)   # 모터 OFF

except KeyboardInterrupt:
    print("종료")
finally:
    GPIO.cleanup()  # GPIO 핀 상태 정리
    ser.close()  # 시리얼 포트 닫기

```
