import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


'''
    Used as a flag trigger. Running selenium headless on lambda and normal 
    selenium locally requires a different set of settings. Very annoying -_-
    but fortunetly this is a decent way to handle that. Must manually switch 
    the flag. 
    Default is a remote run on aws lambda, therefore, LOCAL_RUN=False.
    Must be changed in ui.extract.py as well.
'''

LOCAL_RUN = False

if LOCAL_RUN == True: # Local
    import sys
    sys.path.append(".")
    from src.lib.log import get_logger
    from ui.extract import extract_communication_details, extract_plan_details
else: # Headless selenium with lambda + api gateway
    from lib.log import get_logger
    from func.ui.extract import extract_communication_details, extract_plan_details

log = get_logger(
    "selen.py",
    "'[%(levelname)s] [%(name)s]  [%(asctime)s] [%(funcName)s::%(lineno)d] [%(message)s]'",
)


class SeleniumDriver():
    '''
        Allows a user to perform all necessary selenium tasks associated
        with the RM mail file extraction process. 
    '''
    def __init__(self):
        try:
            self.vars = {}
            if LOCAL_RUN == False:
                options = Options()
                options.binary_location = '/opt/headless-chromium'
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--single-process')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--enable-logging')
                options.add_argument('--log-level=0')
                options.add_argument('--user-data-dir=/tmp/user-data')
                options.add_argument('--ignore-certificate-errors')
                options.add_experimental_option("prefs", {
                  "download.default_directory": r"/downloads",
                  "download.prompt_for_download": False,
                  "download.directory_upgrade": True,
                  "safebrowsing.enabled": True
                })
                self.driver = webdriver.Chrome('/opt/chromedriver',chrome_options=options)
            else:
                self.driver = webdriver.Chrome('chromedriver')
            log.info(f"Headless Chrome Initialized.")
        except Exception as error:
            log.error(
                {
                    "exception_type": type(error).__name__,
                    "error_reason": error.args,
                    "traceback": traceback.format_exc(),
                }
            )


    def login_to_mailing(self, url=None, vars=None):
        '''
            Logs in at the RM url provided.
    
            Parameters:
            - url (str) : Url will be of the following format
                          https://app.recallmasters.com/login/?next=/communications/mailing/DROP_ID
            - vars (Box): Variables from custom_context.
    
            Returns:
            - T/F (bool) : Log in was successful or not.
        '''
        try:
            driver = self.driver
            driver.get(url)
            driver.implicitly_wait(1.5)
    
            driver.find_element_by_id("signin-login").click()
            driver.find_element_by_id("signin-login").clear()
            if LOCAL_RUN == False: driver.find_element_by_id("signin-login").send_keys(str(vars.rm_login.username))
            else: driver.find_element_by_id("signin-login").send_keys('Luis.Escobar')
            driver.implicitly_wait(1.5)
        
            driver.find_element_by_id("signin-password").click()
            driver.find_element_by_id("signin-password").clear()
            if LOCAL_RUN == False: driver.find_element_by_id("signin-password").send_keys(str(vars.rm_login.password))
            else: driver.find_element_by_id("signin-password").send_keys('luis.escobar2019')
            driver.implicitly_wait(1.5)
        
            driver.find_element_by_id("signin-submit").click()
            driver.implicitly_wait(2.5)

            try: links = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/buefy/div/div')
            except: links = driver.find_element(By.XPATH, '/html/head/title')
            driver.implicitly_wait(1.5)

            '''
                Sometimes we are allowed to log into 'No Builds Found'. This
                is a niche/infrequent bug. More logs added for the next time this 
                occurs.
            '''
            if driver.title == 'Not found! | Recall Masters':
                log.info(f"Mail file not found!")
                return False
            elif links.text=='No Builds found for this Drop. Retry?' or links.text=='No Builds found for this Drop!':
                log.info(f"No Builds found for this Drop!")
                return False
            else:
                log.info(f"Logged in! Page title: {driver.title}")
                log.info(f"links.text --> {links.text}")
                return True
        except Exception as error:
            log.error(
                {
                    "exception_type": type(error).__name__,
                    "error_reason": error.args,
                    "traceback": traceback.format_exc(),
                }
            )
            log.info(f"selen.py::login_to_mailing Exception triggered.")
            return False


    def get_mail_df_link(self, xpath=None):
        '''
            Scraps the s3 url of the location of the mail file located on web page 
            https://app.recallmasters.com/communications/mailing/DROP_ID underneath 
            the Build results section.
    
            Parameters:
            - xpath (str) : The location of the s3 file url located within the web page.
                            This is a static xpath.
    
            Returns:
            - (str) : Ethier returns full_url or ''
        '''
        try:
            driver = self.driver
            links = driver.find_elements_by_xpath(str(xpath))
            driver.implicitly_wait(1)
            full_url = links[0].get_attribute("href")
            # log.info(f"Full url extracted from RM xpath: {full_url}")
            return full_url
        except Exception as error:
            log.error(
                {
                    "exception_type": type(error).__name__,
                    "error_reason": error.args,
                    "traceback": traceback.format_exc(),
                }
            )
            return ''


    def get_pandas_df_link(self, xpath=None):
        '''
        Scraps the s3 url of the location of the pandas file located on web page 
        https://app.recallmasters.com/communications/mailing/DROP_ID 


        Parameters:
        - xpath (str) : The location of the s3 file url located within the web page.
                        This is a static xpath.

        Returns:
        - (str) : Ethier returns full_url or ''
        '''
        try:
            driver = self.driver
            last_row =  driver.find_element_by_xpath(xpath)
            driver.implicitly_wait(1)
            full_url = last_row.get_attribute("href")
            return full_url
        except Exception as error:
            log.error(
                {
                    "exception_type": type(error).__name__,
                    "error_reason": error.args,
                    "traceback": traceback.format_exc(),
                }
            )
            return ''



    def parse_s3_url(self, s3_url=None):
        '''
            Takes the s3 file location url from RM ui page and parses that
            url to produce a callable s3 call. An example url -
            https://app.recallmasters.com/storage/reporting/cd/7b/51414.mailing.2019-04-12.00.003.csv
    
            Parameters:
            - s3_url (str) : Url location captured from RM ui site.
    
            Returns:
            - key,bucket (2-tuple) : Either returns the key & buckets extracted 
                                     from the URL or a 2-tuple None object.
        '''
        try:
            # x = ['https://app', 'recallmasters.com/storage/reporting/cd/7b/51414.mailing.2019-04-12.00.003.csv']
            x = s3_url.split(".", 1)
            # y = ['recallmasters.com', 'storage', 'reporting/cd/7b/51414.mailing.2019-04-12.00.003.csv']
            y = x[1].split('/', 2)
            # z = ['recallmasters', 'com/storage/reporting/cd/7b/51414.mailing.2019-04-12.00.003.csv']
            z = x[1].split('.', 1)
            # reporting/cd/7b/51414.mailing.2019-04-12.00.003.csv
            key = y[2]
            # recallmasters
            bucket = z[0]
            # log.info(f"S3 metadata collected. key:{key}, bucket:{bucket}")
            return (key, bucket)
        except Exception as error:
            log.error(
                {
                    "exception_type": type(error).__name__,
                    "error_reason": error.args,
                    "traceback": traceback.format_exc(),
                }
            )
            return (None, None)


    def end_session(self):
        '''
            Simply ends the selenium session.
    
            Parameters:
            - None

            Returns:
            - None
        '''
        try:
            self.driver.close();
            self.driver.quit();
            log.info("Selenium session ended.")
        except Exception as error:
            log.error(
                {
                    "exception_type": type(error).__name__,
                    "error_reason": error.args,
                    "traceback": traceback.format_exc(),
                }
            )



    def navigate_to_communication_from_mailing(self, dropId=None):
        '''
            Allows selenium bot to navigate from 
            START -> https://app.recallmasters.com/communications/mailing/XXXX/
            to
            END -> https://app.recallmasters.com/communications/XXX/
            When triggering this script, selenium bot must be at starting
            webpage position.

            Parameters:
            - dropId (str) : this is included just for testing locally.
    
            Returns:
            - self.driver (selenium obj) : a webdriver with the new current window.
        '''
        driver = self.driver

        # Click on the Back button located at /communications/mailing/DropID
        driver.find_element(By.CSS_SELECTOR, ".fa-arrow-left").click()
        driver.implicitly_wait(2.5)

        # Input Drop ID into search located at /communications/mailing & click search
        driver.find_element_by_id("id_id").click()
        driver.find_element_by_id("id_id").clear()
        driver.find_element_by_id("id_id").send_keys(dropId)
        driver.find_element(By.CSS_SELECTOR, ".btn-primary > .fa").click()
        driver.implicitly_wait(2.5)

        # Grab all current windows. Only 1 window active.
        self.vars["window_handles"] = driver.window_handles

        # Click on Recall Reminder 2.0 located in column Campaign.
        # This will produce a new window because -> <html>::target=_blank.
        self.driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/table/tbody/tr/td[3]/a[1]').click()

        self.vars["new_window"] = self.wait_for_window(timeout=2000, driver=driver)

        driver.switch_to.window(self.vars["new_window"])

        self.driver = driver



    def navigate_to_plans_from_communications(self):
        '''
            Allows selenium bot to navigate from 
            START -> https://app.recallmasters.com/communications/XXXX/
            to
            END -> https://app.recallmasters.com/communications/XXXX/plans/
            When triggering this script, selenium bot must be at starting
            webpage position.

            Parameters:
            - dropId (str) : this is included just for testing locally.
    
            Returns:
            - self.driver (selenium obj) : a webdriver with the new current window.
        '''
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Plans").click()
        driver.implicitly_wait(1.5)



    def wait_for_window(self, timeout=0, driver=None):
        '''
            Allows time for selenium script to execute html code target=_blank.
            Once a new window is opened, isolate new window and return it.

            Parameters:
            - timeout (int) : If a user passes in 2000, then timeout total will be 2 seconds.
            - driver (class obj) : selenium chrome webdriver session.
    
            Returns:
            - new window (str) : Will return the new window id.
        '''
        time.sleep(round(timeout / 1000))
        # All current windows.
        wh_now = driver.window_handles
        # Had previously caputred all current windows when there was only 1 window.
        wh_then = self.vars["window_handles"]

        # .difference .pop will drop all windows that are in common from both sets.
        if len(wh_now) > len(wh_then):

            return set(wh_now).difference(set(wh_then)).pop()



