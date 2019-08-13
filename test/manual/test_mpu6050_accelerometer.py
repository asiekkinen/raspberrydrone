from drone.flight_controller.mpu6050 import MPU6050


def accelerometer():
    module = MPU6050()
    module.setup()
    while True:
        ax, ay, az = module.get_accelerometer_measurement()
        print("X: {:7.4f} Y: {:7.4f} Z: {:7.4f}".format(ax, ay, az))


if __name__ == "__main__":
    accelerometer()
