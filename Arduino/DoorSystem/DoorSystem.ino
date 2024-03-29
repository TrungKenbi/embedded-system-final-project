#include <ServoEasing.h>
#include <LiquidCrystal_I2C.h>

// Cấu hình chân kết nối
#define BUTTON_PIN 2
#define LED_PIN 3
#define SERVO_PIN 9
#define BUZZER_PIN 11

// Cấu hình LCD
#define LCD_ADDRESS 0x27
#define LCD_WIDTH 16
#define LCD_HEIGHT 2

// Cấu hình Serial Port
#define SERIAL_PORT_BAUD_RATE 115200

// Cấu hình hệ thống cửa
#define DOOR_OPEN_ANGLE 90
#define DOOR_CLOSE_ANGLE 0
#define DOOR_SERVO_SPEED 40

// Thời gian giữ nút tối thiểu
#define LONG_PRESS_TIME 1000

// Các biến trạng thái và thời gian
bool currentDoorState = false;
bool isOpeningDoor = false;
bool isClosingDoor = false;
unsigned long pressedTime = 0;
unsigned long releasedTime = 0;

uint8_t bell[8]  = {0x4,0xe,0xe,0xe,0x1f,0x0,0x4};
byte smiley[8] = {
  B00000,
  B10001,
  B00000,
  B00000,
  B10001,
  B01110,
  B00000,
};

ServoEasing doorServo;
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_WIDTH, LCD_HEIGHT);

void displayDoorState(bool);
void openDoor();
void closeDoor();
void alert();

void setup() {
  // Khởi tạo
  Serial.begin(SERIAL_PORT_BAUD_RATE);
  Serial.setTimeout(1);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Khai báo ngắt
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonHandle, CHANGE);

  // Khởi tạo LCD
  lcd.init();
  lcd.backlight();

  lcd.createChar(0, bell);

  // Khởi tạo servo
  if (doorServo.attach(SERVO_PIN) == INVALID_SERVO)
    Serial.println(F("Error attaching servo"));

  // Trạng thái mặc định của các thiết bị
  doorServo.write(DOOR_CLOSE_ANGLE);
  delay(500);
  displayDoorState(false);
  delay(100);
}

void loop() {
  // Nếu có lệnh mở cửa thì sẽ mở cửa
  if (isOpeningDoor && !currentDoorState) {
    doorServo.startEaseTo(DOOR_OPEN_ANGLE, DOOR_SERVO_SPEED, false);
    alert();
    displayDoorState(true);
    isOpeningDoor = false;
    currentDoorState = true;
  }

  // Nếu có lệnh đóng cửa thì sẽ đóng cửa
  if (isClosingDoor && currentDoorState) {
    doorServo.startEaseTo(DOOR_CLOSE_ANGLE, DOOR_SERVO_SPEED, false);
    alert();
    displayDoorState(false);
    isClosingDoor = false;
    currentDoorState = false;
  }

  // Chờ servo đến khi servo quay xong
  while (!doorServo.update())
    delay(REFRESH_INTERVAL / 1000);
}

// Xử lý dữ liệu nhận về từ Serial bằng ngắt
void serialEvent() {
  while (Serial.available()) {
    int inp = Serial.read();
    if (inp == 10)
      break;
    if (inp == 48) {
      // Lệnh đóng cửa
      digitalWrite(LED_BUILTIN, LOW);
      closeDoor();
      alert();
    } else if (inp == 49) {
      // Lệnh mở cửa
      digitalWrite(LED_BUILTIN, HIGH);
      openDoor();
      alert();
    }
  }
}

// Xử lý nút nhấn bằng ngắt
void buttonHandle() {
  long currentMilis = millis();
  bool currentState = digitalRead(BUTTON_PIN);
  if (currentState == HIGH) {
    pressedTime = currentMilis;
    digitalWrite(LED_PIN, HIGH);
    tone(BUZZER_PIN, 1000);
  } else if (currentState == LOW) {
    releasedTime = currentMilis;
    long pressDuration = releasedTime - pressedTime;
    
    // Nếu nút nhấn nhấn đủ lâu sẽ kích hoạt đóng cửa
    if (pressDuration > LONG_PRESS_TIME)
      closeDoor();
      
    digitalWrite(LED_PIN, LOW);
    noTone(BUZZER_PIN);
  }
}

// Mở cửa
void openDoor() {
  Serial.println("OPEN");
  isOpeningDoor = true;
}

// Đóng cửa
void closeDoor() {
  Serial.println("CLOSE");
  isClosingDoor = true;
}

// Phát âm thanh ra loa
void alert() {
  for (int i = 0; i < 2; i++) {
    tone(BUZZER_PIN, 1000);
    delay(100);
    noTone(BUZZER_PIN);
    delay(100);
  }
}

// Hiển thị trạng thái lên màn hình
void displayDoorState(bool isOpen) {
  lcd.clear();
  lcd.setCursor(1, 0);
  lcd.write(byte(0));
  lcd.setCursor(3, 0);
  lcd.print("Door State ");
  lcd.write(byte(0));

  lcd.setCursor(isOpen ? 6 : 5, 1);
  lcd.print(isOpen ? "OPEN" : "CLOSE");
}
