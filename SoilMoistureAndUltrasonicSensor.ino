// 토양 습도 센서 핀 설정
#define soilMoisturePin A1

// 초음파 센서 핀 설정
#define trigPin 9
#define echoPin 10

void setup() {
  Serial.begin(9600);

  // 초음파 센서 핀 모드 설정
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // 토양 습도 측정
  int soilMostureValue = analogRead(soilMoisturePin);

  // 초음파 센서 거리 측정
  long duration, distance;

  // Trig 핀을 LOW로 초기화
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Trig 핀에 HIGH 신호를 10 마이크로초 동안 송신
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Echo 핀에서 반사파 수신 및 시간 측정
  duration = pulseIn(echoPin, HIGH);

  // 거리를 센티미터로 변환
  distance = duration * 0.034 /2;

  // 실제 초음파 센서 거리 오차 적용(+1cm)
  distance += 1;

  Serial.print(soilMostureValue);
  Serial.print(",");
  Serial.println(distance);

  delay(1000);
}
