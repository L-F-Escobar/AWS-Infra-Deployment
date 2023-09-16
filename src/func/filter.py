import collections
import os
import datetime
import numpy as np
import pandas as pd


# All consts used for easily testing only. ~~TEMPORARY~~
RENAME = {'VDP_10': 'make', 'VDP_04': 'make', 'VDP_03':'vehicle_year',
          'VDP_05':'vehicle_model', 'VDP_06':'nhtsa_id', 'VDP_07':'oem_id',
          'VDP_08':'recall_name', 'VDP_20':'appointment 3 data', 
          'VDP_21':'appointment 2 description', 'VDP_22':'toll free phone', 
          'VDP_23':'dealer name', 'VDP_24':'dealer address', 
          'VDP_25':'dealer city state zip', 'VDP_26':'weekday service hours', 
          'VDP_27':'weekend service hours', 'VDP_28':'Dealer Web appointment URL',
          'VDP_29':'appointment 10 data', 'VDP_30':'appointment 9 description', 
          'VDP_31':'appointment 3 description', 'VDP_32':'appointment 4 description', 
          'VDP_33':'exclusive benefits', 'VDP_34':'locator', 'VDP_35':'return address name', 
          'VDP_36':'appointment 1 description', 'VDP_37':'make', 'VDP_38':'disclaimer',
          'VDP_39':'appointment 7 description', 'VDP_42':'return address phone',
          'VDP_46':'appointment 5 description', 'VDP_47':'signature name',
          'VDP_48':'signature title', 'VDP_49':'signature phone', 'VDP_50':'signature email',
          'VDP_51':'OEM abbreviation'
}

VIN_COL = 'VDP_08'

LNAME_COL = 'LNAME1'

EMAIL_COL = 'EMAIL'

DISTANCE_COL = "Distance"

LNAME_FILTERS = ['associates', 'associate', 'inc', 'automotive', 'dealership', 'dealer', 'llc']

# 48 total column checks. 
BLANK_CHECK = ['VIN_ID', 'VDP_10', 'VDP_09', 'VDP_04', 'SEQ_ID',
               'address', 'city', 'state', 'ZipCode', 'POSTNET',
               'CustomerUniqueIdentifier', 'VDP_DATE', 'VDP_02',
               'VDP_03', 'VDP_05', 'VDP_06', 'VDP_08', 'Cust_service',
               'VDP_20', 'VDP_21', 'VDP_22', 'VDP_23', 'VDP_24',
               'VDP_25', 'VDP_26', 'VDP_27', 'VDP_28', 'VDP_29',
               'VDP_30', 'VDP_31', 'VDP_32', 'VDP_33', 'VDP_34',
               'VDP_35', 'VDP_36', 'VDP_37', 'VDP_39', 'VDP_42',
               'VDP_46', 'Datasource', 'DropDate', 'Drop', 'customer_type',
               'recall_id', 'Distance', 'VDP_47', 'VDP_48', 'VDP_51', 'LNAME1'
]
# print(len(BLANK_CHECK))
FAILURE_COL_NAME="Reason_for_failure"


def read_csv(file_path=None):
    return pd.read_csv(file_path)


def rename(df=None, filter_dict=None):
    return df.rename(columns=filter_dict)


def find_empty_recalls(df=None, vin_col=None):
    """
    Function finds all VINs without an open recall.

    Args:
        df (pandas) : df to search
        vin_col (str) : The column of the VIN recall reason.

    Returns:
        df (pandas) : df with passing/failing stamp appended.
        passing (bool) : if the df contains 1 or more VINs without an open recall
                         passing will equal False.
    """
    passing = True
    df_mod = df.replace('', np.nan)

    # If specific column is within the df.
    if vin_col in df_mod.columns:
        # Iterate over all the rows in the df.
        for index, row in df_mod.iterrows():
            # If this cell is np.nan
            if pd.isnull(row[vin_col]):
                # Stamp failure of this cell.
                if df_mod.at[index, FAILURE_COL_NAME] == None:
                    df_mod.at[index, FAILURE_COL_NAME] = 'find_empty_recalls failure'
                else:
                    df_mod.at[index, FAILURE_COL_NAME] = str(df.at[index, FAILURE_COL_NAME]) + ', find_empty_recalls failure'
    else:
        print(f"find_empty_recalls test missing column {vin_col}. Test cannot execute.")

    passing = check_passing(df=df_mod, failure_reason='find_empty_recalls failure')

    return df_mod, passing


