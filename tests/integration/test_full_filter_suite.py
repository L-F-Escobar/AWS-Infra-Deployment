import sys
import pandas as pd
import numpy as np
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import (
    add_reason_for_failure_col,
    remove_seed_records,
    check_passing,
    
    find_NaN,
    find_empty_recalls,
    last_name_checker,
    list_zip_check,
    customer_type_percentages_check,
    multiple_address_check,
    recent_contact_check,
    email_checker,
    distance_checker
)
from pandas.util.testing import assert_frame_equal


FILTERS = ['luis@recallmasters.com','lfescoba@uci.edu','l.driver.escobar@gmail.com',]
LNAME_FILTERS = ['associates', 'associate', 'inc', 'automotive', 'dealership', 'dealer', 'llc']


# pytest -v -s --tb=short tests/integration/test_full_filter_suite.py::test_full_filter_suite_ensure_passing_all
def test_full_filter_suite_ensure_passing_all():
    '''
        Every single filter will pass on this test. 
    '''

    find_NaN_check = ['EMAIL', 'customer_type', 'Distance']

    pros_zips = ['99997', '10112', '66666',]
    dms_zips = ['11111', '0', '-1', '.1', '12345']

    RM_UI_percents = {'total': '300', 'prospect': '45', 'lapsed': '0', 'recent': '0', 
                'sns': '0', 'l1': '20', 'l2': '20', 'l3': '15', 'l4': '0', 
                'l5': '0', 'target_date': '09/06/2019', 'expiration_date': 0, 'delete': 0}

    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            "address": ["abc dr", "ABC ST", "aBc St", "abc sT"], 
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], 
            "state": ["ca", "Ca", "cA", "CA"], 
            "lname1": ["rutland beard florist", "adko ", 'Sullivan', "Escobar"],
            'Distance': [11, 1, 45, 0],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", "death machine", "windows"],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99997-9997', '11111-0111', '11111-2222', '12345-9999'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', '666_lfescoba@uci.edu', 'LFESCOBA_666@UCI.EDU']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df = remove_seed_records(df=df_raw)

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

    process_df, passing = distance_checker(df=df_raw, distance_col='Distance', max_distance=45, customer_type="PROSPECT")

    process_df, passing = distance_checker(df=process_df, distance_col='Distance', max_distance=45, customer_type="dms")

    process_df, passing = email_checker(df=process_df, email_col='EMAIL', filters=FILTERS)

    process_df, passing = find_empty_recalls(df=process_df, vin_col='VDP_08')

    process_df, passing = find_NaN(df=process_df, check_list=find_NaN_check)

    process_df, passing = last_name_checker(df=process_df, lname_col='lname1', filters=LNAME_FILTERS)

    process_df, passing = list_zip_check(df=process_df, prospect_zips=pros_zips, dms_zips=dms_zips, zip_col='ZipCode')

    process_df, passing = multiple_address_check(df=process_df, max_allowed=3)

    process_df, passing = customer_type_percentages_check(df=process_df, col_name='customer_type', percentages_extract_from_RM_ui=RM_UI_percents)

    process_df, passing = recent_contact_check(mail_file_df=process_df, pandas_df=pandas_df, recent_included=True, max_days=105)

    passing = check_passing(df=process_df, complete=True)

    expected_df = pd.DataFrame(
        {
            'DropDate' : ['20190628', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            "address": ["abc dr", "ABC ST", "aBc St", "abc sT"], 
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], 
            "state": ["ca", "Ca", "cA", "CA"], 
            "lname1": ["rutland beard florist", "adko ", 'Sullivan', "Escobar"],
            'Distance': [11, 1, 45, 0],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", "death machine", "windows"],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99997-9997', '11111-0111', '11111-2222', '12345-9999'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':['l@gmail.com', 'L@GMAIL.COM', '666_lfescoba@uci.edu', 'LFESCOBA_666@UCI.EDU'],
            "Reason_for_failure": [None, None, None, None]
        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == True 




# pytest -v -s --tb=short tests/integration/test_full_filter_suite.py::test_full_filter_suite_ensure_failing_all
def test_full_filter_suite_ensure_failing_all():
    '''
        Every single filter will fail this test.
    '''

    find_NaN_check = ['EMAIL', 'customer_type', 'Distance']

    pros_zips = ['99997', '10112', '66666',]
    dms_zips = ['11111', '0', '-1', '.1', '12345']

    RM_UI_percents = {'total': '300', 'prospect': '15', 'lapsed': '0', 'recent': '0', 
                'sns': '0', 'l1': '50', 'l2': '20', 'l3': '15', 'l4': '0', 
                'l5': '0', 'target_date': '09/06/2019', 'expiration_date': 0, 'delete': 0}

    df_raw = pd.DataFrame(
        {   
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            "address": ["abc st", "ABC ST", "aBc St", "abc sT"], 
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], 
            "state": ["ca", "Ca", "cA", "CA"], 
            "lname1": ["rutland beard florist", "adko llc", 'Sullivan', "Escobar"],
            'Distance': [46, 1, 46, 0],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", "death machine", np.nan],
            "home_phone": ["some value", np.nan, "", "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '11111-2222', '12345-9999'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": ['', '', '', ''],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':["", 'luis@recallmasters.com', '666_lfescoba@uci.edu', 'LFESCOBA_666@UCI.EDU']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df = remove_seed_records(df=df_raw)

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

    process_df, passing = distance_checker(df=process_df, distance_col='Distance', max_distance=45, customer_type="PROSPECT")

    process_df, passing = distance_checker(df=process_df, distance_col='Distance', max_distance=45, customer_type="dms")

    process_df, passing = email_checker(df=process_df, email_col='EMAIL', filters=FILTERS)

    process_df, passing = find_empty_recalls(df=process_df, vin_col='VDP_08')

    process_df, passing = find_NaN(df=process_df, check_list=find_NaN_check)

    process_df, passing = last_name_checker(df=process_df, lname_col='lname1', filters=LNAME_FILTERS)

    process_df, passing = list_zip_check(df=process_df, prospect_zips=pros_zips, dms_zips=dms_zips, zip_col='ZipCode')

    process_df, passing = multiple_address_check(df=process_df, max_allowed=3)

    process_df, passing = customer_type_percentages_check(df=process_df, col_name='customer_type', percentages_extract_from_RM_ui=RM_UI_percents)

    process_df, passing = recent_contact_check(mail_file_df=process_df, pandas_df=pandas_df, recent_included=True, max_days=105)

    passing = check_passing(df=process_df, complete=True)

    expected_df = pd.DataFrame(
        {
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            "address": ["abc st", "ABC ST", "aBc St", "abc sT"], 
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], 
            "state": ["ca", "Ca", "cA", "CA"], 
            "lname1": ["rutland beard florist", "adko llc", 'Sullivan', "Escobar"],
            'Distance': [46, 1, 46, 0],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "VDP_08": ["air bags", "tires", "death machine", np.nan],
            "home_phone": ["some value", np.nan, np.nan, "Another value"],
            "ZipCode": ['99999-9997', '11111-0111', '11111-2222', '12345-9999'],
            "business": [np.nan, np.nan, np.nan, np.nan],
            "land_line": [np.nan, np.nan, np.nan, np.nan],
            "cell_phone": ['12', 66, 23.423, '768.678'],
            'EMAIL':[np.nan, 'luis@recallmasters.com', '666_lfescoba@uci.edu', 'LFESCOBA_666@UCI.EDU'],
            "Reason_for_failure": [
                                    'distance_checker failure, find_NaN failure, list_zip_check failure, percentage_check failure, recent_contact_check failure', 
                                    'email_checker failure, last_name_checker failure, percentage_check failure', 
                                    'distance_checker failure, percentage_check failure', 
                                    'find_empty_recalls failure, multiple_address_check failure, percentage_check failure'
                                  ]

        }
    )
    # print('\nexpected_df_check1\n', expected_df)
    # print('\nprocess_df_check1\n', process_df)

    assert_frame_equal(expected_df, process_df)
    assert passing == False 