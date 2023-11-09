import os
import csv
import requests
from bs4 import BeautifulSoup
from collections import Counter
import logging
import datetime

output_dir = '/Users/ryanmcculloch/Desktop/scraped-data/accessibility/'
os.makedirs(output_dir, exist_ok=True)
# Set up logging to a file named accessibility.log
log_file_path = '/Users/ryanmcculloch/Desktop/scraped-data/accessibility/accessibility.log'
logging.basicConfig(filename=log_file_path, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def get_current_datetime():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

# Define the header with column names
header = ['URL', 'Total Non-Text Content', 'Total ARIA Non-Text Content', 'element_counts', 'alt_attr_on_img_total', 'img_elements']

# Function to count non-text content and ARIA labels
def count_non_text_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            non_text_elements = soup.find_all(['img', 'button', 'audio', 'video', 'canvas', 'iframe', 'object'])

            # Use Counter to determine the number of each type
            element_counts = Counter(element.name for element in non_text_elements)

            total_non_text_content = len(non_text_elements)
            total_aria_non_text_content = sum(1 for elem in non_text_elements if elem.get('aria-label') or elem.get('aria-labelledby'))

            # Check for 'img' elements and their 'alt' attribute
            img_elements = soup.find_all('img')
            alt_attr_on_img_total = sum(1 for elem in img_elements if elem.get('alt'))

            if not img_elements:
                logging.info(f"No image elements found on the page: {url}")
            

    #         # Check for G196 groups
    #         G196_groups = 0
    #         HasAltTags = False
    #         current_group = 0

    #         for element in non_text_elements:
    #             tag = element.name
    #             if tag in {'img', 'li', 'ul'}:
    #                 current_group += 1
    #             else:
    #                 if current_group >= 2:
    #                     G196_groups += 1
    #                     if 'alt' in element.attrs:
    #                         HasAltTags = True
    #                 current_group = 0

    #         # Return the values directly
    #         return total_non_text_content, total_aria_non_text_content, element_counts, alt_attr_on_img_total, img_elements, G196_groups, HasAltTags
    #     else:
    #         logging.error(f"Failed to retrieve the webpage: {url}")
    #         return None, None, None, None, None, None, None
    # except Exception as e:
    #     logging.error(f"Error while processing {url}: {str(e)}")
    #     return None, None, None, None, None, None, None

            return total_non_text_content, total_aria_non_text_content, element_counts, alt_attr_on_img_total, img_elements
        else:
            logging.error(f"Failed to retrieve the webpage: {url}")
            return None, None, None, None, None
    except Exception as e:
        logging.error(f"Error while processing {url}: {str(e)}")
        return None, None, None, None, None

# Read input URLs from a file with the full path
input_file = '/Users/ryanmcculloch/Documents/scraper-demo/input_urls.txt'
with open(input_file, 'r') as file:
    urls = [line.strip() for line in file]

results = []

# Process each URL and collect results
for url in urls:
    total_non_text_content, total_aria_non_text_content, element_counts, alt_attr_on_img_total, img_elements = count_non_text_content(url)
    if total_non_text_content is not None:
        result = [url, total_non_text_content, total_aria_non_text_content]
        if element_counts:
            result.extend(element_counts.items())
        results.append(result)

        # Create an actionable insights report for 'img' elements without 'alt' attributes
        if alt_attr_on_img_total < len(img_elements):
            actionable_insights_file = os.path.join(output_dir, 'actionable_insights_report.csv')
            with open(actionable_insights_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                for img_element in img_elements:
                    if not img_element.get('alt'):
                        img_src = img_element.get('src')
                        other_attributes = " ".join([f"{key}='{value}'" for key, value in img_element.attrs.items() if key != 'src'])
                        csv_writer.writerow([url, img_src, other_attributes])

# Write results to a CSV file in the specified output directory
output_file = os.path.join(output_dir, 'accessibility.csv')
with open(output_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    header = ['URL', 'Total Non-Text Content', 'Total ARIA Non-Text Content']
    header.extend(element_counts.keys())
    csv_writer.writerow(header)
    for result in results:
        csv_writer.writerow(result)

print(f"Results saved to {output_file}")
