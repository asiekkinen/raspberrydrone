from drone.flight_controller.mpu6050 import MPU6050
import time
from math import sin, pi, sqrt, atan2, fabs, copysign, asin


class IMU:
    """Inertial measurement unit.

    Module for figuring the current orientation.
    """
    def __init__(self):
        self.roll = None
        self.pitch = None
        self.yaw = None
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.gyroscope_offsets = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.time_of_previous_measurement = None
        self.mpu6050 = MPU6050()
        self.mpu6050.setup()

    def calibrate(self, n=2000):
        """Calculate the offsets for gyroscope.

        The offset is calculated using the average of the measurements.

        Parameters
        ----------
        n : int
            Number of measurements of which the average is taken.
        """
        gyroscope_sums = [0.0, 0.0, 0.0]
        for _ in range(n):
            gx, gy, gz = self.mpu6050.get_gyroscope_measurement()
            gyroscope_sums[0] += gx
            gyroscope_sums[1] += gy
            gyroscope_sums[2] += gz
        self.time_of_previous_measurement = time.time()
        self.gyroscope_offsets["x"] = gyroscope_sums[0] / n
        self.gyroscope_offsets["y"] = gyroscope_sums[1] / n
        self.gyroscope_offsets["z"] = gyroscope_sums[2] / n

    def update_orientation(self, beta=100):
        """Use Madgwick's filter to calculate the orientation.

        The implementation is copied from https://github.com/arduino-libraries/MadgwickAHRS/blob/master/src/MadgwickAHRS.cpp
        and translated to python.

        Parameters
        ----------
        beta : float (default 100)
            Hyperparameter to be used in the calculations of Madgwick's filter.
            The default value has been set to 100, because that value seemed to
            work fairly well. The only problem is that the module is flipped
            upside down, then the orientation is oscillates badly. But this is 
            okay for now.
        """
        # Calculate the time between measurements
        # TODO: The frequency in which the MPU6050 does measurements might
        #       affect the time interval in a wrong way, investigate this more.
        now = time.time()
        time_interval = now - self.time_of_previous_measurement
        self.time_of_previous_measurement = now

        # Get measurements
        gx, gy, gz = self.mpu6050.get_gyroscope_measurement()
        ax, ay, az = self.mpu6050.get_accelerometer_measurement()

        # Substract the offsets
        gx -= self.gyroscope_offsets["x"]
        gy -= self.gyroscope_offsets["y"]
        gz -= self.gyroscope_offsets["z"]

        # convert degrees/sec to radians/sec
        gx *= pi / 180
        gy *= pi / 180
        gz *= pi / 180

        # Rate of change of quaternion from gyroscope
        qDot1 = 0.5 * (-self.q1 * gx - self.q2 * gy - self.q3 * gz)
        qDot2 = 0.5 * (self.q0 * gx + self.q2 * gz - self.q3 * gy)
        qDot3 = 0.5 * (self.q0 * gy - self.q1 * gz + self.q3 * gx)
        qDot4 = 0.5 * (self.q0 * gz + self.q1 * gy - self.q2 * gx)

        # Normalise accelerometer measurement
        recip_norm = 1.0 / sqrt(ax * ax + ay * ay + az * az)
        ax *= recip_norm
        ay *= recip_norm
        az *= recip_norm

        # Auxiliary variables to avoid repeated arithmetic
        _2q0 = 2.0 * self.q0
        _2q1 = 2.0 * self.q1
        _2q2 = 2.0 * self.q2
        _2q3 = 2.0 * self.q3
        _4q0 = 4.0 * self.q0
        _4q1 = 4.0 * self.q1
        _4q2 = 4.0 * self.q2
        _8q1 = 8.0 * self.q1
        _8q2 = 8.0 * self.q2
        q0q0 = self.q0 ** 2
        q1q1 = self.q1 ** 2
        q2q2 = self.q2 ** 2
        q3q3 = self.q3 ** 2

        # Gradient decent algorithm corrective step
        s0 = _4q0 * q2q2 + _2q2 * ax + _4q0 * q1q1 - _2q1 * ay;
        s1 = _4q1 * q3q3 - _2q3 * ax + 4.0 * q0q0 * self.q1 - _2q0 * ay - _4q1 + _8q1 * q1q1 + _8q1 * q2q2 + _4q1 * az
        s2 = 4.0 * q0q0 * self.q2 + _2q0 * ax + _4q2 * q3q3 - _2q3 * ay - _4q2 + _8q2 * q1q1 + _8q2 * q2q2 + _4q2 * az
        s3 = 4.0 * q1q1 * self.q3 - _2q1 * ax + 4.0 * q2q2 * self.q3 - _2q2 * ay
        recip_norm = 1.0 / sqrt(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3)  # normalise step magnitude
        s0 *= recip_norm
        s1 *= recip_norm
        s2 *= recip_norm
        s3 *= recip_norm

        # Apply feedback step
        qDot1 -= beta * s0;
        qDot2 -= beta * s1;
        qDot3 -= beta * s2;
        qDot4 -= beta * s3;

        # Integrate rate of change of quaternion to yield quaternion
        self.q0 += qDot1 / time_interval
        self.q1 += qDot2 / time_interval
        self.q2 += qDot3 / time_interval
        self.q3 += qDot4 / time_interval

        # Normalise quaternion
        recip_norm = 1.0 / sqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3);
        self.q0 *= recip_norm;
        self.q1 *= recip_norm;
        self.q2 *= recip_norm;
        self.q3 *= recip_norm;

        # roll (x-axis rotation)
        sinr_cosp = 2.0 * (self.q0 * self.q1 + self.q2 * self.q3)
        cosr_cosp = 1.0 - 2.0 * (self.q1 * self.q1 + self.q2 * self.q2)
        self.roll = atan2(sinr_cosp, cosr_cosp)
        if self.roll < 0:
            self.roll += pi
        else:
            self.roll -= pi
        
        # pitch (y-axis rotation)
        sinp = 2.0 * (self.q0 * self.q2 - self.q3 * self.q1)
        if fabs(sinp) >= 1:
            self.pitch = copysign(pi / 2, sinp) #  Use 90 degrees if out of range
        else:
            self.pitch = asin(sinp)
        
        # yaw (z-axis rotation)
        siny_cosp = 2.0 * (self.q0 * self.q3 + self.q1 * self.q2)
        cosy_cosp = 1.0 - 2.0 * (self.q2 * self.q2 + self.q3 * self.q3)  
        self.yaw = atan2(siny_cosp, cosy_cosp)
        return self.yaw, self.pitch, self.roll

    def __repr__(self):
        return ("yaw: {:10.4f}, pitch: {:10.4f}, roll: {:10.4f}"
                .format(self.yaw * 180 / pi, self.pitch * 180 / pi,
                        self.roll * 180 / pi))
