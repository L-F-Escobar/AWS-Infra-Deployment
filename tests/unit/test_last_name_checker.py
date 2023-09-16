import sys
import pandas as pd
import numpy as np
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import last_name_checker, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal


LNAME_FILTERS = ['associates', 'associate', 'inc', 'automotive', 'dealership', 'dealer', 'llc']

# pytest -v -s --tb=short tests/unit/test_last_name_checker.py::test_last_name_checker_ensure_failing
def test_last_name_checker_ensure_failing():
    '''
    This test fails because some last names are solely associated with business names.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed

    Column  | Values                    | Result        | Reason
    --------------------------------------------------------------------------------
    lname1  | rutland beard florist inc | Failing <---  | inc
    lname1  | adko associates inc       | Failing <---  | associates, inc
    lname1  | Sullivan                  | Passing       |
    lname1  | Escobar                   | Passing       |
    '''

    df_raw = pd.DataFrame(
        {
            "lname1": ["rutland beard florist inc", "adko associates inc", 'Sullivan', "Escobar"], # <-- This column is being tested.
            "home_phone": ["some value", np.nan, "", "Another value"],
            "address": ["abc street", np.nan, np.nan, np.nan],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = last_name_checker(df=df_raw, lname_col='lname1', filters=LNAME_FILTERS)

    expected_df = pd.DataFrame(
        {
            "lname1": ["rutland beard florist inc", "adko associates inc", 'Sullivan', "Escobar"],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "address": ["abc street", np.nan, np.nan, np.nan],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            "Reason_for_failure": ['last_name_checker failure', 'last_name_checker failure' , None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 



# pytest -v -s --tb=short tests/unit/test_last_name_checker.py::test_last_name_checker_ensure_passing
def test_last_name_checker_ensure_passing():
    '''
    This test fails because some last names are solely associated with business names.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record failed.

    Column  | Values                    | Result        | Reason
    --------------------------------------------------------------------------------
    lname1  | rutland beard florist     | Passing       | 
    lname1  | adko                      | Passing       | 
    lname1  | Sullivan                  | Passing       |
    lname1  | Escobar                   | Passing       |
    '''

    df_raw = pd.DataFrame(
        {
            "lname1": ["rutland beard florist", "adko ", 'Sullivan', "Escobar"], # <-- This column is being tested.
            "home_phone": ["some value", np.nan, "", "Another value"],
            "address": ["abc street", np.nan, np.nan, np.nan],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = last_name_checker(df=df_raw, lname_col='lname1', filters=LNAME_FILTERS)

    expected_df = pd.DataFrame(
        {
            "lname1": ["rutland beard florist", "adko ", 'Sullivan', "Escobar"], # <-- This column is being tested.
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "address": ["abc street", np.nan, np.nan, np.nan],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            "Reason_for_failure": [None, None , None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 