import serial
import time
import RPi.GPIO as GPIO

# 수중 모터 핀 설정
motor_pin = 17  # GPIO 핀 번호

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

# 시리얼 포트 설정
serial_port = '/dev/ttyUSB0' 	# 포트
baud_rate = 9600  		# 보드레이트
ser = serial.Serial(serial_port, baud_rate)

# 토양 습도 값 설정
moisture_threshold = 400 

try:
    while True:
        # 시리얼 데이터 읽기
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip() 
            print(line)  # 수신된 데이터 출력

            # 데이터 파싱
            parts = line.split(' ')
            if len(parts) == 4:  # Distance와 SoilMoisture 값이 있는 경우
                distance = float(parts[1])  	# 거리 값
                soil_moisture = int(parts[3])  # 토양 습도 값

                # 토양 습도 값에 따라 모터 작동
                if soil_moisture < moisture_threshold:
                    print("모터 작동")
                    GPIO.output(motor_pin, GPIO.HIGH)  # 모터 ON
                else:
                    print("모터 정지")
                    GPIO.output(motor_pin, GPIO.LOW)  # 모터 OFF

        time.sleep(1)  # 3초 대기

except KeyboardInterrupt:
    print("종료")
finally:
    GPIO.cleanup()
    ser.close()