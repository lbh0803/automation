import logging
import os
import subprocess
import threading
import time
from collections import defaultdict
from multiprocessing import Process

import pandas as pd

from controller.utility import func_log, monitor_thread
from model.data import DataModel

"""
This area is for custom functions.
"""
"""
Template dictionary for add_config_data function
"""
ADD_TEMPLATES = {
    "io_define": "{step}       {direction} {pin}; {{{signal}}}\n",
    "delete_pin": "{step}       DELETE_PINS {pin};\n",
    "bi_control": "{step}       BIDIRECT_CONTROL {pad} = OUTPUT WHEN {pin} = 1;{{{signal}}}\n",
    "mask_pin": "{step}       MASK_PINS {pad_condition} {pin_condition}; {{{signal}}}\n",
    "alias_pin": "{step}       ALIAS {signal} = {pad};\n"
}
"""
Template dictionary for merge_config_data function
"""
MERGE_TEMPLATES = {
    "pin_type": "{step}    {data}\n",
    "io_define": "{step}    INPUTS {data};\n",
    "more_info": "{step}    {data}\n",
    "add_pin": "{step}    {data}\n",
    "delete_pin": "{step}    {data}\n",
    "mask_pin": "{step}    {data}\n",
    "alias_pin": "{step}    {data}\n"
}


@func_log
def make_base_info(*args, **kwargs):
    """
    This makes dataframe from dftmux excel sheet
    """
    dftmux_excel = args[0][0]
    try:
        df = pd.read_excel(dftmux_excel, sheet_name=0, header=None)
        df.fillna("N/A", inplace=True)
        r_idx = (df != "N/A").any(axis=1).idxmax()
        c_idx = (df != "N/A").any(axis=0).idxmax()
        df = df.iloc[r_idx:, c_idx:]
        callback = kwargs.get("callback", None)
        base_info = kwargs.get("base_info", None)
        make_mode_info(df, base_info, callback)
        base_info.show_all()
        logging.info("Get Dataframe, Success!")
    except Exception as e:
        logging.error(f"Error occured while making base_info: {e}")


def make_mode_info(df, mode_info, callback):
    """
    This makes base mode information from dataframe
    """
    row_size, column_size = df.shape
    skip_list = ["SCAN", "BIST", "JTAG", "IO", "FAKE"]
    for c_idx in range(column_size):
        callback(10000 / (column_size-1))
        time.sleep(0.1)
        if "TEST_MODE" not in df.iloc[0, c_idx]:
            continue
        skip = 0
        mode_name = df.iloc[0, c_idx]
        for mode in skip_list:
            if mode in mode_name:
                skip = 1
                break
        if skip:
            continue
        for r_idx in range(2, row_size):
            if df.iloc[r_idx, c_idx] == "N/A":
                continue
            pad_name = df.iloc[r_idx, 4].strip()
            signal_name = df.iloc[r_idx, c_idx].strip()
            direction = df.iloc[r_idx, c_idx + 1].strip()
            hierarchy = df.iloc[r_idx, c_idx + 6].strip()
            mode_info.set_data(mode_name + "." + pad_name + ".signal", signal_name)
            if direction == "B":
                if "JTAG_TDO" in signal_name:
                    direction = "O"
                else:
                    direction = "I"
            mode_info.set_data(mode_name + "." + pad_name + ".direction", direction)
            if ":" in hierarchy:
                hierarchy = hierarchy.split(":")[1].split("/")[0]
            mode_info.set_data(mode_name + "." + pad_name + ".hierarchy", hierarchy)


@func_log
def make_tb(*args, **kwargs):
    time.sleep(0.5)
    pass


def make_signal_info(signal_excel):
    df = pd.read_excel(signal_excel, sheet_name = 0, header=None)
    df.fillna("N/A", inplace=True)
    idx = (df != "N/A").any(axis=1).idxmax()
    df = df.iloc[idx:]
    signal_info = DataModel("SIGNAL") #$mode_name.$signal_name.value
    path_info = DataModel("")
    row_size, column_size = df.shape


