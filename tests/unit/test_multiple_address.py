import sys
import pandas as pd
import numpy as np
import os
sys.path.append(".")
sys.path.append("./src")
from src.func.filter import multiple_address_check, add_reason_for_failure_col
from pandas.util.testing import assert_frame_equal

# pytest -v -s --tb=short tests/unit/test_multiple_address.py::test_max_3_addresses_ensure_failing
def test_max_3_addresses_ensure_failing():
    '''
    This test fails because the same address appears more than 3 times.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Count = The total amount of times the specific address value appears.
    Result = Indication of a valid/invalid value.

    Columns                 | Values                    | Count     | Result
    --------------------------------------------------------------------------------
    address + city + state  | abc st aliso viejo ca     | 1         | Passing
    address + city + state  | abc st aliso viejo ca     | 2         | Passing
    address + city + state  | abc st aliso viejo ca     | 3         | Passing
    address + city + state  | abc st aliso viejo ca     | 4         | Failing <---
    '''

    df_raw = pd.DataFrame(
        {
            "address": ["abc st", "ABC ST", "aBc St", "abc sT"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, ""], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, '', "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = multiple_address_check(df=df_raw, max_allowed=3)

    expected_df = pd.DataFrame(
        {
            "address": ["abc st", "ABC ST", "aBc St", "abc sT"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, np.nan], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "Reason_for_failure": [None, None , None, 'multiple_address_check failure']
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)
    
    assert_frame_equal(process_df, expected_df)
    assert passing == False



# pytest -v -s --tb=short tests/unit/test_multiple_address.py::test_max_3_addresses_ensure_passing
def test_max_3_addresses_ensure_passing():
    '''
    This test passes because no address appears more than 3 times.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Count = The total amount of times the specific address value appears.
    Result = Indication of a valid/invalid value.

    Columns                 | Values                    | Count     | Result
    --------------------------------------------------------------------------------
    address + city + state  | abc dr aliso viejo ca     | 1         | Passing
    address + city + state  | abc st aliso viejo ca     | 1         | Passing
    address + city + state  | abc st aliso viejo ca     | 2         | Passing
    address + city + state  | abc st aliso viejo ca     | 3         | Passing
    '''

    df_raw = pd.DataFrame(
        {
            "address": ["abc dr", "ABC ST", "aBc St", "abc sT"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, ""], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, '', "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = multiple_address_check(df=df_raw, max_allowed=3)

    expected_df = pd.DataFrame(
        {
            "address": ["abc dr", "ABC ST", "aBc St", "abc sT"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, np.nan], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "Reason_for_failure": [None, None , None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)
    
    assert_frame_equal(process_df, expected_df)
    assert passing == True



# pytest -v -s --tb=short tests/unit/test_multiple_address.py::test_max_1_addresses_ensure_failing
def test_max_1_addresses_ensure_failing():
    '''
    This test fails because an address appears more than once.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Count = The total amount of times the specific address value appears.
    Result = Indication of a valid/invalid value.

    Columns                 | Values                    | Count     | Result
    --------------------------------------------------------------------------------
    address + city + state  | abc dr aliso viejo ca     | 1         | Passing
    address + city + state  | abc st aliso viejo ca     | 1         | Passing
    address + city + state  | abc alley aliso viejo ca  | 1         | Passing
    address + city + state  | abc st aliso viejo ca     | 2         | Failing <---
    '''

    df_raw = pd.DataFrame(
        {
            "address": ["abc dr", "ABC ST", "aBc alley", "abc sT"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, ""], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, '', "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = multiple_address_check(df=df_raw, max_allowed=1)

    expected_df = pd.DataFrame(
        {
            "address": ["abc dr", "ABC ST", "aBc alley", "abc sT"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, np.nan], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "Reason_for_failure": [None, None , None, 'multiple_address_check failure']
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)
    
    assert_frame_equal(process_df, expected_df)
    assert passing == False



# pytest -v -s --tb=short tests/unit/test_multiple_address.py::test_max_1_addresses_ensure_passing
def test_max_1_addresses_ensure_passing():
    '''
    This test passes because no address appears more than once.

    DESK CHECK BELOW
    ----------------
    Columns = The columns this test is checking.
    Values = The values within the cell(s).
    Count = The total amount of times the specific address value appears.
    Result = Indication of a valid/invalid value.

    Columns                 | Values                    | Count     | Result
    --------------------------------------------------------------------------------
    address + city + state  | abc dr aliso viejo ca     | 1         | Passing
    address + city + state  | abc st aliso viejo ca     | 1         | Passing
    address + city + state  | abc alley aliso viejo ca  | 1         | Passing
    address + city + state  | abc ave aliso viejo ca    | 1         | Passing
    '''

    df_raw = pd.DataFrame(
        {
            "address": ["abc dr", "ABC ST", "aBc alley", "abc ave"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, ""], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, '', "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000']
        }
    )

    df_raw = add_reason_for_failure_col(df=df_raw, new_col_name='Reason_for_failure')

    process_df, passing = multiple_address_check(df=df_raw, max_allowed=1)

    expected_df = pd.DataFrame(
        {
            "address": ["abc dr", "ABC ST", "aBc alley", "abc ave"], # <-- this column is being checked.
            "city": ["Aliso Viejo", "Aliso Viejo", "Aliso Viejo", "Aliso Viejo"], # <-- this column is being checked.
            "state": ["ca", "Ca", "cA", "CA"], # <-- this column is being checked.
            "VDP_08": ["air bags", "tires", np.nan, np.nan], 
            'DropDate' : ['20191107', '20150912', '20160104', '20111004'],
            'VIN_ID' : ['5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905', '5UXZV4C54CL744905'],
            'Distance': [11, 100, 50, 49],
            'customer_type': ['prospect', 'l1', 'l2', 'l3'],
            "home_phone": ["some value", np.nan, np.nan, "Another value"], 
            "ZipCode": ['99999-9997', '11111-0111', '66666-6000', '92656-2000'],
            "Reason_for_failure": [None, None , None, None]
        }
    )
    # print('\nprocess_df\n', process_df)
    # print('\nexpected_df\n', expected_df)
    
    assert_frame_equal(process_df, expected_df)
    assert passing == True