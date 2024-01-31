import logging
import time

import pandas as pd
from controller.utility import func_log
from model.data import DataModel


"""
This area is for custom functions.
"""


@func_log
# def make_base_info(dftmux_xls):
def make_base_info(*args, **kwargs):
    print(f"DFT path: {args[0]}")
    dftmux_excel = args[0]
    df = pd.read_excel(dftmux_excel, sheet_name = 0, header=None)
    df = df.fillna("N/A")
    idx = (df!="N/A").any(axis=1).idxmax()
    print(f"Data start line is {idx}")
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
            mode_info.set_data(mode + "." + pad_name + '.signal', signal_name)
            if direction == "B":
                if "JTAG_TDO" in signal_name:
                    direction = "O"
                else:
                    direction = "I"
            mode_info.set_data(mode + "." + pad_name + '.direction', direction)
            if ":" in hierarchy:
                hierarchy = hierarchy.split(":")[1].split("/")[0]
            mode_info.set_data(mode + "." + pad_name + '.hierarchy', hierarchy)
            
    

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
    mode_base_info, mode_user_info = args[0], args[1]
    try:
        eds_path = mode_user_info.data.pop("eds_path")
        print(f"eds_path is {eds_path}")
    except KeyError:
        print(f"var eds_path is not in user_input")
    try:
        related_mode = mode_user_info.data.pop("related_mode")
        print(f"releate_mode is {related_mode}")
    except KeyError:
        print(f'var related_mode is not in user input')
    mode_sequence = list(mode_user_info.data.keys())
    for mode in mode_sequence:
        if mode_user_info.get_data(mode + ".main_mode"):
            main_mode = mode
            print(f"main mode is {mode}!")
    if main_mode not in related_mode:
        logging.error("main mode not in selected mode list")
    sequence = make_pin_template(mode_base_info, mode_user_info, related_mode, main_mode, eds_path)
    make_cfg_template(mode_base_info, mode_user_info, main_mode, eds_path, sequence)

    
@func_log
def make_pin_template(mode_base_info, mode_user_info, main_mode, related_mode, eds_path):
    sequence = DataModel("SEQ")
    for mode in related_mode:
        make_mode_pin_template(mode, main_mode, related_mode, mode_base_info, mode_user_info, eds_path, sequence)
    return sequence
    
        
def make_mode_pin_template(mode_name, main_mode, related_mode_list, mode_base_info, mode_user_info, eds_path, sequence): 
    if mode_name != main_mode:
        new_name = main_mode + mode_name[10:]
    else:
        new_name = main_mode
    mode_setting_pin = ["XTMODE", "XUWB_EN", "XUWB_WAKE", "XCAN_RX"]
    ieee_signal = ["WSI", "SelectWIR", "UpdateWIR", "ShiftWR", "CaptureWR", "WRSTN", "WRCK", "WSO"]
    pad_list = mode_base_info.get_data(main_mode).keys()
    merge_flag = (len(related_mode_list) > 1)
    if mode_user_info.get_data(mode_name + ".need_wgl"):
        target = "wgl"
    else:
        target = "atp"
    io_define = list()
    pin_type = list()
    bi_control = list()
    add_pin = list()
    mask_pin = list()
    delete_pin = list()
    alias_pin = list()
    more_info = mode_user_info.get_data(mode_name + ".more_info")
    if mode_user_info.get_data(mode_name + ".vcd_convert"):
        sequence.set_data(new_name, "vcd")
        bi_ctr_signal = mode_user_info.get_data(mode_name + ".bi_ctr_signal")
        cycle = mode_user_info.get_data(mode_name + ".cycle")
        pin_type += [f"CYCLE = {cycle};\n\nvcd2{target}     PINTYPE NRZ * @ 0;\n", f"vcd2{target}     PINTYPE STB * @ {float(cycle) * 0.9};\n"]
        pin_type += mode_user_info.get_data(mode_name + ".pin_type")
        mask_pin += mode_user_info.get_data(mode_name + ".mask_pin")
        add_pin += mode_user_info.get_data(mode_name + ".add_pin")
        delete_pin += mode_user_info.get_data(mode_name + ".delete_pin")
        alias_pin += mode_user_info.get_data(mode_name + ".alias_pin")
        io_define += [f'vcd2{target}     INPUTS {pin};\n' for pin in mode_setting_pin]
        for pad in pad_list:
            signal, io = mode_base_info.get_data(mode_name + "." + pad + ".signal"), mode_base_info.get_data(mode_name + "." + pad + ".direction")
            if merge_flag:
                io_define.append(f"vcd2{target}     BIDIRECTS {pad}; {{{signal}}}\n")
                if bi_ctr_signal != "":
                    if io == "I":
                        bi_control.append(f"vcd2{target}     BIDIRECT_CONTROL {pad} = OUTPUT WHEN {bi_ctr_signal} = 0;")
                    else:
                        bi_control.append(f"vcd2{target}     BIDIRECT_CONTROL {pad} = OUTPUT WHEN {bi_ctr_signal} = 1;")
                        mask_pin.append(f"vcd22{target}     MASK_PINS {pad}.O @CONDITION {bi_ctr_signal} = 1;{{{signal}}}\n")
            else:
                if io == "I":
                    io_define.append(f"vcd2{target}     INPUTS {pad}; {{{signal}}}\n")
                else:
                    io_define.append(f"vcd2{target}    OUTPUTS {pad}; {{{signal}}}\n")
                    mask_pin.append(f"vcd2{target}     MASK_PINS {pad} @0, 999999999;{{{signal}}}\n")
    
    if mode_user_info.get_data(mode_name + '.wgl2wgl'):
        sequence.set_data(new_name, "wgl")
        mask_pin += mode_user_info.get_data(mode_name + ".mask_pin_wgl")
        add_pin += mode_user_info.get_data(mode_name + ".add_pin_wgl")
        delete_pin += mode_user_info.get_data(mode_name + ".delete_pin_wgl")
        alias_pin += mode_user_info.get_data(mode_name + ".alias_pin_wgl")  
        for pad in pad_list:
            signal = mode_base_info.get_data(mode_name + "." + pad + ".signal")
            for ieee in ieee_signal:
                if ieee in signal:
                    alias_pin.append(f"wgl2wgl      ALIAS {ieee} = {pad};\n")
                    break

    write_list = io_define + pin_type + bi_control + add_pin + mask_pin + alias_pin + delete_pin + more_info
        
    with open(eds_path + "\\CFG\\" + new_name[10:] + "\\PIN_CONTROL.cfg", "w") as wr:
        wr.write("".join(write_list))

    
@func_log
def make_cfg_template():
    pass