import boto3
import os
from config.context import CustomContext
from lib.log import get_logger
from lib.handler_helper import clean_ids, clean_rebuild, categorize_publish_ids
from lib.s3 import ensure_bucket_exists

log = get_logger(
    "publish.py",
    "'[%(levelname)s] [%(name)s]  [%(asctime)s] [%(funcName)s::%(lineno)d] [%(message)s]'",
)


def handler(event, context):
    """
        Is called directly by rest GET rest api.

        Parameters:
        - event (dict)  : This object is created by AWS. API Gayeway event.
                          Will contain drop id from GET url call.
                          Ex. event = {'dropID': '8240, 1111, 1010, 5555, abcd', 'rebuild': 'False'}
        - var(context) (LambdaContext) : aws_request_id, log_group_name, & other info.

        Returns:
        - response (dict) : This wrapper gets the response/results from run and
                            returns those results as a response to the api call.
    """
    custom_context = CustomContext(event, context)
    response={}

    sns = boto3.client('sns')
    log.info(f"SNS client created.")

    ensure_bucket_exists(context=custom_context)

    ids = clean_ids(event=event)
    log.info(f"Ids cleaned: {ids}")

    rebuild = clean_rebuild(event=event)
    log.info(f"Rebuild extracted: {rebuild}")

    (started_processing, still_processing, rejected, done) = categorize_publish_ids(ids=ids, context=custom_context)
    log.info(f"Ids have been categorized by their state.")
    
    event = rebuild_event(original_event=event, remove=rejected, remove_done=done)

    sns_meta_data = publish_to_topic(message=str(event), sns_client=sns)

    response["status_code"] = 200
    response["event"] = event

    if rebuild == True:
        response['started_processing'] = still_processing + started_processing + done
    else:
        response['still_processing'] = still_processing
        response['started_processing'] = started_processing
        response['done'] = done
    response['rejected'] = rejected
    response['bucket'] = os.environ['holding_bucket']
    response['sns_meta_data'] = sns_meta_data
    log.info(f"Response constructed: {response}")
    
    return response


def publish_to_topic(message, sns_client):
    '''
        Sends a message to an Amazon SNS topic

        Parameters:
        - message (str) : An api gateway triggered event obj containing 'dropID' & 'rebuild' keys.
        - sns_client (s3 client obj) : A low-level client representing AWS S3.

        Returns:
        - response (dict) : Response for Publish action.
    '''
    # Publish a simple message to the specified SNS topic
    response = sns_client.publish(
        # TopicArn=f"arn:aws:sns:{os.environ['aws_region']}:{os.environ['acct_id']}:{os.environ['sns_topic']}", 
        TopicArn=os.environ['sns_topic_arn'],
        Message=message,
    )
    return response


def rebuild_event(original_event=None, remove=None, remove_done=None):
    '''
        Function constructs an event object which will allow engine.run 
        to process mail file ids efficiently by only including valid drops ids. 

        Example: start -->  {'dropID': '8240, 1111, 1010, 5555 , abcd', 'rebuild': 'False'}
                 end   -->  {'dropID': '8240,1111,1010,5555', 'rebuild': 'False'}

        Parameters:
        - original_event (dict) : SNS triggered message which includes dropID & rebuild.
        - remove (list) : A list of drop ids which should be removed from the original dropIDs.
        - remove_done (list) : A list of drop ids which have previously been processed and have master df's with test results.

        Returns:
        - original_event (dict) : Returns an event ready object for engine.run. Only valid dropIDs are present. 
    '''
    dropIds = clean_ids(event=original_event)

    rebuild = clean_rebuild(event=original_event)

    '''
        if rebuild==True -> Only remove dropids found in remove list.
        if rebuild==False -> Remove all dropids found in remove & remove_done list.
    '''
    if rebuild == True: dropIds = [x for x in dropIds if x not in remove]
    else: 
        dropIds = [x for x in dropIds if x not in remove]
        
        remove_done_dropIDs = []

        for index in range(len(remove_done)):
            remove_done_dropIDs.append(remove_done[index].split('.')[0])

        dropIds = [x for x in dropIds if x not in remove_done_dropIDs]
    
    dropIds_reformated = ','.join(str(i) for i in dropIds)
    
    original_event['dropID'] = dropIds_reformated
    
    return original_event