def find_NaN(df=None, check_list=None):
    """
    Function checks a df against a list of items. If the item(s) in 
    the passed in list are present in the df, then the function checks
    for whether those cell values are empty/blank/NaN. 

    Args:
        df (pandas) : Df mail file to search.
        check_list (list) : Columns which should be checked.

    Returns:
        df (pandas) : Df with passing/failing stamp appended.
        passing (bool) : If the df contains 1 or more missing cells (Row x Col) 
                         which should not be empty, passing = False.
    """
    passing = True
    df_columns = df.columns
    df_mod = df.replace('', np.nan)
    
    # Iterate over all the rows in the df.
    for index, row in df_mod.iterrows():
        # Iterate over all the items that should not be NaN.
        for item in check_list:
            # Ensure the col is present in df before checking.
            if item in df_columns:
                # If the value is NaN.
                if pd.isnull(row[item]):
                    # Stamp failure of this cell.
                    if df_mod.at[index, FAILURE_COL_NAME] == None:
                        df_mod.at[index, FAILURE_COL_NAME] = 'find_NaN failure'
                    else:
                        df_mod.at[index, FAILURE_COL_NAME] = str(df.at[index, FAILURE_COL_NAME]) + ', find_NaN failure'

    passing = check_passing(df=df_mod, failure_reason='find_NaN failure')

    return df_mod, passing


def last_name_checker(df=None, lname_col=LNAME_COL, filters=LNAME_FILTERS):
    """
    Function finds all/most last names which are not human.

    Args:
        df (pandas) : df to search.
        lname_col (str) : The column of the last name.
        filters (list) : all accepted key words to identify non-human last names.

    Returns:
        df (pandas) : df with 1 appended columns (Human Last Name (T/F))
        passing (bool) : if the df contains 1 or more Last Names which are 
                         determined to not be human, passing = False
    """
    passing = True
    df_mod = df.replace('', np.nan)
    df_columns = df_mod.columns

    # Iterate over all the rows in the df.
    for index, row in df_mod.iterrows():

        if lname_col in df_columns:

            if not(pd.isnull(row[lname_col])):
                lname_list = row[lname_col].lower().split()
            else:
                lname_list = []

            if (any(x in lname_list for x in filters)):
                # Stamp failure of this cell.
                if df_mod.at[index, FAILURE_COL_NAME] == None:
                    df_mod.at[index, FAILURE_COL_NAME] = 'last_name_checker failure'
                else:
                    df_mod.at[index, FAILURE_COL_NAME] = str(df.at[index, FAILURE_COL_NAME]) + ', last_name_checker failure'

    passing = check_passing(df=df_mod, failure_reason='last_name_checker failure')

    return df_mod, passing


