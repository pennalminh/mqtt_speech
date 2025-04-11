import paho.mqtt.client as mqtt
import json
import subprocess
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Thông tin MQTT broker từ biến môi trường
MQTT_BROKER = os.environ.get("MQTT_BROKER", "45.252.249.222")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "cw/speech/CW005")

def play_text_with_edge(text):
    command = f'edge-playback --rate=-20% --voice vi-VN-HoaiMyNeural --text "{text}"'
    print(f"Chạy lệnh: {command}")
    subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

# Callback khi kết nối thành công với MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Kết nối MQTT thành công")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Kết nối MQTT thất bại với mã lỗi {rc}")

# Callback khi nhận tin nhắn từ MQTT
def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    message_json = json.loads(message) 
    print(f"Nhận tin nhắn từ MQTT: {message_json}")

    switch_message = {
        'monitor_1': lambda: subprocess.run(["mpv", "monitor_1.mp3"]),
        'monitor_2': lambda: subprocess.run(["mpv", "monitor_2.mp3"]),
        'monitor_3': lambda: subprocess.run(["mpv", "monitor_3.mp3"]),
        'monitor_4': lambda: subprocess.run(["mpv", "monitor_4.mp3"]),
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
