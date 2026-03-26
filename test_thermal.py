import time
import board
import busio
import adafruit_mlx90640
import numpy as np

print("🔥 Initializing thermal sensor...")

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize sensor with retry
mlx = None
while mlx is None:
    try:
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
        print("✅ Thermal sensor initialized")
    except Exception as e:
        print("❌ Init failed:", e)
        print("🔄 Retrying in 2 seconds...")
        time.sleep(2)

frame = [0] * 768

# Skip unstable startup frames
skip_frames = 5
count = 0

print("🚀 Thermal monitoring started...\n")

while True:
    try:
        mlx.getFrame(frame)

        # Skip first unstable readings
        if count < skip_frames:
            count += 1
            continue

        data = np.array(frame)

        avg_temp = np.mean(data)
        max_temp = np.max(data)

        print(f"🌡 Avg: {avg_temp:.2f}°C | Max: {max_temp:.2f}°C")

        if max_temp > 28:
            print("👤 Human heat detected!\n")
        else:
            print("❄️ No significant heat\n")

        # 🔥 IMPORTANT: slow down reading (prevents crash)
        time.sleep(1)

    except Exception as e:
        print("❌ Runtime error:", e)
        print("🔄 Reinitializing sensor...\n")

        # Reset sensor
        mlx = None
        while mlx is None:
            try:
                mlx = adafruit_mlx90640.MLX90640(i2c)
                mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
                print("✅ Sensor reconnected\n")
            except Exception as e:
                print("❌ Reinit failed:", e)
                time.sleep(2)