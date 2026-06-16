import tkinter as tk
import csv
import time
import os
import socket
import threading

class KNEESENSE_Recorder:
    def __init__(self, root):
        self.root = root
        self.root.title("KNEESENSE Wi-Fi Recorder")
        
        self.is_recording = False
        self.current_folder = ""
        self.udp_socket = None
        
        # --- Giao diện ---
        self.btn_start_server = tk.Button(root, text="START WI-FI SERVER", command=self.start_server, width=65, height=2, bg="orange")
        self.btn_start_server.pack(pady=10)

        tk.Label(root, text="CHỌN TRẠNG THÁI GHI DỮ LIỆU", font=('Arial', 10, 'bold')).pack(pady=5)
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Button(frame, text="SITTING", command=lambda: self.set_folder("Sitting"), width=15).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="STANDING", command=lambda: self.set_folder("Standing"), width=15).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="WALKING", command=lambda: self.set_folder("Walking"), width=15).grid(row=0, column=2, padx=5)

        self.btn_rec = tk.Button(root, text="START RECORDING", command=self.toggle_recording, width=65, height=3, bg="gray", state="disabled")
        self.btn_rec.pack(pady=15)
        
        self.status = tk.Label(root, text="Nhấn START WI-FI SERVER để chờ dữ liệu", fg="red")
        self.status.pack()

    def start_server(self):
        # Mở cổng UDP 8888
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(("0.0.0.0", 8888))
        self.btn_start_server.config(text="SERVER IS RUNNING (Port 8888)", bg="green", state="disabled")
        self.btn_rec.config(state="normal", bg="lightgray")
        self.status.config(text="Đang đợi dữ liệu từ ESP32...", fg="blue")

    def set_folder(self, folder):
        self.current_folder = folder
        if not os.path.exists(folder): os.makedirs(folder)
        self.status.config(text=f"Đã chọn folder: {folder}", fg="blue")

    def toggle_recording(self):
        if not self.current_folder:
            self.status.config(text="LỖI: Hãy chọn Folder trước!", fg="red")
            return

        if not self.is_recording:
            self.filename = os.path.join(self.current_folder, f"data_{int(time.time())}.csv")
            self.file = open(self.filename, 'w', newline='')
            self.writer = csv.writer(self.file)
            self.writer.writerow(['flex', 'fsr1', 'fsr2', 'fsr3', 'pitch', 'roll', 'label'])
            
            self.is_recording = True
            self.btn_rec.config(text="STOP RECORDING", bg="red")
            threading.Thread(target=self.record_data, daemon=True).start()
        else:
            self.is_recording = False
            self.file.close()
            self.btn_rec.config(text="START RECORDING", bg="lightgray")
            self.status.config(text=f"Đã lưu vào {self.filename}")

    def record_data(self):
        while self.is_recording:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                line = data.decode('utf-8').strip()
                row = line.split(',')
                if len(row) == 6:
                    row.append(self.current_folder)
                    self.writer.writerow(row)
                    self.file.flush()
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = KNEESENSE_Recorder(root)
    root.mainloop()