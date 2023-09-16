import os
import ast
import io
from lib.log import get_logger

log = get_logger(
    "handler_helper.py",
    "'[%(levelname)s] [%(name)s]  [%(asctime)s] [%(funcName)s::%(lineno)d] [%(message)s]'",
)

def clean_ids(event=None):
    """
        Receieves a raw api gateway event which contains key 'dropID who's value 
        is a string of ids seperated by commas. Converts the string into a proper
        list.

        Parameters:
        - event (obj) : Api gateway event.

        Returns:
        - ids (list) - Cleaned list of strings, seperated, and striped of 
    """
    # Get all ids passed into endpoint - ids come in as one string. 
    ids = event.get('dropID').split(",")

    # Remove all trailing white spaces from ids.
    ids = list(set(list(map(lambda string: string.strip(), ids))))

    return ids


def clean_rebuild(event=None):
    """
        Receieves a raw api gateway event which contains key 'rebuild who's value 
        is supposed to be only True or False. This function ensures proper intrepretation
        of the value.

        Parameters:
        - event (obj) : Api gateway event.

        Returns:
        - rebuild (bool) - The value of the 'rebuild' key.
    """
    # If this parameter is not valid, simply proceed as False value.
    try: 
        # rebuild = ast.literal_eval(event.get('rebuild'))
        return ast.literal_eval(event.get('rebuild'))
    except Exception as error: 
        # rebuild = False
        return False



def categorize_publish_ids(ids=None, context=None):
    """
        Appends ids to a list indicating the state of that id.
        ex. (new id, currently processing id, processed id, invalid id).

        Parameters:
        - ids (list) : The dropID event value. Ex. '8240, 1111, 1010, 5555, abcd'
        - context (obj) : s3 and const wrapper class.

        Returns:
        - lists (4-tuple of lists) : Ids in correct lists indicating their state.
    """
    # All possible file states.
    started_processing = []
    still_processing = []
    rejected = []
    done = []

    for id in ids:
        try:
            int(id) # Ensure this is a valid integar mail file number.

            # Attempt to find file.
            file_obj = context.s3_client.list_objects_v2(Bucket = os.environ['holding_bucket'],
                                                                Prefix = str(id))
            # If file exists, check its status & add to correct list.
            if "Contents" in file_obj.keys():
                key = file_obj['Contents'][0]['Key'].split(".")

                if 'processing' in key: 
                    still_processing.append(file_obj['Contents'][0]['Key'])
                    log.info(f"{id} has been added to still_processing list.")
                elif 'done' in key:
                    done.append(file_obj['Contents'][0]['Key'])
                    log.info(f"{id} has been added to done list.")

            else:# File does not exist.
                context.s3_client.put_object(Bucket=os.environ['holding_bucket'], Key=(str(id) + str(context.var.get('PROCESSING'))), Body=b'''''')
                started_processing.append((str(id) + str(context.var.get('PROCESSING'))))
                log.info(f"{id} has been added to started_processing list.")
        except ValueError:
            rejected.append(id)
            log.info(f"{id} is not a valid mail file number.")

    return (started_processing, still_processing, rejected, done)



def categorize_result_ids(ids=None, context=None):
    """
        Appends ids to a list indicating the state of that id.
        ex. (new id, currently processing id, processed id, invalid id).

        Parameters:
        - ids (list) : The dropID event value. Ex. '8240, 1111, 1010, 5555, abcd'
        - context (obj) : s3 and const wrapper class.

        Returns:
        - lists (4-tuple of lists) : Ids in correct lists indicating their state.
    """
    # All possible file states.
    not_found = []
    still_processing = []
    rejected = []
    done = []

    # Check if Id's are already processing.
    for id in ids:
        log.info(f"Analysing id: {id}")
        
        try:
            int(id) # Ensure this is a valid integar mail file number.        

            # Attempt to find file.
            file_obj = context.s3_client.list_objects_v2(Bucket = os.environ['holding_bucket'],
                                        Prefix = str(id))

            # If file exists, check its status.
            if "Contents" in file_obj.keys():
                key = file_obj['Contents'][0]['Key'].split(".")
                
                if 'processing' in key: 
                    still_processing.append(file_obj['Contents'][0]['Key'])
                    log.info(f"{id} has been added to still_processing list.")
                elif 'done' in key:
                    done.append(file_obj['Contents'][0]['Key'])
                    log.info(f"{id} has been added to done list.")
            else: # File does not exist.
                not_found.append(str(id))
                log.info(f"{id} has been added to not_found list.")
        except ValueError:
            rejected.append(id)
            log.info(f"{id} is not a valid mail file number.")

    return (not_found, still_processing, rejected, done)



