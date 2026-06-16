#include <Arduino.h>
#include <Wire.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// --- 1. CẤU HÌNH PHẦN CỨNG ---
const int MPU_ADDR = 0x68;
const int flexPin = 35; // Cảm biến góc uốn
const int fsrPin1 = 34; // Cảm biến lực cơ thẳng đùi (Rectus Femoris)
const int fsrPin2 = 32; // Cảm biến lực cơ rộng ngoài (Vastus Lateralis)
const int fsrPin3 = 33; // Cảm biến lực cơ rộng trong (Vastus Medialis)

// Bộ lọc EMA
float alpha = 0.2;
float ema_flex = 0;
float ema_fsr1 = 0;
float ema_fsr2 = 0;
float ema_fsr3 = 0;
float fsr1_offset = 0; 
float fsr2_offset = 0;
float fsr3_offset = 0;

// --- BIẾN CHO BỘ LỌC BÙ (COMPLEMENTARY FILTER) ---
float angle_Pitch = 0, angle_Roll = 0;
long lastTime = 0;
float alpha_imu = 0.96; 

// --- 2. CẤU HÌNH BLUETOOTH BLE ---
BLEServer *pServer = NULL;
BLECharacteristic * pTxCharacteristic;
bool deviceConnected = false;

#define SERVICE_UUID           "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define CHARACTERISTIC_UUID_TX "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };
    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      pServer->getAdvertising()->start();
    }
};

// --- 3. HÀM CHUYỂN ĐỔI ADC SANG LỰC (NEWTON) ---
float adc_to_newtons(float adc_value, float offset) {
    // Trừ đi offset để loại bỏ lực căng dây đai ban đầu
    float corrected_adc = adc_value - offset;
    
    // Nếu giá trị nhỏ hơn 0 (do nhiễu), cho về 0
    if (corrected_adc < 0) return 0.0; 
    
    float ADC_MAX = 2300.0 - offset; // Dải đo thay đổi theo offset
    float NEWTONS_MAX = 30.0;
    
    if (corrected_adc > ADC_MAX) return NEWTONS_MAX;
    
    return (corrected_adc / ADC_MAX) * NEWTONS_MAX;
}

void setup() {
  Serial.begin(115200);

  // Khởi tạo MPU6050
  Wire.begin(21, 22);
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); 
  Wire.write(0);    
  if(Wire.endTransmission(true) == 0) {
    Serial.println("✅ MPU6050 Ready!");
  } else {
    Serial.println("❌ Error MPU6050!");
  }

  // Khởi tạo bộ lọc nền cho cả 4 cảm biến Analog
  ema_flex = analogRead(flexPin);
  ema_fsr1 = analogRead(fsrPin1);
  ema_fsr2 = analogRead(fsrPin2);
  ema_fsr3 = analogRead(fsrPin3);
  
  lastTime = millis(); 

  // Thiết lập Bluetooth
  BLEDevice::init("KNEESENSE_prototype"); 
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pTxCharacteristic = pService->createCharacteristic(
                        CHARACTERISTIC_UUID_TX,
                        BLECharacteristic::PROPERTY_NOTIFY
                      );
  pTxCharacteristic->addDescriptor(new BLE2902());
  
  pService->start();
  pServer->getAdvertising()->start();
  Serial.println("✅ BLE Broadcasting... Waiting for Web Dashboard");

  // --- TÍNH NĂNG ADAPTIVE AUTO-TARE (READ 10 SAMPLES) ---
  Serial.println("Calibrating sensors... Please keep the strap stable.");
  float sum1 = 0, sum2 = 0, sum3 = 0;
  
  for(int i = 0; i < 10; i++) {
    sum1 += analogRead(fsrPin1);
    sum2 += analogRead(fsrPin2);
    sum3 += analogRead(fsrPin3);
    delay(20); // Đợi 200ms tổng cộng
  }
  
  fsr1_offset = sum1 / 10.0;
  fsr2_offset = sum2 / 10.0;
  fsr3_offset = sum3 / 10.0;
  
  Serial.printf("Auto-Tare Complete. Offsets: %.2f, %.2f, %.2f\n", fsr1_offset, fsr2_offset, fsr3_offset);
}

