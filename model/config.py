from collections import namedtuple
from model.data import Query
from view.ui_widget import (
    CheckBoxWidget,
    ComboBoxWidget,
    LineEditWidget,
    PlainTextEditWidget,
)


JOB_A = "A> Make TESTMODE TB\n => DFTMUX connection check\n => PAD <-> IP"
JOB_B = "B> Make VECTOR CFG File\n => Setup stage before making VECTOR"
JOB_C = "C> Make Vector\n => ATP/PAT type are supported"


def construct_query():
    """
    You can update query if you need.
    This function makes database for query.
    """
    query = namedtuple("query", "common, jobA, jobB, jobC")
    common = Query()
    common.set_query(
        0,
        "job",
        ComboBoxWidget,
        "#Select job",
        JOB_A,
        JOB_B,
        JOB_C,
    )

    jobA = Query()
    jobA.set_query(
        0, "dftmux_xls", LineEditWidget, "#Write dftmux info excel \n ex) dftmux.xlsx"
    )

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

    jobB = Query(repeat=True)
    jobB.set_query(0, "dftmux_xls", LineEditWidget, "#Write dftmux info excel")
    jobB.set_query(
        0, "eds_path", LineEditWidget, "#Write your EDS working path,\n ex) /TOP/EDS"
    )

    jobB.set_query(
        1,
        "test_mode",
        ComboBoxWidget,
        "#Please select mode up to your mode sequence",
        "modeA",
        "modeB",
        "modeC",
    )
    jobB.set_query(1, "main_mode", CheckBoxWidget, "#Is this your main test mode?", "Y")
    jobB.set_query(1, "repeat", LineEditWidget, "#Write repeat threshold,\n ex) 2")
    jobB.set_query(1, "dev", LineEditWidget, "#Write dev step,\n ex) EVT0_ML3_DEV00")
    jobB.set_query(1, "vcd2wgl", CheckBoxWidget, "#Check run step", "vcd2wgl")
    jobB.set_query(1, "vcd_path", LineEditWidget, "=> Write testmode vcd directory")
    jobB.set_query(
        1,
        "vcd_info",
        PlainTextEditWidget,
        "=> If you need more info, please write hear\
            \n ex) CYCLE = 38.46;\
            \n ex) ADD_PIN XTCXO input = 0;\
            \n ex) DELETE_PINS A,B,C;\
            \n ex) MASK_PINS PIN_OUT1 @0, 999999999;",
    )
    jobB.set_query(1, "wgl2wgl", CheckBoxWidget, "", "wgl2wgl")
    jobB.set_query(1, "wgl_path", LineEditWidget, "=> Write ip wgl directory")
    jobB.set_query(
        1,
        "wgl_info",
        PlainTextEditWidget,
        "=> If you need more info, please write hear\
            \n ex) ADD_PIN XTCXO input = 0;\
            \n ex) DELETE_PINS A,B,C;\
            \n ex) MASK_PINS PIN_OUT1 @0, 999999999;",
    )

    jobC = Query()
    jobC.set_query(
        0, "eds_path", LineEditWidget, "#Write your EDS working path,\n ex) /TOP/EDS"
    )
    jobC.set_query(
        1,
        "main_mode",
        ComboBoxWidget,
        "#Select your test mode",
        "modeA",
        "modeB",
        "modeC",
    )

    query.common = common
    query.jobA = jobA
    query.jobB = jobB
    query.jobC = jobC
    return query
