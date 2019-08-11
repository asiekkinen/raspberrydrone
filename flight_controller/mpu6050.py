import smbus


class MPU6050:
    """Module containing an accelerometer and a gyroscope."""

    # The i2c address of the MPU6050 module.
    i2c_address = 0x68

    # Register addresses.
    # For register specs, see https://www.invensense.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
    PWR_MGMT_1 = 0x6B
    ACCEL_CONFIG = 0x1B
    GYRO_CONFIG = 0x1C
    
    ACCEL_XOUT_H = 0x3B
    ACCEL_XOUT_L = 0x3C
    ACCEL_YOUT_H = 0x3D
    ACCEL_YOUT_L = 0x3E
    ACCEL_ZOUT_H = 0x3F
    ACCEL_ZOUT_L = 0x40

    GYRO_XOUT_H = 0x43
    GYRO_XOUT_L = 0x44
    GYRO_YOUT_H = 0x45
    GYRO_YOUT_L = 0x46
    GYRO_ZOUT_H = 0x47
    GYRO_ZOUT_L = 0x48
    
    def __init__(self, bus=1):
        self.bus = smbus.SMBus(bus)
        self.accelerometer_scale_factor = None
        self.gyroscope_scale_factor = None

    def setup(self):
        """Common setup routine for the module.

        Turns on the power and configures the accelerometer and gyroscope.
        """
        self.bus.write_byte_data(self.i2c_address, self.PWR_MGMT_1, 0x00)
        self.setup_accelerometer()
        self.setup_gyroscope()

    def setup_accelerometer(self):
        """Initialize accelerometer registers."""
        self.bus.write_byte_data(self.i2c_address, self.ACCEL_CONFIG, 0b00000000)
        self.accelerometer_scale_factor = 16384.0

    def setup_gyroscope(self):
        """Initialize gyroscope registers."""
        self.bus.write_byte_data(self.i2c_address, self.GYRO_CONFIG, 0b00000000)
        self.gyroscope_scale_factor = 131.0

    def get_accelerometer_measurement(self):
        """Get accelerations for each axis

        Returns
        -------
        tuple of floats
            Accelerations for x, y and z in the given order
        """
        raw_x, raw_y, raw_z = self._read_accelerometer_registers()
        x = raw_x / self.accelerometer_scale_factor
        y = raw_y / self.accelerometer_scale_factor
        z = raw_z / self.accelerometer_scale_factor
        return x, y, z

    def get_gyroscope_measurement(self):
        """Get angular speeds around each axis.

        Returns
        -------
        tuple of floats
            Angular speeds around x, y and z in the given order
        """
        raw_x, raw_y, raw_z = self._read_gyroscope_registers()
        x = raw_x / self.gyroscope_scale_factor
        y = raw_y / self.gyroscope_scale_factor
        z = raw_z / self.gyroscope_scale_factor
        return x, y, z

    def _read_accelerometer_registers(self):
        x = self._read_word_2c(self.ACCEL_XOUT_H)
        y = self._read_word_2c(self.ACCEL_YOUT_H)
        z = self._read_word_2c(self.ACCEL_ZOUT_H)
        return x, y, z

    def _read_gyroscope_registers(self):
        x = self._read_word_2c(self.GYRO_XOUT_H)
        y = self._read_word_2c(self.GYRO_YOUT_H)
        z = self._read_word_2c(self.GYRO_ZOUT_H)
        return x, y, z

    def _read_word_2c(self, register):
        high, low = self.bus.read_i2c_block_data(self.i2c_address, register, 2)
        value = high << 8 | low
        if value >= 0x8000:
            return -((65535 - value) + 1)
        return value
