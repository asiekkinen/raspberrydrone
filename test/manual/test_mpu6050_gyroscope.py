from drone.flight_controller.mpu6050 import MPU6050


def gyroscope():
    module = MPU6050()
    module.setup()
    while True:
        gx, gy, gz = module.get_gyroscope_measurement()
        print("X: {:7.4f} Y: {:7.4f} Z: {:7.4f}".format(gx, gy, gz))



if __name__ == "__main__":
    gyroscope()
