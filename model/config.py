from model.data import DataModel, Query
from model.dft_config import make_dft_query
from model.lib_config import make_lib_query
from model.register_config import make_register_query
from view.ui_widget import ComboBoxWidget

JOB_A = "LIB"
JOB_B = "DFT"
JOB_C = "SFR"


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
        ">> Select App",
        JOB_A,
        JOB_B,
        JOB_C,
    )
    return base


def construct_app_query():
    query_data = DataModel("QUERY")
    query_data.set_data(JOB_A, make_lib_query())
    query_data.set_data(JOB_B, make_dft_query())
    query_data.set_data(JOB_C, make_register_query())
    return query_data