def engine_file_clean_up(context=None, event=None, key=None):
    """
        Removes all un-necessary files from s3. 

        Parameters:
        - context (obj) : Environment & constant variable wrapper class.
        - event (obj) : Sns message containing 'dropId' & 'rebuild' keys.
        - key (int) : A mail file drop id.

        Returns:
        - 
    """
    # Attempt to find file.
    file_obj = context.s3_client.list_objects_v2(Bucket = os.environ['holding_bucket'],
                                                 Prefix = str(key))
    # If file exists, check its status.
    if "Contents" in file_obj.keys():
        for index in range(len(file_obj['Contents'])):
            key = file_obj['Contents'][index]['Key'].split(".")

            if ast.literal_eval(event.get('rebuild')) == True:
                context.s3_client.delete_object(Bucket=os.environ['holding_bucket'], Key=file_obj['Contents'][index]['Key'])
                log.info(f"Rebuild = True -> {file_obj['Contents'][index]['Key']} has been deleted.")

            elif ast.literal_eval(event.get('rebuild')) == False and 'processing' in key:
                context.s3_client.delete_object(Bucket=os.environ['holding_bucket'], Key=file_obj['Contents'][index]['Key'])
                log.info(f"Rebuild = False -> {file_obj['Contents'][index]['Key']} has been deleted.")



def engine_put_files_s3(df=None, mail_file_object=None, context=None, key=None):
    """
        Puts all necessary files into s3; both in the current aws s3 environment and 
        in the lagacy rambo s3 environment.

        Parameters:
        - df (pandas df) : The df which should be dropped into s3.
        - mail_file_object (obj) : Contains the key, bucket, and contents of the df.
        - context (obj) : Environment & constant variable wrapper class.
        - key (int) : The mail file drop id.

        Returns:
        - 
    """
    # If the file is bigger then the RAM you have available this action will fail.
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)

    # Get a legacy s3 resource & current environment s3 resource.
    s3_legacy = context.legacy_session.resource('s3')
    s3_current_environment = context.session.resource('s3')

    # Get the 'file path' of the mail file location within legacy s3.
    mail_key = mail_file_object["mail_key"].split("/") # reporting/f7/64/50068.mailing.2019-10-04.00.010.csv
    del mail_key[-1]
    mail_key = '/'.join(mail_key) # reporting/f7/64

    # Set the 'file_key' to the 'folder location' of the mail file in s3.
    file_key = mail_key + '/' + str(key) + str(context.var.get('FINISHED')) # reporting/f7/64/1111.done.test.csv

    s3_legacy.Object(mail_file_object["mail_bucket"], file_key).put(Body=csv_buffer.getvalue())
    s3_current_environment.Object(os.environ['holding_bucket'], (str(key) + str(context.var.get('FINISHED')))).put(Body=csv_buffer.getvalue())

    log.info(f"Legacy s3 Master df location -> BUCKET: {mail_file_object['mail_bucket']} KEY: {file_key}")
    log.info(f"Current s3 Master df location -> BUCKET: {os.environ['holding_bucket']} KEY: {(str(key) + str(context.var.get('FINISHED')))}")



def engine_login_fail(prefix=None, context=None):
    log.info('Log in failed.')
    # Attempt to find file.
    file_obj = context.s3_client.list_objects_v2(Bucket = os.environ['holding_bucket'],
                                                 Prefix = prefix)
    # If file exists, check its status.
    if "Contents" in file_obj.keys():
        for index in range(len(file_obj['Contents'])):
            context.s3_client.delete_object(Bucket=os.environ['holding_bucket'], Key=file_obj['Contents'][index]['Key'])
            log.info(f"{file_obj['Contents'][index]['Key']} has been deleted.")