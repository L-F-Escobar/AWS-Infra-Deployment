import sys
import pandas as pd
import numpy as np
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import find_empty_recalls, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal


# pytest -v -s --tb=short tests/unit/test_empty_recalls.py::test_empty_recall_ensure_failing
def test_empty_recall_ensure_failing():
    '''
    This test fails because column 'VDP-08 has 2 entries that are not valid values.

    DESK CHECK BELOW
    ----------------
    VDP_08 = Column whose cell values are being evaluated. 
    Valid = Indicating if the value is passing or failing.

    VDP_08            | Valid
    --------------------------------
    air bags          | Valid
    tires             | Valid
    np.nan            | Invalid <--- Failing
    ""                | Invalid
    '''
    df_raw = pd.DataFrame(
        {
            "VDP_08": ["air bags", "tires", np.nan, ""], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = find_empty_recalls(df=df_raw, vin_col='VDP_08')

    expected_df = pd.DataFrame(
        {
            "VDP_08": ["air bags", "tires", np.nan, np.nan,], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, None , 'find_empty_recalls failure', 'find_empty_recalls failure']
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 




# pytest -v -s --tb=short tests/unit/test_empty_recalls.py::test_empty_recall_ensure_passing
def test_empty_recall_ensure_passing():
    '''
    This test fails because column 'VDP-08 has 2 entries that are not valid values.

    DESK CHECK BELOW
    ----------------
    VDP_08 = Column whose cell values are being evaluated. 
    Valid = Indicating if the value is passing or failing.

    VDP_08            | Valid
    --------------------------------
    air bags          | Valid
    tires             | Valid
    death trap        | Valid
    death on wheels   | Valid
    '''
    df_raw = pd.DataFrame(
        {
            "VDP_08": ["air bags", "666", 'death trap', "death on wheels"], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = find_empty_recalls(df=df_raw, vin_col='VDP_08')

    expected_df = pd.DataFrame(
        {
            "VDP_08": ["air bags", "666", 'death trap', "death on wheels"], # <-- this column is being checked.
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, None , None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True