def list_zip_check(df=None, prospect_zips=None, dms_zips=None, zip_col=None):
    """
    Function checks mail file column `ZipCode` to ensure that all
    zips fall in range of their respective radius. Acceptable 
    zip radius is pulled from 
    https://app.recallmasters.com/communications/XXXX/ & checked 
    against the passed in df. 

    Args:
        df (pandas) : a df which represents a remote s3 recallmasters bucket csv file.
        prospect_zips/dms_zips (list of STRINGS) : list of zips extracted from RM site.
        zip_col (str) : the column to check against.

    Returns:
        df (pandas) : df 
        passing (bool) : if the df contains 1 or more ZipCodes which are 
                         not contained in zip lists, then, passing = False
    """

    passing = True
    df_mod = df.replace('', np.nan)

    # Ensure zip column is present in the data frame.
    if zip_col in df_mod.columns:
        # Iterate over all the rows in the df.
        for index, row in df_mod.iterrows():
            # Get the 5 digit zip & the +4. Seperate into the 5 digit zip & +4.
            zip_range = row[zip_col].split('-')

            # Check all prospect customer types to ensure their zips are present.
            if row['customer_type'].lower() == 'prospect':
                if zip_range[0] not in prospect_zips:
                    if df_mod.at[index, FAILURE_COL_NAME] == None:
                        df_mod.at[index, FAILURE_COL_NAME] = 'list_zip_check failure'
                    else:
                        df_mod.at[index, FAILURE_COL_NAME] = str(df_mod.at[index, FAILURE_COL_NAME]) + ', list_zip_check failure'
            else: # Check all other customer types to ensure their zips are present.
                if zip_range[0] not in dms_zips:
                    if df_mod.at[index, FAILURE_COL_NAME] == None:
                        df_mod.at[index, FAILURE_COL_NAME] = 'list_zip_check failure' 
                    else:
                        df_mod.at[index, FAILURE_COL_NAME] = str(df_mod.at[index, FAILURE_COL_NAME]) + ', list_zip_check failure'

        passing = check_passing(df=df_mod, failure_reason='list_zip_check failure')
    else:# Column not present.
        passing = False

    return df_mod, passing


def customer_type_percentages_check(df=None, col_name=None, percentages_extract_from_RM_ui=None):
    """
    Function compares percentage customer types of a particular mail file and its corresponding plan outlay. 
    Whichever df is passed into this function will have a corresponding customer type plan 
    percentage target located at https://app.recallmasters.com/communications/xxxx/plans, which 
    will be passed into the function as percentages_extract_from_RM_ui. 

    This check is performed on customer types percentages, from left to right order of operations on 
    the plans page. This type of execution allows for a 'Surge roll over' mechanism which RMBO utilizes
    on the back end. 

    Ex. If on the RM UI website, Prospect target percentage is set to 25% & the mail file contains only
        20% Prospects, than the additional/extra 5% from the RM UI percentage will be rolled into the 
        next customer type. Since the order of operation is from left to right, the next customer is Lapsed.
        If on the RM UI website, Lapsed target percentage is set to 10%, due to the surge roll over mechanism, 
        the mail file being checked can contain up to 15% lapsed customer types. 

        If the mail file contains 14% Lapsed customer types, then 1% will surge over to the next customer type, 
        Recent. And so forth and so on until we reach the right most customer type on the plans page or we hit 100%
        capacity.

    This test is an "all or nothing". Either, all records pass or all records fail.

    Args:
        df (pandas) : The mail file being checked & tested.
        col_name (str) : The column to check, in this case, customer_type.
        percentages_extract_from_RM_ui (list of 2-tuples) : extracted percentages from RM plan page.

    Returns:
        df (pandas) : A return df whose last column indicates the results of this test.
        passing (bool) : The mail file can contain at most an equal amount of customer types percantages
                         found on the RM UI plans page + whatever surge roll over is present. If Lapses 
                         on the RM UI plans percantage is 10% + surge roll over happens to be 5%, then the 
                         maximum of Lapsed customer types that can be present in the mail file is 15%. So 
                         if (lapsed_mail_file_customer_type_percentage) > (lapsed_RM_UI_customer_type_percantage + surge_roll_over) -> fail.
    """
    passing = None
    df_mod = df.replace('', np.nan)
    all_customer_types = []

    # Iterate over all the rows in the df.
    for index, row in df_mod.iterrows():
        # Get all customer type values into all_customers list.
        all_customer_types.append(row[col_name].lower())
    
    # Use all_customer list to calculate percentages of each customer type & save result in cust_type_percents.
    customer_type_percents = collections.Counter(all_customer_types)

    # result = list of tuples -> [('prospect', 61.05610561056105), ]
    results = [(i, customer_type_percents[i] / len(all_customer_types) * 100.0) for i, count in customer_type_percents.most_common()]
    
    # When code enters this function we have the percentages of the mail file df and the extracted percentages from RM.
    # Now we need to compare those two to arrive at a conclusion. 
    passing = compare_percents(extracted_from_ui=percentages_extract_from_RM_ui, extracted_from_mail_file=results)

    # All or nothing pass/fail. 
    if passing == False:
        for index, row in df.iterrows():
            if df_mod.at[index, FAILURE_COL_NAME] == None:
                df_mod.at[index, FAILURE_COL_NAME] = 'percentage_check failure'
            else:
                df_mod.at[index, FAILURE_COL_NAME] = str(df_mod.at[index, FAILURE_COL_NAME]) + ', percentage_check failure'

    return df_mod, passing