@func_log
def make_cfg(*args, **kwargs):
    """
    This function does refactoring data structure to make config/pin template
    It executes make_templtates function using multithreading
    """
    mode_base_info, basic_info_from_user = args[0], args[1]
    mode_info_from_user = DataModel("MODE")
    try:
        mode_info_from_user.data = basic_info_from_user.data.pop("loop_data")
        logging.info("Mode info : ")
        mode_info_from_user.show_all()
    except KeyError:
        logging.error("No mode informaion")
    main_mode = basic_info_from_user.get_data("main_mode")
    eds_path = basic_info_from_user.get_data("eds_path")
    callback = kwargs.get("callback", None)
    if main_mode not in mode_info_from_user.data:
        logging.error(f"main mode {main_mode} not in selected mode list")
    merge_flag = len(mode_info_from_user.data) > 1
    threads = list()
    add_value = 100 / len(mode_info_from_user.data) * 2
    for mode_name in mode_info_from_user.data:
        thread = threading.Thread(target=make_templates,
                                  args=(mode_name, main_mode, merge_flag, mode_base_info,
                                        mode_info_from_user, basic_info_from_user, eds_path,))
        monitor = threading.Thread(target=monitor_thread,
                                   args=(thread, callback, add_value))
        threads.append(monitor)
        thread.start()
        monitor.start()
    for monitor in threads:
        monitor.join()


def make_templates(mode_name, main_mode, merge_flag, mode_base_info, mode_info_from_user,
                   basic_info_from_user, eds_path):
    """
    Makes thread for pin/config template respectively
    """
    thread1 = threading.Thread(target=make_pin_template,
                               args=(mode_name, main_mode, merge_flag, mode_base_info,
                                     mode_info_from_user, basic_info_from_user, eds_path))
    thread2 = threading.Thread(target=make_config_template,
                               args=(mode_name, main_mode, mode_info_from_user,
                                     basic_info_from_user, eds_path))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def make_pin_template(mode_name, main_mode, merge_flag, mode_base_info, mode_info_from_user, 
                      basic_info_from_user, eds_path):
    """
    This makes pin template file under $EDS/CFG
    """
    mode_setting_pin = ["XTMODE", "XUWB_EN", "XUWB_WAKE", "XCAN_RX"]
    ieee_signal = ["WSI", "SelectWIR", "UpdateWIR", "ShiftWR", "CaptureWR", "WRSTN", "WRCK", "WSO"]
    pad_list = mode_base_info.get_data(mode_name).keys()
    write_list = list()
    for step, step_info_from_user in mode_info_from_user.get_data(mode_name).items():
        config_data = defaultdict(list)
        step = step.lower()
        if "vcd2" in step:
            bidirection_control = step_info_from_user["bidirection_control"]
            cycle = step_info_from_user["cycle"]
            config_data["pin_type"] += [
                f"{step}     CYCLE = {cycle};\n",
                f"{step}     PINTYPE NRZ * @ 0;\n",
                f"{step}     PINTYPE STB * @ {float(cycle) * 0.9};\n",
            ]
            merge_config_data(config_data, "pin_type", step, step_info_from_user["pin_type"])
            merge_config_data(config_data, "io_define", step, mode_setting_pin)
            if bidirection_control != "":
                add_config_data(
                    config_data,
                    "io_define",
                    step=step,
                    direction="INPUTS",
                    pin=bidirection_control,
                )
                add_config_data(config_data, "delete_pin", step=step, pin=bidirection_control)
            for pad in pad_list:
                signal = mode_base_info.get_data(mode_name + "." + pad + ".signal")
                io = mode_base_info.get_data(mode_name + "." + pad + ".direction")
                if merge_flag:
                    add_config_data(
                        config_data, "io_define", step=step, direction="BIDIRECTS", pin=pad, signal=signal)
                    if bidirection_control != "":
                        if io == "I":
                            pass
                            # config_data["bi_control"].append(f"{step}     BIDIRECT_CONTROL {pad} = OUTPUT WHEN {bidirection_control} = 0;")
                        else:
                            add_config_data(config_data, "bi_control", step=step, 
                                            pad=pad, pin=bidirection_control, signal=signal)
                            add_config_data(config_data, "mask_pin", step=step, 
                                            pad=pad, pin=bidirection_control, signal=signal)
                else:
                    if io == "I":
                        add_config_data(config_data, "io_define", step=step, 
                                        direction="INPUTS", pin=pad, signal=signal)
                    else:
                        add_config_data(config_data, "io_define", step=step, 
                                        direction="OUTPUTS", pin=pad, signal=signal)
                        add_config_data(config_data, "mask_pin", step=step, pad=pad, signal=signal)

        elif "wgl2" in step:
            for pad in pad_list:
                signal = mode_base_info.get_data(mode_name + "." + pad + ".signal")
                for ieee in ieee_signal:
                    if ieee in signal:
                        add_config_data(config_data, "alias_pin", step=step, signal=ieee, pad=pad)
                        break

        merge_config_data(config_data, "add_pin", step, step_info_from_user["add_pin"])
        merge_config_data(config_data, "mask_pin", step, step_info_from_user["mask_pin"])
        merge_config_data(config_data, "delete_pin", step, step_info_from_user["delete_pin"])
        merge_config_data(config_data, "alias_pin", step, step_info_from_user["alias_pin"])
        write_list += (config_data["io_define"] + config_data["pin_type"] +
                      config_data["bi_control"] + config_data["add_pin"] + config_data["mask_pin"] +
                      config_data["alias_pin"] + config_data["delete_pin"])

    if mode_name != main_mode:
        new_name = main_mode[10:] + "_" + mode_name[10:]
    else:
        new_name = main_mode[10:]
        merge_config_data(config_data, "more_info", "merge2atp",
                          basic_info_from_user.get_data("more_info"))

    write_list += config_data["more_info"]

    file_path = os.path.join(eds_path, "CFG", new_name, "PIN_CONTROL.cfg")
    write_list_to_file(file_path, write_list)