if LOCAL_RUN == True:

    test = SeleniumDriver()

    logged_in = test.login_to_mailing(url='https://app.recallmasters.com/login/?next=/communications/mailing/1010')

    if logged_in == True:

        s3_file_url = test.get_mail_df_link(xpath='//*[@id="content"]/buefy/div/div/table/tbody[2]/tr/td[2]/a')
        key, bucket = test.parse_s3_url(s3_url=s3_file_url)
        print(f"s3_file_url --> {s3_file_url}")
        print(f"Key-->{key} \nBucket-->{bucket}\n\n")

        pandas_s3_url = test.get_pandas_df_link(xpath='//*[@id="content"]/buefy/div/div/div[5]/div/table/tbody[position()=last()]/tr[1]/td[3]/a')
        (key, bucket) = test.parse_s3_url(s3_url=pandas_s3_url)
        print(f"pandas_s3_url --> {pandas_s3_url}")
        print(f"Key-->{key} \nBucket-->{bucket}\n\n")

        # test.navigate_to_communication_from_mailing('8240')
        # communication_info = extract_communication_details(session=test.driver)
        # print(f"\ncommunication_info\n {communication_info}")

        # test.navigate_to_plans_from_communications()
        # plan_info = extract_plan_details(session=test.driver, communication_data=communication_info)
        # print(f"\nplan_info\n {plan_info}")

    test.end_session()

