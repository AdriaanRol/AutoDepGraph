# Module that contains the calibration functions of the nodes.
import time


def test_calibration_True():
    '''
    Dummy calibration function for test cases. Always returns True.
    '''
    return True


def test_calibration_True_delayed(delay=.5):
    '''
    Dummy calibration function for test cases. Always returns True.
    '''
    time.sleep(delay)
    return True


def test_calibration_False():
    '''
    Dummy calibration function for test cases. Always returns False.
    '''
    return False


def NotImplementedCalibration():
    raise NotImplementedError('Calibration not implemented')