def make_config_template(mode_name, main_mode, mode_info_from_user, basic_info_from_user, eds_path):
    """
    This makes $mode.cfg file under $EDS/CFG
    """
    config_data = []
    dev = basic_info_from_user.get_data("dev")
    config_data.append(f'HDL_REVISION   {dev}\n')
    if mode_name != main_mode:
        new_name = main_mode[10:] + "_" + mode_name[10:]
    else:
        new_name = main_mode[10:]
        config_data.append(f'REPEAT_THRESHOLD   {basic_info_from_user.get_data("repeat")}\n')
    for step in mode_info_from_user.get_data(mode_name):
        if step == "VCD2WGL":
            config_data.append(
                f'TESTMODE_VCD_SOURCE   {mode_info_from_user.get_data(mode_name + "." + step + ".src_path")}\n'
            )
        if step == "WGL2WGL":
            config_data.append(
                f'IP_WGL_SOURCE   {mode_info_from_user.get_data(mode_name + "." + step + ".src_path")}\n'
            )
    if mode_name == main_mode:
        cnt = 0
        main_vector = None
        run_info = list()
        for mode in mode_info_from_user.data:
            if mode == main_mode:
                sub_name = main_mode[10:]
            else:
                sub_name = main_mode[10:] + "_" + mode[10:]
            run_info.append(f"clean {sub_name}\n")
            run_info.append(f"setup {sub_name}\n")
            if "VCD2WGL" in mode_info_from_user.get_data(mode):
                cnt += 1
                config_data.append(
                    f"IP_TOP_WGL{cnt}_SOURCE    {eds_path}/OUTPUT/{sub_name}/{dev}/TESTMODE_WGL\n")
                run_info.append(f"vcd2wgl {sub_name}\n")
                if mode_info_from_user.get_data(mode + ".VCD2WGL.main_step"):
                    main_vector = cnt
            if "WGL2WGL" in mode_info_from_user.get_data(mode):
                cnt += 1
                config_data.append(
                    f"IP_TOP_WGL{cnt}_SOURCE    {eds_path}/OUTPUT/{sub_name}/{dev}/IP_TOP_WGL\n")
                run_info.append(f"wgl2wgl {sub_name}\n")
                if mode_info_from_user.get_data(mode + ".WGL2WGL.main_step"):
                    main_vector = cnt
        run_info.append(f"merge2atp {main_mode[10:]}\n")
        file_path = os.path.join(eds_path, "CFG", mode_name[10:], "run_list.txt")
        write_list_to_file(file_path, run_info)

        config_data.append(f"WGL_NUM    {cnt}\n")
        config_data.append(f"MAIN_WGL   {main_vector}\n")
        config_data.append(f"EXPORT_DIR     {basic_info_from_user.get_data('export')}\n")
    file_path = os.path.join(eds_path, "CFG", new_name, f"{new_name}.cfg")
    write_list_to_file(file_path, config_data)


