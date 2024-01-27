import time
from utility_logging import func_log, print_dict


@func_log
# def make_base_info(dftmux_xls):
def make_base_info(**data):
    # print_dict(data)
    time.sleep(0.5)
    pass


@func_log
# def make_tmode_info(signal_xls):
def make_tmode_info(**data):
    # print_dict(data)
    time.sleep(0.5)
    pass


@func_log
# def make_tb(output_path):
def make_tb(**data):
    # print_dict(data)
    time.sleep(0.5)
    pass


@func_log
# def make_atp(eds_path):
def make_atp(**data):
    # print_dict(data)
    time.sleep(0.5)
    pass


@func_log
def make_cfg(**data):
    try:
        dftmux_xls = data.pop("dftmux_xls")
        print(f"dftmux_xls file is {dftmux_xls}")
    except KeyError:
        print(f"var dftmux_xls is not in input data")
    try:
        eds_path = data.pop("eds_path")
        print(f"eds_path is {eds_path}")
    except KeyError:
        print(f"var eds_path is not in input data")
    mode_sequence = list(data.keys())
    for mode in mode_sequence:
        if data[mode]["main_mode"]:
            print(f"main mode is {mode}!")
    time.sleep(0.5)
    pass