def compare_percents(extracted_from_ui=None, extracted_from_mail_file=None, margin_of_error=1):
    """
    Helper function for customer_type_percentages_check. Combines percents extracted from 
    the mail file & the RM UI plans page into a dictionary of { 'customer_type' : (mail file %, RM ui %) }.

    Args:
        extracted_from_ui (dict): Contains all data extracted from the RM UI plans page.
        extracted_from_mail_file (dict): Contains percentage data from the mail file being tested.
        margin_of_error (): 1% margin of error allowed by default.

    Returns:
        passing (bool) : If RM UI plans page percentages are 100% or less and RM UI 
                         percentage for specific customer type + surge roll over is 
                         less than or equal to the percentages in the mail file for 
                         that corresponding customer type; passing = True.
    """
    # Remove extra data extracted from UI which wont be in mail file.
    del extracted_from_ui['total']
    del extracted_from_ui['target_date']
    del extracted_from_ui['expiration_date']
    del extracted_from_ui['delete']

    # From left to right on RM UI site. https://app.recallmasters.com/communications/xxxx/plans/
    order_of_operation = ['prospect', 'lapsed', 'recent', 'sns', 'l1', 'l2', 'l3', 'l4', 'l5']
    passing = True
    overfill = False
    surge_roll_over = 0
    total_possible_percentage = 100

    # Convert list of tuples into dictionary mail_file.
    mail_file = {}
    for _tuple in extracted_from_mail_file:
        customer_type, percent = _tuple
        mail_file[customer_type] = round(percent)

    A = set(mail_file.keys())
    B = set(extracted_from_ui.keys())

    # Combine both dicts into combined:{'customer_type':(mail_file %, extracted from UI %)}
    intersect_keys = A.intersection(B)
    combined = {i : (mail_file[i], extracted_from_ui[i]) for i in intersect_keys if mail_file[i] != extracted_from_ui[i]}

    # Iterate order_of_operation from RM UI (left to right)
    for index in range(len(order_of_operation)):

        if order_of_operation[index] in combined.keys():
            # Get the mail file percent & the RM UI percent.
            mail_file_percent, rm_ui_percent = combined[order_of_operation[index]]

            # Add any surge roll over %'s to the RM UI percent.
            rm_ui_percent = int(rm_ui_percent) + int(surge_roll_over)

            # Overfills are failures. If the mail file percent is greater than what is indicated on the RM UI site, fail.
            if (int(mail_file_percent)) > (int(rm_ui_percent) + int(margin_of_error)): 
                # print(f"Setting overfill to TRUE.\n")
                overfill = True

            # Calculate how many percents to carry over to the next customer type.
            # else: surge_roll_over = int(rm_ui_percent) - int(mail_file_percent)
            surge_roll_over = int(rm_ui_percent) - int(mail_file_percent)

        # 100% is the total amount of customers we want - ensure RM UI plans page gives us max 100% customer types. 
        total_possible_percentage = int(total_possible_percentage) - int(extracted_from_ui[order_of_operation[index]])

    if total_possible_percentage < 0: passing = False
    if overfill == True : passing = False

    return passing


