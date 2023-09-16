import sys
import pandas as pd
import numpy as np
import os
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import list_zip_check, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal



# pytest -v -s --tb=short tests/unit/test_list_zip.py::test_list_zip_check_ensure_failing
def test_list_zip_check_ensure_failing():
    '''
    This test fails because there are some ZipCode(s) which are not present 
    in their respective lists.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed

    Column   | Values           | Result        | Reason
    --------------------------------------------------------------------------------
    ZipCode  | '99999-9997'     | Failing <---  | Zip 99999 not present in pros_zips.
    ZipCode  | '11111-0111'     | Passing       | 
    ZipCode  | '66666-6000'     | Failing <---  | Zip 6666 not present in dms_zips.
    ZipCode  | '92656-2000'     | Failing <---  | Zip 92656 not present in dms_zips.
    '''

    pros_zips = ['99997', '10112', '66666',]
    dms_zips = ['11111', '0', '-1', '.1']

    df_raw = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],# <-- Column being tested.
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = list_zip_check(df=df_raw, prospect_zips=pros_zips, dms_zips=dms_zips, zip_col='ZipCode')

    expected_df = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'], # <-- Column being tested.
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            "Reason_for_failure": ['list_zip_check failure', None, 
                                   'list_zip_check failure', 'list_zip_check failure']
        }
    )
    # print('\nexpected_df\n', expected_df)
    # print('\nprocess_df\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False



# pytest -v -s --tb=short tests/unit/test_list_zip.py::test_list_zip_check_ensure_passing
def test_list_zip_check_ensure_passing():
    '''
    This test passes because there are zero ZipCode(s) which are not present 
    in their respective lists.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Result = Indication of a valid/invalid value.
    Reason = Why a record passed/failed

    Column   | Values           | Result        | Reason
    --------------------------------------------------------------------------------
    ZipCode  | '99999-9997'     | Passing       |
    ZipCode  | '11111-0111'     | Passing       |
    ZipCode  | '11111-2222'     | Passing       |
    ZipCode  | '12345-9999'     | Passing       |
    '''

    pros_zips = ['99997', '10112', '66666',]
    dms_zips = ['11111', '0', '-1', '.1', '12345']

    df_raw = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, ""],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99997-9997', '11111-0111', '11111-2222', '12345-9999'],# <-- Column being tested.
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = list_zip_check(df=df_raw, prospect_zips=pros_zips, dms_zips=dms_zips, zip_col='ZipCode')

    expected_df = pd.DataFrame(
        {
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],# <-- Column being tested.
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99997-9997', '11111-0111', '11111-2222', '12345-9999'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            "Reason_for_failure": [None, None, None, None]
        }
    )
    # print('\nexpected_df\n', expected_df)
    # print('\nprocess_df\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True