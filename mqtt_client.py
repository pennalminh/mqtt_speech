import paho.mqtt.client as mqtt
import json
import subprocess
import os
import threading
import time
from dotenv import load_dotenv

repeat_thread = None
stop_event = threading.Event()

# Load environment variables from .env file
load_dotenv()

# Thông tin MQTT broker từ biến môi trường
MQTT_BROKER = os.environ.get("MQTT_BROKER", "45.252.249.222")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "cw/speech/CW001")

def play_text_with_edge(text):
    command = f'edge-playback --rate=-20% --voice vi-VN-HoaiMyNeural --text "{text}"'
    print(f"Chạy lệnh: {command}")
    subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

def repeat_play(audio_file, max_repeat=5):
    count = 0
    while not stop_event.is_set() and count < max_repeat:
        subprocess.run(["mpv", audio_file])
        count += 1
        time.sleep(1)

# Callback khi kết nối thành công với MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Kết nối MQTT thành công")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Kết nối MQTT thất bại với mã lỗi {rc}")

# Callback khi nhận tin nhắn từ MQTT
def on_message(client, userdata, msg):
    global repeat_thread, stop_event

    message = msg.payload.decode('utf-8')
    message_json = json.loads(message)
    print(f"Nhận tin nhắn từ MQTT: {message_json}")

    # Dừng phát lặp lại hiện tại (nếu có)
    if repeat_thread and repeat_thread.is_alive():
        stop_event.set()
        repeat_thread.join()

    stop_event.clear()

    if message_json["text"] == "monitor_1":
        repeat_thread = threading.Thread(target=repeat_play, args=("monitor_1.mp3",5))
        repeat_thread.start()
    elif message_json["text"] == "monitor_4":
        repeat_thread = threading.Thread(target=repeat_play, args=("monitor_4.mp3",5))
        repeat_thread.start()
    elif message_json["isRepeat"] == True:
        repeat_thread = threading.Thread(target=repeat_play, args=(message_json["text"],5))
        repeat_thread.start()
    else:
        # Nếu không phải monitor_3 hoặc monitor_4, thì phát 1 lần
        switch_message = {
            'monitor_2': lambda: subprocess.run(["mpv", "monitor_2.mp3"]),
            'monitor_3': lambda: subprocess.run(["mpv", "monitor_3.mp3"]),
            'monitor_6': lambda: subprocess.run(["mpv", "monitor_6.mp3"]),
            'status_3': lambda: subprocess.run(["mpv", "status_3.mp3"]),
            'status_4': lambda: subprocess.run(["mpv", "status_4.mp3"]),
        }
        action = switch_message.get(message_json["text"], lambda: play_text_with_edge(message_json["text"]))
        action()

# Cấu hình MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Kết nối tới MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Vòng lặp chính để giữ kết nối
client.loop_forever()
