from collections import namedtuple

from model.data import Query
from view.ui_widget import (
    CheckBoxWidget,
    ComboBoxWidget,
    DirPathWidget,
    FilePathWidget,
    LineEditWidget,
    MultiCheckBoxWidget,
    PlainTextEditWidget,
)

JOB_A1 = "A-1> Make TESTMODE TB\n=> DFTMUX connection check (PAD <-> IP)"
JOB_A2 = "A-2> Make TESTMODE TB\n=> UDS signal check in TESTMODE"
JOB_B = "B> Make VECTOR CFG File\n=> Setup stage before making VECTOR"
JOB_C = "C> Make VECTOR\n=> ATP/PAT type are supported"


def construct_base_query():
    """
    You can update query if you need.
    This function makes database for query.
    """
    base = Query()
    base.set_query(
        False,
        0,
        "job",
        ComboBoxWidget,
        ">> Select Job",
        JOB_A1,
        JOB_A2,
        JOB_B,
        JOB_C,
    )
    base.set_query(
        False,
        0,
        "dftmux_xlsx",
        FilePathWidget,
        ">> Base Information - DFTMUX Info Excel\nex) /USER/DFT/DFTMUX.xlsx",
    )

    return base


def construct_a1_query(base_info):
    job = Query()
    job.set_query(
        False,
        0,
        "top_module",
        LineEditWidget,
        ">> Top Module Name\n>> ex) TB or top",
    )
    job.set_query(
        False,
        0,
        "tb_path",
        LineEditWidget,
        ">> Testbench Path\nex) /USER/DFT/TB.sv",
    )
    return job


def construct_a2_query(base_info):
    job = Query()
    job.set_query(
        False,
        0,
        "signal_xls",
        FilePathWidget,
        ">> UDS Singal Info Excel\nex) /USER/DFT/SIGNAL_INFO.xlsx",
    )
    job.set_query(
        False,
        0,
        "top_module",
        LineEditWidget,
        ">> Top Module Name\n>> ex) TB or top",
    )
    job.set_query(
        False,
        0,
        "tb_path",
        LineEditWidget,
        ">> Testbench Path\nex) /USER/DFT/TB.sv",
    )
    return job


def construct_b_query(base_info):
    job = Query()
    job.set_query(
        False, 0, "eds_path", DirPathWidget, ">> EDS Working Directory\nex) /USER/EDS"
    )

    job.set_query(
        False,
        1,
        "main_mode",
        ComboBoxWidget,
        ">> Target Mode",
        *base_info.data.keys(),
    )

    job.set_query(
        True,
        2,
        "test_mode",
        ComboBoxWidget,
        "<<<Please fill the below lines according to your test sequence>>>",
        *base_info.data.keys(),
    )
    job.set_query(
        True, 2, "step", ComboBoxWidget, ">> Run Step", "VCD2WGL", "VCD2ATP", "WGL2WGL"
    )
    job.set_query(
        True,
        2,
        "main_step",
        CheckBoxWidget,
        ">> Main Step?\n>> It determines vector name",
        "Y",
    )
    job.set_query(
        True, 2, "src_path", DirPathWidget, ">> Source File Directory\nex) /USER/SRC"
    )
    job.set_query(
        True,
        2,
        "add_pin",
        PlainTextEditWidget,
        ">> ADD_PIN Information\nex)\nADD_PIN XTCXO input = 0; \nADD_PIN XO32 OUTPUT = X;",
    )
    job.set_query(
        True,
        2,
        "mask_pin",
        PlainTextEditWidget,
        ">> MASK_PINS Information \nex) MASK_PINS XGPIO3 @0, 99999999;",
    )
    job.set_query(
        True,
        2,
        "delete_pin",
        PlainTextEditWidget,
        ">> DELETE_PINS Information \nex) DELETE_PINS XGPIO1, XGPIO2;",
    )
    job.set_query(
        True,
        2,
        "alias_pin",
        PlainTextEditWidget,
        ">> ALIAS Information \nex) ALIAS ADC_EN = XGPIO5;",
    )
    job.set_query(
        True,
        2,
        "cycle",
        LineEditWidget,
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n***FROM HERE, DATA FOR VCD CONVERSION***\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n >> CYCLE Information - Period\nex) 100",
    )
    job.set_query(
        True,
        2,
        "pin_type",
        PlainTextEditWidget,
        ">> PINTYPE Information\n>> If you want to override default pintype, write here \nDefault) \ninput -> PINTYPE NRZ XGPIO4 @0;\noutput -> PINTYPE STB XGPIO5 @CYCLE * 0.9",
    )
    job.set_query(
        True, 2, "bidirection_control", LineEditWidget, ">> Bidirection Control Signal"
    )
    job.set_query(
        True,
        2,
        "last",
        CheckBoxWidget,
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n>> Is last? \n>> If it is the last sequence, check this",
        "Y",
    )

    job.set_query(False, 3, "repeat", LineEditWidget, ">> Repeat Threshold,\nex) 2")
    job.set_query(False, 3, "dev", LineEditWidget, ">> DEV Step,\nex) EVT0_ML3_DEV00")
    job.set_query(
        False, 3, "export", DirPathWidget, ">> Export Directory,\nex) /USER/EDS/EXPORT"
    )
    job.set_query(
        False,
        3,
        "more_info",
        PlainTextEditWidget,
        ">> If you need more information, write here in format \n>> This would be applied to the merge2atp step\nex) ADD_PIN XTCXO input = 0;",
    )

    return job


def construct_c_query(base_info):
    job = Query()
    job.set_query(
        False, 0, "eds_path", DirPathWidget, ">> EDS Working Path\nex) /USER/EDS"
    )
    job.set_query(
        False,
        1,
        "mode_list",
        MultiCheckBoxWidget,
        ">> Target Mode",
        *base_info.data.keys(),
    )
    return job
