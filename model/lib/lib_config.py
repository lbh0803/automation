from model.data import DataModel, Query
from model.lib.lib_logic import make_base_info, make_lib_status_info
from view.ui_widget import (
    CheckBoxWidget,
    ComboBoxWidget,
    DirPathWidget,
    FilePathWidget,
    LineEditWidget,
    MultiCheckBoxWidget,
    PlainTextEditWidget,
)

JOB_A = "A> Make LIB Status Sheet\n=> This will show corner status"


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
    )
    base.set_query(
        False,
        0,
        "prj_config",
        FilePathWidget,
        ">> Base Information - prj.config File Path\nex) /USER/prj.config",
    )
    base.set_query(
        False,
        0,
        "lib_xlsx",
        FilePathWidget,
        ">> Base Information - LIB/Signoff Information\nex) /USER/DKIT/LIB.xlsx",
    )
    return base


def construct_a_query(base_info):
    job = Query()
    job.set_query(
        False,
        0,
        "project",
        LineEditWidget,
        ">> Project Name(lower case) in VWP\n>> ex) s3ju200 / s5n6175",
    )
    job.set_query(
        False,
        0,
        "lib_list",
        MultiCheckBoxWidget,
        ">> LIB List",
        "LIB1",
        "LIB2",
        "LIB3",
        "LIB4",
    )
    return job


def make_lib_query():
    query_data = DataModel("QUERY")
    query_data.set_data(f"logo", "lib_logo.png")
    query_data.set_data(f"base_function", make_base_info)
    query_data.set_data(f"base_query", construct_base_query())
    query_data.set_data(f"{JOB_A}.query_func", construct_a_query)
    query_data.set_data(f"{JOB_A}.execute_func", make_lib_status_info)
    return query_data
