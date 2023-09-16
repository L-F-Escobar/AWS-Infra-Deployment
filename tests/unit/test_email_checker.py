import sys
import pandas as pd
import numpy as np
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import email_checker, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal


FILTERS = ['luis@recallmasters.com','lfescoba@uci.edu','l.driver.escobar@gmail.com',]

# pytest -v -s --tb=short tests/unit/test_email_checker.py::test_email_checker_ensure_failing
def test_email_checker_ensure_failing():
    '''
    This test fails because some emails are present which are in an email suppression list
    FILTERS.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed.
    Email Suppression List = FILTERS.

    Column  | Values            | Result        | Reason
    --------------------------------------------------------------------------------
    EMAIL  | 'l@gmail.com'      | Passing       | 
    EMAIL  | 'L@GMAIL.COM'      | Passing       | 
    EMAIL  | 'lfescoba@uci.edu' | Failing <---  | Present in suppression list.
    EMAIL  | 'LFESCOBA@UCI.EDU' | Failing <---  | Present in suppression list.
    '''

    df_raw = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU']# <-- this column is being tested
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = email_checker(df=df_raw, email_col='EMAIL', filters=FILTERS)

    expected_df = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],# <-- this column is being tested
            "Reason_for_failure": [None, None,'email_checker failure', 'email_checker failure']
        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 



# pytest -v -s --tb=short tests/unit/test_email_checker.py::test_email_checker_ensure_passing
def test_email_checker_ensure_passing():
    '''
    This test passes because zero emails are present which are in an email suppression list
    FILTERS.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed.
    Email Suppression List = FILTERS.

    Column  | Values                | Result        | Reason
    --------------------------------------------------------------------------------
    EMAIL  | 'l@gmail.com'          | Passing       | 
    EMAIL  | 'L@GMAIL.COM'          | Passing       | 
    EMAIL  | '666_lfescoba@uci.edu' | Passing       | Present in suppression list.
    EMAIL  | 'LFESCOBA_666@UCI.EDU' | Passing       | Present in suppression list.
    '''

    df_raw = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', '666_lfescoba@uci.edu', 'LFESCOBA_666@UCI.EDU']# <-- this column is being tested
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = email_checker(df=df_raw, email_col='EMAIL', filters=FILTERS)

    expected_df = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', '666_lfescoba@uci.edu', 'LFESCOBA_666@UCI.EDU'],# <-- this column is being tested
            "Reason_for_failure": [None, None,None,None]
        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 




# for i in process_df_check1.columns:
#     print(process_df_check1[i].dtype)