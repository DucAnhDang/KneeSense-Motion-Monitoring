from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

app = Flask(__name__)
# Cho phép trình duyệt (HTML) gọi API mà không bị chặn bảo mật (CORS)
CORS(app)

print("Đang nạp mô hình AI...")
try:
    model = joblib.load('knee_model.pkl')
    print("✅ Mô hình đã sẵn sàng!")
except Exception as e:
    print(f"❌ Lỗi nạp mô hình: {e}")
    exit()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Nhận mảng 6 giá trị cảm biến từ Dashboard HTML
        sensor_data = request.json['data'] 
        
        # Đưa vào mô hình dự đoán
        prediction = model.predict([sensor_data])[0]
        
        # Trả kết quả về cho HTML
        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("🚀 Máy chủ AI đang chạy tại: http://127.0.0.1:5000")
    # Chạy server không có log debug để tránh rối màn hình
    app.run(port=5000, debug=False, use_reloader=False)