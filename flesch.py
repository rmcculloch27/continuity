import csv
import datetime
import requests
from bs4 import BeautifulSoup
import nltk
from nltk import sent_tokenize, word_tokenize

nltk.download('punkt')
# Function to calculate the Flesch readability metrics
def calculate_flesch_metrics(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)

    total_words = len(words)
    total_sentences = len(sentences)

    total_syllables = 0
    for word in words:
        total_syllables += count_syllables(word)

    flesch_reading_ease = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    flesch_grade_level = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59

    return total_words, total_sentences, total_syllables, flesch_reading_ease, flesch_grade_level

# Function to count syllables in a word
def count_syllables(word):
    word = word.lower()
    if len(word) <= 3:
        return 1
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count = 1
    return count

# Function to scrape a URL and extract text
def scrape_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from <p> tags under <h1> through <h4>
        text_data = []
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for header in headers:
            header_text = header.get_text().strip()
            p_elements = header.find_all_next('p')
            for p in p_elements:
                p_text = p.get_text().strip()
                if p_text:
                    text_data.append((header_text, p_text))

        return text_data

    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return []

def main():
    input_txt_file = '/Users/ryanmcculloch/Documents/scraper-demo/input_urls.txt'  # Replace with the path to your input URLs text file
    output_dir = '/Users/ryanmcculloch/Desktop/scraped-data/Flesch'  # Replace with the path where you want to save the CSV

    # Create a filename based on the current date and time
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    flesch_csv_file = f'{output_dir}/flesch_csv_{current_datetime}.csv'

    with open(flesch_csv_file, 'w', newline='') as csvfile:
        fieldnames = ['URL', 'Header', 'Text', 'Total Words', 'Total Sentences', 'Total Syllables', 'Flesch Reading Ease', 'Flesch Grade Level']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(input_txt_file, 'r') as input_txt:
            for line in input_txt:
                url = line.strip()
                if url:
                    text_data = scrape_url(url)
                    total_flesch_reading_ease = 0
                    total_flesch_grade_level = 0
                    total_segments = 0
                    for header, text in text_data:
                        total_words, total_sentences, total_syllables, flesch_reading_ease, flesch_grade_level = calculate_flesch_metrics(text)
                        writer.writerow({
                            'URL': url,
                            'Header': header,
                            'Text': text,
                            'Total Words': total_words,
                            'Total Sentences': total_sentences,
                            'Total Syllables': total_syllables,
                            'Flesch Reading Ease': flesch_reading_ease,
                            'Flesch Grade Level': flesch_grade_level
                        })
                        total_flesch_reading_ease += flesch_reading_ease
                        total_flesch_grade_level += flesch_grade_level
                        total_segments += 1

                    if total_segments > 0:
                        # Calculate average Flesch scores for the URL
                        avg_flesch_reading_ease = total_flesch_reading_ease / total_segments
                        avg_flesch_grade_level = total_flesch_grade_level / total_segments

                        # Write the average scores to the CSV for the URL
                        writer.writerow({
                            'URL': url,
                            'Header': 'URL Average',
                            'Text': '',
                            'Total Words': '',
                            'Total Sentences': '',
                            'Total Syllables': '',
                            'Flesch Reading Ease': avg_flesch_reading_ease,
                            'Flesch Grade Level': avg_flesch_grade_level
                        })


if __name__ == '__main__':
    main()
