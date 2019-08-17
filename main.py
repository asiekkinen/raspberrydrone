import subprocess
import re
import multiprocessing as mp
from time import sleep
from drone.flight_controller.flight_controller import FlightController
import drone.web.server as server


class Drone:
    def __init__(self):
        self.message_queue = mp.Queue()
        self.flight_controller = FlightController()
        self.server_process = None
        self.flight_controller_process = None

    def setup(self):
        server.QUEUE = self.message_queue
        self.server_process = mp.Process(target=server.APP.run,
                                         args=("0.0.0.0", 8080))
        self.server_process.start()
        while True:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                if message["alive"] == True:
                    fc = FlightController()
                    fc.setup()
                    self.flight_controller_process = mp.Process(
                        target=fc.loop, args=(self.message_queue, ))
                    self.flight_controller_process.start()
                    return
                else:
                    print(message)
                    raise AssertionError("Got incorrect start message.")
            sleep(1)

    def loop(self):
        while True:
            if not self.flight_controller_process.is_alive():
                raise AssertionError("Flight controller stopped")
            elif not self.server_process.is_alive():
                raise AssertionError("Web server stopped")
            sleep(1)

    def teardown(self):
        output = str(subprocess.Popen("ps ax | grep pigpiod", shell=True, stdout=subprocess.PIPE).stdout.read())
        pid = re.search(r"[0-9]+", output).group(0)
        subprocess.Popen("sudo kill {}".format(pid), shell=True)
        try:
            self.flight_controller_process.terminate()
        except Exception as e:
            print(e)
        try:
            self.server_process.terminate()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    drone = Drone()
    try:
        drone.setup()
        drone.loop()
    except Exception as e:
        print(e)
    finally:
        drone.teardown()
