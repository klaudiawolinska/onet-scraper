# Onet News Archive Scraper

This program scrapes the news archive of Onet.pl for metadata, including dates, times, URLs, and titles. Additionally, it extracts the full content of each article based on the metadata and saves the data as individual text files.

## Features

- Scrape news metadata from Onet's archive for a specified date range.
- Extract full article content.
- Save the extracted metadata as a CSV file.
- Save the content of each article as a text file.

## Requirements

- Python 3.x
- pandas
- requests
- BeautifulSoup from bs4

You can install the required Python libraries using pip:

```
pip install pandas requests beautifulsoup4
```

## Usage

To run the program:

```
python onet_scraper.py -s START_DATE -e END_DATE -p SAVE_PATH
```

- `START_DATE`: The start date for scraping in the format `YYYY-MM-DD`.
- `END_DATE`: The end date for scraping in the format `YYYY-MM-DD`.
- `SAVE_PATH`: Directory path where you want to save the CSV and article files.

### Example:

```
python onet_scraper.py -s 2023-01-01 -e 2023-01-31 -p /path/to/save/directory
```

This command will scrape metadata and articles from January 1, 2023, to January 31, 2023, and save the data to the specified directory.

## Docker Instructions

If you'd prefer to run this scraper within a Docker container, follow these steps:

### Building the Docker Image

1. Navigate to the project directory where the `Dockerfile` is located.
2. Run the following command to build the Docker image:
```bash
docker build -t onet-scraper .
```
This command builds the Docker image with the tag `onet-scraper`.

### Running the Docker Container

After building the image, run the container with the following command:
```bash
docker run -v $(pwd):/app/ onet-scraper -s START_DATE -e END_DATE -p PATH
```
Replace `START_DATE`, `END_DATE`, and `PATH` with appropriate values.

## Disclaimer

Web scraping may be subject to legal and ethical considerations, especially if it disrupts the operation of the target website. Before using this script, please consult Onet.pl's terms of service and ensure you have the right to access and scrape the data. This program is intended for educational purposes only, and users are responsible for how they choose to utilize it.

## Contributing

Feel free to fork this repository, create a feature branch, and send us a pull request. For major changes, please open an issue first to discuss what you'd like to change.

## License

This project is licensed under the MIT License.