from model.data import DataModel, Query
from model.register_logic import (make_base_info, make_register_header,
                                  make_register_rtl)
from view.ui_widget import (CheckBoxWidget, ComboBoxWidget, DirPathWidget,
                            FilePathWidget, LineEditWidget,
                            MultiCheckBoxWidget, PlainTextEditWidget)

JOB_A = "A> Make SFR RTL\n=> Verilog RTL based on excel info"
JOB_B = "B> Make SFR Header\n=> Make .h file in ARM CMSIS format"


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
        JOB_A,
        JOB_B,
    )
    base.set_query(
        False,
        0,
        "sfr_xlsx",
        FilePathWidget,
        ">> Base Information - SFR Info Excel \nex) /USER/IP/SFR.xlsx",
    )
    return base


def construct_a_query(base_info):
    job = Query()
    job.set_query(
        False,
        0,
        "top_module",
        LineEditWidget,
        ">> Top Module Name\n>> ex) WDT, TMR etc..",
    )
    job.set_query(
        False,
        0,
        "rtl_path",
        LineEditWidget,
        ">> RTL Output Path\nex) /USER/IP/SFR.sv",
    )
    return job


def construct_b_query(base_info):
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
        ">> Top Module Name\n>> ex) WDT, TMR etc..",
    )
    job.set_query(
        False,
        0,
        "header_path",
        LineEditWidget,
        ">> Testbench Path\nex) /USER/IP/SFR.h",
    )
    return job


def make_register_query():
    query_data = DataModel("QUERY")
    query_data.set_data(f"base_function", make_base_info)
    query_data.set_data(f"base_query", construct_base_query())
    query_data.set_data(f"{JOB_A}.query_func", construct_a_query)
    query_data.set_data(f"{JOB_A}.execute_func", make_register_rtl)
    query_data.set_data(f"{JOB_B}.query_func", construct_b_query)
    query_data.set_data(f"{JOB_B}.execute_func", make_register_header)
    return query_data
