```
import multiprocessing
from soil_moisture_control import monitor_and_control_soil_moisture
from water_tank_monitor import monitor_and_log_water_tank_level

def serial_reader(queue):
    import serial
    serial_port = '/dev/ttyACM0'  # 아두이노의 시리얼 포트
    baud_rate = 9600
    ser = serial.Serial(serial_port, baud_rate)
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            parts = line.split(',')
            soil_moisture = int(parts[0])  # 첫 번째 값: 토양 습도
            water_distance = float(parts[1])  # 두 번째 값: 물탱크 거리

            # 데이터를 Queue에 넣기
            queue.put((soil_moisture, water_distance))

if __name__ == "__main__":
    # 시리얼 데이터와 다른 데이터 전달을 위한 큐 생성
    queue = multiprocessing.Queue()

    # 시리얼 데이터를 읽는 프로세스
    serial_process = multiprocessing.Process(target=serial_reader, args=(queue,))
    
    # 토양 습도 관리 프로세스
    soil_moisture_process = multiprocessing.Process(target=monitor_and_control_soil_moisture, args=(queue,))
    
    # 물탱크 수위 관리 프로세스
    water_tank_process = multiprocessing.Process(target=monitor_and_log_water_tank_level, args=(queue,))

    # 프로세스 시작
    serial_process.start()
    soil_moisture_process.start()
    water_tank_process.start()

    # 프로세스들이 종료되지 않도록 기다리기
    serial_process.join()
    soil_moisture_process.join()
    water_tank_process.join()

```
