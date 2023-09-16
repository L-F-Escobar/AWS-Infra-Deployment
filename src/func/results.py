import boto3
import os
import io
import collections
import pandas as pd
from config.context import CustomContext
from lib.log import get_logger
from lib.handler_helper import clean_ids, clean_rebuild, categorize_result_ids
from lib.s3 import ensure_bucket_exists


log = get_logger(
    "results.py",
    "'[%(levelname)s] [%(name)s]  [%(asctime)s] [%(funcName)s::%(lineno)d] [%(message)s]'",
)


def handler(event, context):
    """
        Is called directly by rest GET rest api.

        Parameters:
        - event (AWSEvent)  : This object is created by AWS. API Gayeway event.
                              Will contain drop id from GET url call.

        Returns:
        - response (dict) : This wrapper gets the response/results from run and
                            returns those results as a response to the api call.
    """
    custom_context = CustomContext(event, context)
    response={}
    
    ensure_bucket_exists(context=custom_context)

    ids = clean_ids(event=event)
    log.info(f"Ids cleaned: {ids}")
    
    rebuild = clean_rebuild(event=event)
    log.info(f"Rebuild extracted: {rebuild}")
    
    (not_found, still_processing, rejected, done) = categorize_result_ids(ids=ids, context=custom_context)
    
    done_metadata_dict = {}
    for index in range(len(done)):
        master_df = reconstruct_master_df(s3_client=custom_context.s3_client, 
                                          bucket=os.environ['holding_bucket'], 
                                          key= str(done[index]))
        stats, total_records = get_master_df_failure_stats(master_df=master_df, context=custom_context)

        done_metadata_dict[done[index].split('.')[0]] = {"Total Records":total_records, "Bucket":os.environ['holding_bucket'], "Key":done[index], "stats":stats}
        log.info(f"Bucket: {os.environ['holding_bucket']}")
        log.info(f"Key: {str(done[index])}")

    response["status_code"] = 200
    response["event"] = event
    response['done'] = done
    response['done_metadata'] = done_metadata_dict
    response['still_processing'] = still_processing
    response['not_found'] = not_found
    response['rejected'] = rejected
    response['bucket_checked'] = os.environ['holding_bucket']
    return response


def reconstruct_master_df(s3_client=None, bucket=None, key=None):
    data = s3_client.get_object(Bucket=bucket, Key=key)
    contents = data['Body'].read()
    df_raw = pd.read_csv(io.BytesIO(contents), encoding='utf8', sep=",")

    return df_raw


def get_master_df_failure_stats(master_df=None, context=None):
    """
        Aggregates all test results of a master df. 

        Parameters:
        - master_df (pandas df) : The df which contains all test results in last column.
        - context (object) : Evironment & const wrapper.

        Returns:
        - results (list of tuples) : Percentage break-down of all records.
                                     Ex. [('find_NaN failure', 100.0), ('last_name_checker failure', 12.5)]]
                                     Ex. 12.5% of records failed the last_name_checker test.
        - total_records (int) : Total number of records contained in df.
    """
    # EX. results_list=['find_NaN failure, percentage_check failure', 'percentage_check failure, distance_checker failure']
    results_list = list(master_df[str(context.var.get('FAILURE_COL_NAME'))])
    total_records = len(results_list)

    all_results = []
    for index in range(len(results_list)):
        results = results_list[index].split(',')
        results = list(map(lambda string: string.strip(), results))
        all_results.extend(results)

    # Total of each failure type.
    # Ex. all_failures = Counter({'percentage_check failure': 24, 'last_name_checker failure': 3})
    all_failures = collections.Counter(all_results)

    # result = list of tuples -> [('prospect', 61.05610561056105), ]
    results = [(i, all_failures[i] / total_records * 100.0) for i, count in all_failures.most_common()]

    # Ex. results = [('percentage_check failure', 100.0), ('last_name_checker failure', 12.5)]
    return results, total_records
