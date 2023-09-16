import traceback
from selenium.webdriver.common.by import By
from box import Box


'''
    Used as a flag trigger. Running selenium headless on lambda and normal 
    selenium locally requires a different set of settings. Very annoying -_-
    but fortunetly this is a decent way to handle that. Must manually switch 
    the flag. 
    Default is a remote run on aws lambda, therefore, LOCAL_RUN=False.
    Must be changed in func.selen.py as well.
'''
LOCAL_RUN = False 
PRINT = True


if LOCAL_RUN == True: 
    import sys
    sys.path.append(".")
    from src.lib.log import get_logger
else: # Headless selenium with lambda + api gateway
    from lib.log import get_logger


log = get_logger(
    "extract.py",
    "'[%(levelname)s] [%(name)s]  [%(asctime)s] [%(funcName)s::%(lineno)d] [%(message)s]'",
)


# https://selenium-python.readthedocs.io/api.html#selenium.webdriver.remote.webelement.WebElement.get_attribute
def extract_communication_details(session=None, name_xpath='//*[@id="id_name"]',
                                started_date='//*[@id="id_started_date"]', 
                                dealer_xpath='//*[@id="select2-id_dealer-container"]',
                                hyperion_xpath='//*[@id="id_store_hyperion"]', 
                                isActive='is_active', 
                                include_other_dealers='include_other_dealers',
                                deduplicate_by_address='deduplicate_by_address', 
                                exclude_if_previously_contacted='exclude_if_previously_contacted',
                                is_manual='is_manual',
                                is_seed='is_seed',
                                centroid_zip='//*[@id="select2-id_dealer_zipcode_centroid-container"]',
                                is_dms='is_dms',
                                dms_max_radius='//*[@id="id_dms_max_radius"]',
                                dms_zipcode_list='id_dms_zipcode_list',
                                exclude_dms_pma='exclude_dms_pma',
                                is_prospect='is_prospect',
                                prospect_max_radius='//*[@id="id_prospect_max_radius"]',
                                prospect_zipcode_list='id_prospect_zipcode_list',
                                exclude_prospect_pma='exclude_prospect_pma',
                                co_op='co_op',
                                dealer_name='//*[@id="id_dealer_name"]',
                                dealer_phone='//*[@id="id_dealer_phone"]',
                                dealer_website_link='//*[@id="id_dealer_website_link"]',
                                curr_dealer_address='//*[@id="id_current_dealer_address"]',
                                override_dealer_address='override_dealer_address',
                                has_email_append='has_email_append',
                                has_phone_append='has_phone_append',
                                recall_reminder_checked='//*[@id="id_type_0"]'):
    '''
        Scraps individual campaign data located at 
        https://app.recallmasters.com/communications/###/
        Function has built in dom locations for static web objects where
        data is expected to be located. All locations can be overwritten 
        with the function call. 
        
        Parameters:
        - DOM locations (str) : This function takes several xpath & ids to locate static
                                dom objects.

        Returns:
        - communication_data (Box) : all extracted data from page https://app.recallmasters.com/communications/xxxx/
    '''
    try:
        driver = session # ~~ Must be the session driver, not the session class.  ~~
        communication_data = {}

        # If checked == True, then proceed with extraction -> 'Recall Reminder 2.0'.
        links = driver.find_elements_by_xpath(str(recall_reminder_checked))
        driver.implicitly_wait(1)
        recall_reminder_checked = links[0].get_attribute('checked')
        communication_data['recall_reminder_checked'] = recall_reminder_checked
        local('recall_reminder_checked', recall_reminder_checked)

        
        if bool(recall_reminder_checked) == True:
            # 'Name' at the top of the page : type=text.
            links = driver.find_elements_by_xpath(str(name_xpath))
            driver.implicitly_wait(1)
            name = links[0].get_attribute('value')
            communication_data['name'] = name
            local('name', name)

            # 'Started date' at the top of the page : type=text.
            links = driver.find_elements_by_xpath(str(started_date))
            driver.implicitly_wait(1)
            started_date = links[0].get_attribute('value')
            communication_data['started_date'] = started_date
            local('started_date', started_date)

            # 'Dealer' at the top of the page : type=combobox.
            links = driver.find_elements_by_xpath(str(dealer_xpath))
            driver.implicitly_wait(1)
            dealer = links[0].get_attribute('title')
            communication_data['dealer'] = dealer
            local('dealer', dealer)

            # 'Store Hyperion' at the top of the page : type=text.
            links = driver.find_elements_by_xpath(str(hyperion_xpath))
            driver.implicitly_wait(1)
            store_hyperion = links[0].get_attribute('value')
            communication_data['store_hyperion'] = store_hyperion
            local('store_hyperion', store_hyperion)

            # 'Is active' checkbox at the top of the page : type=checkbox.
            links = driver.find_elements_by_name(str(isActive))
            driver.implicitly_wait(1)
            isActive = links[0].is_selected()
            communication_data['isActive'] = isActive
            local('isActive', isActive)

            # 'Do Not Suppress VINs Contacted or Reserved by Other Active Dealers' near top : type=checkbox.
            links = driver.find_elements_by_name(str(include_other_dealers))
            driver.implicitly_wait(1)
            include_other_dealers = links[0].is_selected()
            communication_data['include_other_dealers'] = include_other_dealers
            local('include_other_dealers', include_other_dealers)

            # 'Deduplicate by address' near top of page : type=checkbox.
            links = driver.find_elements_by_name(str(deduplicate_by_address))
            driver.implicitly_wait(1)
            deduplicate_by_address = links[0].is_selected()
            communication_data['deduplicate_by_address'] = deduplicate_by_address
            local('deduplicate_by_address', deduplicate_by_address)

            # 'Do Not Include Records If Previously Contracted' near top of page : type=checkbox.
            links = driver.find_elements_by_name(str(exclude_if_previously_contacted))
            driver.implicitly_wait(1)
            exclude_if_prev_contacted = links[0].is_selected()
            communication_data['exclude_if_prev_contacted'] = exclude_if_prev_contacted
            local('exclude_if_prev_contacted', exclude_if_prev_contacted)

            # 'Manual Campaign' near top of page: type=checkbox.
            links = driver.find_elements_by_name(str(is_manual))
            driver.implicitly_wait(1)
            is_manual_campaign = links[0].is_selected()
            communication_data['is_manual_campaign'] = is_manual_campaign
            local('is_manual_campaign', is_manual_campaign)

            # 'Seed Mailer?' near top of page : type=checkbox.
            links = driver.find_elements_by_name(str(is_seed))
            driver.implicitly_wait(1)
            is_seed = links[0].is_selected()
            communication_data['is_seed'] = is_seed
            local('is_seed', is_seed)

            # 'Centroid ZIP code' near middle of website : type=combobox.
            centroid_zip = driver.find_elements_by_xpath(str(centroid_zip))
            driver.implicitly_wait(1)
            centroid_zip_title = centroid_zip[0].get_attribute('title')
            communication_data['centroid_zip_title'] = centroid_zip_title
            local('centroid_zip_title', centroid_zip_title)

            '''
                DMS Section of website
            '''
            # 'DMS' near middle of website : type=checkbox.
            links = driver.find_elements_by_name(str(is_dms))
            driver.implicitly_wait(1)
            is_dms = links[0].is_selected()
            communication_data['is_dms'] = is_dms
            local('is_dms', is_dms)
            
            if bool(is_dms) == True: 
                # 'DMS Max Radius' near middle of website : type=text.
                dms_max_radius = driver.find_elements_by_xpath(str(dms_max_radius))
                driver.implicitly_wait(1)
                dms_max_radius = dms_max_radius[0].get_attribute('value')
                communication_data['dms_max_radius'] = dms_max_radius
                local('dms_max_radius', dms_max_radius)
    
                # 'DMS ZIPCODE LIST' near middle of website : type=textarea.
                elem = driver.find_elements_by_id(dms_zipcode_list)
                for i, textarea in enumerate(elem):
                    dms_str_obj = textarea.text
                dms_zipcode_list = dms_str_obj.split('\n')
                communication_data['dms_zipcode_list'] = dms_zipcode_list
                local('dms_zipcode_list', dms_zipcode_list)
    
                # with open('DMS_zips.txt', 'w') as filehandle:
                #     for listitem in dms_zipcode_list:
                #         filehandle.write('%s\n' %listitem)
    
                # 'Exclude PMA?' near middle of website : type=checkbox.
                links = driver.find_elements_by_name(str(exclude_dms_pma))
                driver.implicitly_wait(1)
                exclude_dms_pma = links[0].is_selected()
                communication_data['exclude_dms_pma'] = exclude_dms_pma
                local('exclude_dms_pma', exclude_dms_pma)
            else:
                log.info(f"is_dms is off. Value:{is_dms}")

            '''
                Prospect Section of website
            '''
            # 'PROSPECT' near middle of website : type=checkbox.
            links = driver.find_elements_by_name(str(is_prospect))
            driver.implicitly_wait(1)
            is_prospect = links[0].is_selected()
            communication_data['is_prospect'] = is_prospect
            local('is_prospect', is_prospect)

            if bool(is_prospect) == True: 
                # 'Prospect Max Radius' near middle of website : type=text.
                prospect_max_radius = driver.find_elements_by_xpath(str(prospect_max_radius))
                driver.implicitly_wait(1)
                prospect_max_radius = prospect_max_radius[0].get_attribute('value')
                communication_data['prospect_max_radius'] = prospect_max_radius
                local('prospect_max_radius', prospect_max_radius)
    
                # 'PROSPECT ZIPCODE LIST' near middle of website : type=textarea.
                elem = driver.find_elements_by_id(prospect_zipcode_list)
                for i, textarea in enumerate(elem):
                    prospect_str_obj = textarea.text
                prospect_zipcode_list = prospect_str_obj.split('\n')
                communication_data['prospect_zipcode_list'] = prospect_zipcode_list
                local('prospect_zipcode_list', prospect_zipcode_list)
    
                with open('Prospect_zips.txt', 'w') as filehandle:
                    for listitem in prospect_zipcode_list:
                        filehandle.write('%s\n' %listitem)
    
                # 'Exclude PMA?' near middle of website : type=checkbox.
                links = driver.find_elements_by_name(str(exclude_prospect_pma))
                driver.implicitly_wait(1)
                exclude_prospect_pma = links[0].is_selected()
                communication_data['exclude_prospect_pma'] = exclude_prospect_pma
                local('exclude_prospect_pma', exclude_prospect_pma)
            else:
                log.info(f"is_prospect is off. Value:{is_prospect}")

            '''
                VDP Template
            '''
            # 'VDP Template' near bottom of website : type=combobox.
            links = driver.find_elements_by_name(str(co_op))
            driver.implicitly_wait(1)
            co_op = links[0].is_selected()
            communication_data['co_op'] = co_op
            local('co_op', co_op)

            '''
                Override dealer settings
            '''
            # 'Dealer Name' near bottom of page : type=text.
            dealer_name = driver.find_elements_by_xpath(str(dealer_name))
            driver.implicitly_wait(1)
            dealer_name = dealer_name[0].get_attribute('value')
            communication_data['dealer_name'] = dealer_name
            local('dealer_name', dealer_name)

            # 'Dealer Phone' near bottom of page. : type=text.
            dealer_phone = driver.find_elements_by_xpath(str(dealer_phone))
            driver.implicitly_wait(1)
            dealer_phone = dealer_phone[0].get_attribute('value')
            communication_data['dealer_phone'] = dealer_phone
            local('dealer_phone', dealer_phone)

            # 'Dealer Website Link' near bottom of page : type=text.
            dealer_website_link = driver.find_elements_by_xpath(str(dealer_website_link))
            driver.implicitly_wait(1)
            dealer_website_link = dealer_website_link[0].get_attribute('value')
            communication_data['dealer_website_link'] = dealer_website_link
            local('dealer_website_link', dealer_website_link)

            # 'Current dealer address' near nottom of page : type=text.
            curr_dealer_address = driver.find_elements_by_xpath(str(curr_dealer_address))
            driver.implicitly_wait(1)
            curr_dealer_address = curr_dealer_address[0].get_attribute('value')
            communication_data['curr_dealer_address'] = curr_dealer_address
            local('curr_dealer_address', curr_dealer_address)

            # 'Override dealer address for this Campaign?' near borrom : type=checkbox.
            links = driver.find_elements_by_name(str(override_dealer_address))
            driver.implicitly_wait(1)
            override_dealer_address = links[0].is_selected()
            communication_data['override_dealer_address'] = override_dealer_address
            local('override_dealer_address', override_dealer_address)

            '''
                Append settings
            '''
            # 'Need Email Appead?' at bottom of page : type=checkbox.
            links = driver.find_elements_by_name(str(has_email_append))
            driver.implicitly_wait(1)
            has_email_append = links[0].is_selected()
            communication_data['has_email_append'] = has_email_append
            local('has_email_append', has_email_append)

            # 'Need Phone Append?' at bottom of page : type=checkbox.
            links = driver.find_elements_by_name(str(has_phone_append))
            driver.implicitly_wait(1)
            has_phone_append = links[0].is_selected()
            communication_data['has_phone_append'] = has_phone_append
            local('has_phone_append', has_phone_append)

            return Box(communication_data)
        else:
            log.info(f"Communication data is not a Recall Reminder 2.0")
            return {}
    except Exception as error:
        log.error(
            {
                "exception_type": type(error).__name__,
                "error_reason": error.args,
                "traceback": traceback.format_exc(),
            }
        )

        return {}




