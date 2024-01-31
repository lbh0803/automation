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
    jobB.set_query(2, "need_wgl", CheckBoxWidget, "#Do you need WGL?", "Y")
    jobB.set_query(2, "vcd_convert", CheckBoxWidget, "#Check run step", "vcd2wgl/vcd2atp")
    jobB.set_query(2, "vcd_path", LineEditWidget, "=> Write testmode vcd directory")
    jobB.set_query(2, "cycle", LineEditWidget, "=> Write cycle information")
    jobB.set_query(2, "pin_type", PlainTextEditWidget, "=> Write if you want to override default pintype, \n default) input - PINTYPE NRZ XGPIO4 @0;, output - PINTYPE STB XGPIO5 @cycle * 0.9")
    jobB.set_query(2, "bi_ctr_signal", PlainTextEditWidget, "=> Write bidirection control signal")
    jobB.set_query(2, "add_pin", PlainTextEditWidget, "=> Write add pin information, \n ex) ADD_PIN XTCXO input = 0; \n ADD_PIN XO32 output = X;")
    jobB.set_query(2, "mask_pin", PlainTextEditWidget, "=> Write mask pin information \n ex) MASK_PINS XGPIO3 @0, 99999999;")
    jobB.set_query(2, "delete_pin", PlainTextEditWidget, "=> Write delete pin information \n ex) DELETE_PINS XGPIO1, XGPIO2;")
    jobB.set_query(2, "alias_pin", PlainTextEditWidget, "=> Write alias pin information \n ex) ALIAS ADC_EN = XGPIO5;")

    jobB.set_query(2, "wgl2wgl", CheckBoxWidget, "", "wgl2wgl")
    jobB.set_query(2, "wgl_path", LineEditWidget, "=> Write ip wgl directory")
    jobB.set_query(2, "add_pin_wgl", PlainTextEditWidget, "=> Write add pin information, \n ex) ADD_PIN XTCXO input = 0; \n ADD_PIN XO32 output = X;")
    jobB.set_query(2, "mask_pin_wgl", PlainTextEditWidget, "=> Write mask pin information \n ex) MASK_PINS XGPIO3 @0, 99999999;")
    jobB.set_query(2, "delete_pin_wgl", PlainTextEditWidget, "=> Write delete pin information \n ex) DELETE_PINS XGPIO1, XGPIO2;")
    jobB.set_query(2, "alias_pin_wgl", PlainTextEditWidget, "=> Write alias pin information \n ex) ALIAS ADC_EN = XGPIO5;")
    jobB.set_query(2, "more_info", PlainTextEditWidget, "If you need more information, write here \n $STEP $COMMAND ex) merge2atp ADD_PIN XTCXO input = 0;")

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