# address,city,state,ZipCode
def multiple_address_check(df=None, max_allowed=None):
    """
    Function ensures that there are no more than the max allowed of 
    duplicate addresses.

    Args:
        df (pandas) : a df which represents a remote s3 recallmasters bucket csv file.
        max_allowed (int) : the maximum amount of allowed duplicate addresses.

    Returns:
        passing (bool) : If there is one address that exceeds the designated max
                         allowed threshold, then, passing = False
    """
    passing = True
    df_mod = df.replace('', np.nan)
    all_addresses = {}

    # Iterate over all the rows in the df.
    for index, row in df_mod.iterrows():

        count = 0
        address = str(row['address'].lower()) + " " + str(row['city'].lower()) \
                  + " " + str(row['state'].lower())

        if address in all_addresses.keys():
            count = all_addresses[address]
            count += 1
            all_addresses[address] = count
        else:
            all_addresses[address] = 1

        if count > max_allowed:
            if df_mod.at[index, FAILURE_COL_NAME] == None:
                df_mod.at[index, FAILURE_COL_NAME] = 'multiple_address_check failure'
            else:
                df_mod.at[index, FAILURE_COL_NAME] = str(df_mod.at[index, FAILURE_COL_NAME]) + ', multiple_address_check failure'

    passing = check_passing(df=df_mod, failure_reason='multiple_address_check failure')

    return df_mod, passing


