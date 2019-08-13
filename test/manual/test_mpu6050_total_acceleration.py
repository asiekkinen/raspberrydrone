from drone.flight_controller.mpu6050 import MPU6050
from math import sqrt


def total_acceleration():
    module = MPU6050()
    module.setup()
    while True:
        ax, ay, az = module.get_accelerometer_measurement()
        total = sqrt(ax ** 2 + ay ** 2 + az ** 2)
        print("{:6.4f}".format(total))    


if __name__ == "__main__":
    total_acceleration()
