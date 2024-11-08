import time
from influxdb import InfluxDBClient as influxdb

# 물탱크 높이 설정
TANK_HEIGHT_CM = 20  # 물탱크 높이 (cm)

# 물탱크 수위 퍼센트 변환 함수
def get_tank_level_percent(distance_to_water):
    water_height = TANK_HEIGHT_CM - distance_to_water
    level_percent = max(0, min(100, (water_height / TANK_HEIGHT_CM) * 100))
    return int(level_percent)

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
    client = None
    try:
        client = influxdb()
        client.write_points(data)
    except Exception as e:
        print("Error writing water tank level to InfluxDB:", e)
    finally:
        if client is not None:
            client.close()

# 물탱크 수위 확인 및 기록
def monitor_and_log_water_tank_level(queue):
    while True:
        if not queue.empty():
            data_type, value = queue.get()
            if data_type == 'water_tank_value':
                distance_to_water = value
            print(distance_to_water)

            # 물탱크 수위 계산
            level_percent = get_tank_level_percent(distance_to_water)

            # 물탱크 수위 기록
            log_water_tank_level(level_percent)

        time.sleep(1)  # 대기(테스트)
        #time.sleep(3600)  # 대기(1시간)