def extract_plan_details(session=None, communication_data=None):
    '''
        Scraps data from table located at 
        https://app.recallmasters.com/communications/xxxx/plans/
        Only the last row on the table is valid. Function stops 
        executing once it detects that a row is empty. 

        Helpful notes:
        <th>	Defines a header cell in a table
        <tr>	Defines a row in a table
        <td>	Defines a cell in a table

        Parameters:
        - session (selenium) : an active web session driver.
        Returns:
        - results (box) : values extracted from last valid row on table.
    '''
    try:
        # The variable that will capture extracted data.
        results = {'total':0, 'prospect':0, 'lapsed':0, 'recent':0, 'sns':0, 'l1':0, 'l2':0,
                    'l3':0, 'l4':0, 'l5':0, 'target_date':0, 'expiration_date':0, 'delete':0}

        if bool(communication_data.get('recall_reminder_checked')) == True:
            driver = session # ~~ Must be the session driver, not the session class.  ~~
    
            # Helps determine when the code has reached the last valid row.
            done = False 
    
            # Need to iterate on xpaths as bot moves down the rows of the table.
            index = 0 
    
            # The row headers.
            headers = ['total', 'prospect', 'lapsed', 'recent', 'sns', 'l1', 'l2', 'l3', 'l4', 'l5',
                        'target_date', 'expiration_date', 'delete']
    
            # Used to keep track/iterate over the headers column/list.
            header_index = 0
    
            # # The variable that will capture extracted data.
            # results = {'total':0, 'prospect':0, 'lapsed':0, 'recent':0, 'sns':0, 'l1':0, 'l2':0,
            #             'l3':0, 'l4':0, 'l5':0, 'target_date':0, 'expiration_date':0, 'delete':0}
    
            # Locate the specific table on the website.
            table_id = driver.find_element(By.ID, 'id_plan')
    
            # Get all the rows within that table.
            rows = table_id.find_elements(By.TAG_NAME, "tr")
    
            # Remove <thead> row.
            body_rows = rows[1:]
    
            # Iterate over the table row by row.
            for row in body_rows:
                # If done, then exit the function.
                if done==True: break
    
                # Get all the cells located within this row.
                cells = row.find_elements(By.TAG_NAME, "td")
    
                # Iteracte over the cells, cell by cell.
                for cell in cells:
                    # # If done, then exit the function.  
                    # if done==True: break
    
                    # print('\nIndex:', index)
                    # print(f'header_column:{headers[header_index]} --> Header_index:{header_index}')
    
                    # Dynamically change the xpath according to which cell the bot is looking at.
                    # Necessary due to nature of table -> nested <span> tags within each cell -_-
                    if header_index==0:
                        xpath= f'//*[@id="id_form-{index}-{headers[header_index]}_quantity"]'
                    elif header_index==10 or header_index==11:
                        xpath = f'//*[@id="id_form-{index}-{headers[header_index]}"]'
                    else:
                        xpath= f'//*[@id="id_form-{index}-{headers[header_index]}_percent"]'
    
                    # Here is another piece of code necessary due to table composition.
                    # Index 12 is the strange/useless delete cell <td><\td>
                    if header_index != 12:
                        # Use dynamic xpath on the percent <span>.
                        percent_cell = cell.find_element(By.XPATH, xpath)
                        # Get its value.
                        value = percent_cell.get_attribute('value')
    
                        # Helps to detect if the bot is reading a blank row. If so -> done.
                        if header_index==0 and (value==None or value=='' or value==0):
                            done = True
    
                        # If this is this is still a valid row.
                        if done == False:
                            # For some reason value is returned as '# %'
                            percentTotal_symbol = value.split()
    
                            # print('value:', value)
                            # print('type(value):', type(value))
                            # print('percentTotal_symbol:', percentTotal_symbol)
    
                            # Need this because sometimes target_date & Expiration_date are empty.
                            # If they are empty, simply leave the default value declared, else
                            # assign the new value.
                            if percentTotal_symbol != []:
                                results[headers[header_index]] = percentTotal_symbol[0]
    
                        # print('value:', value)
                        # print('type(value):', type(value))
                        # print('done:', done)
    
                    # On to the next column in the table.
                    header_index += 1
    
                # if index == 0: break
    
                # iterate on xpath code.
                index += 1
    
                # Reset columns because we are now on a new row.
                header_index = 0
    
            # log.info(f"Results: {results}")
            # print(results)
            return Box(results)
        else:
            log.info(f"Communication data is not a Recall Reminder 2.0, therefore \
            do not extract plan details.")
            return {}

    except Exception as error:
        log.error(
            {
                "exception_type": type(error).__name__,
                "error_reason": error.args,
                "traceback": traceback.format_exc(),
            }
        )
        return results


def local(name, item):
    if LOCAL_RUN==True and PRINT==True:
        print(f"\n{name}: {item} \n")