void loop() {
  // ==========================================
  // 1. ĐỌC VÀ DUNG HỢP DỮ LIỆU MPU6050
  // ==========================================
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true);
  
  if(Wire.available() == 14) {
    // 1.1 Đọc giá trị THÔ nguyên bản từ phần cứng
    int16_t raw_ax = Wire.read() << 8 | Wire.read();
    int16_t raw_ay = Wire.read() << 8 | Wire.read();
    int16_t raw_az = Wire.read() << 8 | Wire.read();
    
    Wire.read(); Wire.read(); // Bỏ qua nhiệt độ
    
    int16_t raw_gx = Wire.read() << 8 | Wire.read();
    int16_t raw_gy = Wire.read() << 8 | Wire.read();
    int16_t raw_gz = Wire.read() << 8 | Wire.read();

    // =========================================================
    // 1.2 HOÁN ĐỔI TRỤC TỌA ĐỘ (AXIS REMAPPING)
    // Tình huống: Đứng -> MPU nằm ngang; Ngồi -> MPU dựng đứng
    // =========================================================
    float ax = raw_ay;  // Trục Y nguyên bản không bị đổi khi gập gối
    float ay = raw_ax;  // Trục X nguyên bản gánh trọng lực khi ngồi -> Đưa vào tính Pitch
    float az = raw_az;  // Trục Z nguyên bản gánh trọng lực khi đứng

    
    // Gyro cũng phải được tráo đổi y hệt như gia tốc
    float gx = raw_gy;
    float gy = raw_gx;
    float gz = raw_gz;
    // =========================================================

    long currentTime = millis();
    float dt = (currentTime - lastTime) / 1000.0;
    lastTime = currentTime;

    // 1.3 Tính toán vận tốc góc (độ/s)
    float gyro_rate_x = gx / 131.0;
    float gyro_rate_y = gy / 131.0;

    // 1.4 Tính góc Euler bằng lượng giác
    float acc_Pitch = atan2(ay, sqrt(pow(ax, 2) + pow(az, 2))) * 180 / PI;
    float acc_Roll  = atan2(-ax, sqrt(pow(ay, 2) + pow(az, 2))) * 180 / PI;

    // 1.5 Bộ lọc bù (Complementary Filter)
    angle_Pitch = alpha_imu * (angle_Pitch + gyro_rate_x * dt) + (1.0 - alpha_imu) * acc_Pitch;
    angle_Roll  = alpha_imu * (angle_Roll  + gyro_rate_y * dt) + (1.0 - alpha_imu) * acc_Roll;
  }

  // ==========================================
  // 2. ĐỌC VÀ LỌC NHIỄU CỤM CẢM BIẾN (FLEX & 3xFSR)
  // ==========================================
  ema_flex = (alpha * analogRead(flexPin)) + ((1.0 - alpha) * ema_flex);
  ema_fsr1 = (alpha * analogRead(fsrPin1)) + ((1.0 - alpha) * ema_fsr1);
  ema_fsr2 = (alpha * analogRead(fsrPin2)) + ((1.0 - alpha) * ema_fsr2);
  ema_fsr3 = (alpha * analogRead(fsrPin3)) + ((1.0 - alpha) * ema_fsr3);
  
  // Gọi hàm quy đổi ra Newton
  // Gọi hàm với offset đã lưu
  float force_n1 = adc_to_newtons(ema_fsr1, fsr1_offset);
  float force_n2 = adc_to_newtons(ema_fsr2, fsr2_offset);
  float force_n3 = adc_to_newtons(ema_fsr3, fsr3_offset);

  // ==========================================
  // 3. ĐÓNG GÓI DỮ LIỆU VÀ GỬI QUA BLE
  // ==========================================
  String dataStr = String((int)ema_flex) + "," + 
                   String(force_n1, 2) + "," + 
                   String(force_n2, 2) + "," + 
                   String(force_n3, 2) + "," + 
                   String(angle_Pitch, 2) + "," + 
                   String(angle_Roll, 2) + "\n";

  // 1. KÊNH BLE (Cho Dashboard thời gian thực)
  if (deviceConnected) {
    pTxCharacteristic->setValue(dataStr.c_str());
    pTxCharacteristic->notify(); 
  }

  delay(20); // Duy trì tốc độ lấy mẫu 50Hz
}