# Complex functinality occuring, please read docs well to understand. 
def recent_contact_check(mail_file_df=None, pandas_df=None, recent_included=None, max_days=None):
    """
    This function applies the 105 day rule. This check includes scarping two different dfs from  
    https://app.recallmasters.com/communications/mailing/xxxx/. One is a pandas df and the other is 
    a mailing df. These two df must be checked and crossed referenced against each other.

    The goal of this check is to test the mail file df.

    Records located within both df's are matched by VIN values.

    Once a match is found within both df's, the logic below is applied.

    Within the pandas df, wherever column value excluded.filter_name is blank, grab column value
    mailed.global.last_date
    
    Within the mailing df, grab column value DropDate.

    If ((mailed.global.last_date - mailed.global.last_date) < max_days); the test fails based off
    the fact that the customer has been mailed recently. 

    If there are records present within the mail file df which are not matched on the pandas df, the
    test will fail. 

    Args:
        mail_file_df (pandas) : a df which represents a remote s3 recallmasters bucket csv file.
        pandas_df (pandas) : a df which represents a remote s3 recallmasters bucket csv file.
        recent_included (bool) : if false, then, recently mailed customer can be mailed to. 
                                 if true, then, recently mailed customer cannot be mailed to.
        max_days (int) : How long its had to been since a customer has been mailed to.

    Returns:
        mail_file_df_mod (pandas) : Processed df with results appended to last column.
        passing (bool) : If there is one address that exceeds the designated max
                         allowed threshold, then, passing = False.
    """
    passing = True
    within_max_days = True
    vin_match_found = False

    mail_file_df_mod = mail_file_df.replace('', np.nan)
    pandas_df_mod = pandas_df.replace('', np.nan)

    # Get indexes for which column excluded.filter_name is not null.
    non_nan_rows = pandas_df_mod[pandas_df_mod['excluded.filter_name'].notnull()].index

    # Remove these not null row(s) indexes from the dataFrame, leave only NaN values.
    pandas_df_mod.drop(non_nan_rows, inplace=True)

    if recent_included == True:
        
        # O(n^2) operation with the smallest possible pandas df.
        for mail_file_index, mail_file_row in mail_file_df.iterrows():
            for pandas_index, pandas_row in pandas_df_mod.iterrows():

                # If the VINS match.
                if str(mail_file_row['VIN_ID']) == str(pandas_row['vehicle.vin']):
                    vin_match_found = True

                    # Comes in invalid format 20191004 (YYYYMMDD).
                    mail_file_dropDate = str(mail_file_row['DropDate'])

                    # Correct for invalid format of mail_file_row['DropDate'] value & convert to datetime object.
                    mail_file_dropDate = mail_file_dropDate[:4] + '-' + mail_file_dropDate[4:]
                    mail_file_dropDate = mail_file_dropDate[:7] + '-' + mail_file_dropDate[7:]
                    mail_file_dropDate = datetime.datetime.strptime(mail_file_dropDate, '%Y-%m-%d')

                    # Comes in valid format 2019-10-04 (YYYY-MM-DD).
                    pandas_file_dropDate = str(pandas_row['mailed.global.last_date'])

                    # Convert pandas_row['mailed.global.last_date'] value to datetime object.
                    pandas_file_dropDate = datetime.datetime.strptime(pandas_file_dropDate, '%Y-%m-%d')

                    # Subtract the two datetime objects.
                    duration = pandas_file_dropDate - mail_file_dropDate

                    # Correct for negative days if necessary. Total difference will be in variable: days.
                    if duration.days < 0: days = duration.days * -1
                    else: days = duration.days

                    # if days < max_days: within_max_days = False
                    if max_days > days: within_max_days = False

                if vin_match_found==True: 
                    break

            if (vin_match_found == False or within_max_days == False):
                if mail_file_df_mod.at[mail_file_index, FAILURE_COL_NAME] == None:
                    mail_file_df_mod.at[mail_file_index, FAILURE_COL_NAME] = 'recent_contact_check failure'
                else:# If this particular record has failed previously.
                    mail_file_df_mod.at[mail_file_index, FAILURE_COL_NAME] = str(mail_file_df_mod.at[mail_file_index, FAILURE_COL_NAME]) + ', recent_contact_check failure'

            vin_match_found = False
            within_max_days = True
    else:# exclude_if_prev_contracted button on RM ui is turned off.
        passing = True
        print("exclude_if_prev_contracted is OFF.")
        
    passing = check_passing(df=mail_file_df_mod, failure_reason='recent_contact_check failure')

    return mail_file_df_mod, passing


def email_checker(df=None, email_col=None, filters=None):
    """
    Function checks a specified column within a df against an email suppression list.

    Args:
        df (pandas) : Df to search.
        email_col (str) : The email column.
        filters (list) : The suppression list of emails to search against.

    Returns:
        df (pandas) : Df with results.
        passing (bool) : If the df contains 1 or more emails located within the filters list, passing=False.
    """
    passing = True
    df_mod = df.replace('', np.nan)
    # Convert the filters list to all lowercase.
    filters = [x.lower() for x in filters]

    # Ensure distance column is present in the data frame.
    if email_col in df.columns:
        # Iterate over all the rows in the df.
        for index, row in df_mod.iterrows():
            # If cell isnt nan and its value is in the filter list.
            if (pd.isnull(row[email_col]) == False) and (row[email_col].lower() in filters):
                if df.at[index, FAILURE_COL_NAME] == None:
                    df.at[index, FAILURE_COL_NAME] = 'email_checker failure'
                else:# If this particular record has failed previously.
                    df.at[index, FAILURE_COL_NAME] = str(df.at[index, FAILURE_COL_NAME]) + ', email_checker failure'

        passing = check_passing(df=df, failure_reason='email_checker failure')
    else:# Column not present.
        passing = False

    return df, passing


