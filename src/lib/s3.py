'''
  functions related to aws s3 read/write/download/upload/presign
'''
import os
from lib.log import get_logger

log = get_logger(
    "s3.py",
    "'[%(levelname)s] [%(name)s]  [%(asctime)s] [%(funcName)s::%(lineno)d] [%(message)s]'",
)

# If bucket does not exist, create it.
def ensure_bucket_exists(context=None):
    if not(bucket_exists(bucket_name=os.environ['holding_bucket'], s3_client=context.s3_client)):
        location = {'LocationConstraint': os.environ['aws_region']}
        bucket = context.s3_client.create_bucket(Bucket=os.environ['holding_bucket'], CreateBucketConfiguration=location)
        log.info(f"{os.environ['holding_bucket']} did not exist; it has been created.")



def bucket_exists(bucket_name=None, s3_client=None):
    '''
        Determine whether bucket_name exists and the user 
        has permission to access it

        Parameters:
        - bucket_name (string) : The name of the bucket to search for.
        - s3_client (s3 client obj) : A low-level client representing AWS S3.

        Returns:
        - (bool) : True if the referenced bucket_njoinedlist = listone + listtwoame exists, otherwise False
    '''
    try:
        response = s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        return False
        
    return True