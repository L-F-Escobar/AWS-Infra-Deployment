import traceback
import ast
from config.context import CustomContext
from func.selen import SeleniumDriver
from func.engine import run


def endpoint(event, context):
    """
        Is called directly by rest GET rest api.

        Parameters:
        - event (AWSEvent)  : This object is created by AWS. API Gayeway event.
                              Will contain drop id from GET url call.

        Returns:
        - response (dict) : This wrapper gets the response/results from run and
                            returns those results as a response to the api call.
    """
    try:
        event_dict = ast.literal_eval(event["Records"][0]["Sns"]["Message"])
        # event_items = event["Records"][0]["Sns"]["Message"].split(",")
        # print(f"event_items -> {event_items}")
        # for k,value in event_dict.items():
        #     print(f"key:{k}, value:{value}")
        
        custom_context = CustomContext(event_dict, context)
        session = SeleniumDriver()
        response = run(event=event_dict, context=custom_context, session=session)
        session.end_session()

        
        return response
    except Exception as e:

        custom_context.log.error(
            {
                "exception_type": type(e).__name__,
                "error_reason": e.args,
                "traceback": traceback.format_exc(),
            }
        )
        
        response = {
            "status_code": 500,
            'event': event,
            "exception_type": type(e).__name__,
            "error_reason": e.args,
            "traceback": traceback.format_exc()
        }

        return response