def distance_checker(df=None, distance_col=None, max_distance=None, customer_type=None):
    """
    Function checks against the a maximum distance value. This value is
    exracted from page https://app.recallmasters.com/communications/xxxx/. 
    Two distance values are present, one for DMS & the other for PROSPECT. This 
    test must be run once for each type of customer. 

    Args:
        df (pandas) : Df to search.
        distance_col (str) : The column name to check.
        max_distance (int) : The maximum value located at specified column.
        customer_type (str) : Should only be 1 of 2 values: 'prospect' or 'dms'.

    Returns:
        df (pandas) : Df with results.
        passing (bool) : If there is 1 or more records with a distance value that is greater than
                         the max_distance, passing=False.
    """
    passing = True
    df_mod = df.replace('', np.nan)

    if str(customer_type).lower() == 'prospect':
        customer_target_list = ['prospect']
    else:
        customer_target_list = ['lapsed', 'recent', 'sns', 'l1', 'l2', 'l3', 'l4', 'l5']

    # Ensure distance column is present in the data frame.
    if distance_col in df_mod.columns:
        # Iterate over all the rows in the df.
        for index, row in df_mod.iterrows():
            if row['customer_type'].lower() in customer_target_list:
                # If cell isnt nan and its value is greater than the max distance allowed.
                if (pd.isnull(row[distance_col]) == False) and (int(row[distance_col]) > int(max_distance)):
                    # If this particular record has not failed any other tests.
                    if df_mod.at[index, FAILURE_COL_NAME] == None:
                        df_mod.at[index, FAILURE_COL_NAME] = 'distance_checker failure'
                    else:# If this particular record has failed previously.
                        df_mod.at[index, FAILURE_COL_NAME] = str(df.at[index, FAILURE_COL_NAME]) + ', distance_checker failure'

        passing = check_passing(df=df_mod, failure_reason='distance_checker failure')
    else:# Column not present.
        passing = False

    return df_mod, passing


def add_reason_for_failure_col(df=None, new_col_name=FAILURE_COL_NAME):
    """
    Function add a new column to the end of a df. 

    Args:
        df (pandas) : A mail file extracted from legacy s3 rambo.
        new_col_name (str) : The name of the new column to add.

    Returns:
        df (pandas) : The new df with column appended. 
    """
    df[new_col_name] = None

    return df


def remove_seed_records(df=None):
    """
    Function simply removes all records which are of customer type 'seed'.

    Args:
        df (pandas) : A mail file to check.

    Returns:
        df (pandas) : A mail file without any seed records.   
    """

    df =  df[df['customer_type'].map(lambda x: str(x).lower() != "seed")]

    return df


def check_passing(df=None, failure_reason=None, complete=False):
    '''
    This helper function serves two purposes, 1) can provide individual tests results 
    from any filter test, & 2) can provide test results for a master df after having 
    been filter with n number of tests.

    Args:
        df (pandas) : A mail file to check.
        failure_reason (str) : The failure condition to search for.
        complete (bool) : Search a master df after having been filtered through n number of tests.

    Returns:
        passing (bool) : The results of filter(s) execution.
    '''
    passing = True

    if complete==False:
        # Get all values from the target column.
        col_value_list = df[FAILURE_COL_NAME].values.tolist()
        # Should significantly reduce the size of the list. 
        col_value_list = remove_values_from_list(the_list=col_value_list, value_to_remove=None)

        # Iterate through the smallest possible list.
        for index, value in enumerate(col_value_list): 
            # The break statement causes a program to break out of a loop early if need be.
            # This is perfectly normal behavior and does not constitute bad form.
            # https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops
            if passing == False: break

            value = value.split(',')

            if (failure_reason in value) == True:
                passing = False
    else:
        col_value_list = df[FAILURE_COL_NAME].values.tolist()
        if None not in col_value_list: passing = False
    
    return passing


def remove_values_from_list(the_list=None, value_to_remove=None):
    '''
    Helper function which removes all items which match one value.

    Args:
        the_list (list) : List to filter.
        value_to_remove (any) : The failure condition to search for.

    Returns:
        value (list) : Filtered list.
    '''
    return [value for value in the_list if value != value_to_remove]
