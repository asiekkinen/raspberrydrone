import subprocess
from time import sleep

from drone.flight_controller.imu import IMU
from drone.flight_controller.pid import PID
from drone.flight_controller.esc import ESC


class FlightController:
    """Flight controller for quadcopter.

    The motors are indexed as follows
    0   1
     \ /
      |
     / \
    3   2
    """

    _min_roll = -30  # angle in degrees
    _max_roll = 30  # angle in degrees
    _min_pitch = -30  # angle in degrees
    _max_pich = 30  # angle in degrees
    _min_yaw = -90  # angular speed in degrees/sec
    _max_yaw = 90  # angular speed in degrees/sec

    # If throttle is set to higher than this value, then it is assumed that
    # the drone is flying and the PID values are calculated.
    _flying_threshold = 1100

    def __init__(self):
        self._imu = None
        self._errors = {"yaw": None, "pitch": None, "roll": None}
        self._pids = {"yaw": PID(0, 0, 0), "pitch": PID(0, 0, 0), "roll": PID(0, 0, 0)}
        self._pulses = [1000, 1000, 1000, 1000]
        self._commands = {"throttle": 100, "yaw": 0, "pitch": 0, "roll": 0}
        self._escs = [None, None, None, None]
        self._flying = False

    def setup(self):
        """Common setup wrapper.

        Initialize the inertial measurement unit and the electronic speed
        controllers.
        """
        self._initialize_imu()
        self._initialize_escs()

    def loop(self, queue):
        """Flight loop.

        At each loop update orientation, read commands, calculate errors, PIDs
        and pulses, and last send the pulses to the ESCs.

        Use multiprocessing.Queue to receive commands. If there are no commands
        recieved for a while, then it is assumed that something is wrong and an
        error is raised.

        Parameters
        ----------
        queue : multiprocessing.Queue
        """
        no_message_counter = 0
        while True:
            self._imu.update_orientation()
            if not queue.empty():
                no_message_counter = 0
                data = queue.get()
                if "alive" in data:
                    if data["alive"] == False:
                        print("Shutting down")
                        return
                if "command" in data:
                    self._parse_commands(data["command"])
            else:
                no_message_counter += 1
                if no_message_counter > 1000:
                    raise AssertionError("No message received in 1000 epochs")
            if self._flying:
                self._calculate_pids()
            else:
                for pid in self._pids:
                    self._pids[pid].pid = 0
            self._calculate_pulses()
            self._send_pulses()

    def _parse_commands(self, commands):
        """Handle inputted commands.

        Parse the commands and set the flying status. If throttle is set to
        greater than 1100, then it is assumed that the drone is airborne.

        Throttle's value stays intact.

        Yaw is linearly transformed to between self._min_yaw and self._max_yaw
        corresponding to angular speeds in deg/s

        Roll is linearly transformed to between self._min_roll and
        self._max_roll corresponding to orientation in the roll axis.

        Pitch is linearly transformed to between self._min_pitch and
        self._max_pitch corresponding to orientation in the pitch axis.

        Parameters
        ----------
        commands : dict
            The keys can be throttle, yaw, pitch and/or roll. The values need
            to be in range 1000-2000.
        """
        for key, value in commands.items():
            if key == "yaw":
                self._commands[key] = -90 + (value - 1000) * 180 / 1000
            elif key == "roll":
                self._commands[key] = -30 + (value - 1000) * 60 / 1000
            elif key == "pitch":
                self._commands[key] = -30 + (value - 1000) * 60 / 1000
            elif key == "throttle":
                self._commands[key] = value
        if self._commands["throttle"] > self._flying_threshold:
            self._flying = True
        else:
            self._flying = False

    def _initialize_imu(self):
        """Connect and calibrate the inertial measurement unit."""
        self._imu = IMU()
        self._imu.calibrate()

    def _initialize_escs(self, front_left_pin=18, front_right_pin=24,
                        back_right_pin=12, back_left_pin=13):
        """Initialize the electronic speed controllers.

        Sets the pulsewidths to 1000 which initializes the escs. Assuming that
        the escs have went through the first time initialization.

        Starts the pigpiod daemon.

        Parameters
        ----------
        front_left_pin : int
            The front left motor's gpio pin in the raspberry pi
        front_right_pin : int
            The front right motor's gpio pin in the raspberry pi
        back_right_pin : int
            The back right motor's gpio pin in the raspberry pi
        back_left_pin : int
            The back left motor's gpio pin in the raspberry pi
        """
        subprocess.Popen("sudo pigpiod", shell=True)
        sleep(2)
        self._escs = [ESC(front_left_pin), ESC(front_right_pin),
                     ESC(back_right_pin), ESC(back_left_pin)]
        for esc in self._escs:
            esc.set_pulsewidth(1000)

    def _calculate_pids(self):
        """Calculate the PID values.

        The PID is calculated for each yaw, pitch and roll individually.
        """
        self._errors["yaw"] = self._commands["yaw"] - self._imu.yaw
        self._errors["pitch"] = self._commands["pitch"] - self._imu.pitch
        self._errors["roll"] = self._commands["roll"] - self._imu.roll
        for pid in self._pids:
            self._pids[pid].calculate(self._errors[pid])

    def _calculate_pulses(self):
        """Calculate the pulses to be send to the escs.

        Uses the PID to calculate the pulsewidths.
        """
        self._pulses[0] = int(self._commands["throttle"] + self._pids["roll"].pid
                             + self._pids["pitch"].pid - self._pids["yaw"].pid)
        self._pulses[1] = int(self._commands["throttle"] - self._pids["roll"].pid
                             + self._pids["pitch"].pid + self._pids["yaw"].pid)
        self._pulses[2] = int(self._commands["throttle"] - self._pids["roll"].pid
                             - self._pids["pitch"].pid - self._pids["yaw"].pid)
        self._pulses[3] = int(self._commands["throttle"] + self._pids["roll"].pid
                             - self._pids["pitch"].pid + self._pids["yaw"].pid)

    def _send_pulses(self):
        """Change pulsewidths for the escs."""
        for i in range(4):
            self._escs[i].set_pulsewidth(self._pulses[i])
