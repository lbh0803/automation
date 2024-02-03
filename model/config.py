from collections import namedtuple

from model.data import Query
from view.ui_widget import (CheckBoxWidget, ComboBoxWidget, LineEditWidget,
                            MultiCheckBoxWidget, PlainTextEditWidget)

JOB_A = "A> Make TESTMODE TB\n => DFTMUX connection check\n => PAD <-> IP"
JOB_B = "B> Make VECTOR CFG File\n => Setup stage before making VECTOR"
JOB_C = "C> Make VECTOR\n => ATP/PAT type are supported"


def construct_base_query():
    """
    You can update query if you need.
    This function makes database for query.
    """
    base = Query()
    base.set_query(
        0,
        "job",
        ComboBoxWidget,
        ">> Select Job",
        JOB_A,
        JOB_B,
        JOB_C,
    )
    base.set_query(
        0,
        "dftmux_xls",
        LineEditWidget,
        ">> Base Information - DFTMUX Info Excel\nex) /USER/DFT/DFTMUX.xlsx",
    )

    return base


def construct_a_query(base_info):
    jobA = Query()
    jobA.set_query(
        0,
        "signal_xls",
        LineEditWidget,
        ">> Testmode Singal Info Excel>\nIf not exists put 'N'\nex)/USER/DFT/SIGNAL_INFO.xlsx",
    )

    jobA.set_query(
        0,
        "tb_path",
        LineEditWidget,
        ">>Testbench path\nex) /USER/DFT/TB.sv",
    )
    return jobA


def construct_b_query(base_info):
    jobB = Query(repeat=2)
    jobB.set_query(0, "eds_path", LineEditWidget, ">> EDS Working Directory\nex) /USER/EDS")

    jobB.set_query(
        1,
        "main_mode",
        ComboBoxWidget,
        ">> Target Mode",
        *base_info.data.keys(),
    )

    jobB.set_query(
        2,
        "test_mode",
        ComboBoxWidget,
        "<<<Please fill the below lines according to your test sequence>>>",
        *base_info.data.keys(),
    )
    jobB.set_query(2, "step", ComboBoxWidget, ">> Run Step", "VCD2WGL", "VCD2ATP", "WGL2WGL")
    jobB.set_query(2, "main_step", CheckBoxWidget, ">> Main Step?\n>> It determines vector name", "Y")
    jobB.set_query(2, "path", LineEditWidget, ">> Source File Directory\nex) /USER/SRC")
    jobB.set_query(
        2,
        "add_pin",
        PlainTextEditWidget,
        ">> ADD_PIN Information\nex)\nADD_PIN XTCXO input = 0; \nADD_PIN XO32 OUTPUT = X;",
    )
    jobB.set_query(
        2,
        "mask_pin",
        PlainTextEditWidget,
        ">> MASK_PINS Information \nex) MASK_PINS XGPIO3 @0, 99999999;",
    )
    jobB.set_query(
        2,
        "delete_pin",
        PlainTextEditWidget,
        ">> DELETE_PINS Information \nex) DELETE_PINS XGPIO1, XGPIO2;",
    )
    jobB.set_query(
        2,
        "alias_pin",
        PlainTextEditWidget,
        ">> ALIAS Information \nex) ALIAS ADC_EN = XGPIO5;",
    )
    jobB.set_query(
        2,
        "cycle",
        LineEditWidget,
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\nFrom this, for vcd conversion\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n >> CYCLE Information - Period\nex) 100",
    )
    jobB.set_query(
        2,
        "pin_type",
        PlainTextEditWidget,
        ">> PINTYPE Information\n>> If you want to override default pintype, write here \nDefault) \ninput -> PINTYPE NRZ XGPIO4 @0;\noutput -> PINTYPE STB XGPIO5 @cycle * 0.9",
    )
    jobB.set_query(2, "bidirection_control", LineEditWidget, ">> Bidirection Control Signal")
    jobB.set_query(2, "last", CheckBoxWidget, ">> Is last? \nIf it is the last sequence, check this", "Y")
    
    jobB.set_query(3, "repeat", LineEditWidget, ">> Repeat Threshold,\nex) 2")
    jobB.set_query(3, "dev", LineEditWidget, ">> DEV Step,\nex) EVT0_ML3_DEV00")
    jobB.set_query(3, "export", LineEditWidget, ">> Export Directory,\nex) /USER/EDS/EXPORt")
    jobB.set_query(
        3,
        "more_info",
        PlainTextEditWidget,
        ">> If you need more information, write here in format '$STEP $COMMAND'\nex) merge2atp ADD_PIN XTCXO input = 0;",
    )

    return jobB


def construct_c_query(base_info):
    jobC = Query()
    jobC.set_query(0, "eds_path", LineEditWidget, ">> EDS Working Path\nex) /USER/EDS")
    jobC.set_query(
        1,
        "main_mode",
        ComboBoxWidget,
        ">> Target Mode",
        *base_info.data.keys(),
    )
    return jobC
