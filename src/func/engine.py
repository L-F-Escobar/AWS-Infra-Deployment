import os
import io
import traceback
import boto3
import ast
import pandas as pd
from lib.log import get_logger
from lib.handler_helper import (
    engine_file_clean_up, 
    engine_put_files_s3, 
    engine_login_fail
)
from lib.run_filters import engine_run_filters
from func.filter import (
    add_reason_for_failure_col,
    remove_seed_records,
    check_passing
)
from func.ui.extract import (
    extract_communication_details,
    extract_plan_details
)

log = get_logger(
    "engine.py",
    "'[%(levelname)s] [%(name)s]  [%(asctime)s] [%(funcName)s::%(lineno)d] [%(message)s]'",
)


def run(event=None, context=None, session=None):
    response = {}

    ids = event.get('dropID').split(",")
    log.info(f'All ids: {ids}')

    for id in ids:
        log.info(f'Processing id {id}.')

        logged_in = session.login_to_mailing(url='https://app.recallmasters.com/login/?next=/communications/mailing/{}'.format(id), 
                                             vars=context.var)
        if logged_in == True:
            log.info('Logged in.')

            try: 
                ''' This try/catch loop is associated with data extraction. '''
                mail_file_obj = make_mail_file_obj(selenium_session=session, custom_context=context)
                # log.info(f'mail_file_obj : {mail_file_obj}')
                
                pandas_file_obj = make_pandas_df_obj(selenium_session=session, custom_context=context)
                # log.info(f'pandas_file_obj : {pandas_file_obj}')
                
                session.navigate_to_communication_from_mailing(dropId=id)
                communication_info = extract_communication_details(session=session.driver)
                # print(f"communication_info\n{communication_info}")
                
                session.navigate_to_plans_from_communications()
                plans_info = extract_plan_details(session=session.driver, communication_data=communication_info)
                # print(f"plans_info\n{plans_info}")
            except Exception as error:
                log_error(error=error, msg="Data Extraction.")
                return "Failure processing aws s3."

            try:
                ''' This try/catch loop is associated with applying all filter tests. '''
                df_raw = add_reason_for_failure_col(df=mail_file_obj['mail_file_df'], new_col_name='Reason_for_failure')
                # log.info(f'Added reason for failure column onto the df.')

                df_raw = remove_seed_records(df=df_raw)
                log.info(f'Added reason for failure column onto the df & removed seed customer types.')

                df_raw = engine_run_filters(context=context, communication_info=communication_info, 
                                            plans_info=plans_info, pandas_file_obj=pandas_file_obj, df_raw=df_raw)

                passing = check_passing(df=df_raw, complete=True)
                log.info('DF processing & analysis complete.')
            except Exception as error:
                log_error(error=error, msg="filter tests.")
                return "Failure running test logic or extraction."

            try:
                ''' This try/catch is associated removing and adding files to s3.'''
                engine_file_clean_up(context=context, event=event, key=id)
                engine_put_files_s3(df=df_raw, mail_file_object=mail_file_obj, context=context, key=id)
            except Exception as error: 
                log_error(error=error, msg="file cleanup + file puts.")
                return "Failure deleting or putting files into s3."

            communication_info.clear()
            plans_info.clear()
        else:
            engine_login_fail(prefix=id, context=context)
    return "success"



def make_mail_file_obj(selenium_session=None, custom_context=None):
    '''
        Constructs a dictionary object containing three values; a 
        mail file df, the name of the s3 bucket the file was found in, 
        & the key of said file. 

        Parameters:
        - selenium_session (driver) : Live seleniun webdriver.
        - custom_context (object) : Environment & constant variables wrapper.

        Returns:
        - pandas_obj (object) : Dictionary containing specific mail file meta data. 
    '''
    mail_file_obj = {}
    
    s3_file_url = selenium_session.get_mail_df_link(xpath='//*[@id="content"]/buefy/div/div/table/tbody[2]/tr/td[2]/a')
    (mail_file_obj['mail_key'], mail_file_obj['mail_bucket']) = selenium_session.parse_s3_url(s3_url=s3_file_url)
    data = custom_context.s3_legacy.get_object(Bucket=mail_file_obj['mail_bucket'], Key=mail_file_obj['mail_key'])
    contents = data['Body'].read()
    mail_file_obj['mail_file_df'] = pd.read_csv(io.BytesIO(contents), encoding='utf8', sep=",")
    
    return mail_file_obj



def make_pandas_df_obj(selenium_session=None, custom_context=None):
    '''
        Constructs a dictionary object containing three values; a 
        mail file df, the name of the s3 bucket the file was found in, 
        & the key of said file. 

        Parameters:
        - selenium_session (driver) : Live seleniun webdriver.
        - custom_context (object) : Environment & constant variables wrapper.

        Returns:
        - pandas_obj (object) : Dictionary containing specific mail file meta data. 
    '''
    pandas_obj = {}

    s3_file_url = selenium_session.get_pandas_df_link(xpath='//*[@id="content"]/buefy/div/div/div[5]/div/table/tbody[position()=last()]/tr[1]/td[3]/a')
    (key, bucket) = selenium_session.parse_s3_url(s3_url=s3_file_url)
    data = custom_context.s3_legacy.get_object(Bucket=bucket, Key=key)
    contents = data['Body'].read()
    df_raw = pd.read_csv(io.BytesIO(contents), encoding='utf8', sep=",")

    pandas_obj['pandas_file_df'] = df_raw
    pandas_obj['panda_bucket'] = bucket
    pandas_obj['pandas_key'] = key

    return pandas_obj


def log_error(error=None, msg=None):
    log.error(
        {
            "engine_part":msg,
            "exception_type": type(error).__name__,
            "error_reason": error.args,
            "traceback": traceback.format_exc(),
        }
    )