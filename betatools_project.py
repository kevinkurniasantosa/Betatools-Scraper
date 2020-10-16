import requests
import pygsheets
import re
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

######################################################## Global variables

# Define variables for Google Sheets
# gsheet_url = 'https://docs.google.com/spreadsheets/d/1k844exKXWi1GqLGveF6ECTd7XMztH5IAGF7RhpXoySA/edit#gid=0'
gsheet_url = 'https://docs.google.com/spreadsheets/d/1hCNu7YIt8f29ccTzc-lwtsu4aDUjE9qadRMwVFDvESI/edit#gid=2019527429'
gsheet_main_sheet = 'Data'
gsheet_credential = 'idkevinautomation.json'

# Get gsheet service
gc = pygsheets.authorize(service_file=gsheet_credential)
wb = gc.open_by_url(gsheet_url)
sheet = wb.worksheet_by_title(gsheet_main_sheet)

# For requests
# main_url = 'http://www.beta-tools.co.uk/online-brochure/'
main_url = 'https://www.beta-tools.com/en/products.html?betaframeconfig=a'

########################################################

def main():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable_infobars")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)  

    values = list(filter(None, sheet.get_col(1)))
    len_data = len(values)
    print('Number of data: ' + str(len_data))

    for x in range(len_data):
        print('---------------------------')
        data = sheet.cell('A' + str(x+2)).value
        data_name = sheet.cell('B' + str(x+2)).value

        if data == '' or data == None:
            break
        # For testing
        # elif x == 2:
        #     break
    
        driver.get(main_url)
        print('Scrape ' + data + ' - ' + data_name)
        search_bar = wait.until(lambda driver: driver.find_element_by_xpath("//input[@class='input-text']"))
        search_bar.send_keys(data)
        search_btn = driver.find_element_by_xpath("//button[@title='Search']")
        search_btn.click()

        try:
            time.sleep(1.5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            list_sku = soup.find('div', class_='category-products').ul
            first_sku = list_sku.find('li')
            sku_url = first_sku.div.find('a', class_='product-image')['href']
            
            res = requests.get(sku_url, headers={'User-Agent': 'Mozilla/5.0'})
            soupx = BeautifulSoup(res.text, 'html.parser')

            try:
                desc = soupx.find('div', class_='short-description').find('div', class_='std').find_all('div')
                # Text/Desc
                try:
                    text_result = ''
                    for y in range(len(desc)):
                        # if desc[0].text == 'NEW DESIGN' or desc[0].text == 'Can be fitted with thermoformed trays':
                        #     text_result = desc[1].text
                        # else:
                        #     text_result = desc[0].
                        if 'kg' in desc[y].text and '' in desc[y].text: 
                            break
                        else:
                            if y == 0:
                                text_result = text_result +  desc[y].text
                            else:
                                text_result = text_result + ' ' + desc[y].text
                except:
                    text_result = '-'
                print('Text: ' + str(text_result))

                # Weight
                try:
                    # weight_result = '-'
                    # if desc[0].text.strip() == 'NEW DESIGN' or desc[0].text == 'Can be fitted with thermoformed trays':
                    #     if 'kg' in desc[2].text.strip():
                    #         weight_result = desc[2].text.strip()
                    #         try:
                    #             m = re.match('.+ (.+)', str(weight_result))                              
                    #         except:
                    #             pass
                    #         try:
                    #             m = re.match(' (.+)', str(weight_result))                              
                    #         except:
                    #             pass
                    #         weight_result = m.group(1) 
                    # else:
                    #     if 'kg' in desc[1].text.strip():
                    #         weight_result = desc[1].text.strip()
                    #         try:
                    #             m = re.match('.+ (.+)', str(weight_result))                              
                    #         except:
                    #             pass
                    #         try:
                    #             m = re.match(' (.+)', str(weight_result))                              
                    #         except:
                    #             pass
                    #         weight_result = m.group(1)
                    weight_result = '-'
                    for z in range(len(desc)):
                        if 'kg' in desc[z].text and '' in desc[z].text:
                            weight_result = desc[z].text
                            try:
                                m = re.match(' (.+) kg', str(weight_result))   
                                weight_result = m.group(1) + ' kg'                           
                            except:
                                pass
                            try:
                                m = re.match('.+ (.+) kg', str(weight_result))     
                                weight_result = m.group(1) + ' kg'                         
                            except:
                                pass
                except:
                    weight_result = '-'
                print('Weight: ' + str(weight_result))
            except:
                text_result = '-'
                weight_result = '-'

            # Dimension
            try:
                dimension_content = soupx.find('div', class_='row linea_mediqa_right_prod')
                dimension_result = dimension_content.find('a', class_='img-disegno').img['src']
            except:
                dimension_result = '-'
            print('Dimension link: ' + str(dimension_result))
            
        except: # If the search returns no result
            print('NO SEARCH RESULT')
            text_result = '-'
            weight_result = '-'
            dimension_result = '-'
            pass

        ################################

        # Write the data to Gsheet
        try:
            sheet.update_value('C' + str(x+2), text_result) # Write text
            sheet.update_value('D' + str(x+2), weight_result) # Write weight
            sheet.update_value('E' + str(x+2), dimension_result) # Write dimension link
        except Exception as err:
            print('Error writing to gsheet: ' + str(err))


###################################### START HERE

if __name__ == '__main__':
    main()





