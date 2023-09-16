import sys
import pandas as pd
import numpy as np
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import distance_checker, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal



# pytest -v -s --tb=short tests/unit/test_distance_checker.py::test_distance_checker_prospect_ensure_passing
def test_distance_checker_prospect_ensure_passing():
    '''
    This test fails because some Distances are greater than the max distance allowed.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed.
    Max_Distance = 45.

    Column  | Values    | Result        | Customer Type | Reason
    ----------------------------------------------------------------------------------
    Distance  | 11      | Passing       | prospect      |
    Distance  | 100     | not checked   | l1            | Not a prospect customer type
    Distance  | 50      | not checked   | l2            | Not a prospect customer type
    Distance  | 49      | not checked   | l3            | Not a prospect customer type
    '''

    df_raw = pd.DataFrame(
        {   
            'Distance': [11, 100, 50, 49], # <-- this column is being tested
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = distance_checker(df=df_raw, distance_col='Distance', max_distance=45, customer_type="PROSPECT")

    expected_df = pd.DataFrame(
        {
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, None, None, None]
        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 



# pytest -v -s --tb=short tests/unit/test_distance_checker.py::test_distance_checker_prospect_ensure_failing
def test_distance_checker_prospect_ensure_failing():
    '''
    This test fails because some Distances are greater than the max distance allowed.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed.
    Max_Distance = 45.

    Column  | Values    | Result        | Customer Type | Reason
    ----------------------------------------------------------------------------------
    Distance  | 46      | Failing       | prospect      | Value > Max_Distance
    Distance  | 100     | not checked   | l1            | Not a prospect customer type
    Distance  | 50      | not checked   | l2            | Not a prospect customer type
    Distance  | 49      | not checked   | l3            | Not a prospect customer type
    '''

    df_raw = pd.DataFrame(
        {   
            'Distance': [46, 100, 50, 49], # <-- this column is being tested
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = distance_checker(df=df_raw, distance_col='Distance', max_distance=45, customer_type="PROSPECT")

    expected_df = pd.DataFrame(
        {
            'Distance': [46, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": ['distance_checker failure', None, None, None]
        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 




# pytest -v -s --tb=short tests/unit/test_distance_checker.py::test_distance_checker_dms_ensure_failing
def test_distance_checker_dms_ensure_failing():
    '''
    This test fails because some Distances are greater than the max distance allowed.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed.
    Max_Distance = 45.

    Column  | Values    | Result        | Customer Type | Reason
    ----------------------------------------------------------------------------------
    Distance  | 46      | not checked   | prospect      | Not a DMS customer type
    Distance  | 100     | failing       | l1            | Value > Max_Distance
    Distance  | 50      | failing       | l2            | Value > Max_Distance
    Distance  | 49      | failing       | l3            | Value > Max_Distance
    '''

    df_raw = pd.DataFrame(
        {   
            'Distance': [46, 100, 50, 49], # <-- this column is being tested
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = distance_checker(df=df_raw, distance_col='Distance', max_distance=45, customer_type="dMs")

    expected_df = pd.DataFrame(
        {
            'Distance': [46, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, 'distance_checker failure', 'distance_checker failure', 'distance_checker failure']
        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 



# pytest -v -s --tb=short tests/unit/test_distance_checker.py::test_distance_checker_dms_ensure_passing
def test_distance_checker_dms_ensure_passing():
    '''
    This test fails because some Distances are greater than the max distance allowed.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed.
    Max_Distance = 45.

    Column  | Values    | Result        | Customer Type | Reason
    ----------------------------------------------------------------------------------
    Distance  | 11      | not checked   | prospect      | Not a DMS customer type
    Distance  | 45      | passing       | l1            | 
    Distance  | 44      | passing       | l2            | 
    Distance  | 0       | passing       | l3            | 
    '''

    df_raw = pd.DataFrame(
        {   
            'Distance': [11, 45, 44, 0], # <-- this column is being tested
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = distance_checker(df=df_raw, distance_col='Distance', max_distance=45, customer_type="dms")

    expected_df = pd.DataFrame(
        {
            'Distance': [11, 45, 44, 0],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, None, None, None]
        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 