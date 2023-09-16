import sys
import pandas as pd
import numpy as np
import os
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import customer_type_percentages_check, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal


# pytest -v -s --tb=short tests/unit/test_plan_percentages.py::test_percentage_check_ensure_failing
def test_percentage_check_ensure_failing():
    '''
    This test fails because there are a greater percentage of L3 customers in the mail file than 
    the RM UI plans page + surge roll over. 

    ((L3 customer percentage in mail file) > (RM UI plan + surge roll)) --> fail

    DESK CHECK BELOW
    ----------------
    RM UI = Percentage plan extracted from RM UI site.
    Mail File = Percentages according to customer type found in file.
    Surge Roll = Excess amount of %'s that can carry over to the next customer type.

    Customer Type           | RM UI         | Mail File         | Surge Roll
    ------------------------------------------------------------------------
    Prospect                | 45%           | 25%               | 20%
    L1                      | 45% + 20%     | 25%               | 40%
    L2                      | 0% + 40%      | 25%               | 15%
    L3                      | 0% + 15%      | 25%               | -10% <--- Failing 

    '''
    RM_UI_percents = {'total': '300', 'prospect': '45', 'lapsed': '45', 'recent': '8', 
                'sns': '5', 'l1': '45', 'l2': '0', 'l3': '0', 'l4': '5', 
                'l5': '5', 'target_date': '09/06/2019', 'expiration_date': 0, 'delete': 0}

    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'], # This column produces the Mail File percentage
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

    process_df, passing = customer_type_percentages_check(df=df_raw, col_name='customer_type', percentages_extract_from_RM_ui=RM_UI_percents)

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
            "Reason_for_failure": ['percentage_check failure', 'percentage_check failure' ,'percentage_check failure', 'percentage_check failure']
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 




# pytest -v -s --tb=short tests/unit/test_plan_percentages.py::test_percentage_check_over_100_Percent_ensure_failing
def test_percentage_check_over_100_Percent_ensure_failing():
    '''
    This test fails because the RM UI percentage plan is asking for customer type totals which 
    are over 100%.

    DESK CHECK BELOW
    ----------------
    RM UI = Percentage plan extracted from RM UI site.
    100% Total = Total amount of percentage possible.

    Customer Type       | RM UI     | 100% Total
    --------------------------------------------
    Prospect            | 45%       | 100-45 = 55%
    Lapsed              | 45%       | 55-45 = 10%
    Recent              | 8%        | 10-8 = 2%
    SNS                 | 5%        | 2-5= -3% <-- test fails here
    L1                  | 45%       | -3-45 = -48%
    L2                  | 0%        | -48-0 = -48%
    L3                  | 0%        | -48-0 = -48%
    L4                  | 5%        | -48-5 = -63%
    L5                  | 5%        | -63-5 = -68&
    '''
    RM_UI_percents = {'total': '300', 'prospect': '45', 'lapsed': '45', 'recent': '8', 
                'sns': '5', 'l1': '45', 'l2': '0', 'l3': '10', 'l4': '5', 
                'l5': '5', 'target_date': '09/06/2019', 'expiration_date': 0, 'delete': 0}

    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'], # This column produces the Mail File percentage
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

    process_df, passing = customer_type_percentages_check(df=df_raw, col_name='customer_type', percentages_extract_from_RM_ui=RM_UI_percents)

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
            "Reason_for_failure": ['percentage_check failure', 'percentage_check failure' ,'percentage_check failure', 'percentage_check failure']
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 




# pytest -v -s --tb=short tests/unit/test_plan_percentages.py::test_percentage_check_no_surge_ensure_passing
def test_percentage_check_no_surge_ensure_passing():
    '''
    This test passes -> check Desk Check.
    
    DESK CHECK BELOW
    ----------------
    RM UI = Percentage plan extracted from RM UI site.
    Mail File = Percentages according to customer type found in file.
    Surge Roll = Excess amount of %'s that can carry over to the next customer type.

    Customer Type           | RM UI         | Mail File         | Surge Roll
    ------------------------------------------------------------------------
    Prospect                | 25%           | 25%               | 0%
    L1                      | 25%           | 25%               | 0%
    L2                      | 25%           | 25%               | 0%
    L3                      | 25%           | 25%               | 0%  <-- Passing -->

    '''
    RM_UI_percents = {'total': '300', 'prospect': '25', 'lapsed': '0', 'recent': '0', 
                'sns': '0', 'l1': '25', 'l2': '25', 'l3': '25', 'l4': '0', 
                'l5': '0', 'target_date': '09/06/2019', 'expiration_date': 0, 'delete': 0}

    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'], # This column produces the Mail File percentage
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

    process_df, passing = customer_type_percentages_check(df=df_raw, col_name='customer_type', percentages_extract_from_RM_ui=RM_UI_percents)

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
            "Reason_for_failure": [None, None, None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 





# pytest -v -s --tb=short tests/unit/test_plan_percentages.py::test_percentage_check_with_surge_ensure_passing
def test_percentage_check_with_surge_ensure_passing():
    '''
    This test passes -> check Desk Check.
    
    DESK CHECK BELOW
    ----------------
    RM UI = Percentage plan extracted from RM UI site.
    Mail File = Percentages according to customer type found in file.
    Surge Roll = Excess amount of %'s that can carry over to the next customer type.

    Customer Type           | RM UI         | Mail File         | Surge Roll
    ------------------------------------------------------------------------
    Prospect                | 30%           | 25%               | 5%
    L1                      | 25% + 5%      | 25%               | 5%%
    L2                      | 25% + 5%      | 25%               | 5%
    L3                      | 20% + 5%      | 25%               | 0%  <-- Passing -->

    '''
    RM_UI_percents = {'total': '300', 'prospect': '30', 'lapsed': '0', 'recent': '0', 
                'sns': '0', 'l1': '25', 'l2': '25', 'l3': '20', 'l4': '0', 
                'l5': '0', 'target_date': '09/06/2019', 'expiration_date': 0, 'delete': 0}

    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'], # This column produces the Mail File percentage
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

    process_df, passing = customer_type_percentages_check(df=df_raw, col_name='customer_type', percentages_extract_from_RM_ui=RM_UI_percents)

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
            "Reason_for_failure": [None, None, None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 