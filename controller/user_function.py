from collections import defaultdict
import logging
import os
import threading
import time

import pandas as pd
from controller.utility import func_log
from model.data import DataModel


"""
This area is for custom functions.
"""


TEMPLATES = {
    "io_define": "{step}       {direction} {pin}; {{{signal}}}\n",
    "delete_pin": "{step}       DELETE_PINS {pin};\n",
    "bi_control": "{step}       BIDIRECT_CONTROL {pad} = OUTPUT WHEN {pin} = 1;{{{signal}}}\n",
    "mask_pin": "{step}       MASK_PINS {pad_condition} {pin_condition}; {{{signal}}}\n",
    "alias_pin": "{step}       ALIAS {signal} = {pad};\n"
}


@func_log
def make_base_info(*args, **kwargs):
    dftmux_excel = args[0]
    df = pd.read_excel(dftmux_excel, sheet_name=0, header=None)
    df = df.fillna("N/A")
    idx = (df != "N/A").any(axis=1).idxmax()
    df = df.iloc[idx:]
    mode_info = DataModel("BASE")
    get_mode_info(df, mode_info)
    mode_info.show_all()
    return mode_info


@func_log
def get_mode_info(df, mode_info):
    row_size, column_size = df.shape
    skip_list = ["SCAN", "BIST", "JTAG", "IO", "FAKE"]
    for c_idx in range(column_size):
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
    if main_mode not in mode_info_from_user.data:
        logging.error(f"main mode {main_mode} not in selected mode list")
    merge_flag = len(mode_info_from_user.data) > 1
    threads = list()
    for mode_name in mode_info_from_user.data:
        thread = threading.Thread(target = make_templates, args = (mode_name, main_mode, merge_flag, mode_base_info, mode_info_from_user, basic_info_from_user, eds_path))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def make_templates(mode_name, main_mode, merge_flag, mode_base_info, mode_info_from_user, basic_info_from_user, eds_path):
    thread1 = threading.Thread(target = make_pin_template, args = (mode_name, main_mode, merge_flag, mode_base_info, mode_info_from_user, eds_path))
    thread2 = threading.Thread(target = make_config_template, args = (mode_name, main_mode, mode_info_from_user, basic_info_from_user, eds_path))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def make_pin_template(mode_name,main_mode,merge_flag,mode_base_info,mode_info_from_user,eds_path,):
    config_data = defaultdict(list)
    mode_setting_pin = ["XTMODE", "XUWB_EN", "XUWB_WAKE", "XCAN_RX"]
    ieee_signal = ["WSI","SelectWIR","UpdateWIR","ShiftWR","CaptureWR","WRSTN","WRCK","WSO",]
    if mode_name != main_mode:
        new_name = main_mode + "_" + mode_name[10:]
    else:
        new_name = main_mode
    pad_list = mode_base_info.get_data(mode_name).keys()
    for step, basic_info_from_user in mode_info_from_user.get_data(mode_name).items():
        step = step.lower()
        more_info = basic_info_from_user["more_info"]
        if "vcd2" in step:
            bidirection_control = basic_info_from_user["bidirection_control"]
            cycle = basic_info_from_user["cycle"]
            config_data["pin_type"] += [
                f"CYCLE = {cycle};\n\n{step}     PINTYPE NRZ * @ 0;\n",
                f"{step}     PINTYPE STB * @ {float(cycle) * 0.9};\n",
            ]
            pin_str_format = "{step}    {data}\n"
            input_str_format = "{step}    INPUTS {data};\n"
            merge_config_data(config_data, "pin_type", step, pin_str_format, basic_info_from_user["pin_type"])
            merge_config_data(config_data, "io_define", step, input_str_format, mode_setting_pin)
            if bidirection_control != "":
                add_config_data(config_data,"io_define",step=step,direction="INPUTS",pin=bidirection_control,)
                add_config_data(config_data, "delete_pin", step=step, pin=bidirection_control)
            for pad in pad_list:
                signal, io = mode_base_info.get_data(mode_name + "." + pad + ".signal"), mode_base_info.get_data(
                    mode_name + "." + pad + ".direction"
                )
                if merge_flag:
                    add_config_data(config_data,"io_define",step=step,direction="BIDIRECTS",pin=pad,signal=signal,)
                    if bidirection_control != "":
                        if io == "I":
                            pass
                            # config_data["bi_control"].append(f"{step}     BIDIRECT_CONTROL {pad} = OUTPUT WHEN {bidirection_control} = 0;")
                        else:
                            add_config_data(config_data,"bi_control",step=step,pad=pad,pin=bidirection_control,signal=signal,)
                            add_config_data(config_data,"mask_pin",step=step,pad=pad,pin=bidirection_control,signal=signal,)
                else:
                    if io == "I":
                        add_config_data(config_data, "io_define", step=step, direction="INPUTS", pin=pad, signal=signal,)
                    else:
                        add_config_data(config_data, "io_define", step=step, direction="OUTPUTS", pin=pad, signal=signal,)
                        add_config_data(config_data, "mask_pin", step=step, pad=pad, signal=signal)

        elif "wgl2" in step:
            for pad in pad_list:
                signal = mode_base_info.get_data(mode_name + "." + pad + ".signal")
                for ieee in ieee_signal:
                    if ieee in signal:
                        add_config_data(config_data, "alias_pin", step=step, signal=ieee, pad=pad)
                        break

        merge_config_data(config_data, "add_pin", step, pin_str_format, basic_info_from_user["add_pin"])
        merge_config_data(config_data, "mask_pin", step, pin_str_format, basic_info_from_user["mask_pin"])
        merge_config_data(config_data, "delete_pin", step, pin_str_format, basic_info_from_user["delete_pin"])
        merge_config_data(config_data, "alias_pin", step, pin_str_format, basic_info_from_user["alias_pin"])

    write_list = (config_data["io_define"] + config_data["pin_type"] + config_data["bi_control"] + config_data["add_pin"]
    + config_data["mask_pin"] + config_data["alias_pin"] + config_data["delete_pin"] + more_info)

    file_path = os.path.join(eds_path, "CFG", new_name[10:], "PIN_CONTROL.cfg")
    write_list_to_file(file_path, write_list)


