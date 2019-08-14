from gpiozero import MCP3008


class VoltageMeter:
    """Voltage meter using MCP3008 as an analog to digital converter."""
    def __init__(self):
        self.adc = MCP3008(channel=0, device=0)

    def get_measurement(self):
        """Get measurement from the analog to digital converter.

        Returns
        -------
        int 
            Integer between 0-1023, where 0 corresponds to 0 volts and 1023 
            corresponds to 3.3 volts.
        """
        return self.adc.value
