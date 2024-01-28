import time
from controller.utility import func_log

"""
This area is for custom functions.
"""


@func_log
# def make_base_info(dftmux_xls):
def make_base_info(*args, **kwargs):
    # print_dict(kwargs)
    time.sleep(0.5)
    pass


@func_log
# def make_tmode_info(signal_xls):
def make_tmode_info(*args, **kwargs):
    # print_dict(kwargs)
    time.sleep(0.5)
    pass


@func_log
# def make_tb(output_path):
def make_tb(*args, **kwargs):
    # print_dict(kwargs)
    time.sleep(0.5)
    pass


@func_log
# def make_atp(eds_path):
def make_atp(*args, **kwargs):
    # print_dict(kwargs)
    time.sleep(0.5)
    pass


@func_log
def make_cfg(*args, **kwargs):
    try:
        dftmux_xls = kwargs.pop("dftmux_xls")
        print(f"dftmux_xls file is {dftmux_xls}")
    except KeyError:
        print(f"var dftmux_xls is not in input kwargs")
    try:
        eds_path = kwargs.pop("eds_path")
        print(f"eds_path is {eds_path}")
    except KeyError:
        print(f"var eds_path is not in input kwargs")
    mode_sequence = list(kwargs.keys())
    for mode in mode_sequence:
        if kwargs[mode]["main_mode"]:
            print(f"main mode is {mode}!")
    time.sleep(0.5)
    pass
