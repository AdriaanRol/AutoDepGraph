"""
This is a
"""

def task_example():
    return {
        'actions': [find_resonator],
        # passing the python object here this can be customized to find a function with a name
        'task_dep': ['my_input_file'],
        'targets': ['result_file'],
    }


def task_RB_experiment():
    """
    """
    return {
        'actions': [RB_experiment],
        'task_dep': ['my_input_file'],
        'targets': ['result_file'],
    }


def task_RB_experiment():
    """
    """
    return {
        'actions': ['find_resonator'],
        'file_dep': ['my_input_file'],
        'targets': ['result_file'],
    }


def find_resonator():
    """
    """
    return 7.1e9


def find_qubit_frequency():
    return 5.4e9

def find_qubit_frequency_fine():
    return 5.43452e9

def find_pulse_amp_rabi():
    return .42
