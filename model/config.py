from collections import namedtuple
from model.data import Query
from view.ui_widget import (
    CheckBoxWidget,
    ComboBoxWidget,
    LineEditWidget,
    MultiCheckBoxWidget,
    PlainTextEditWidget,
)


JOB_A = "A> Make TESTMODE TB\n => DFTMUX connection check\n => PAD <-> IP"
JOB_B = "B> Make VECTOR CFG File\n => Setup stage before making VECTOR"
JOB_C = "C> Make Vector\n => ATP/PAT type are supported"


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
        "#Select job",
        JOB_A,
        JOB_B,
        JOB_C,
    )
    base.set_query(
        0, "dftmux_xls", LineEditWidget, "#Base information\n => Write dftmux info excel, ex) dftmux.xlsx"
    )

    return base

def construct_a_query(base_info):
    jobA = Query()
    jobA.set_query(
        0,
        "signal_xls",
        LineEditWidget,
        "#Write tmode signal xls path, if it not exists put 'N'\n ex) signal_info.xlsx",
    )

    jobA.set_query(
        0,
        "tb_path",
        LineEditWidget,
        "#Write output testbench path,\n ex) /DFT/sim/tests/tb.sv",
    )
    return jobA


def construct_b_query(base_info):
    jobB = Query(repeat=True)
    jobB.set_query(
        0, "eds_path", LineEditWidget, "#Write your EDS working path,\n ex) /TOP/EDS"
    )

    jobB.set_query(
        1, "related mode", MultiCheckBoxWidget, "Select all related test mode.", *base_info.data.keys()
    )

    jobB.set_query(
        2,
        "test_mode",
        ComboBoxWidget,
        "#Please select mode up to your mode sequence",
        *base_info.data.keys(),
    )
    jobB.set_query(2, "main_mode", CheckBoxWidget, "#Is this your main test mode?", "Y")
    jobB.set_query(2, "repeat", LineEditWidget, "#Write repeat threshold,\n ex) 2")
    jobB.set_query(2, "dev", LineEditWidget, "#Write dev step,\n ex) EVT0_ML3_DEV00")
    jobB.set_query(2, "vcd2wgl", CheckBoxWidget, "#Check run step", "vcd2wgl")
    jobB.set_query(2, "vcd_path", LineEditWidget, "=> Write testmode vcd directory")
    jobB.set_query(
        2,
        "vcd_info",
        PlainTextEditWidget,
        "=> If you need more info, please write hear\
            \n ex) CYCLE = 38.46;\
            \n ex) ADD_PIN XTCXO input = 0;\
            \n ex) DELETE_PINS A,B,C;\
            \n ex) MASK_PINS PIN_OUT1 @0, 999999999;",
    )
    jobB.set_query(2, "wgl2wgl", CheckBoxWidget, "", "wgl2wgl")
    jobB.set_query(2, "wgl_path", LineEditWidget, "=> Write ip wgl directory")
    jobB.set_query(
        2,
        "wgl_info",
        PlainTextEditWidget,
        "=> If you need more info, please write hear\
            \n ex) ADD_PIN XTCXO input = 0;\
            \n ex) DELETE_PINS A,B,C;\
            \n ex) MASK_PINS PIN_OUT1 @0, 999999999;",
    )
    return jobB


def construct_c_query(base_info):
    jobC = Query()
    jobC.set_query(
        0, "eds_path", LineEditWidget, "#Write your EDS working path,\n ex) /TOP/EDS"
    )
    jobC.set_query(
        1,
        "main_mode",
        ComboBoxWidget,
        "#Select your test mode",
        *base_info.data.keys(),
    )
    return jobC
