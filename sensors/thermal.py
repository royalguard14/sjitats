import board
import busio
import adafruit_mlx90640
import numpy as np
import time

class ThermalSensor:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.init_sensor()

        self.frame = [0] * 768
        self.skip_frames = 5
        self.count = 0
        self.last_read_time = 0

    def init_sensor(self):
        try:
            self.mlx = adafruit_mlx90640.MLX90640(self.i2c)
            self.mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
            print("🔥 Thermal sensor initialized")
        except Exception as e:
            print("❌ Init error:", e)
            self.mlx = None

    def detect_heat(self):
        try:
            # 🔥 LIMIT READ SPEED (VERY IMPORTANT)
            if time.time() - self.last_read_time < 1:
                return False

            self.last_read_time = time.time()

            if self.mlx is None:
                self.init_sensor()
                return False

            self.mlx.getFrame(self.frame)

            # Skip unstable startup frames
            if self.count < self.skip_frames:
                self.count += 1
                return False

            data = np.array(self.frame)
            max_temp = np.max(data)

            print(f"🌡 Thermal max: {max_temp:.2f}°C")

            if max_temp > 28:
                return True

            return False

        except Exception as e:
            print("❌ Thermal error:", e)

            # 🔥 AUTO RECOVER
            self.mlx = None
            time.sleep(0.5)

            return False