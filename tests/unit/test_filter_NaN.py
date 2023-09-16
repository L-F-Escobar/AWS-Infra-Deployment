import sys
import pandas as pd
import numpy as np
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import find_NaN, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal


# pytest -v -s --tb=short tests/unit/test_filter_NaN.py::test_find_NaN_ensure_failing
def test_find_NaN_ensure_failing():
    '''
    This test fails. The 'check' variable contains a list of values which cannot contain empty/blank
    values in their df cells. 

    DESK CHECK BELOW
    ----------------
    Cell Name = The name of the cell(s) which cannot contain empty value(s).
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.

    Cell Name       | Values                                                                | Result
    ---------------------------------------------------------------------------------------------------------------------------
    email           | 'l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'  | Passing
    home_phone      | "some value", np.nan, '', "Another value"                             | Failing on the np.nan & '' values
    address         | NONE
    '''

    check = ['email', 'home_phone', 'address']

    df_raw = pd.DataFrame(
        {
            "VDP_08": ["air bags", "tires", np.nan, ""], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, '', "Another value"], # <-- this column is being checked.
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'], # <-- this column is being checked.
        }
    )
    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = find_NaN(df=df_raw, check_list=check)

    expected_df = pd.DataFrame(
        {
            "VDP_08": ["air bags", "tires", np.nan, np.nan], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"], # <-- this column is being checked.
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'], # <-- this column is being checked.
            "Reason_for_failure": [None, 'find_NaN failure' , 'find_NaN failure', None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)
    
    assert_frame_equal(process_df, expected_df)
    assert passing == False 




# pytest -v -s --tb=short tests/unit/test_filter_NaN.py::test_find_NaN_ensure_passing
def test_find_NaN_ensure_passing():
    '''
    This test passes. The 'check' variable contains a list of values which cannot contain empty/blank
    values in their df cells. 

    DESK CHECK BELOW
    ----------------
    Cell Name = The name of the cell(s) which cannot contain empty value(s).
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.

    Cell Name       | Values                                                                | Result
    ---------------------------------------------------------------------------------------------------------------------------
    email           | 'l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'  | Passing
    '''

    check = ['email']

    df_raw = pd.DataFrame(
        {
            "VDP_08": ["air bags", "tires", np.nan, ""], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, '', "Another value"], # <-- this column is being checked.
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'], # <-- this column is being checked.
        }
    )
    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = find_NaN(df=df_raw, check_list=check)

    expected_df = pd.DataFrame(
        {
            "VDP_08": ["air bags", "tires", np.nan, np.nan], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"], # <-- this column is being checked.
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'], # <-- this column is being checked.
            "Reason_for_failure": [None, None , None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)
    
    assert_frame_equal(process_df, expected_df)
    assert passing == True 