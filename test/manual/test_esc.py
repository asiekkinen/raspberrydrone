from drone.flight_controller.esc import ESC
from time import sleep


# The GPIO pins that are used for the escs.
PINS = [12, 13, 18, 24]


def test():
    module = ESC(24)
    while True:
        value = int(input("Pulsewidth: "))
        module.set_pulsewidth(value)


if __name__ == "__main__":
    test()