@func_log
def make_config_template(mode_name, main_mode, mode_info_from_user, basic_info_from_user, eds_path):
    config_data = []
    dev = basic_info_from_user.get_data("dev")
    config_data.append(f'HDL_REVISION   {dev}\n')
    if mode_name != main_mode:
        new_name = main_mode + "_" + mode_name[10:]
    else:
        new_name = main_mode
        config_data.append(f'REPEAT_THRESHOLD   {basic_info_from_user.get_data("repeat")}\n')
    for step in mode_info_from_user.get_data(mode_name):
        if step == "VCD2WGL":
            config_data.append(f'TESTMODE_VCD_SOURCE   {mode_info_from_user.get_data(mode_name + "." + step + ".path")}\n')
        if step == "WGL2WGL":
            config_data.append(f'IP_WGL_SOURCE   {mode_info_from_user.get_data(mode_name + "." + step + ".path")}\n')
    if mode_name == main_mode:
        cnt = 0
        main_vector = None
        for mode in mode_info_from_user.data:
            if "VCD2WGL" in mode_info_from_user.get_data(mode):
                cnt += 1
                config_data.append(f"IP_TOP_WGL{cnt}    {eds_path}/OUTPUT/{mode}/{dev}/IP_TOP_WGL\n")
                if mode_info_from_user.get_data(mode + ".VCD2WGL.main_step"):
                    main_vector = cnt
            if "WGL2WGL" in mode_info_from_user.get_data(mode):
                cnt += 1
                config_data.append(f"IP_TOP_WGL{cnt}    {eds_path}/OUTPUT/{mode}/{dev}/TESTMODE_WGL\n")
                if mode_info_from_user.get_data(mode + ".WGL2WGL.main_step"):
                    main_vector = cnt
        config_data.append(f"WGL_NUM    {cnt}\n")
        config_data.append(f"MAIN_WGL   {main_vector}\n")
    file_path = os.path.join(eds_path, "CFG", new_name[10:], f"{new_name[10:]}.cfg")
    write_list_to_file(file_path, config_data)


@func_log
def merge_config_data(config_data, key, step, str_format, data_list):
    config_data[key] += [str_format.format(step=step, data=data) for data in data_list if data != ""]
    print(f"key : {key}, list : {config_data[key]}")


@func_log
def add_config_data(config_data, key, step=None, direction=None, pin=None, pad=None, signal=None):
    if key == "mask_pin":
        pad_condition = f'{pad}.O  @CONDITION' if pin else pad
        pin_condition = f'{pin} = 1' if pin else "@0, 9999999999"
        str_format = TEMPLATES[key].format(step=step, pad_condition=pad_condition, pin_condition = pin_condition, signal=signal)
    else:
        str_format = TEMPLATES[key].format(step=step, direction=direction, pin=pin, signal=signal, pad=pad)
    config_data[key].append(str_format)
    print(f"key {key}, element : {str_format}, list: {config_data[key]}")


@func_log
def create_directory(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


@func_log
def write_list_to_file(file_path, write_list):
    create_directory(file_path)
    with open(file_path, "w") as wr:
        wr.write("".join(write_list))
