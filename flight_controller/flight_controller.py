from drone.flight_controller.imu import IMU
from drone.flight_controller.pid import PID
from drone.flight_controller.esc import ESC


class FlightController:
    """Flight controller for quadcopter."""

    def __init__(self):
        """Initialize variables."""
        self.imu = None
        self.pids = {"yaw": PID(0, 0, 0), "pitch": PID(0, 0, 0), "roll": PID(0, 0, 0)}
        self.pulses = [1000, 1000, 1000, 1000]
        self.commands = {"throttle": 100, "yaw": 0, "pitch": 0, "roll": 0}
        self.escs = [None, None, None, None]
        self.flying = False
        self.flying_threshold = 1100

    def setup(self):
        """Common setup wrapper.

        Initialize IMU and the ESCs.
        """
        self._initialize_imu()
        self._initialize_escs()

    def loop(self, queue):
        """Flight loop.

        At each loop update orientation, read commands, calculate errors, PIDs 
        and pulses, and last send the pulses to the ESCs.
        
        Use multiprocessing.Queue to receive commands.

        Parameters
        ----------
        queue : multiprocessing.Queue
        """
        while True:
            self.imu.update_orientation()
            if not queue.empty():
                data = queue.get()
                if "command" in data:
                    self._parse_commands(data["command"])
            if self.flying:
                self._calculate_errors()
                self._calculate_pids()
            self._calculate_pulses()
            self._send_pulses()

    def _parse_commands(self, commands):
        """Handle inputted commands.

        Parse the commands and set the flying status. If throttle is set to 
        greater than 1100, then it is assumed that the drone is airborne.

        Throttle's value stays intact.

        Yaw is linearly transformed to between -90 and 90 corresponding to
        angular speeds in deg/s
        
        Roll is linearly transformed to between -30 and 30 corresponding to 
        orientation in the roll axis.

        Pitch is linearly transformed to between -30 and 30 corresponding to 
        orientation in the pitch axis.

        Parameters
        ----------
        commands : dict
            The keys can be throttle, yaw, pitch and/or roll. The values need
            to be in range 1000-2000.
        """
        for key, value in commands.items():
            if key == "yaw":
                self.commands[key] = -90 + (value - 1000) * 180 / 1000
            elif key == "roll":
                self.commands[key] = -30 + (value - 1000) * 60 / 1000
            elif key == "pitch":
                self.commands[key] = -30 + (value - 1000) * 60 / 1000
        if self.commands["throttle"] > self.flying_threshold:
            self.flying = True
        else:
            self.flying = False

    def _initialize_imu(self):
        """Connect and calibrate the inertial measurement unit."""
        self.imu = IMU()
        self.imu.calibrate()

    def _initialize_escs(self, front_left_pin=18, front_right_pin=24,
                        back_right_pin=12, back_left_pin=13):
        """Initialize the electronic speed controllers.

        Sets the pulsewidths to 1000 which initializes the escs. Assuming that
        the escs have went through the first time initialization.

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
        self.escs = [ESC(front_left_pin), ESC(front_right_pin),
                     ESC(back_right_pin), ESC(back_left_pin)]
        for esc in self.escs:
            esc.set_pulsewidth(1000)

    def _calculate_errors(self):
        """Calculate the errors based on commands and IMU."""
        self.errors["yaw"] = self.commands["yaw"] - self.imu.yaw
        self.errors["pitch"] = self.commands["pitch"] - self.imu.pitch
        self.errors["roll"] = self.commands["roll"] - self.imu.roll

    def _calculate_pids(self):
        """Calculate the PID values.

        The PID is calculated for each yaw, pitch and roll individually.
        """
        self.errors["yaw"] = self.commands["yaw"] - self.imu.yaw
        self.errors["pitch"] = self.commands["pitch"] - self.imu.pitch
        self.errors["roll"] = self.commands["roll"] - self.imu.roll
        for pid in self.pids:
            pids[pid].calculate()

    def _calculate_pulses(self):
        """Calculate the pulses to be send to the escs.
        
        Uses the PID to calculate the pulsewidths.
        """
        self.pulses[0] = (self.commands["throttle"] + self.pids["roll"]
                          + self.pids["pitch"] - self.pids["yaw"])
        self.pulses[1] = (self.commands["throttle"] - self.pids["roll"] 
                          + self.pids["pitch"] + self.pids["yaw"])
        self.pulses[2] = (self.commands["throttle"] - self.pids["roll"] 
                          - self.pids["pitch"] - self.pids["yaw"])
        self.pulses[3] = (self.commands["throttle"] + self.pids["roll"] 
                          - self.pids["pitch"] + self.pids["yaw"])

    def _send_pulses(self):
        """Change pulsewidths for the escs."""
        for i in range(4):
            self.escs[i].set_pulsewidth(self.pulses[i])