def merge_config_data(config_data, key, step, data_list):
    """
    This merges list data to config_data[key]
    """
    str_format = MERGE_TEMPLATES[key]
    config_data[key] += [
        str_format.format(step=step, data=data) for data in data_list if data != ""
    ]


def add_config_data(config_data, key, step=None, direction=None, pin=None, pad=None, signal=None):
    """
    This adds data to config_data[key]
    """
    if key == "mask_pin":
        pad_condition = f'{pad}.O  @CONDITION' if pin else pad
        pin_condition = f'{pin} = 1' if pin else "@0, 9999999999"
        str_format = ADD_TEMPLATES[key].format(step=step,
                                               pad_condition=pad_condition,
                                               pin_condition=pin_condition,
                                               signal=signal)
    else:
        str_format = ADD_TEMPLATES[key].format(step=step,
                                               direction=direction,
                                               pin=pin,
                                               signal=signal,
                                               pad=pad)
    config_data[key].append(str_format)


def create_directory(file_path):
    """
    This makes directory path for file_path
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def write_list_to_file(file_path, write_list):
    """
    Write list data to file_path
    """
    create_directory(file_path)
    with open(file_path, "w") as wr:
        wr.write("".join(write_list))


@func_log
def make_atp(*args, **kwargs):
    """
    Extract data from user input to make atp vector
    """
    basic_info_from_user = args[0]
    eds_path = basic_info_from_user.get_data("eds_path")
    mode_list = basic_info_from_user.get_data("mode_list")
    threads = list()
    for mode_name in mode_list:
        file_path = os.path.join(eds_path, "CFG", mode_name[10:], "run_list.txt")
        thread = threading.Thread(target=run_vtran, args=(file_path,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    logging.info("All completed!")
        

def run_vtran(file_path):
    with open(file_path, "r") as rd:
        lines = rd.readlines()
    submit_job(lines)

def submit_job(run_list):
    """
    Run vtran script based on multithreading
    """
    threads = list()
    for line in run_list[:-1]:
        step, target = line.split()
        command = f"make {step}"
        #need multi line?
        input_data = f"""\
        {target}
        """
        thread = threading.Thread(target=run_command, args=(command, input_data))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    line = run_list[-1]
    step, target = line.split()
    command = f"make {step}"
    input_data = f"""\
    {target}
    """
    run_command(command, input_data)


def run_command(command, input_data):
    """
    Execute linux command using subprocess module
    """
    try:
        process = subprocess.Popen(command.split(), stdin=subprocess.PIPE, universal_newlines=True)
        process.communicate(input=input_data)
        logging.info(
            f"command : {command}, input : {input_data} done!, return code : {process.returncode}")
    except Exception:
        logging.error(f"command : {command}, input : {input_data} fail!")
        raise
