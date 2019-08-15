import subprocess
import re
import multiprocessing as mp
from drone.flight_controller.flight_controller import FlightController
import drone.wifi_access_point as wifiap
import drone.web.server as server


class Drone:
    def __init__(self):
        self.controller = server.app
        self.flight_controller = FlightController()
        
    def setup(self):
        wifiap.start_access_point()

    def run(self):
        self.controller.run("0.0.0.0", 5000)

    def teardown(self):
        """Kills the pigpiod daemon and this in turn cuts the power to the escs."""
        output = str(subprocess.Popen("ps ax | grep pigpiod", shell=True, stdout=subprocess.PIPE).stdout.read())
        pid = re.search(r"[0-9]+", output).group(0)
        subprocess.Popen("sudo kill {}".format(pid), shell=True)
        wifiap.stop_access_point()


if __name__ == "__main__":
    drone = Drone()
    try:
        drone.setup()
        drone.run()
    except Exception as e:
        print(e)
    finally:
        drone.teardown()
