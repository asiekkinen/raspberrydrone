from drone.flight_controller.imu import IMU


def orientation():
    module = IMU()
    module.calibrate()
    while True:
        module.update_orientation()
        print(module)


if __name__ == "__main__":
    orientation()
