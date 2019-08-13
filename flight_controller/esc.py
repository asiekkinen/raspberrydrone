import pigpio
from time import sleep


class ESC:
    """Electronic Speed Controller.

    Use PWM to control the esc which controls a motor.

    A good tutorial on using PWM is at 
    https://www.teachmemicro.com/raspberry-pi-pwm-servo-tutorial/
    """

    min_value = 1000
    max_value = 2000

    def __init__(self, gpio_pin):
        """Initialize variables.

        Parameters
        ----------
        gpio_pin : int
            The pin in which the esc is attached to. The pin number is in the 
            name of the pin and not the index. For the pin layout see https://pinout.xyz/
        """
        self.pi = pigpio.pi()
        self.gpio_pin = gpio_pin

    def set_pulsewidth(self, pulsewidth):
        """Set the speed of a motor.

        The pulsewidth will be restricted between 1000 and 1900.

        Parameters
        ----------
        pulsewidth : int
            Pulsewidth in microseconds.
        """
        if pulsewidth > self.max_value:
            pulsewidth = 1900
        elif pulsewidth < self.min_value:
            pulsewidth = 1000
        self.pi.set_servo_pulsewidth(self.gpio_pin, pulsewidth)

    def initialize(self):
        """Initialize the electronic speed controllers.

        Following the guide from https://www.motionrc.com/blogs/motion-rc-blog/are-you-initializing-your-esc
        and according to the guide this should be run only once and not at the 
        start of every flight.
        """
        raise NotImplementedError("Is not tested properly.")
