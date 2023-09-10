#!/usr/bin/env python

# Standard libraries
import os
import logging
import argparse
from datetime import date, timedelta

# Web scraping and HTTP related
import requests
from bs4 import BeautifulSoup

# Data processing
import pandas as pd

import re


# Setting up basic configuration for logging with an INFO level.
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')


def get_metadata(start_date, end_date, headers):
    """
    Retrieves news metadata from Onet's archive for a given date range.

    Parameters:
    - start_date: Start of the date range.
    - end_date: End of the date range.

    Returns:
    - Pandas DataFrame containing news metadata.
    """
    
    # Calculate the total number of days in the given date range.
    no_of_days = (end_date - start_date).days

    # Generate a list of formatted date strings for the given range.
    date_list = [(start_date + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(no_of_days + 1)]
        
    # Construct URLs for each date to scrape the Onet archive.
    urls_list = ['https://wiadomosci.onet.pl/archiwum/' + date for date in date_list]

    # Initialize empty lists to store scraped data.
    times, urls, titles = [], [], []
    result = pd.DataFrame()

    # Iterate over each URL to scrape data.
    for url in urls_list:
        try:
            response = requests.get(url, headers=headers, timeout=10) 
            response.raise_for_status()  # raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        except requests.RequestException as e:
            logging.error(f"Error fetching URL {url}. Error: {e}")
            continue
        
        content = BeautifulSoup(response.text, 'html.parser')
        
        # Find the day's archive section on the webpage.
        dayInArchive = content.find(class_='dayInArchive')
        
        # Extract news times from the webpage.
        times_raw = dayInArchive.find_all(class_="itemTime")
        for time_raw in times_raw:
            times.append(time_raw.contents[0].strip())

        # Extract news URLs and titles from the webpage.
        items_raw = dayInArchive.find_all(class_="itemTitle")
        for item_raw in items_raw:
            urls.append(item_raw['href'])
            titles.append(item_raw.contents[0])
            
        archive_date = url.split('/')[-1]

        # Aggregate the scraped data into a DataFrame.
        result = pd.concat([result, pd.DataFrame(list(zip([archive_date]*len(titles), times, urls, titles)),
                                columns=['date', 'time', 'url', 'title'])])

    return result


def create_metadata_file(start_date, end_date, path, metadata):
    """
    Creates a CSV file containing news metadata.

    Parameters:
    - start_date: Start of the date range.
    - end_date: End of the date range.
    - path: Directory to save the CSV file.

    Returns:
    None
    """
    filepath = f'{path}/onet_metadata.csv'

    # Ensure the directory exists; if not, create it.
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Generate the metadata and save it to a CSV file.
    metadata.to_csv(filepath, index=False)
    
    # Log the successful creation of the file.
    logging.info(f'New file created: {filepath}')


def extract_and_save_articles(start_date, end_date, path, metadata):
    """
    Extracts article details and saves them as text files.

    Parameters:
    - start_date: Start of the date range.
    - end_date: End of the date range.
    - path: Directory to save the article files.
    - metadata: DataFrame containing article metadata.
    """
    
    logging.info(f"Starting data extraction for dates: {start_date} to {end_date}")
    
    # Iterate over each row (article metadata) in the metadata DataFrame.
    for _, article_details in metadata.iterrows():
        url = article_details['url']

        try:
            # Make a GET request to fetch the content of the article.
            response = requests.get(url)
            content = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the 'lead' section of the article.
            lead_elements = content.find(class_="hyphenate lead")

            # Check if the 'lead' section is present; if not, log a warning and skip the article.
            if not lead_elements:
                logging.warning(f"No lead found for URL: {url}")
                continue

            # Construct the full text of the article from the lead and main body.
            lead = lead_elements.text
            main_body = content.find_all('p')
            full_text = lead + ' ' + ' '.join([m.text for m in main_body])

            # Define the file path where the article will be saved.
            # The format will be 'specified_path/date/article_id.txt'
            filepath = os.path.join(path, article_details['date'], f"{url.split('/')[-1]}.txt")

            # Ensure the target directory exists; if not, create the necessary directories.
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Open the target file in write mode and save the article's content.
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(full_text)
            
            # Log the successful extraction and saving of the article.
            logging.info(f"Data extracted and saved for URL: {url}")

        except Exception as e:
            # Log any errors encountered during the processing of an article.
            logging.error(f"Error processing URL {url}. Error: {e}")

    # Log the completion of data extraction for the given date range.
    logging.info(f"Finished data extraction for dates: {start_date} to {end_date}")


def is_valid_date(date_string):
    """Check if the provided date string matches the format YYYY-MM-DD."""
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', date_string))


if __name__ == "__main__":
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Scrape Onet's news archive for metadata.")

    # Add the arguments
    parser.add_argument("-s", "--start_date", type=str, help="Start date in the format YYYY-MM-DD.", required=True)
    parser.add_argument("-e", "--end_date", type=str, help="End date in the format YYYY-MM-DD.", required=True)
    parser.add_argument("-p", "--path", type=str, help="Directory path to save the CSV file.", required=True)

    args = parser.parse_args()

    if not (is_valid_date(args.start_date) and is_valid_date(args.end_date)):
        logging.error("Dates should be in the format YYYY-MM-DD.")
        exit(1)

    start_date_obj = date(*map(int, args.start_date.split('-')))
    end_date_obj = date(*map(int, args.end_date.split('-')))

    # Fetch the metadata for articles between the specified start and end dates.
    logging.info(f"Starting metadata scraping for dates: {args.start_date} to {args.end_date}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    metadata = get_metadata(start_date_obj, end_date_obj, headers=headers)
 
    # Generate and save a CSV file containing the fetched metadata.
    create_metadata_file(start_date_obj, end_date_obj, args.path, metadata)

    # Using the fetched metadata, extract the full content of each article and save it as a text file.
    extract_and_save_articles(start_date_obj, end_date_obj, args.path, metadata)