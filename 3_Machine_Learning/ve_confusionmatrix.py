import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

print("1. Đang tải mô hình và dữ liệu...")
# Tải mô hình đã nạp sẵn
model = joblib.load('knee_model.pkl')

# Đọc dữ liệu từ 3 file CSV tư thế của bạn
df_sitting = pd.read_csv('C:\\Users\\ddanh\\Desktop\\KNEESENSE_Project\\Sitting\\data_1781281677.csv')
df_standing = pd.read_csv('C:\\Users\\ddanh\\Desktop\\KNEESENSE_Project\\Standing\\data_1781281874.csv')
df_walking = pd.read_csv('C:\\Users\\ddanh\\Desktop\\KNEESENSE_Project\\Walking\\data_1781282157.csv')


# Gộp dữ liệu lại thành một tập duy nhất để đánh giá
df_final = pd.concat([df_sitting, df_standing, df_walking], ignore_index=True)

# Tách đặc trưng (X) và nhãn thực tế (y_true)
X = df_final[['flex', 'fsr1', 'fsr2', 'fsr3', 'pitch', 'roll']]
y_true = df_final['label']

print("2. Mô hình đang tiến hành dự đoán...")
# Cho mô hình dự đoán thử trên tập dữ liệu này
y_pred = model.predict(X)

print("3. Đang tính toán và vẽ Ma trận nhầm lẫn...")
# Tính toán ma trận nhầm lẫn dựa trên nhãn thực tế và nhãn dự đoán
cm = confusion_matrix(y_true, y_pred, labels=model.classes_)

# Khởi tạo khung vẽ
fig, ax = plt.subplots(figsize=(8, 6))

# Cấu hình hiển thị ma trận nhầm lẫn
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
# Sử dụng bảng màu Blues (Xanh dương) chuẩn nghiên cứu khoa học
disp.plot(cmap=plt.cm.Blues, ax=ax, values_format='d')

# Thêm tiêu đề tiếng Việt cho biểu đồ
plt.title('MA TRẬN NHẦM LẪN (CONFUSION MATRIX) - KNEESENSE', fontsize=12, fontweight='bold', pad=15)
plt.xlabel('Nhãn Dự Đoán từ AI (Predicted Label)', fontsize=10, fontweight='bold')
plt.ylabel('Nhãn Thực Tế từ Cảm Biến (True Label)', fontsize=10, fontweight='bold')

# Tối ưu giao diện ảnh
plt.tight_layout()

# Lưu biểu đồ thành file ảnh chất lượng cao (300 DPI) để chèn vào Word/PDF báo cáo
plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
print("-> THÀNH CÔNG! Đã lưu ảnh ma trận nhầm lẫn vào file 'confusion_matrix.png'.")

# Hiển thị biểu đồ lên màn hình
plt.show()