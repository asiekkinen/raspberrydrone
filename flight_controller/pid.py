class PID:
    """Proportional, Integral and Derivative controller.

    PID is an algorithm used to calculate actions for given state.
    """
    def __init__(self, p, i, d):
        """Initialize variables.

        Parameters
        ----------
        p : float
        i : float
        d : float
        """
        self.p = p
        self.i = i
        self.d = d
        self._error_sum = 0.0
        self._previous_error = 0.0

    def calculate(self, error):
        """Calculate the actions to be done.

        Parameters
        ----------
        error : float
            Error between measurement and wanted action.

        Returns
        -------
        float
            Value of the PID calculation.
        """
        # I
        self._error_sum += error
        
        # D
        delta_error = error - self._previous_error
        self._previous_error = error
        
        # PID
        return (error * self.p) + (self._error_sum * self.i) + (delta_error * self.d)
