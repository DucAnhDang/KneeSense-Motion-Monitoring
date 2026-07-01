# KneeTrack(formerly KNEESENSE): Real-Time Knee Joint Motion Monitoring System

## 1. Introduction
This project aims to recognize human motion states (Sitting, Standing, Walking) in real-time using a wearable device attached to the knee.

## 2. System Architecture
- **Hardware:** ESP32, MPU6050 (IMU), SF15 Flex Sensor, FSRs.
- **Data Transmission:** Bluetooth Low Energy (BLE).
- **Machine Learning:** Random Forest classifier trained on sensor data.
<img width="1006" height="526" alt="image" src="https://github.com/user-attachments/assets/0f2a1897-00d3-4d5f-8d9b-b14dd55023cb" />

## 3. Folder Structure
- `/ESP32_Firmware`: Source code for Edge computing & filtering (EMA, Complementary Filter).
- `/AI_Model`: Training scripts and confusion matrix evaluations.
- `/Dashboard_App`: Real-time tracking GUI.

## 4. Real Model
<img width="544" height="615" alt="image" src="https://github.com/user-attachments/assets/41b77a39-97c3-4edb-97c6-8bd4db2198a9" />
