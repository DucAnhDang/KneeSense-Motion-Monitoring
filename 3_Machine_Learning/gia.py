import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

print("1. Đang đọc dữ liệu từ file CSV...")
try:
    # Đọc 3 file (đảm bảo tên file của bạn khớp chính xác với tên ở đây)
    df_sitting = pd.read_csv('C:\\Users\\ddanh\\Desktop\\KNEESENSE_Project\\Sitting\\data_1781281677.csv')
    df_standing = pd.read_csv('C:\\Users\\ddanh\\Desktop\\KNEESENSE_Project\\Standing\\data_1781281874.csv')
    df_walking = pd.read_csv('C:\\Users\\ddanh\\Desktop\\KNEESENSE_Project\\Walking\\data_1781282157.csv')

except FileNotFoundError as e:
    print(f"LỖI: Không tìm thấy file. Vui lòng kiểm tra lại tên file. Chi tiết: {e}")
    exit()

# Gộp 3 bảng lại thành 1 bảng duy nhất
df_final = pd.concat([df_sitting, df_standing, df_walking], ignore_index=True)
print(f"-> Tổng cộng có {len(df_final)} dòng dữ liệu được nạp.")

print("\n2. Đang tách Đặc trưng (X) và Nhãn (y)...")
# X: Các giá trị cảm biến dùng để đoán
X = df_final[['flex', 'fsr1', 'fsr2', 'fsr3', 'pitch', 'roll']]
# y: Kết quả tư thế thực tế
y = df_final['label']

print("3. Đang chia dữ liệu thành tập Huấn luyện (80%) và tập Kiểm tra (20%)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n4. Đang tiến hành huấn luyện mô hình Random Forest...")
# Khởi tạo mô hình với 100 cây quyết định
model = RandomForestClassifier(n_estimators=100, random_state=42)
# Cho mô hình học từ tập Train
model.fit(X_train, y_train)
print("-> Huấn luyện hoàn tất!")

print("\n5. Kiểm tra chất lượng mô hình trên tập Test...")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

print("\n6. Đang lưu mô hình...")
# Lưu mô hình thành file .pkl để sau này chỉ việc lôi ra dùng
joblib.dump(model, 'knee_model.pkl')
print("-> THÀNH CÔNG! Đã lưu mô hình vào file 'knee_model.pkl'.")