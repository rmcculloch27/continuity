import re
import csv
import time
import logging
import datetime
import requests
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import from css_parser_local.py
from css_parser_local import usa_components

# Initialize the Selenium WebDriver with the path to your Chrome WebDriver executable
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    driver = webdriver.Chrome(options=options)
    return driver

input_txt_file = '/Users/ryanmcculloch/Documents/scraper-demo/input_urls.txt'  # Input file is in the same directory as your script
output_dir = '/Users/ryanmcculloch/Desktop/scraped-data/output.csv'  # Output directory with a trailing slash
os.makedirs(output_dir, exist_ok=True)

def get_current_datetime():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

# Create a filename based on the current date and time
current_datetime = get_current_datetime()
flesch_csv_file = os.path.join(output_dir, '1_flesch.csv')
uswds_csv_file = os.path.join(output_dir, f'{current_datetime}_uswds.csv')

 # Initialize the Selenium WebDriver
driver = initialize_driver()


# Open the output CSV file for writing for USWDS
with open(uswds_csv_file, 'w', newline='') as uswds_csvfile:
    uswds_fieldnames = ['Full URL', 'Total HTML Elements', 'Total CSS Elements', 'USWDS Present', 'USWDS Total', 'Page Depth', 'USWDS Percent', 'Charlie Components'] + list(usa_components.keys())
    uswds_writer = csv.DictWriter(uswds_csvfile, fieldnames=uswds_fieldnames)
    uswds_writer.writeheader()


# Define the components you want to count
for key in usa_components:
    usa_components[key] = 0

charlie = re.compile(r'(usa|aria)')


# Define a function to wait for the LCP element
def wait_for_lcp_or_title(driver):
    try:
        # Wait for the LCP element to be loaded
        lcp_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="usa"]'))  
        )
        logging.error("LCP image loaded successfully!")
        return lcp_element
    except TimeoutException:
        # If the LCP element doesn't appear, wait for the page title to change (indicating page load)
        WebDriverWait(driver, 5).until(EC.title_contains(""))  # Wait for a non-empty page title
        print("Page title changed, indicating page load.")
        return None
    except Exception as e:
       logging.error(f"Error waiting for LCP image or page title: {str(e)}")
       

# Define a function to scrape and write data for a single URL
def scrape_and_write_data(full_url, driver, writer):
    if not full_url:
        return

    try:
        driver.get(full_url)

        # Wait for the LCP image to be loaded
        lcp_element = wait_for_lcp_or_title(driver)
        if lcp_element:
            logging.error("LCP image loaded successfully!")

        # Scrape data and write to CSV
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.debug("Page source:\n%s", driver.page_source)

    #USWDS compliance section
        total_html_elements = len(soup.find_all())
        charlie_components = []

        # Loop through the discovered selectors on the webpage and count elements
        for selector in soup.select('[class]'):
            if selector.has_attr('class'):
                selector_names = selector['class']

        # Check each class name for 'usa' or 'aria' using regex
            for selector_name in selector_names:
                if re.search(r'.*(usa|aria).*', selector_name):
                    charlie_components.append(selector_name)
            else:
                logging.error(f"No CSS class found: {selector}")


            # Update the components dictionary with counts
            if selector_name in usa_components:
                usa_components[selector_name] += 1
            else: 
                logging.error(f"No CSS class found: {selector}")
            # Check if the selector contains 'usa' or 'aria'
            if charlie.search(selector_name):
                charlie_components.append(selector_name)
            else:
                logging.error(f"No aria or usa named components")

        uswds_src = re.compile(r'uswds|usa')
        # See if 'uswds.css' or 'uswds.min.css' is present in the page source
        

        #this needs tweaking but is returning values. Says re. match values span etc. 
        uswds_present = re.search(uswds_src, driver.page_source) or re.search(uswds_src+'min.css', driver.page_source)

        # Calculate the total number of unique CSS elements (charlie components)
        uswds_elements = len(set(charlie_components))

         # Find all unique CSS selectors
        css_selectors = set()
        for element in soup.find_all(True, class_=True, id=True):
            if element.has_attr('class'):
                css_selectors.add(element.get('class')[0])
            if element.has_attr('id'):
                css_selectors.add(element.get('id'))
        total_css_elements = len(css_selectors)

        # Calculate Page Depth
        page_depth = total_html_elements + total_css_elements

        # Calculate USWDS Percent (as a percentage)
        uswds_total = len(charlie_components)
        uswds_percent = (uswds_total / page_depth) * 100 if page_depth != 0 else 0
       

            # Write data to CSV
        data = {
                'Full URL': full_url,
                'Total HTML Elements': total_html_elements,
                'Total CSS Elements': total_css_elements,
                'USWDS Present': uswds_present,
                'USWDS Total': uswds_total,
                'Page Depth': page_depth,
                'USWDS Percent': uswds_percent,
                'Charlie Components': ', '.join(charlie_components)
        }
        uswds_writer.writerow(data)
        
    #return the data

    except Exception as e:
        # Log the error and continue to the next URL
        logging.error(f"Error scraping URL {full_url}: {str(e)}")
        
# Configure logging
logging.basicConfig(filename='scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')






# Open the output CSV file for writing for Flesch
with open(uswds_csv_file, 'w', newline='') as uswds_csvfile:
    uswds_fieldnames = ['Full URL', 'Total HTML Elements', 'Total CSS Elements', 'USWDS Present', 'USWDS Total', 'Page Depth', 'USWDS Percent', 'Charlie Components'] + list(usa_components.keys())
    uswds_writer = csv.DictWriter(uswds_csvfile, fieldnames=uswds_fieldnames)

    # Write the header for the file
    uswds_writer.writeheader()

    with open(input_txt_file, 'r') as input_txt:
        for line in input_txt:
            full_url = line.strip()  # Remove whitespace
            if full_url:
                data = scrape_and_write_data(full_url, driver, uswds_writer)
                if data: 
                     uswds_writer.writerow(data)   

# Close the Selenium WebDriver
driver.quit()
print(f"Done!")
