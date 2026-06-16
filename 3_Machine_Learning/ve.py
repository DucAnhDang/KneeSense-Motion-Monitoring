import joblib
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

# 1. Load mô hình của bạn
print("Đang tải mô hình...")
model = joblib.load('knee_model.pkl')

# 2. Rút trích một cây quyết định tiêu biểu (ví dụ: cây đầu tiên có index = 0)
# Random Forest của bạn có 100 cây (n_estimators=100), bạn có thể thay số 0 bằng số bất kỳ từ 0-99
single_tree = model.estimators_[0]

# Tên các đặc trưng (phải khớp với thứ tự lúc bạn train)
feature_names = ['flex', 'fsr1', 'fsr2', 'fsr3', 'pitch', 'roll']
# Tên các nhãn (theo thứ tự bảng chữ cái mà mô hình đã học)
class_names = model.classes_ 

# 3. Vẽ biểu đồ
plt.figure(figsize=(20, 10)) # Đặt kích thước ảnh lớn để nét chữ không bị vỡ
plot_tree(single_tree, 
          feature_names=feature_names,  
          class_names=class_names,
          filled=True,      # Tô màu các hộp
          rounded=True,     # Bo góc hộp
          max_depth=3,      # CẮT TỈA: Chỉ hiển thị 3 tầng đầu tiên cho báo cáo đỡ rối
          fontsize=10)

# 4. Lưu thành file ảnh chất lượng cao
plt.savefig('decision_tree.png', dpi=300, bbox_inches='tight')
print("Đã xuất thành công file ảnh: decision_tree.png")