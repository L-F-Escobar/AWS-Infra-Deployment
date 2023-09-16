import sys
import pandas as pd
import numpy as np
import os
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import recent_contact_check, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal


# pytest -v -s --tb=short tests/unit/test_recently_contacted.py::test_recent_contact_check_less_than_105_days_ensure_failing
def test_recent_contact_check_less_than_105_days_ensure_failing():
    '''
    This test ensures that despite the fact that all vins are present within the df_raw & pandas_df,
    that the DropDate is less than 105 days. This test proves that if  
    (Drop_Date - mailed.global.last_date) < 105 days, then, test is failing.

    This test fails because there is a record included in df_raw which has been mailed to 
    within the last 105 days.

    DESK CHECK BELOW
    ----------------
    df_raw col = The columns this test is checking.
    df_raw col value = The values within the cell(s).
    df_raw Vin matched to pandas_df Vin = If a record in the df_raw matches another in the pandas_df.
    Days since last mailed = How long its been since that record has been mailed to.
    Result: Whether the record is passing/failing.
    recent_included = True. Means that recently mailed cannot be included.
    max_days = 105. Means that a record has to wait at least 105 days to be mailed again.

    df_raw col | df_raw col value | df_raw Vin matched to pandas_df Vin     | Days since last mailed    | Result
    ---------------------------------------------------------------------------------------------------------
    DropDate   | '20191107'       | True -> pandas_df date: 2019-10-11      | 27                        | Failing <---
    DropDate   | '20150912'       | True -> pandas_df date: 2019-10-11      | 1490                      | Passing
    DropDate   | '20160104'       | True -> pandas_df date: 2019-10-11      | 1376                      | Passing
    DropDate   | '20111004'       | True -> pandas_df date: 2019-10-11      | 2929                      | Passing
    '''
    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
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

    pandas_df = pd.DataFrame(
        {   
            'test': [11, 100, 50, 49],
            'test1': ['prospect', 'l1', 'l2', 'l3'],
            "test3": ["air bags", "tires", np.nan, ""],
            "excluded.filter_name": [np.nan, np.nan, np.nan, np.nan],
            "vehicle.vin": ['WBADT63473CK37045', '5UXZV4C54CL744905', '2134123413242341', 'WBADT43463G023130'],
            "mailed.global.last_date": ['2019-10-21', '2019-10-11', '2019-10-11', '2019-10-07']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = recent_contact_check(mail_file_df=df_raw, pandas_df=pandas_df, recent_included=True, max_days=105)

    expected_df = pd.DataFrame(
        {
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": ['recent_contact_check failure', None ,None, None]
        }
    )
    # print('\nexpected_df\n', expected_df)
    # print('\nprocess_df\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 





# pytest -v -s --tb=short tests/unit/test_recently_contacted.py::test_recent_contact_check_greater_than_105_days_ensure_passing
def test_recent_contact_check_greater_than_105_days_ensure_passing():
    '''
    This contains a record DropDate 20190628 which is exactly 105 days from date 
    mailed.global.last_date 2019-10-11. Therefore, all records qualify to be mailed to.

    All vins in df_raw are accounted for. 

    DESK CHECK BELOW
    ----------------
    df_raw col = The columns this test is checking.
    df_raw col value = The values within the cell(s).
    df_raw Vin matched to pandas_df Vin = If a record in the df_raw matches another in the pandas_df.
    Days since last mailed = How long its been since that record has been mailed to.
    Result: Whether the record is passing/failing.
    recent_included = True. Means that recently mailed cannot be included.
    max_days = 105. Means that a record has to wait at least 105 days to be mailed again.

    df_raw col | df_raw col value | df_raw Vin matched to pandas_df Vin     | Days since last mailed    | Result
    ---------------------------------------------------------------------------------------------------------
    DropDate   | '20190628'       | True -> pandas_df date: 2019-10-11      | 105                       | Passing
    DropDate   | '20150912'       | True -> pandas_df date: 2019-10-11      | 1490                      | Passing
    DropDate   | '20160104'       | True -> pandas_df date: 2019-10-11      | 1376                      | Passing
    DropDate   | '20111004'       | True -> pandas_df date: 2019-10-11      | 2929                      | Passing
    '''
    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
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

    pandas_df = pd.DataFrame(
        {   
            'test': [11, 100, 50, 49],
            'test1': ['prospect', 'l1', 'l2', 'l3'],
            "test3": ["air bags", "tires", np.nan, ""],
            "excluded.filter_name": [np.nan, np.nan, np.nan, np.nan],
            "vehicle.vin": ['WBADT63473CK37045', '5UXZV4C54CL744905', '2134123413242341', 'WBADT43463G023130'],
            "mailed.global.last_date": ['2019-10-21', '2019-10-11', '2019-10-11', '2019-10-07']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = recent_contact_check(mail_file_df=df_raw, pandas_df=pandas_df, recent_included=True, max_days=105)

    expected_df = pd.DataFrame(
        {
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, None ,None, None]
        }
    )
    # print('\nexpected_df\n', expected_df)
    # print('\nprocess_df\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 





# pytest -v -s --tb=short tests/unit/test_recently_contacted.py::test_recent_contact_check_vins_missing_ensure_failing
def test_recent_contact_check_vins_missing_ensure_failing():
    '''
    This contains a record DropDate 20190628 which is exactly 105 days from date 
    mailed.global.last_date 2019-10-11. Therefore, all records qualify to be mailed to.

    However, this test includes VINs in the df_raw which are unaccounted for in the 
    pandas_df. Therefore, it will fail. VIN 1111111111111111 is not accounted for in 
    the panda_df.

    DESK CHECK BELOW
    ----------------
    df_raw col = The columns this test is checking.
    df_raw col value = The values within the cell(s).
    df_raw Vin matched to pandas_df Vin = If a record in the df_raw matches another in the pandas_df.
    Days since last mailed = How long its been since that record has been mailed to.
    Result: Whether the record is passing/failing.
    recent_included = True. Means that recently mailed cannot be included.
    max_days = 105. Means that a record has to wait at least 105 days to be mailed again.

    df_raw col | df_raw col value | df_raw Vin matched to pandas_df Vin     | Days since last mailed    | Result
    ---------------------------------------------------------------------------------------------------------
    DropDate   | '20190628'       | True -> pandas_df date: 2019-10-11      | 105                       | Passing
    DropDate   | '20150912'       | True -> pandas_df date: 2019-10-11      | 1490                      | Passing
    DropDate   | '20160104'       | True -> pandas_df date: 2019-10-11      | 1376                      | Passing
    DropDate   | '20111004'       | True -> pandas_df date: 2019-10-11      | 2929                      | Passing

    df_raw col | df_raw col value   | df_raw Vin matched to pandas_df Vin     | Result
    ---------------------------------------------------------------------------------------------------------
    VIN_ID   | '5UXZV4C54CL744905'  | True                                    | Passing
    VIN_ID   | '5UXZV4C54CL744905'  | True                                    | Passing
    VIN_ID   | '5UXZV4C54CL744905'  | True                                    | Passing
    VIN_ID   | '1111111111111111'   | False                                   | Failing <--
    '''
    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '1111111111111111'],
            'Distance': [11, 100, 50, 49],
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

    pandas_df = pd.DataFrame(
        {   
            'test': [11, 100, 50, 49],
            'test1': ['prospect', 'l1', 'l2', 'l3'],
            "test3": ["air bags", "tires", np.nan, ""],
            "excluded.filter_name": [np.nan, np.nan, np.nan, np.nan],
            "vehicle.vin": ['WBADT63473CK37045', '5UXZV4C54CL744905', '2134123413242341', 'WBADT43463G023130'],
            "mailed.global.last_date": ['2019-10-21', '2019-10-11', '2019-10-11', '2019-10-07']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = recent_contact_check(mail_file_df=df_raw, pandas_df=pandas_df, recent_included=True, max_days=105)

    expected_df = pd.DataFrame(
        {
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '1111111111111111'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, None ,None, 'recent_contact_check failure']
        }
    )
    # print('\nexpected_df\n', expected_df)
    # print('\nprocess_df\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 




# pytest -v -s --tb=short tests/unit/test_recently_contacted.py::test_recent_contact_check_vins_missing_ensure_passing
def test_recent_contact_check_vins_missing_ensure_passing():
    '''
        This contains a record DropDate 20190628 which is exactly 105 days from date 
        mailed.global.last_date 2019-10-11. Therefore, all records qualify to be mailed to.

        All VINs accounted for as well. 
    '''
    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', 'WBADT63473CK37045', 'WBADT43463G023130', '2134123413242341'],
            'Distance': [11, 100, 50, 49],
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

    pandas_df = pd.DataFrame(
        {   
            'test': [11, 100, 50, 49],
            'test1': ['prospect', 'l1', 'l2', 'l3'],
            "test3": ["air bags", "tires", np.nan, ""],
            "excluded.filter_name": [np.nan, np.nan, np.nan, np.nan],
            "vehicle.vin": ['WBADT63473CK37045', '5UXZV4C54CL744905', '2134123413242341', 'WBADT43463G023130'],
            "mailed.global.last_date": ['2019-10-21', '2019-10-11', '2019-10-11', '2019-10-07']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = recent_contact_check(mail_file_df=df_raw, pandas_df=pandas_df, recent_included=True, max_days=105)

    expected_df = pd.DataFrame(
        {
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', 'WBADT63473CK37045', 'WBADT43463G023130', '2134123413242341'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", np.nan, np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', 'lfescoba@uci.edu', 'LFESCOBA@UCI.EDU'],
            "Reason_for_failure": [None, None ,None, None]
        }
    )
    # print('\nexpected_df\n', expected_df)
    # print('\nprocess_df\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 