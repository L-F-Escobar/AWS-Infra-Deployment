from func.filter import (
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

def engine_run_filters(context=None, communication_info=None, plans_info=None, pandas_file_obj=None, df_raw=None):
    """
        Applies all test filters to a df. 

        Parameters:
        - context (obj) : Environment & constant variable wrapper class.
        - communication_info (obj) : Contains all scrapped info from RM page.
        - plans_info (obj) : Contains all scrapped info from RM plsnd page.
        - pandas_file_obj (obj) : Contains the bucket, key, & contents of an extract df from RM page.
        - df_raw (pandas df) : The df which should be dropped into s3.

        Returns:
        - df_raw (pandas df) : A df with results of all tests appended to the last column.
    """
    df_raw, find_NaN_result = find_NaN(df=df_raw, check_list=context.var.get('BLANK_CHECK'))

    df_raw, find_empty_recalls_result = find_empty_recalls(df=df_raw, vin_col=context.var.get('VIN_COL'))

    df_raw, find_human_lname_results = last_name_checker(df=df_raw, 
                                                        lname_col=context.var.get('LNAME_COL'), 
                                                        filters=context.var.get('LNAME_FILTERS'))

    df_raw, list_zip_check_result = list_zip_check(df=df_raw, 
                                                    prospect_zips=communication_info.prospect_zipcode_list, 
                                                    dms_zips=communication_info.dms_zipcode_list, 
                                                    zip_col=context.var.get('ZIP_COL'))

    df_raw, customer_type_percentages_check_result = customer_type_percentages_check(df=df_raw, 
                                                                                    col_name=context.var.get('CUSTOMER_TYPE'), 
                                                                                    percentages_extract_from_RM_ui=plans_info)

    if communication_info.deduplicate_by_address == False: max_allow = 3
    else: max_allow = 1

    df_raw, multiple_address_check_result = multiple_address_check(df=df_raw, max_allowed=max_allow)
    
    df_raw, recent_contact_check_result = recent_contact_check(mail_file_df=df_raw, 
                                                                pandas_df=pandas_file_obj['pandas_file_df'],
                                                                recent_included=communication_info.exclude_if_prev_contacted,
                                                                max_days=context.var.get('MAX_DAYS'))

    df_raw, email_checker_result = email_checker(df=df_raw, 
                                                email_col=context.var.get('EMAIL_COL'), 
                                                filters=context.var.get('email_suppression'))
    
    if bool(communication_info.is_prospect) == True:
        df_raw, distance_checker_result = distance_checker(df=df_raw, 
                                                            distance_col=context.var.get('DISTANCE_COL'), 
                                                            max_distance=communication_info.prospect_max_radius,
                                                            customer_type='prospect')

    if bool(communication_info.is_dms) == True:                                                  
        df_raw, distance_checker_result = distance_checker(df=df_raw, 
                                                            distance_col=context.var.get('DISTANCE_COL'), 
                                                            max_distance=communication_info.dms_max_radius,
                                                            customer_type='dms')
    
    return df_raw